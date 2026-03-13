import { NextRequest, NextResponse } from "next/server";

/**
 * Legacy endpoint - redirects to new RESTful structure
 * @deprecated Use GET /api/problems/sets with query parameters instead
 * 
 * This endpoint maintains backward compatibility by redirecting
 * POST requests to the new RESTful GET endpoint
 */
export async function POST(req: NextRequest) {
   try {
      const { userid, examName, sectionName, tags } = await req.json();
      
      // Redirect to new RESTful endpoint
      const searchParams = new URLSearchParams({
         userid: userid?.toString() || "1",
         examName: examName || "GRE",
         sectionName: sectionName || "quants",
         tags: JSON.stringify(tags || [])
      });

      const url = new URL(`/api/problems/sets?${searchParams}`, req.url);
      const getRequest = new NextRequest(url, { method: "GET" });
      
      // Import the new handler dynamically to avoid circular dependencies
      const { GET } = await import("../sets/route");
      const response = await GET(getRequest);
      
      // Transform response to match legacy format
      const data = await response.json();
      
      // Return in legacy format (without metadata)
      return NextResponse.json({
         problemSetWithProblems: data.problemSetWithProblems,
         totalProblemSets: data.totalProblemSets
      });
      
   } catch (error: any) {
      console.error("Error in legacy getProblemsSets endpoint:", error);
      return NextResponse.json(
         { error: "Internal Server Error." },
         { status: 500 }
      );
   }
}
