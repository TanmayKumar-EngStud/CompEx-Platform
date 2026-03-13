import { NextRequest, NextResponse } from "next/server";
import { submitUserAttempt } from "@/features/question-solving/services/question-queries";

/**
 * POST /api/problems/[id]/attempts - Submit user attempt for a specific problem
 *
 * Path Parameters:
 * - id: string - Problem ID
 *
 * Request Body:
 * {
 *   userID: number,
 *   Attempt: [{
 *     questionID: number,
 *     option: string
 *   }]
 * }
 */
export async function POST(
   req: NextRequest,
   context: { params: Promise<{ id: string }> }
) {
   const { id } = await context.params;
   try {
      const text = await req.text();
      if (!text.trim()) {
         return NextResponse.json(
            { error: "Request body is empty" },
            { status: 400 }
         );
      }
      
      let body;
      try {
         body = JSON.parse(text);
      } catch (parseError) {
         return NextResponse.json(
            { error: "Invalid JSON in request body" },
            { status: 400 }
         );
      }

      // Validate that the attempt is for the correct problem
      const problemId = parseInt(id);
      if (body.Attempt && body.Attempt.length > 0) {
         const firstAttempt = body.Attempt[0];
         const attemptProblemId =
            firstAttempt.questionID || firstAttempt.problemId;
         if (attemptProblemId && attemptProblemId !== problemId) {
            return NextResponse.json(
               {
                  error: "Problem ID in URL does not match attempt data",
                  expected: problemId,
                  received: attemptProblemId,
               },
               { status: 400 }
            );
         }
      }

      const sentDetails = await submitUserAttempt(body);

      return NextResponse.json({
         success: true,
         data: sentDetails,
         metadata: {
            problemId,
            attemptCount: body.Attempt?.length || 0,
            userId: body.userID,
         },
      });
   } catch (error) {
      console.error(`Error submitting user attempt for problem ${id}:`, error);
      return NextResponse.json(
         {
            error: `Error submitting user attempt for problem ${id}`,
         },
         { status: 500 }
      );
   }
}

/**
 * GET /api/problems/[id]/attempts - Retrieve user attempts for a specific problem
 *
 * Path Parameters:
 * - id: string - Problem ID
 *
 * Query Parameters:
 * - userId: number - User ID to filter attempts
 */
export async function GET(
   request: NextRequest,
   context: { params: Promise<{ id: string }> }
) {
   const { id } = await context.params;
   try {
      const { searchParams } = request.nextUrl;
      const userId = searchParams.get("userId");

      if (!userId) {
         return NextResponse.json(
            { error: "userId query parameter is required" },
            { status: 400 }
         );
      }

      // TODO: Implement getUserAttemptsForProblem service
      // const attempts = await getUserAttemptsForProblem(parseInt(id), parseInt(userId));

      return NextResponse.json({
         problemId: parseInt(id),
         userId: parseInt(userId),
         attempts: [], // Placeholder - implement actual service
         message: "GET attempts endpoint - implementation pending",
      });
   } catch (error) {
      console.error(`Error fetching attempts for problem ${id}:`, error);
      return NextResponse.json(
         { error: `Error fetching attempts for problem ${id}` },
         { status: 500 }
      );
   }
}
