
import { jwtVerify } from "jose";
import { NextRequest } from "next/server";

const JWT_SECRET = new TextEncoder().encode(
    process.env.JWT_SECRET || "fallback-secret-for-development-must-change-later"
);

export async function getUserIdFromRequest(request: NextRequest): Promise<number | null> {
    const token = request.cookies.get("session_token")?.value;
    if (!token) return null;

    try {
        const { payload } = await jwtVerify(token, JWT_SECRET);
        return payload.userId as number || null;
    } catch (error) {
        console.error("JWT Verification failed:", error);
        return null;
    }
}

export async function getCurrentUser(): Promise<number | null> {
    const { cookies } = await import("next/headers");
    const cookieStore = await cookies();
    const token = cookieStore.get("session_token")?.value;
    if (!token) return null;

    try {
        const { payload } = await jwtVerify(token, JWT_SECRET);
        return payload.userId as number || null;
    } catch (error) {
        return null;
    }
}
