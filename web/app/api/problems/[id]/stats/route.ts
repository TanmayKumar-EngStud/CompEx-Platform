import { NextRequest, NextResponse } from "next/server";
import { getQuestionStats } from "@/features/user-analytics/services/question-stats-service";

/**
 * GET /api/problems/[id]/stats - Retrieve solve statistics for a specific question
 * 
 * Path Parameters:
 * - id: string - Question ID
 */
export async function GET(
    request: NextRequest,
    context: { params: Promise<{ id: string }> }
) {
    try {
        const { id } = await context.params;
        const problemId = parseInt(id);

        if (isNaN(problemId)) {
            return NextResponse.json({ error: "Invalid question ID" }, { status: 400 });
        }

        const stats = await getQuestionStats(problemId);

        return NextResponse.json(stats);
    } catch (error) {
        console.error(`Error fetching question stats:`, error);
        return NextResponse.json(
            { error: "Error fetching question stats" },
            { status: 500 }
        );
    }
}
