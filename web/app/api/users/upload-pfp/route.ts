import { NextRequest, NextResponse } from "next/server";
import { getUserIdFromRequest } from "@/shared/lib/utils/auth";
import { prisma } from "@/shared/lib/configs/prisma";
import { writeFile, mkdir } from "fs/promises";
import path from "path";

export async function POST(req: NextRequest) {
    try {
        const userId = await getUserIdFromRequest(req);
        if (!userId) {
            return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
        }

        const formData = await req.formData();
        const file = formData.get("file") as File;

        if (!file) {
            return NextResponse.json({ error: "No file uploaded" }, { status: 400 });
        }

        // Validate basic image types
        const allowedTypes = ["image/jpeg", "image/png", "image/webp", "image/gif"];
        if (!allowedTypes.includes(file.type)) {
            return NextResponse.json({ error: "Invalid file type. Only JPG, PNG, WEBP, and GIF are allowed." }, { status: 400 });
        }

        // Limit size (e.g., 2MB)
        if (file.size > 2 * 1024 * 1024) {
            return NextResponse.json({ error: "File too large. Max size is 2MB." }, { status: 400 });
        }

        const bytes = await file.arrayBuffer();
        const buffer = Buffer.from(bytes);

        // Define storage path
        const extension = file.name.split('.').pop() || 'png';
        const fileName = `avatar_${userId}_${Date.now()}.${extension}`;
        const relativePath = `/api/uploads/avatars/${fileName}`;

        // Next.js standalone workaround: 
        // We write to all possible public directories to ensure persistence and visibility
        const possiblePublicDirs = [
            path.join(process.cwd(), "public/uploads/avatars"),       // Local to process (nested)
            path.join(process.cwd(), "..", "public/uploads/avatars"), // Standalone root
            path.join(process.cwd(), "../../..", "public/uploads/avatars") // Project root (persistent)
        ];

        // Ensure directories exist and save file to all
        await Promise.all(possiblePublicDirs.map(async (dir) => {
            try {
                await mkdir(dir, { recursive: true });
                await writeFile(path.join(dir, fileName), new Uint8Array(buffer));
            } catch (err) {
                // Silently skip if path doesn't exist or is unwritable
            }
        }));

        // Update database with the local URL
        const updatedUser = await prisma.users.update({
            where: { userid: userId },
            data: {
                image_url: relativePath,
            } as any,
            select: {
                userid: true,
                username: true,
                image_url: true,
            } as any,
        });

        return NextResponse.json(updatedUser);
    } catch (error) {
        console.error("Error saving PFP locally:", error);
        return NextResponse.json({ error: "Internal Server Error" }, { status: 500 });
    }
}
