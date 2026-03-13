import { NextRequest, NextResponse } from "next/server";
import { getQuestionDetails } from "@/features/question-solving/services/question-queries";

/**
 * GET /api/problems/[id] - Retrieve specific question details
 * 
 * Path Parameters:
 * - id: string - Question ID or comma-separated list of IDs
 * 
 * Query Parameters:
 * - includeOptions: boolean - Include answer options (default: true)
 * - includeSolution: boolean - Include solution (default: false)
 */
export async function GET(
   request: NextRequest,
   context: { params: Promise<{ id: string }> }
) {
   try {
      const { id } = await context.params;
      const { searchParams } = request.nextUrl;
      const includeOptions = searchParams.get("includeOptions") !== "false";
      const includeSolution = searchParams.get("includeSolution") === "true";

      // Parse ID(s) - support both single ID and comma-separated IDs
      const questionIds = id.includes(",") 
         ? id.split(",").map(Number)
         : [Number(id)];

      const questionDetails = await getQuestionDetails(questionIds);

      return NextResponse.json({
         questions: questionDetails,
         metadata: {
            requestedIds: questionIds,
            includeOptions,
            includeSolution,
            count: questionDetails.length
         }
      });
   } catch (error) {
      console.error(`Error fetching question details:`, error);
      return NextResponse.json(
         { error: "Error fetching question details" },
         { status: 500 }
      );
   }
}

/**
 * POST /api/problems/[id] - Legacy endpoint for backward compatibility
 * @deprecated Use GET /api/problems/[id] instead
 */
export async function POST(
   req: NextRequest,
   context: { params: Promise<{ id: string }> }
) {
   try {
      const body = await req.json();
      const { questionId } = body;

      // Convert to array format for consistency
      const questionIds = Array.isArray(questionId) ? questionId : [questionId];
      
      const questionDetails = await getQuestionDetails(questionIds);
      return NextResponse.json(questionDetails);
   } catch (error) {
      console.error(`Error fetching question details:`, error);
      return NextResponse.json(
         { error: "Error fetching question details" },
         { status: 500 }
      );
   }
}