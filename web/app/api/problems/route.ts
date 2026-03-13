import { NextRequest, NextResponse } from "next/server";
import { getProblemsForPagination } from "@/features/question-solving/services/question-queries";
import { prisma } from "@/shared/lib/configs/prisma";

/**
 * GET /api/problems - Retrieve problems with pagination and filtering
 *
 * Query Parameters:
 * - userid: number - User ID for tracking attempts
 * - examName: string - Exam type (GRE, GMAT, CAT)
 * - sectionName: string - Section name (varies by exam)
 * - topics: string[] - JSON string of topics for filtering
 * - themes: string[] - JSON string of themes for filtering
 * - types: string[] - JSON string of types for filtering
 * - page: number - Page number for pagination (optional)
 * - pageSize: number - Number of items per page (optional)
 * - questionIds: string - Comma-separated list of specific question IDs to fetch (optional)
 */
export async function GET(request: NextRequest) {
   const { searchParams } = request.nextUrl;
   const userid = parseInt(searchParams.get("userid") || "1");
   const examNameParam = searchParams.get("examName");
   const sectionNameParam = searchParams.get("sectionName");

   const examNameRaw = (examNameParam && examNameParam !== 'undefined') ? examNameParam : "GRE";
   const sectionNameRaw = (sectionNameParam && sectionNameParam !== 'undefined') ? sectionNameParam : "quants";

   const examName = examNameRaw.toUpperCase();
   const sectionName = sectionNameRaw.toLowerCase();

   const topicsParam = searchParams.get("topics");
   const themesParam = searchParams.get("themes");
   const typesParam = searchParams.get("types");
   const page = searchParams.get("page") ? parseInt(searchParams.get("page")!) : null;
   const pageSize = searchParams.get("pageSize") ? parseInt(searchParams.get("pageSize")!) : null;
   const questionIdsParam = searchParams.get("questionIds");

   const topics = topicsParam ? JSON.parse(topicsParam) : null;
   const themes = themesParam ? JSON.parse(themesParam) : null;
   const types = typesParam ? JSON.parse(typesParam) : null;

   const filters = { topics, themes, types };

   // Parse specific question IDs if provided
   const specificQuestionIds = questionIdsParam ?
      questionIdsParam.split(',').map(id => parseInt(id.trim())) : null;

   try {
      // 1. Resolve Exam Type Dynamically
      const examTypeRecord = await prisma.examtypes.findFirst({
         where: { name: { equals: examName, mode: 'insensitive' } }
      });

      if (!examTypeRecord) {
         return NextResponse.json(
            { error: `Invalid exam type: ${examName}`, validExamTypes: ["GRE", "GMAT", "CAT"] },
            { status: 400 }
         );
      }

      const examtypeid = examTypeRecord.examtypeid;

      // 2. Resolve Section(s) Dynamically
      let sections;
      if (sectionName === "mixed" || sectionName === "all") {
         sections = await prisma.sections.findMany({
            where: { examtypeid: examtypeid }
         });
      } else {
         sections = await prisma.sections.findMany({
            where: {
               examtypeid: examtypeid,
               name: { equals: sectionName, mode: 'insensitive' }
            }
         });
      }

      if (sections.length === 0) {
         return NextResponse.json(
            { error: `Section '${sectionName}' not found for exam ${examName}` },
            { status: 404 }
         );
      }

      // Use all matching section IDs (supports legacy duplicates or multiple partitions)
      // eslint-disable-next-line
      const sectionid = sections.length === 1 ? sections[0].sectionid : sections.map((s: any) => s.sectionid);

      // Handle specific question IDs request (for cache system)
      if (specificQuestionIds && specificQuestionIds.length > 0) {
         console.log(`🎯 Fetching specific questions by IDs: ${specificQuestionIds.slice(0, 5).join(', ')}`);

         // Use pagination service to get both individual problems and problem sets
         const { problemData: allProblems } = await getProblemsForPagination(userid, examtypeid, sectionid, filters);

         // Filter to only include problems/sets that contain our target question IDs
         // eslint-disable-next-line
         const filteredProblems = allProblems.filter((item: any) => {
            if ('problems' in item && 'isExpanded' in item) {
               // For problem sets, check if any child problems match our IDs
               // eslint-disable-next-line
               return item.problems.some((child: any) => specificQuestionIds.includes(Number(child.problemid)));
            } else {
               // For individual problems, check if the ID matches
               return specificQuestionIds.includes(Number(item.problemid));
            }
         });

         return NextResponse.json({
            problemData: filteredProblems,
            totalProblems: filteredProblems.length,
            requestType: 'specific_ids',
            pagination: {
               examName,
               sectionName,
               topics,
               themes,
               types,
               questionIds: specificQuestionIds,
            },
         });
      }

      // Get all problems
      const { problemData, totalProblems } = await getProblemsForPagination(
         userid,
         examtypeid,
         sectionid,
         filters
      );

      // Handle page-specific fetching (client-side slicing simulator)
      if (page !== null && pageSize !== null) {
         const startIndex = (page - 1) * pageSize;
         const endIndex = startIndex + pageSize;
         const paginatedData = problemData.slice(startIndex, endIndex);

         return NextResponse.json({
            problemData: paginatedData,
            totalProblems,
            requestType: 'paginated',
            pagination: {
               examName,
               sectionName,
               topics,
               themes,
               types,
               page,
               pageSize,
               startIndex,
               endIndex,
               hasNextPage: endIndex < totalProblems,
               hasPreviousPage: page > 1,
            },
         });
      }

      // Return all data
      return NextResponse.json({
         problemData,
         totalProblems,
         requestType: 'all_data',
         pagination: {
            examName,
            sectionName,
            topics,
            themes,
            types,
         },
      });
   } catch (error) {
      console.error(`Error in /api/problems:`, error);
      return NextResponse.json(
         {
            error: "Error fetching problems from database",
            details: error instanceof Error ? error.message : String(error)
         },
         { status: 500 }
      );
   }
}

/**
 * POST /api/problems - Legacy endpoint support
 */
export async function POST(req: NextRequest) {
   try {
      const body = await req.json();
      const { userid, examName, sectionName, topics, themes, types } = body;

      const searchParams = new URLSearchParams({
         userid: (userid || 1).toString(),
         examName: examName || "GRE",
         sectionName: sectionName || "quants",
      });

      if (topics) searchParams.set("topics", JSON.stringify(topics));
      if (themes) searchParams.set("themes", JSON.stringify(themes));
      if (types) searchParams.set("types", JSON.stringify(types));

      const url = new URL(`/api/problems?${searchParams.toString()}`, req.url);
      const getRequest = new NextRequest(url, { method: "GET" });

      return GET(getRequest);
   } catch (error) {
      return NextResponse.json({ error: "Invalid JSON body" }, { status: 400 });
   }
}
