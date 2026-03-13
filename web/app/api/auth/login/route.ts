
import { NextRequest, NextResponse } from "next/server";
import { prisma } from "@/shared/lib/configs/prisma";
import bcrypt from "bcryptjs";
import { SignJWT } from "jose";

const JWT_SECRET = new TextEncoder().encode(
    process.env.JWT_SECRET || "fallback-secret-for-development-must-change-later"
);

export async function POST(req: NextRequest) {
    try {
        const { identifier, password } = await req.json();

        if (!identifier || !password) {
            return NextResponse.json({ error: "Missing credentials" }, { status: 400 });
        }

        // Find user by email or username
        const user = await prisma.users.findFirst({
            where: {
                OR: [
                    { email: identifier },
                    { username: identifier }
                ]
            }
        });

        if (!user) {
            return NextResponse.json({ error: "Invalid credentials" }, { status: 401 });
        }

        const match = await bcrypt.compare(password, user.password);

        if (!match) {
            return NextResponse.json({ error: "Invalid credentials" }, { status: 401 });
        }

        if (!user.isverified) {
            return NextResponse.json({ error: "Account not verified", isVerified: false }, { status: 403 });
        }

        // Generate JWT
        const token = await new SignJWT({
            userId: user.userid,
            email: user.email
        })
            .setProtectedHeader({ alg: "HS256" })
            .setIssuedAt()
            .setExpirationTime("24h")
            .sign(JWT_SECRET);

        const response = NextResponse.json({
            message: "Login successful",
            user: {
                id: user.userid,
                username: user.username,
                email: user.email
            }
        });

        // Set Cookie
        response.cookies.set("session_token", token, {
            httpOnly: true,
            secure: process.env.NODE_ENV === "production",
            sameSite: "lax",
            maxAge: 60 * 60 * 24, // 24 hours
            path: "/"
        });

        return response;

    } catch (error) {
        console.error("Login Error:", error);
        return NextResponse.json({ error: "Internal Server Error" }, { status: 500 });
    }
}
