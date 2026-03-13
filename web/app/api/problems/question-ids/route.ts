import { NextRequest, NextResponse } from "next/server";
import { prisma } from "@/shared/lib/configs/prisma";

/**
 * GET /api/problems/question-ids - Get all question IDs for a section
 * 
 * This endpoint returns all question IDs for a specific section without
 * the actual question data, allowing the cache system to manage question
 * ordering and pagination efficiently.
 * 
 * Query Parameters:
 * - sectionId: string - Section identifier (e.g., "GRE-quants")
 * - userId?: number - Optional user ID for future personalization
 */
export async function GET(request: NextRequest) {
  try {
    const { searchParams } = request.nextUrl;
    const sectionId = searchParams.get("sectionId");
    const userId = searchParams.get("userId");

    if (!sectionId) {
      return NextResponse.json(
        { error: "sectionId is required" },
        { status: 400 }
      );
    }

    // Parse section ID to extract exam type and section
    const [examName, sectionName] = sectionId.split('-');
    if (!examName || !sectionName) {
      return NextResponse.json(
        { error: "Invalid sectionId format. Expected: 'ExamType-SectionName'" },
        { status: 400 }
      );
    }

    // Map exam names to IDs
    const examtypeid = ["GMAT", "GRE", "CAT"].indexOf(examName.toUpperCase()) + 1;
    if (examtypeid === 0) {
      return NextResponse.json(
        { error: "Invalid exam type" },
        { status: 400 }
      );
    }

    // Map section names to IDs
    let sectionid = -1;
    switch (examtypeid) {
      case 1: // GMAT
        sectionid = ["quants", "verbal", "integrated reasoning"].indexOf(sectionName.toLowerCase()) + 1;
        break;
      case 2: // GRE
        sectionid = ["verbal", "quants"].indexOf(sectionName.toLowerCase()) + 4;
        break;
      case 3: // CAT
        sectionid = ["DI", "LR", "VA", "RC"].indexOf(sectionName.toUpperCase()) + 8;
        break;
    }

    if (sectionid === 0) {
      return NextResponse.json(
        { error: "Invalid section name for the specified exam type" },
        { status: 400 }
      );
    }

    console.log(`📋 Fetching all question IDs for section: ${sectionId}`);

    // Fetch all question IDs for individual problems
    const allProblems = await prisma.problems.findMany({
      where: {
        examtypeid,
        sectionid,
        isChildren: false,
        type: {
          not: "",
        },
      },
      select: {
        problemid: true,
        addedDate: true,
        problemsSetId: true,
      },
      orderBy: {
        addedDate: 'asc', // Maintain consistent ordering
      },
    });

    // Fetch all problem sets for this section
    const allProblemSets = await prisma.problemsSet.findMany({
      where: {
        examtypeid,
        sectionid,
      },
      select: {
        problemsSetId: true,
        problems: {
          select: {
            problemid: true,
            addedDate: true,
          },
          orderBy: {
            addedDate: 'asc',
          },
        },
      },
    });

    // Collect all question IDs in consistent order
    const questionIds: string[] = [
      // eslint-disable-next-line
      ...allProblems.map((p: any) => p.problemid.toString()),
      // eslint-disable-next-line
      ...allProblemSets.flatMap((ps: any) =>
        // eslint-disable-next-line
        ps.problems.map((p: any) => p.problemid.toString())
      ),
    ];

    // Remove duplicates while preserving order
    const uniqueQuestionIds = Array.from(new Set(questionIds));

    console.log(`📊 Found ${uniqueQuestionIds.length} total question IDs for ${sectionId}`);

    return NextResponse.json({
      questionIds: uniqueQuestionIds,
      totalQuestions: uniqueQuestionIds.length,
      sectionId,
      metadata: {
        examType: examName,
        section: sectionName,
        examtypeid,
        sectionid,
        individualProblems: allProblems.length,
        problemSets: allProblemSets.length,
        // eslint-disable-next-line
        totalProblemsInSets: allProblemSets.reduce((sum: any, ps: any) => sum + ps.problems.length, 0),
      },
    });

  } catch (error) {
    console.error("❌ Error fetching question IDs:", error);
    return NextResponse.json(
      {
        error: "Failed to fetch question IDs",
        details: error instanceof Error ? error.message : "Unknown error"
      },
      { status: 500 }
    );
  }
}

/**
 * POST /api/problems/question-ids - Get question IDs with additional filtering
 * 
 * This endpoint allows for more complex filtering scenarios while still
 * returning just the question IDs for cache management.
 */
export async function POST(request: NextRequest) {
  try {
    const { sectionId, excludeTags, includeTags, userId } = await request.json();

    if (!sectionId) {
      return NextResponse.json(
        { error: "sectionId is required" },
        { status: 400 }
      );
    }

    // Parse section ID
    const [examName, sectionName] = sectionId.split('-');
    if (!examName || !sectionName) {
      return NextResponse.json(
        { error: "Invalid sectionId format" },
        { status: 400 }
      );
    }

    // Get exam and section IDs (same logic as GET)
    const examtypeid = ["GMAT", "GRE", "CAT"].indexOf(examName.toUpperCase()) + 1;
    let sectionid = -1;

    switch (examtypeid) {
      case 1: sectionid = ["quants", "verbal", "integrated reasoning"].indexOf(sectionName.toLowerCase()) + 1; break;
      case 2: sectionid = ["verbal", "quants"].indexOf(sectionName.toLowerCase()) + 4; break;
      case 3: sectionid = ["DI", "LR", "VA", "RC"].indexOf(sectionName.toUpperCase()) + 8; break;
    }

    if (examtypeid === 0 || sectionid === 0) {
      return NextResponse.json(
        { error: "Invalid exam type or section" },
        { status: 400 }
      );
    }

    // Build filtering conditions
    const tagFilter: any = {};

    if (includeTags && includeTags.length > 0) {
      tagFilter.some = {
        OR: [
          { tags: { topic: { in: includeTags } } },
          { tags: { theme: { in: includeTags } } },
          { tags: { type: { in: includeTags } } },
        ]
      };
    }

    if (excludeTags && excludeTags.length > 0) {
      tagFilter.none = {
        OR: [
          { tags: { topic: { in: excludeTags } } },
          { tags: { theme: { in: excludeTags } } },
          { tags: { type: { in: excludeTags } } },
        ]
      };
    }

    // Apply filtering conditions
    const whereConditions: any = {
      examtypeid,
      sectionid,
      isChildren: false,
      type: {
        not: "",
      },
    };

    if (Object.keys(tagFilter).length > 0) {
      whereConditions.problemtags = tagFilter;
    }

    console.log(`🔍 Fetching filtered question IDs for ${sectionId} with complex filters`);

    const filteredProblems = await prisma.problems.findMany({
      where: whereConditions,
      select: {
        problemid: true,
        addedDate: true,
      },
      orderBy: {
        addedDate: 'asc',
      },
    });

    // eslint-disable-next-line
    const questionIds = filteredProblems.map((p: any) => p.problemid.toString());

    console.log(`📊 Found ${questionIds.length} filtered question IDs with complex filters`);

    return NextResponse.json({
      questionIds,
      totalQuestions: questionIds.length,
      sectionId,
      appliedFilters: {
        includeTags: includeTags || [],
        excludeTags: excludeTags || [],
      },
    });

  } catch (error) {
    console.error("❌ Error fetching filtered question IDs:", error);
    return NextResponse.json(
      {
        error: "Failed to fetch filtered question IDs",
        details: error instanceof Error ? error.message : "Unknown error"
      },
      { status: 500 }
    );
  }
}