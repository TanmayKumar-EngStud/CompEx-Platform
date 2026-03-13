import { NextRequest, NextResponse } from "next/server";

/**
 * Legacy endpoint - redirects to new RESTful structure
 * @deprecated Use POST /api/problems/[id]/attempts instead
 * 
 * This endpoint maintains backward compatibility by redirecting
 * to the new RESTful endpoint based on the first question ID in the attempt
 */
export async function POST(req: NextRequest) {
   try {
      const body = await req.json();
      // body => {userID: 12, Attempt: [{questionID: 12, option:'A'}, {questionID: 13, option: 'C'}]}
      
      if (!body.Attempt || body.Attempt.length === 0) {
         return NextResponse.json(
            { error: "No attempts provided" },
            { status: 400 }
         );
      }

      // For backward compatibility, use the first question ID as the primary ID
      const primaryQuestionId = body.Attempt[0].questionID;
      
      // Redirect to new RESTful endpoint
      const url = new URL(`/api/problems/${primaryQuestionId}/attempts`, req.url);
      const postRequest = new NextRequest(url, { 
         method: "POST",
         body: JSON.stringify(body),
         headers: req.headers
      });
      
      // Import the new handler dynamically to avoid circular dependencies
      const { POST: newPOST } = await import("../[id]/attempts/route");
      const response = await newPOST(postRequest, { params: Promise.resolve({ id: primaryQuestionId.toString() }) });
      
      // Transform response to match legacy format
      const data = await response.json();
      
      // Return just the data without metadata for backward compatibility
      return NextResponse.json(data.data || data);
      
   } catch (error) {
      console.error(`Error in legacy returnAttempt endpoint:`, error);
      return NextResponse.json(
         {
            error: "Error submitting the user attempts for problem's section",
         },
         { status: 500 }
      );
   }
}
