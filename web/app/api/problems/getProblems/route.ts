import { NextRequest, NextResponse } from "next/server";

/**
 * Legacy endpoint - redirects to new RESTful structure
 * @deprecated Use GET /api/problems with query parameters instead
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
      });

      // Only add tags if they exist and are not null
      if (tags && tags.length > 0) {
         searchParams.append("tags", JSON.stringify(tags));
      }

      const url = new URL(`/api/problems?${searchParams}`, req.url);
      const getRequest = new NextRequest(url, { method: "GET" });

      // Import the new handler dynamically to avoid circular dependencies
      const { GET } = await import("../route");
      const response = await GET(getRequest);

      // Transform response to match legacy format
      const data = await response.json();

      // Return in legacy format (without metadata)
      return NextResponse.json({
         problemData: data.problemData,
         totalProblems: data.totalProblems,
      });
   } catch (error) {
      console.error(`Error in legacy getProblems endpoint:`, error);
      return NextResponse.json(
         {
            error: "Error fetching problems, probably Docker for DB is not running!",
         },
         { status: 500 }
      );
   }
}
