
import { NextRequest, NextResponse } from "next/server";
import { prisma } from "@/shared/lib/configs/prisma";

export const dynamic = 'force-dynamic';

export async function GET(request: NextRequest) {
    const { searchParams } = request.nextUrl;
    const examNameRaw = searchParams.get("examName") || "GRE";
    const userid = parseInt(searchParams.get("userid") || "0");
    const examName = examNameRaw.toUpperCase();

    try {
        // 1. Resolve Exam Type
        const examType = await prisma.examtypes.findFirst({
            where: { name: { equals: examName, mode: 'insensitive' } }
        });

        if (!examType) {
            console.warn(`⚠️ Exam type "${examName}" not found in database.`);
            return NextResponse.json({
                mocks: [],
                examName,
                message: "No mock tests available for this exam type yet."
            });
        }

        const examtypeid = examType.examtypeid;

        // 1. Fetch active mock tests for this exam type
        const mockTests = await prisma.mocktests.findMany({
            where: {
                examtypeid: examtypeid,
                isactive: true
            },
            include: {
                mocksections: {
                    include: {
                        problems: {
                            select: { problemid: true }
                        },
                        ProblemsSet: {
                            select: { problemsSetId: true }
                        }
                    }
                },
                usermocktestattempts: {
                    select: {
                        attemptid: true,
                        totalscore: true,
                        userid: true,
                        isofficialattempt: true
                    }
                }
            }
        });

        // 2. Process and aggregate data
        // eslint-disable-next-line
        const processedMocks = mockTests.map((mock: any) => {
            // Verify content existence
            let hasContent = false;
            let questionCount = 0;

            // eslint-disable-next-line
            mock.mocksections.forEach((section: any) => {
                const pCount = section.problems.length;
                const setCount = section.ProblemsSet.length;
                if (pCount > 0 || setCount > 0) {
                    hasContent = true;
                    questionCount += pCount + setCount; // Rough count of entities
                }
            });

            // If no content, we might skip this mock (or show it as empty)
            // For now, let's include it but maybe user can filter on UI

            // Aggregates
            // Filter to only count OFFICIAL attempts (unique users)
            // eslint-disable-next-line
            const attempts = mock.usermocktestattempts.filter((a: any) => a.isofficialattempt === true);
            const attemptCount = attempts.length;

            let highestScore = 0;
            let totalScoreSum = 0;

            // eslint-disable-next-line
            attempts.forEach((att: any) => {
                const score = Number(att.totalscore) || 0;
                if (score > highestScore) highestScore = score;
                totalScoreSum += score;
            });

            const averageScore = attemptCount > 0 ? (totalScoreSum / attemptCount) : 0;

            return {
                id: mock.mocktestid,
                title: `Mock Paper ${mock.mocktestid}`, // Fallback title
                date: mock.date,
                difficulty: mock.difficulty,
                questionCount,
                stats: {
                    attempts: attemptCount,
                    highestScore: parseFloat(Number(highestScore).toFixed(2)),
                    averageScore: parseFloat(Number(averageScore).toFixed(2))
                },
                hasContent
            };
        });

        // Filter out mocks with absolutely no content if desired
        // const validMocks = processedMocks.filter(m => m.hasContent);
        const validMocks = processedMocks;

        return NextResponse.json({
            mocks: validMocks,
            examName
        });

    } catch (error) {
        console.error("Error fetching mock tests:", error);
        return NextResponse.json(
            { error: "Internal Server Error fetching mock tests" },
            { status: 500 }
        );
    }
}
