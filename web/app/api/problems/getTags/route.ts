import { NextRequest, NextResponse } from "next/server";

/**
 * Legacy endpoint - redirects to new RESTful structure
 * @deprecated Use GET /api/problems/tags with query parameters instead
 * 
 * This endpoint maintains backward compatibility by redirecting
 * POST requests to the new RESTful GET endpoint
 */
export async function POST(req: NextRequest) {
   try {
      const { examName, sectionName } = await req.json();
      
      // Redirect to new RESTful endpoint
      const searchParams = new URLSearchParams({
         examName: examName || "GRE",
         sectionName: sectionName || "quants"
      });

      const url = new URL(`/api/problems/tags?${searchParams}`, req.url);
      const getRequest = new NextRequest(url, { method: "GET" });
      
      // Import the new handler dynamically to avoid circular dependencies
      const { GET } = await import("../tags/route");
      const response = await GET(getRequest);
      
      // Transform response to match legacy format
      const data = await response.json();
      
      // Return just the tags array for backward compatibility
      return NextResponse.json(data.tags || data);
      
   } catch (error) {
      console.error(`Error in legacy getTags endpoint:`, error);
      return NextResponse.json(
         {
            error: "Error fetching tags, probably Docker for DB is not running!",
         },
         { status: 500 }
      );
   }
}
