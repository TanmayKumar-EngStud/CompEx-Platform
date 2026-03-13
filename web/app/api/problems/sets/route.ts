import { NextRequest, NextResponse } from "next/server";
import { getProblemsSetForPagination } from "@/features/question-solving/services/problemset-queries";

/**
 * GET /api/problems/sets - Retrieve problem sets with pagination and filtering
 * 
 * Query Parameters:
 * - userid: number - User ID for tracking attempts
 * - examName: string - Exam type (GRE, GMAT, CAT)
 * - sectionName: string - Section name (varies by exam)
 * - tags: string[] - Array of tags for filtering (JSON encoded)
 * - page: number - Page number for pagination
 * - pageSize: number - Number of items per page
 */
export async function GET(request: NextRequest) {
   const { searchParams } = request.nextUrl;
   const userid = parseInt(searchParams.get("userid") || "1");
   const examNameRaw = searchParams.get("examName") || "GRE";
   const sectionNameRaw = searchParams.get("sectionName") || "quants";
   const examName = examNameRaw.toUpperCase();
   const sectionName = sectionNameRaw.toLowerCase();

   const topicsParam = searchParams.get("topics");
   const themesParam = searchParams.get("themes");
   const typesParam = searchParams.get("types");
   const topics = topicsParam ? JSON.parse(topicsParam) : [];
   const themes = themesParam ? JSON.parse(themesParam) : [];
   const types = typesParam ? JSON.parse(typesParam) : [];
   const filters = { topics, themes, types };

   const page = parseInt(searchParams.get("page") || "1");
   const pageSize = parseInt(searchParams.get("pageSize") || "10");

   if (!examName || !sectionName) {
      console.error("❌ Problem sets route: Missing Parameters", { examName, sectionName });
      return NextResponse.json(
         { error: "Missing examName or sectionName query parameters" },
         { status: 400 }
      );
   }

   const examtypeid = ["GMAT", "GRE", "CAT"].indexOf(examName) + 1;

   if (examtypeid === 0) {
      console.error("❌ Problem sets route: Invalid examName", { examName });
      return NextResponse.json(
         {
            error: "Invalid examName provided",
            validExamTypes: ["GRE", "GMAT", "CAT"]
         },
         { status: 400 }
      );
   }

   let sectionid: number | number[] = -1;
   switch (examtypeid) {
      case 1: // GMAT
         const gmatSections = ["quants", "verbal", "integrated reasoning"];
         sectionid = gmatSections.indexOf(sectionName) + 1;
         if (sectionid === 0) {
            return NextResponse.json(
               {
                  error: `Invalid sectionName for GMAT: ${sectionName}`,
                  validSections: gmatSections
               },
               { status: 400 }
            );
         }
         break;
      case 2: // GRE
         if (sectionName === "quants") {
            sectionid = [4, 7];
         } else if (sectionName === "verbal") {
            sectionid = [5, 6];
         } else {
            return NextResponse.json(
               {
                  error: `Invalid sectionName for GRE: ${sectionName}`,
                  validSections: ["quants", "verbal"]
               },
               { status: 400 }
            );
         }
         break;
      case 3: // CAT
         const catSections = ["DI", "LR", "VA", "RC"];
         sectionid = catSections.indexOf(sectionName) + 8;
         if (sectionid === 7) { // indexOf returns -1
            return NextResponse.json(
               {
                  error: `Invalid sectionName for CAT: ${sectionName}`,
                  validSections: catSections
               },
               { status: 400 }
            );
         }
         break;
      default:
         return NextResponse.json(
            { error: "Invalid exam type" },
            { status: 400 }
         );
   }

   try {
      const { problemSetWithProblems, totalProblemSets } =
         await getProblemsSetForPagination(userid, examtypeid, sectionid, filters);

      return NextResponse.json({
         problemSetWithProblems,
         totalProblemSets,
         pagination: {
            page,
            pageSize,
            totalPages: Math.ceil(totalProblemSets / pageSize)
         },
         metadata: {
            examName,
            sectionName,
            examTypeId: examtypeid,
            sectionId: sectionid,
            topics,
            themes,
            types,
            userId: userid
         }
      });
   } catch (error: any) {
      console.error("Error in problem sets route:", error);
      return NextResponse.json(
         { error: "Internal Server Error fetching problem sets" },
         { status: 500 }
      );
   }
}

/**
 * POST /api/problems/sets - Legacy endpoint for backward compatibility
 * @deprecated Use GET /api/problems/sets with query parameters instead
 */
export async function POST(req: NextRequest) {
   const { userid, examName, sectionName, topics, themes, types } = await req.json();

   // Redirect to GET method with query parameters
   const searchParams = new URLSearchParams({
      userid: userid?.toString() || "1",
      examName: examName || "GRE",
      sectionName: sectionName || "quants",
      topics: JSON.stringify(topics || []),
      themes: JSON.stringify(themes || []),
      types: JSON.stringify(types || [])
   });

   const url = new URL(`/api/problems/sets?${searchParams}`, req.url);
   const getRequest = new NextRequest(url, { method: "GET" });

   return GET(getRequest);
}