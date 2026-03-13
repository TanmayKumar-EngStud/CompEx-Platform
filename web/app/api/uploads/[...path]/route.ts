
import { NextRequest, NextResponse } from "next/server";
import { readFile } from "fs/promises";
import path from "path";
import fs from "fs";

export async function GET(
    req: NextRequest,
    { params }: { params: { path: string[] } }
) {
    try {
        const filePath = params.path.join("/");

        // Find the storage directory
        // We look for where we saved it in the upload route
        const possibleRoots = [
            path.join(process.cwd(), "public/uploads"),       // Local to process (nested)
            path.join(process.cwd(), "..", "public/uploads"), // Standalone root
            path.join(process.cwd(), "../../..", "public/uploads") // Project root (persistent)
        ];

        let absolutePath = "";
        for (const root of possibleRoots) {
            const checkPath = path.join(root, filePath);
            if (fs.existsSync(checkPath)) {
                absolutePath = checkPath;
                break;
            }
        }

        if (!absolutePath) {
            return new NextResponse("File not found", { status: 404 });
        }

        const fileBuffer = await readFile(absolutePath);
        const extension = path.extname(absolutePath).toLowerCase();

        const contentTypes: Record<string, string> = {
            ".jpg": "image/jpeg",
            ".jpeg": "image/jpeg",
            ".png": "image/png",
            ".gif": "image/gif",
            ".webp": "image/webp",
        };

        return new NextResponse(new Uint8Array(fileBuffer), {
            headers: {
                "Content-Type": contentTypes[extension] || "application/octet-stream",
                "Cache-Control": "public, max-age=31536000, immutable",
            },
        });
    } catch (error) {
        console.error("Error serving upload:", error);
        return new NextResponse("Internal Server Error", { status: 500 });
    }
}
