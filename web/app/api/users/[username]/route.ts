
import { NextRequest, NextResponse } from "next/server";
import { getUserIdFromRequest } from "@/shared/lib/utils/auth";
import { prisma } from "@/shared/lib/configs/prisma";

export async function DELETE(
    req: NextRequest,
    { params }: { params: Promise<{ username: string }> }
) {
    try {
        const { username } = await params;
        const currentUserId = await getUserIdFromRequest(req);

        if (!currentUserId) {
            return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
        }

        // Fetch the user to be deleted
        const userToDelete = await prisma.users.findUnique({
            where: { username },
            select: { userid: true, username: true }
        });

        if (!userToDelete) {
            return NextResponse.json({ error: "User not found" }, { status: 404 });
        }

        // Security check: only the owner can delete their account
        if (userToDelete.userid !== currentUserId) {
            return NextResponse.json({ error: "Forbidden: You can only delete your own account" }, { status: 403 });
        }

        // Delete the user (Prisma cascade will handle the rest)
        await prisma.users.delete({
            where: { userid: userToDelete.userid }
        });

        return NextResponse.json({ message: "Account deleted successfully" });
    } catch (error: any) {
        console.error("Error deleting user:", error);
        return NextResponse.json({ error: "Internal Server Error" }, { status: 500 });
    }
}
