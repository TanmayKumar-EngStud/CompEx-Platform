
import { NextRequest, NextResponse } from "next/server";
import { getUserIdFromRequest } from "@/shared/lib/utils/auth";
import { prisma } from "@/shared/lib/configs/prisma";

export async function GET(req: NextRequest) {
    try {
        const userId = await getUserIdFromRequest(req);

        if (!userId) {
            return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
        }

        const user = await prisma.users.findUnique({
            where: { userid: userId },
            select: {
                userid: true,
                username: true,
                email: true,
                image_url: true,
            } as any
        });

        if (!user) {
            const response = NextResponse.json({ error: "User not found" }, { status: 404 });
            response.cookies.delete("session_token");
            return response;
        }

        const response = NextResponse.json(user);
        response.headers.set('Cache-Control', 'no-store, no-cache, must-revalidate, proxy-revalidate');
        return response;
    } catch (error) {
        console.error("Error fetching current user:", error);
        return NextResponse.json({ error: "Internal Server Error" }, { status: 500 });
    }
}
