
import { NextRequest, NextResponse } from "next/server";
import { getMockAnalytics } from "@/features/user-analytics/services/analytics.service";

export async function GET(
    request: NextRequest,
    props: { params: Promise<{ username: string }> }
) {
    const params = await props.params;
    const { username } = params;

    if (!username) {
        return NextResponse.json({ error: "Username is required" }, { status: 400 });
    }

    try {
        const { searchParams } = new URL(request.url);
        const examName = searchParams.get("exam") || undefined;

        const data = await getMockAnalytics(username, examName);

        if (!data) {
            return NextResponse.json({ error: "User not found" }, { status: 404 });
        }

        return NextResponse.json(data);

    } catch (error) {
        console.error("Mock analytics error:", error);
        return NextResponse.json({ error: "Failed to fetch mock analytics" }, { status: 500 });
    }
}
