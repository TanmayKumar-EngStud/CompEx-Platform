
import { NextRequest, NextResponse } from "next/server";
import { SignJWT } from "jose";
import { cookies } from "next/headers";
import { prisma } from "@/shared/lib/configs/prisma";

const JWT_SECRET = new TextEncoder().encode(
    process.env.JWT_SECRET || "fallback-secret-for-development-must-change-later"
);

export async function POST(request: NextRequest) {
    try {
        const body = await request.json();
        const { userId } = body;

        if (!userId) {
            return NextResponse.json({ error: "User ID required" }, { status: 400 });
        }

        // Verify user exists
        const user = await prisma.users.findUnique({
            where: { userid: userId }
        });

        if (!user) {
            return NextResponse.json({ error: "User not found" }, { status: 404 });
        }

        // Create new session token since we are simulating a switch
        const token = await new SignJWT({ userId: user.userid, email: user.email })
            .setProtectedHeader({ alg: "HS256" })
            .setIssuedAt()
            .setExpirationTime("24h")
            .sign(JWT_SECRET);

        const cookieStore = await cookies();
        cookieStore.set("session_token", token, {
            httpOnly: true,
            secure: process.env.NODE_ENV === "production",
            sameSite: "strict",
            path: "/",
            maxAge: 86400 // 24 hours
        });

        return NextResponse.json({ message: "User switched successfully", user: { userid: user.userid, username: user.username } });

    } catch (error) {
        console.error("Switch User Error:", error);
        return NextResponse.json({ error: "Internal Server Error" }, { status: 500 });
    }
}
