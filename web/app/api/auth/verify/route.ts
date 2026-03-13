
import { NextRequest, NextResponse } from "next/server";
import { prisma } from "@/shared/lib/configs/prisma";
import { SignJWT } from "jose";

const JWT_SECRET = new TextEncoder().encode(
    process.env.JWT_SECRET || "fallback-secret-for-development-must-change-later"
);

export async function POST(req: NextRequest) {
    try {
        const { email, otp } = await req.json();

        if (!email || !otp) {
            return NextResponse.json({ error: "Missing email or OTP" }, { status: 400 });
        }

        const user = await prisma.users.findUnique({
            where: { email }
        });

        if (!user) {
            return NextResponse.json({ error: "User not found" }, { status: 404 });
        }

        if (user.otp === otp) {
            // Success -> Auto Login
            await prisma.users.update({
                where: { email },
                data: {
                    isverified: true,
                    otp: null // Clear OTP after verification
                }
            });

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
                message: "Verification successful",
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
        } else {
            return NextResponse.json({ error: "Invalid OTP" }, { status: 400 });
        }

    } catch (error) {
        console.error("Verification Error:", error);
        return NextResponse.json({ error: "Internal Server Error" }, { status: 500 });
    }
}
