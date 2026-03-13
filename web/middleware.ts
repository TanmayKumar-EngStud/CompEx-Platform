
import { NextRequest, NextResponse } from "next/server";
import { jwtVerify } from "jose";

const JWT_SECRET = new TextEncoder().encode(
    process.env.JWT_SECRET || "fallback-secret-for-development-must-change-later"
);

export async function middleware(request: NextRequest) {
    const token = request.cookies.get("session_token")?.value;

    // Paths that require authentication
    if (request.nextUrl.pathname.startsWith("/dashboard")) {
        if (!token) {
            return NextResponse.redirect(new URL("/login", request.url));
        }

        try {
            await jwtVerify(token, JWT_SECRET);
            return NextResponse.next();
        } catch (error) {
            console.error("JWT Verification failed:", error);
            // Token is invalid or expired
            const response = NextResponse.redirect(new URL("/login", request.url));
            response.cookies.delete("session_token");
            return response;
        }
    }

    // Paths that should not be accessible by logged-in users (unless forcing a new session)
    const authPaths = ["/login", "/signup"];
    if (authPaths.some(path => request.nextUrl.pathname.startsWith(path))) {
        const force = request.nextUrl.searchParams.get("force") === "true";
        
        if (token && !force) {
            try {
                await jwtVerify(token, JWT_SECRET);
                // Already logged in, go to dashboard
                return NextResponse.redirect(new URL("/dashboard/mock", request.url));
            } catch (e) {
                // Invalid token, allow access to auth pages
                return NextResponse.next();
            }
        }
        
        if (token && force) {
            // Force clear session to allow new signup/login
            const response = NextResponse.next();
            response.cookies.delete("session_token");
            return response;
        }
    }

    return NextResponse.next();
}

export const config = {
    matcher: ["/dashboard/:path*", "/login", "/signup"],
};
