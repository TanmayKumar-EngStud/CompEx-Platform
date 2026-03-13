import { NextRequest, NextResponse } from "next/server";
import { getUserIdFromRequest } from "@/shared/lib/utils/auth";
import { prisma } from "@/shared/lib/configs/prisma";
import { z } from "zod";

const ProfileUpdateSchema = z.object({
    username: z.string().min(3).max(50).optional(),
});

export async function PATCH(req: NextRequest) {
    try {
        const userId = await getUserIdFromRequest(req);
        if (!userId) {
            return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
        }

        const body = await req.json();
        const validated = ProfileUpdateSchema.safeParse(body);

        if (!validated.success) {
            return NextResponse.json({ error: "Invalid input", details: validated.error.format() }, { status: 400 });
        }

        const { username } = validated.data;

        if (username) {
            // Check if username is already taken
            const existingUser = await prisma.users.findUnique({
                where: { username },
            });

            if (existingUser && existingUser.userid !== userId) {
                return NextResponse.json({ error: "Username already taken" }, { status: 400 });
            }
        }

        const updatedUser = await prisma.users.update({
            where: { userid: userId },
            data: {
                ...(username && { username }),
            },
            select: {
                userid: true,
                username: true,
                email: true,
                image_url: true,
            } as any,
        });

        return NextResponse.json(updatedUser);
    } catch (error) {
        console.error("Error updating profile:", error);
        return NextResponse.json({ error: "Internal Server Error" }, { status: 500 });
    }
}
