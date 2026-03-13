import { NextRequest, NextResponse } from "next/server";
import { prisma } from "@/shared/lib/configs/prisma";
import bcrypt from "bcryptjs";
import { SignJWT } from "jose";
import crypto from "crypto";

const JWT_SECRET = new TextEncoder().encode(
    process.env.JWT_SECRET || "fallback-secret-for-development-must-change-later"
);

interface GoogleTokenResponse {
    access_token: string;
    id_token: string;
    token_type: string;
}

interface GoogleUserInfo {
    id: string;
    email: string;
    name: string;
    picture: string;
    verified_email: boolean;
}

export async function GET(req: NextRequest) {
    const baseUrl = process.env.NODE_ENV === "production"
        ? "https://www.compex.live"
        : "http://localhost:3000";

    try {
        const code = req.nextUrl.searchParams.get("code");
        const error = req.nextUrl.searchParams.get("error");

        if (error) {
            return NextResponse.redirect(`${baseUrl}/login?error=google_denied`);
        }

        if (!code) {
            return NextResponse.redirect(`${baseUrl}/login?error=no_code`);
        }

        // 1. Exchange code for tokens
        const redirectUri = `${baseUrl}/api/auth/callback/google`;
        const tokenRes = await fetch("https://oauth2.googleapis.com/token", {
            method: "POST",
            headers: { "Content-Type": "application/x-www-form-urlencoded" },
            body: new URLSearchParams({
                code,
                client_id: process.env.GOOGLE_CLIENT_ID!,
                client_secret: process.env.GOOGLE_CLIENT_SECRET!,
                redirect_uri: redirectUri,
                grant_type: "authorization_code",
            }),
        });

        if (!tokenRes.ok) {
            console.error("Google token exchange failed:", await tokenRes.text());
            return NextResponse.redirect(`${baseUrl}/login?error=token_exchange_failed`);
        }

        const tokens: GoogleTokenResponse = await tokenRes.json();

        // 2. Fetch user profile
        const userRes = await fetch("https://www.googleapis.com/oauth2/v2/userinfo", {
            headers: { Authorization: `Bearer ${tokens.access_token}` },
        });

        if (!userRes.ok) {
            console.error("Google userinfo fetch failed:", await userRes.text());
            return NextResponse.redirect(`${baseUrl}/login?error=userinfo_failed`);
        }

        const googleUser: GoogleUserInfo = await userRes.json();

        if (!googleUser.email) {
            return NextResponse.redirect(`${baseUrl}/login?error=no_email`);
        }

        // 3. Find or create user
        let user = await prisma.users.findUnique({
            where: { email: googleUser.email },
        });

        if (!user) {
            // Generate unique username from email prefix
            const baseUsername = googleUser.email.split("@")[0].replace(/[^a-zA-Z0-9]/g, "").slice(0, 40);
            let username = baseUsername;
            let suffix = 1;

            // Handle username collisions
            while (await prisma.users.findUnique({ where: { username } })) {
                username = `${baseUsername}${suffix}`;
                suffix++;
            }

            // Sentinel password (schema requires non-null) — unhashable random value
            const sentinelPassword = await bcrypt.hash(crypto.randomUUID(), 10);

            user = await prisma.users.create({
                data: {
                    username,
                    email: googleUser.email,
                    password: sentinelPassword,
                    isverified: true,
                    image_url: googleUser.picture || null,
                },
            });
        } else {
            // Update profile picture if changed
            if (googleUser.picture && googleUser.picture !== user.image_url) {
                await prisma.users.update({
                    where: { userid: user.userid },
                    data: { image_url: googleUser.picture },
                });
            }
        }

        // 4. Sign JWT (same pattern as login/route.ts)
        const token = await new SignJWT({
            userId: user.userid,
            email: user.email,
        })
            .setProtectedHeader({ alg: "HS256" })
            .setIssuedAt()
            .setExpirationTime("24h")
            .sign(JWT_SECRET);

        // 5. Set cookie and redirect
        const response = NextResponse.redirect(`${baseUrl}/dashboard/explore`);
        response.cookies.set("session_token", token, {
            httpOnly: true,
            secure: process.env.NODE_ENV === "production",
            sameSite: "lax",
            maxAge: 60 * 60 * 24, // 24 hours
            path: "/",
        });

        return response;

    } catch (error) {
        console.error("Google OAuth callback error:", error);
        return NextResponse.redirect(`${baseUrl}/login?error=oauth_failed`);
    }
}
