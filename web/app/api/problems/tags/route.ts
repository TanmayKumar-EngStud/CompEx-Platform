import { NextRequest, NextResponse } from "next/server";
import { getTags } from "@/features/exam-management/services/tag-queries";
import { prisma } from "@/shared/lib/configs/prisma";

/**
 * GET /api/problems/tags - Retrieve available tags for filtering
 * 
 * Query Parameters:
 * - examName: string - Exam type (GRE, GMAT, CAT)
 * - sectionName: string - Section name (varies by exam type)
 */
export async function GET(request: NextRequest) {
   const { searchParams } = request.nextUrl;
   const examName = searchParams.get("examName") || "GRE";
   const sectionName = searchParams.get("sectionName") || "quants";

   try {
      // 1. Resolve Exam Type
      const examType = await prisma.examtypes.findFirst({
         where: { name: { equals: examName, mode: 'insensitive' } }
      });

      if (!examType) {
         return NextResponse.json({ error: "Exam type not found" }, { status: 404 });
      }

      // 2. Resolve Section(s)
      let sections;
      if (sectionName === "mixed" || sectionName === "all") {
         sections = await prisma.sections.findMany({
            where: { examtypeid: examType.examtypeid }
         });
      } else {
         sections = await prisma.sections.findMany({
            where: {
               examtypeid: examType.examtypeid,
               name: { equals: sectionName, mode: 'insensitive' }
            }
         });
      }

      if (sections.length === 0) {
         return NextResponse.json({ error: "Section not found for this exam" }, { status: 404 });
      }

      const examtypeid = examType.examtypeid;
      // eslint-disable-next-line
      const sectionid = sections.length === 1 ? sections[0].sectionid : sections.map((s: any) => s.sectionid);

      const tagData = await getTags(examtypeid, sectionid);

      return NextResponse.json({
         tags: tagData,
         metadata: {
            examName,
            sectionName,
            examTypeId: examtypeid,
            sectionId: sectionid,
            count: tagData?.length || 0
         }
      });
   } catch (error) {
      console.error(`Error fetching tags: ${error}\t\tapi/problems/tags/route.ts`);
      return NextResponse.json(
         {
            error: "Error fetching tags, probably Docker for DB is not running!",
         },
         { status: 500 }
      );
   }
}

/**
 * POST /api/problems/tags - Legacy endpoint for backward compatibility
 * @deprecated Use GET /api/problems/tags with query parameters instead
 */
export async function POST(req: NextRequest) {
   const { examName, sectionName } = await req.json();

   // Redirect to GET method with query parameters
   const searchParams = new URLSearchParams({
      examName: examName || "GRE",
      sectionName: sectionName || "quants"
   });

   const url = new URL(`/api/problems/tags?${searchParams}`, req.url);
   const getRequest = new NextRequest(url, { method: "GET" });

   return GET(getRequest);
}