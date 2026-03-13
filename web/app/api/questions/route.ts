
import { NextRequest, NextResponse } from "next/server";
import { prisma } from "@/shared/lib/configs/prisma";

export const dynamic = 'force-dynamic';

export async function GET(request: NextRequest) {
    const { searchParams } = request.nextUrl;
    const page = parseInt(searchParams.get("page") || "1");
    const limit = parseInt(searchParams.get("limit") || "20");
    const examName = searchParams.get("examName"); // optional filter
    const search = searchParams.get("search"); // optional text search

    const skip = (page - 1) * limit;

    try {
        const whereClause: any = {};

        if (examName) {
            whereClause.examtypes = {
                name: { contains: examName, mode: 'insensitive' }
            };
        }

        if (search) {
            whereClause.OR = [
                { title: { contains: search, mode: 'insensitive' } },
                { text: { contains: search, mode: 'insensitive' } }
            ];
        }

        const [questions, total] = await Promise.all([
            prisma.problems.findMany({
                where: whereClause,
                skip,
                take: limit,
                orderBy: { problemid: 'desc' },
                include: {
                    examtypes: { select: { name: true } },
                    sections: { select: { name: true } },
                    problemoptions: true
                }
            }),
            prisma.problems.count({ where: whereClause })
        ]);

        return NextResponse.json({
            data: questions,
            meta: {
                total,
                page,
                limit,
                totalPages: Math.ceil(total / limit)
            }
        });

    } catch (error) {
        console.error("Error fetching questions:", error);
        return NextResponse.json(
            { error: "Internal Server Error fetching questions" },
            { status: 500 }
        );
    }
}
