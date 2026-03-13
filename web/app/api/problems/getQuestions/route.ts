import { NextRequest, NextResponse } from "next/server";

/**
 * Legacy endpoint - redirects to new RESTful structure
 * @deprecated Use GET /api/problems/[id] instead
 * 
 * This endpoint maintains backward compatibility by redirecting
 * POST requests to the new RESTful GET endpoint
 */
export async function POST(req: NextRequest) {
   try {
      const body = await req.json();
      const { questionId } = body;

      // Handle both single ID and array of IDs
      const ids = Array.isArray(questionId) ? questionId.join(",") : questionId.toString();
      
      // Redirect to new RESTful endpoint
      const url = new URL(`/api/problems/${ids}`, req.url);
      const getRequest = new NextRequest(url, { method: "GET" });
      
      // Import the new handler dynamically to avoid circular dependencies
      const { GET } = await import("../[id]/route");
      const response = await GET(getRequest, { params: Promise.resolve({ id: ids }) });
      
      // Transform response to match legacy format
      const data = await response.json();
      
      // Return just the questions array for backward compatibility
      return NextResponse.json(data.questions || data);
      
   } catch (error) {
      console.error(`Error in legacy getQuestions endpoint:`, error);
      return NextResponse.json(
         { error: "Error fetching question details" },
         { status: 500 }
      );
   }
}