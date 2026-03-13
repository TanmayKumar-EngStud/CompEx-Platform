import { NextResponse } from "next/server";

export async function GET() {
    const clientId = process.env.GOOGLE_CLIENT_ID;
    if (!clientId) {
        return NextResponse.json({ error: "Google OAuth not configured" }, { status: 500 });
    }

    const redirectUri = process.env.NODE_ENV === "production"
        ? "https://www.compex.live/api/auth/callback/google"
        : "http://localhost:3000/api/auth/callback/google";

    const params = new URLSearchParams({
        client_id: clientId,
        redirect_uri: redirectUri,
        response_type: "code",
        scope: "email profile",
        access_type: "offline",
        prompt: "select_account",
    });

    return NextResponse.redirect(`https://accounts.google.com/o/oauth2/v2/auth?${params.toString()}`);
}
