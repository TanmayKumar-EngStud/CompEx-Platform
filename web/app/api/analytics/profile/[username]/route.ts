
import { NextRequest, NextResponse } from "next/server";
import { getUserAnalytics } from "@/features/user-analytics/services/analytics.service";

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
        const sectionName = searchParams.get("section") || undefined;
        const includeMock = searchParams.get("includeMock") === "true";

        const data = await getUserAnalytics(username, examName, sectionName, includeMock);

        if (!data) {
            return NextResponse.json({ error: "User not found" }, { status: 404 });
        }

        return NextResponse.json(data);

    } catch (error) {
        console.error("Profile analytics error:", error);
        return NextResponse.json({ error: "Failed to fetch analytics" }, { status: 500 });
    }
}
