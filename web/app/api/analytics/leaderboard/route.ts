
import { NextRequest, NextResponse } from "next/server";
import { prisma as p } from "@/shared/lib/configs/prisma";

export const dynamic = 'force-dynamic';

export async function GET(request: NextRequest) {
    const { searchParams } = new URL(request.url);
    const exam = searchParams.get("exam") || "GRE";
    const targetUsername = searchParams.get("username");
    const pageSize = 15;

    const examMap: Record<string, number> = { "GRE": 1, "GMAT": 2 };
    const examTypeId = examMap[exam] || 1;

    try {
        // 1. Get all users who have at least one attempt or mock attempt in this exam
        const users = await p.users.findMany({
            select: {
                userid: true,
                username: true,
                usermocktestattempts: {
                    where: { mocktests: { examtypeid: examTypeId } },
                    orderBy: { totalscore: 'desc' },
                    take: 1,
                    select: { totalscore: true }
                },
                mocktestrankings: {
                    where: { mocktests: { examtypeid: examTypeId } },
                    orderBy: { rankingid: 'desc' },
                    take: 1,
                    select: { percentile: true }
                }
            }
        });

        // 2. Get all correct practice attempts for these users in this exam
        const allCorrectAttempts = await p.userattempts.findMany({
            where: {
                iscorrect: true,
                problems: { examtypeid: examTypeId }
            },
            select: {
                userid: true,
                problems: { select: { difficulty: true } }
            }
        });

        // 3. Aggregate Practice XP per user
        const practiceWeights: Record<number, number> = { 1: 10, 2: 30, 3: 80, 4: 200, 5: 500 };
        const userPracticeXP: Record<number, number> = {};
        allCorrectAttempts.forEach((attempt: any) => {
            if (!attempt.userid) return;
            const diff = attempt.problems?.difficulty || 1;
            userPracticeXP[attempt.userid] = (userPracticeXP[attempt.userid] || 0) + (practiceWeights[diff] || 0);
        });

        // 4. Calculate Global Rating for each user
        const practiceSoftCap = 50000;
        // eslint-disable-next-line
        const leaderboardData = users.map((user: any) => {
            const pxp = userPracticeXP[user.userid] || 0;
            const normalizedPS = Math.min((pxp / practiceSoftCap) * 100, 100);

            const bestMockScore = user.usermocktestattempts[0]?.totalscore ? Number(user.usermocktestattempts[0].totalscore) : 0;
            const latestPercentile = user.mocktestrankings[0]?.percentile ? Number(user.mocktestrankings[0].percentile) : 0;

            const mockMaxBaseline = bestMockScore > 170 ? 800 : 170;
            const normalizedBestMock = bestMockScore > 0 ? Math.min((bestMockScore / mockMaxBaseline) * 100, 100) : 0;

            const mockScore = (latestPercentile * 0.7) + (normalizedBestMock * 0.3);
            const globalRating = (normalizedPS * 0.4) + (mockScore * 0.6);

            return {
                userid: user.userid,
                username: user.username,
                xp: pxp, // Still keep XP for potential secondary display
                rating: Math.round(globalRating)
            };
        });

        // 5. Sort by Global Rating
        const sortedLeaderboard = leaderboardData
            // eslint-disable-next-line
            .sort((a: any, b: any) => b.rating - a.rating || b.xp - a.xp || a.username.localeCompare(b.username))
            // eslint-disable-next-line
            .map((user: any, index: number) => ({
                ...user,
                rank: index + 1
            }));

        // 6. Find target user's page
        let targetPage = 1;
        if (targetUsername) {
            // eslint-disable-next-line
            const userIndex = sortedLeaderboard.findIndex((u: any) => u.username === targetUsername);
            if (userIndex !== -1) {
                targetPage = Math.floor(userIndex / pageSize) + 1;
            }
        }

        // 7. Handle requested page
        const requestedPage = Number(searchParams.get("page")) || targetPage;
        const start = (requestedPage - 1) * pageSize;
        const pagedData = sortedLeaderboard.slice(start, start + pageSize);

        return NextResponse.json({
            users: pagedData,
            totalUsers: sortedLeaderboard.length,
            currentPage: requestedPage,
            userPage: targetPage,
            pageSize
        });

    } catch (error) {
        console.error("Leaderboard API Error:", error);
        return NextResponse.json({ error: "Failed to fetch leaderboard" }, { status: 500 });
    }
}
