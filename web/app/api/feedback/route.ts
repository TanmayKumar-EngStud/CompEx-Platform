
import { NextRequest, NextResponse } from "next/server";
import { prisma } from "@/shared/lib/configs/prisma";
import { getUserIdFromRequest } from "@/shared/lib/utils/auth";
import { z } from "zod";

const feedbackSchema = z.object({
    type: z.enum(["suggestion", "bug", "feature_request"]),
    content: z.string().min(1).max(2000),
    url: z.string().optional(),
});

export async function POST(req: NextRequest) {
    try {
        const body = await req.json();
        const validated = feedbackSchema.safeParse(body);

        if (!validated.success) {
            return NextResponse.json({ error: "Invalid input", details: validated.error.format() }, { status: 400 });
        }

        const userId = await getUserIdFromRequest(req);

        const feedback = await (prisma as any).userfeedback.create({
            data: {
                type: validated.data.type,
                content: validated.data.content,
                url: validated.data.url,
                userid: userId || null,
            },
        });

        return NextResponse.json({ message: "Feedback submitted successfully!", id: feedback.feedbackid }, { status: 201 });

    } catch (error) {
        console.error("Feedback API Error:", error);
        return NextResponse.json({ error: "Internal Server Error" }, { status: 500 });
    }
}
