import { NextRequest, NextResponse } from "next/server";
import { getProblemsForPagination } from "@/features/question-solving/services/question-queries";
import { prisma } from "@/shared/lib/configs/prisma";

/**
 * GET /api/exams/[examType]/[section] - Retrieve problems for specific exam type and section
 * 
 * Path Parameters:
 * - examType: string - Exam type (gre, gmat, cat)
 * - section: string - Section name (quants, verbal, etc.)
 */
export async function GET(
   request: NextRequest,
   context: { params: Promise<{ examType: string; section: string }> }
) {
   const { examType, section } = await context.params;
   const { searchParams } = request.nextUrl;

   const userid = parseInt(searchParams.get("userid") || "1");
   const tagsParam = searchParams.get("tags");
   const tags = tagsParam ? JSON.parse(tagsParam) : [];
   const page = parseInt(searchParams.get("page") || "1");
   const pageSize = parseInt(searchParams.get("pageSize") || "10");

   // Normalize exam type to uppercase for consistency
   const examName = examType.toUpperCase();
   const sectionName = section.toLowerCase();

   try {
      // 1. Resolve Exam Type
      const examTypeRecord = await prisma.examtypes.findFirst({
         where: { name: { equals: examName, mode: 'insensitive' } }
      });

      if (!examTypeRecord) {
         return NextResponse.json(
            { error: `Invalid exam type: ${examType}`, validExamTypes: ["gre", "gmat", "cat"] },
            { status: 400 }
         );
      }

      // 2. Resolve Section
      const sectionRecord = await prisma.sections.findFirst({
         where: {
            examtypeid: examTypeRecord.examtypeid,
            name: { equals: sectionName, mode: 'insensitive' }
         }
      });

      if (!sectionRecord) {
         return NextResponse.json(
            { error: `Invalid section '${section}' for ${examName}` },
            { status: 400 }
         );
      }

      const examtypeid = examTypeRecord.examtypeid;
      const sectionid = sectionRecord.sectionid;

      if (tags?.length > 0) {
         tags.map((tag: string) => `"${tag}"`);
         console.log("Tags in :", tags);
      }

      const { problemData, totalProblems } = await getProblemsForPagination(
         userid,
         examtypeid,
         sectionid,
         tags
      );

      return NextResponse.json({
         problemData,
         totalProblems,
         pagination: {
            page,
            pageSize,
            totalPages: Math.ceil(totalProblems / pageSize)
         },
         metadata: {
            examType: examName,
            section: sectionName,
            examTypeId: examtypeid,
            sectionId: sectionid,
            tags,
            userId: userid
         }
      });
   } catch (error) {
      console.error(`Error fetching problems for ${examType}/${section}:`, error);
      return NextResponse.json(
         {
            error: `Error fetching problems for ${examType}/${section}`,
         },
         { status: 500 }
      );
   }
}