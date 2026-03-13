import { NextRequest, NextResponse } from "next/server";
import { prisma } from "@/shared/lib/configs/prisma";

/**
 * POST /api/problems/filtered-ids - Get filtered question IDs for cache system
 * 
 * This endpoint returns just the question IDs that match the filter criteria,
 * allowing the cache system to know which questions to fetch without
 * fetching the actual question data.
 * 
 * Request Body:
 * - sectionId: string - Section identifier (e.g., "GRE-quants")
 * - tags: string[] - Array of tag names to filter by
 * - userId?: number - Optional user ID for personalized filtering
 */
export async function POST(request: NextRequest) {
  try {
    const { sectionId, tags, topics, themes, types, userId } = await request.json();

    if (!sectionId) {
      return NextResponse.json(
        { error: "sectionId is required" },
        { status: 400 }
      );
    }

    // Prepare tag filters
    const tagFilter: any = [];

    // If specific categories are provided, use them
    if (topics && Array.isArray(topics) && topics.length > 0) {
      tagFilter.push({ tags: { topic: { in: topics } } });
    }
    if (themes && Array.isArray(themes) && themes.length > 0) {
      tagFilter.push({ tags: { theme: { in: themes } } });
    }
    if (types && Array.isArray(types) && types.length > 0) {
      tagFilter.push({ tags: { type: { in: types } } });
    }

    // Fallback: If only 'tags' is provided (legacy or generic search), search across all fields
    if (tagFilter.length === 0 && Array.isArray(tags) && tags.length > 0) {
      tagFilter.push({ tags: { topic: { in: tags } } });
      tagFilter.push({ tags: { theme: { in: tags } } });
      tagFilter.push({ tags: { type: { in: tags } } });
    }

    const hasFilters = tagFilter.length > 0;

    // Parse section ID to extract exam type and section
    const [examName, sectionName] = sectionId.split('-');
    if (!examName || !sectionName) {
      return NextResponse.json(
        { error: "Invalid sectionId format. Expected: 'ExamType-SectionName'" },
        { status: 400 }
      );
    }

    // 1. Resolve Exam Type
    const examTypeRecord = await prisma.examtypes.findFirst({
      where: { name: { equals: examName, mode: 'insensitive' } }
    });

    if (!examTypeRecord) {
      return NextResponse.json({ error: "Invalid exam type" }, { status: 400 });
    }

    // 2. Resolve Section
    const sectionRecord = await prisma.sections.findFirst({
      where: {
        examtypeid: examTypeRecord.examtypeid,
        name: { equals: sectionName, mode: 'insensitive' }
      }
    });

    if (!sectionRecord) {
      return NextResponse.json({ error: "Invalid section name" }, { status: 400 });
    }

    const examtypeid = examTypeRecord.examtypeid;
    const sectionid = sectionRecord.sectionid;

    console.log(`🏷️ Fetching filtered question IDs for ${sectionId} with filters:`, { topics, themes, types, tags });

    // Fetch filtered question IDs for individual problems
    const filteredProblems = await prisma.problems.findMany({
      where: {
        examtypeid,
        sectionid,
        isChildren: false,
        type: {
          not: "",
        },
        ...(hasFilters ? {
          problemtags: {
            some: {
              OR: tagFilter
            },
          },
        } : {}),
      },
      select: {
        problemid: true,
        addedDate: true,
      },
      orderBy: {
        addedDate: 'asc', // Maintain consistent ordering
      },
    });

    // Fetch filtered problem sets
    const filteredProblemSets = await prisma.problemsSet.findMany({
      where: {
        examtypeid,
        sectionid,
        ...(hasFilters ? {
          problems: {
            some: {
              problemtags: {
                some: {
                  OR: tagFilter
                },
              },
            },
          },
        } : {}),
      },
      select: {
        problemsSetId: true,
        problems: {
          select: {
            problemid: true,
            addedDate: true,
          },
        },
      },
    });

    // Combine and sort by addedDate to maintain consistent order across pages
    const combinedEntries: any[] = [
      // eslint-disable-next-line
      ...filteredProblems.map((p: any) => ({
        type: 'problem',
        addedDate: p.addedDate,
        entry: {
          problemid: p.problemid
        }
      })),
      // eslint-disable-next-line
      ...filteredProblemSets.map((ps: any) => ({
        type: 'set',
        // Use the addedDate of the first question in the set for sorting
        addedDate: ps.problems[0]?.addedDate || new Date(0),
        entry: {
          problemsSetId: ps.problemsSetId,
          // eslint-disable-next-line
          problems: ps.problems.map((p: any) => ({ problemid: p.problemid }))
        }
      }))
    ];

    // Sort by addedDate
    // eslint-disable-next-line
    combinedEntries.sort((a: any, b: any) => {
      const dateA = new Date(a.addedDate).getTime();
      const dateB = new Date(b.addedDate).getTime();
      return dateA - dateB;
    });

    const questionEntries = combinedEntries.map(e => e.entry);

    console.log(`📊 Found ${questionEntries.length} filtered question entries (rows) for ${sectionId}`);

    return NextResponse.json({
      questionEntries,
      totalQuestions: questionEntries.length,
      sectionId,
      appliedTags: tags,
      metadata: {
        examType: examName,
        section: sectionName,
        examtypeid,
        sectionid,
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