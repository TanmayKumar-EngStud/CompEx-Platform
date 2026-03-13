
import { NextResponse } from "next/server";
import { prisma } from "@/shared/lib/configs/prisma";

export async function GET() {
    try {
        const user = await prisma.users.findFirst({
            orderBy: { userid: 'asc' },
            select: {
                email: true,
                username: true
            }
        });

        if (!user) {
            return NextResponse.json({ error: "No users found" }, { status: 404 });
        }

        return NextResponse.json({
            email: user.email,
            username: user.username
        });
    } catch (error) {
        console.error("Dev First User Error:", error);
        return NextResponse.json({ error: "Internal Server Error" }, { status: 500 });
    }
}
