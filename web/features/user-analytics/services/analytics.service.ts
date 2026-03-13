import { prisma } from "../../../shared/lib/configs/prisma";
import { truncateBrackets, parseTimeToSeconds } from "../../../shared/lib/utils/formatting";

export async function getUserAnalytics(username: string, examName?: string, sectionName?: string, includeMock: boolean = false) {
    try {
        if (!prisma) {
            console.error("Prisma client not initialized");
            return null;
        }

        const p = prisma as any;
        const user = await p.users.findUnique({
            where: { username },
            select: {
                userid: true,
                username: true,
                registrationdate: true,
                isverified: true,
                email: true,
                image_url: true,
            } as any
        });

        if (!user) return null;

        // Map exam name to ID
        const examMap: Record<string, number> = { "GRE": 1, "GMAT": 2 };
        const examTypeId = examName ? examMap[examName] : undefined;

        // Fetch latest rank separately - Filtered by Exam
        const latestRank = await p.mocktestrankings.findFirst({
            where: {
                userid: user.userid,
                mocktests: {
                    examtypeid: examTypeId
                }
            },
            orderBy: { rankingid: 'desc' },
            select: { rank: true, percentile: true }
        });

        // 1. O(1) Overall Performance & Time Analysis
        const overallStatsRecords = await p.user_overall_performance.findMany({
            where: {
                userid: user.userid,
                ...(!includeMock && { is_mock: false })
            }
        });

        const overallStats = overallStatsRecords.reduce((acc: any, curr: any) => ({
            total_attempts: (acc.total_attempts || 0) + curr.total_attempts,
            total_correct: (acc.total_correct || 0) + curr.total_correct,
            total_incorrect: (acc.total_incorrect || 0) + curr.total_incorrect,
            correct_total_time: (acc.correct_total_time || 0) + curr.correct_total_time,
            incorrect_total_time: (acc.incorrect_total_time || 0) + curr.incorrect_total_time
        }), {
            total_attempts: 0,
            total_correct: 0,
            total_incorrect: 0,
            correct_total_time: 0,
            incorrect_total_time: 0
        });

        // 2. Heatmap & Trend Data
        const attempts = await p.userattempts.findMany({
            where: {
                userid: user.userid,
                problems: {
                    ...(!includeMock && { isMockQuestion: false }),
                    ...(examTypeId && { examtypeid: examTypeId })
                }
            },
            select: {
                attemptdate: true,
                iscorrect: true,
                timetaken: true
            },
            orderBy: { attemptdate: 'asc' }
        });

        const heatmapData: Record<string, number> = {};
        const trendData: Record<string, { correct: number, total: number, totalTime: number }> = {};

        attempts.forEach((attempt: any) => {
            if (attempt.attemptdate) {
                const date = attempt.attemptdate.toISOString().split('T')[0];
                heatmapData[date] = (heatmapData[date] || 0) + 1;
                if (!trendData[date]) trendData[date] = { correct: 0, total: 0, totalTime: 0 };
                trendData[date].total += 1;
                if (attempt.iscorrect) trendData[date].correct += 1;
                trendData[date].totalTime += parseTimeToSeconds(attempt.timetaken);
            }
        });

        const accuracyTrend = Object.entries(trendData)
            .map(([date, stats]: [string, any]) => ({
                date,
                accuracy: Math.round((stats.correct / stats.total) * 100),
                submissions: stats.total,
                avgSpeed: Math.round(stats.totalTime / stats.total)
            }))
            .sort((a, b) => new Date(a.date).getTime() - new Date(b.date).getTime());

        // 3. O(1) Skill Breakdown & Section Distribution
        const allTagScopes = await p.tag_scopes.findMany({
            where: { examtypeid: examTypeId },
            include: {
                tags: true,
                sections: { select: { name: true } }
            }
        });

        const allTagIds = allTagScopes.map((ts: any) => ts.tagScopeId);

        const allTagPerformanceRecords = await p.user_tag_performance.findMany({
            where: {
                userid: user.userid,
                tagScopeId: { in: allTagIds },
                ...(!includeMock && { is_mock: false })
            }
        });

        const perfMap = new Map<number, any>();
        allTagPerformanceRecords.forEach((tp: any) => {
            const sid = tp.tagScopeId;
            if (!perfMap.has(sid)) {
                perfMap.set(sid, {
                    total_attempts: tp.total_attempts,
                    total_correct: tp.total_correct,
                    total_time_seconds: tp.total_time_seconds
                });
            } else {
                const existing = perfMap.get(sid);
                existing.total_attempts += tp.total_attempts;
                existing.total_correct += tp.total_correct;
                existing.total_time_seconds += tp.total_time_seconds;
            }
        });

        const bankCounts = await p.problemtags.groupBy({
            by: ['tagScopeId'],
            where: {
                tagScopeId: { in: allTagIds },
                problems: { ...(!includeMock && { isMockQuestion: false }) }
            },
            _count: { problemid: true }
        });
        const bankCountMap = new Map(bankCounts.map((bc: any) => [bc.tagScopeId, bc._count.problemid]));

        const sectionDistMap: Record<string, number> = {};
        allTagScopes.forEach((ts: any) => {
            const sName = ts.sections?.name || "Unknown";
            if (!sectionDistMap[sName]) sectionDistMap[sName] = 0;
            const perf = perfMap.get(ts.tagScopeId);
            if (perf) sectionDistMap[sName] += perf.total_attempts;
        });

        const sectionDistribution = Object.entries(sectionDistMap).map(([name, count]) => ({ name, count }));

        const skillGroupMap = new Map<string, any>();
        allTagScopes.forEach((ts: any) => {
            const isTopic = ts.tags?.category?.toLowerCase() === 'topic';
            const matchesSection = !sectionName || (ts.sections?.name?.toLowerCase() === sectionName.toLowerCase());
            if (isTopic && matchesSection) {
                const tagName = truncateBrackets(ts.tags?.name || "Unknown");
                const s = ts.sections?.name || "Unknown";
                const key = `${tagName}|${s}`;
                const perf = perfMap.get(ts.tagScopeId) || { total_attempts: 0, total_correct: 0, total_time_seconds: 0 };
                const bankTotal = bankCountMap.get(ts.tagScopeId) || 0;

                if (!skillGroupMap.has(key)) {
                    skillGroupMap.set(key, {
                        tag: tagName, section: s, correct: perf.total_correct, incorrect: perf.total_attempts - perf.total_correct,
                        totalInBank: bankTotal, total_attempts: perf.total_attempts, total_time_seconds: perf.total_time_seconds
                    });
                } else {
                    const existing = skillGroupMap.get(key);
                    existing.correct += perf.total_correct;
                    existing.incorrect += (perf.total_attempts - perf.total_correct);
                    existing.totalInBank += bankTotal;
                    existing.total_attempts += perf.total_attempts;
                    existing.total_time_seconds += perf.total_time_seconds;
                }
            }
        });

        const skillBarData = Array.from(skillGroupMap.values())
            // Only show tags that have at least one question in the bank under the
            // current mock-data setting.  When includeMock=false, mock-only tags
            // produce totalInBank=0 and are excluded.  Truly empty tag_scopes
            // (no problems at all) are also excluded regardless of the toggle.
            .filter((s: any) => s.totalInBank > 0)
            .map((s: any) => ({
                tag: s.tag, section: s.section, correct: s.correct, incorrect: s.incorrect, totalInBank: s.totalInBank,
                avgTime: s.total_attempts > 0 ? Math.round(s.total_time_seconds / s.total_attempts) : 0,
                accuracy: s.total_attempts > 0 ? Math.round((s.correct / s.total_attempts) * 100) : 0,
                attemptCount: s.total_attempts
            }))
            .sort((a: any, b: any) => b.attemptCount - a.attemptCount || b.totalInBank - a.totalInBank)
            .slice(0, 50);

        // 4. O(1) Difficulty Breakdown - REFACTORED for Exam Isolation
        const rawStats = await p.userattempts.findMany({
            where: {
                userid: user.userid,
                problems: {
                    examtypeid: examTypeId,
                    ...(!includeMock && { isMockQuestion: false })
                }
            },
            select: {
                iscorrect: true,
                problems: { select: { difficulty: true } }
            }
        });

        const statsByLevel: Record<number, { total: number, correct: number }> = {
            1: { total: 0, correct: 0 },
            2: { total: 0, correct: 0 },
            3: { total: 0, correct: 0 },
            4: { total: 0, correct: 0 },
            5: { total: 0, correct: 0 }
        };
        rawStats.forEach((rs: any) => {
            const diff = rs.problems?.difficulty;
            if (diff && statsByLevel[diff]) {
                statsByLevel[diff].total += 1;
                if (rs.iscorrect) statsByLevel[diff].correct += 1;
            }
        });

        const bankTotalsDb = await p.problems.groupBy({
            by: ['difficulty'],
            where: { ...(!includeMock && { isMockQuestion: false }), ...(examTypeId && { examtypeid: examTypeId }) },
            _count: { problemid: true }
        });

        const bankTotals: Record<number, number> = {};
        bankTotalsDb.forEach((bt: any) => { if (bt.difficulty) bankTotals[bt.difficulty] = bt._count.problemid; });

        const difficultyData = [1, 2, 3, 4, 5].map(level => {
            const stats = statsByLevel[level];
            return {
                difficulty: level,
                totalAttempts: stats.total,
                correctAttempts: stats.correct,
                totalQuestionsInLevel: bankTotals[level] || 0
            };
        });

        // 5. Detailed Time Analysis (User vs Community)
        const userCorrectTimes = attempts.filter((a: any) => a.iscorrect).map((a: any) => parseTimeToSeconds(a.timetaken));
        const userIncorrectTimes = attempts.filter((a: any) => !a.iscorrect).map((a: any) => parseTimeToSeconds(a.timetaken));

        const userTimeStats = {
            correct: {
                min: userCorrectTimes.length > 0 ? Math.min(...userCorrectTimes) : 0,
                max: userCorrectTimes.length > 0 ? Math.max(...userCorrectTimes) : 0,
                avg: overallStats.total_correct > 0 ? Math.round(overallStats.correct_total_time / overallStats.total_correct) : 0
            },
            incorrect: {
                min: userIncorrectTimes.length > 0 ? Math.min(...userIncorrectTimes) : 0,
                max: userIncorrectTimes.length > 0 ? Math.max(...userIncorrectTimes) : 0,
                avg: overallStats.total_incorrect > 0 ? Math.round(overallStats.incorrect_total_time / overallStats.total_incorrect) : 0
            }
        };

        const allAttempts = await p.userattempts.findMany({
            where: { problems: { ...(!includeMock && { isMockQuestion: false }), ...(examTypeId && { examtypeid: examTypeId }) } },
            select: { iscorrect: true, timetaken: true }
        });

        const commCorrectTimes = allAttempts.filter((a: any) => a.iscorrect).map((a: any) => parseTimeToSeconds(a.timetaken));
        const commIncorrectTimes = allAttempts.filter((a: any) => !a.iscorrect).map((a: any) => parseTimeToSeconds(a.timetaken));

        const communityTimeStats = {
            correct: {
                min: commCorrectTimes.length > 0 ? Math.min(...commCorrectTimes) : 0,
                max: commCorrectTimes.length > 0 ? Math.max(...commCorrectTimes) : 0,
                avg: commCorrectTimes.length > 0 ? Math.round(commCorrectTimes.reduce((a: any, b: any) => a + b, 0) / commCorrectTimes.length) : 0
            },
            incorrect: {
                min: commIncorrectTimes.length > 0 ? Math.min(...commIncorrectTimes) : 0,
                max: commIncorrectTimes.length > 0 ? Math.max(...commIncorrectTimes) : 0,
                avg: commIncorrectTimes.length > 0 ? Math.round(commIncorrectTimes.reduce((a: any, b: any) => a + b, 0) / commIncorrectTimes.length) : 0
            }
        };

        // 6. Global Score Calculation - REFACTORED to Restore Summation while Keeping Isolation
        const practiceWeights: Record<number, number> = { 1: 10, 2: 30, 3: 80, 4: 200, 5: 500 };

        // Calculate User Earned XP for this Exam (Cumulative)
        const practiceXP = difficultyData.reduce((sum, d) => sum + (d.correctAttempts * (practiceWeights[d.difficulty] || 0)), 0);

        // Fetch best mock score for normalization - Filtered by Exam
        const bestMockAttempt = await p.usermocktestattempts.findFirst({
            where: {
                userid: user.userid,
                mocktests: {
                    examtypeid: examTypeId
                }
            },
            orderBy: { totalscore: 'desc' },
            select: { totalscore: true }
        });

        const latestPercentile = latestRank?.percentile ? Number(latestRank.percentile) : 0;
        const bestMockScore = bestMockAttempt?.totalscore ? Number(bestMockAttempt.totalscore) : 0;

        // Normalize Best Mock Score
        const mockMaxBaseline = bestMockScore > 170 ? 800 : 170;
        const normalizedBestMock = Math.min((bestMockScore / mockMaxBaseline) * 100, 100);

        const mockScore = (latestPercentile * 0.7) + (normalizedBestMock * 0.3);

        // Global Score: weighted blend of Practice and Mock
        // PS Normalization: Soft cap of 50,000 for 0-100 mapping
        const normalizedPS = Math.min((practiceXP / 50000) * 100, 100);
        const globalScore = (normalizedPS * 0.4) + (mockScore * 0.6);

        return {
            user: {
                userid: user.userid,
                username: user.username,
                email: user.email,
                joinDate: user.registrationdate,
                rank: latestRank?.rank || null,
                percentile: latestRank?.percentile ? Number(latestRank.percentile) : null,
                isVerified: user.isverified,
                image_url: user.image_url,
                scores: {
                    practice: Math.round(practiceXP),
                    mock: Math.round(mockScore),
                    global: Math.round(globalScore)
                }
            },
            analytics: {
                heatmap: Object.entries(heatmapData).map(([date, count]) => ({ date, count })),
                skills: skillBarData,
                difficulty: difficultyData,
                accuracyTrend,
                timeAnalysis: {
                    user: userTimeStats,
                    community: communityTimeStats,
                    correctCount: overallStats.total_correct || 0,
                    incorrectCount: overallStats.total_incorrect || 0
                },
                sectionDistribution
            }
        };
    } catch (error: any) {
        console.error("Critical Analytics Error (getUserAnalytics):", error.message);
        throw error;
    }
}


export async function getMockAnalytics(username: string, examName?: string) {
    try {
        const p = prisma as any;
        const user = await p.users.findUnique({
            where: { username },
            select: { userid: true }
        });

        if (!user) return null;

        const examMap: Record<string, number> = { "GRE": 1, "GMAT": 2 };
        const examTypeId = examName ? examMap[examName] : undefined;

        // 1. Fetch User Mock Attempts (O(m) where m is mocks taken)
        const userAttempts = await p.usermocktestattempts.findMany({
            where: {
                userid: user.userid,
                ...(examTypeId && { mocktests: { examtypeid: examTypeId } })
            },
            include: {
                mocktests: true,
                mocktestsectionscores: {
                    include: {
                        sections: true
                    }
                }
            },
            orderBy: { endtime: 'asc' }
        });

        // Deduplicate
        const latestAttemptsMap = new Map<number, any>();
        userAttempts.forEach((attempt: any) => {
            if (attempt.mocktestid) {
                latestAttemptsMap.set(attempt.mocktestid, attempt);
            }
        });
        const uniqueAttempts = Array.from(latestAttemptsMap.values());

        // 2. Fetch O(1) Community Stats for each mock
        const mockIds = uniqueAttempts.map(a => a.mocktestid).filter(Boolean) as number[];
        const communityStats = await p.mock_community_aggregates.findMany({
            where: { mocktestid: { in: mockIds } }
        });

        const userRankings = await p.mocktestrankings.findMany({
            where: { userid: user.userid, mocktestid: { in: mockIds } }
        });

        const mockPerformance = uniqueAttempts.map(attempt => {
            const stats = communityStats.find((s: any) => s.mocktestid === attempt.mocktestid);
            const ranking = userRankings.find((r: any) => r.mocktestid === attempt.mocktestid);
            const userScore = Number(attempt.totalscore || 0);

            return {
                mockId: attempt.mocktestid,
                date: attempt.endtime,
                userScore,
                difficulty: attempt.mocktests?.difficulty || 0,
                rank: ranking?.rank || 0,
                totalParticipants: stats?.participants_count || 0,
                percentile: Number(ranking?.percentile || 0),
                communityStats: stats ? {
                    min: stats.min_score,
                    max: stats.max_score,
                    avg: stats.avg_score,
                    q1: stats.q1,
                    median: stats.median,
                    q3: stats.q3
                } : null,
                sections: attempt.mocktestsectionscores.map((s: any) => ({
                    name: s.sections?.name,
                    score: Number(s.score || 0)
                }))
            };
        });

        // 3. Community Score Distribution for Latest Mock (O(1))
        let latestMockDistribution: { score: number, frequency: number }[] = [];
        if (uniqueAttempts.length > 0) {
            const latestMockId = uniqueAttempts[uniqueAttempts.length - 1].mocktestid;
            if (latestMockId) {
                const dist = await (prisma as any).mock_score_distribution_stats.findMany({
                    where: { mocktestid: latestMockId },
                    orderBy: { score: 'asc' }
                });
                latestMockDistribution = dist.map((d: any) => ({ score: d.score, frequency: d.frequency }));
            }
        }

        return {
            mocks: mockPerformance,
            sectionAverages: [], // Placeholder
            latestMockDistribution,
            percentileTrend: mockPerformance.map(m => ({
                date: m.date,
                percentile: m.percentile
            }))
        };
    } catch (error: any) {
        console.error("Critical Analytics Error (getMockAnalytics):", error.message);
        console.log("Available Prisma keys:", Object.keys(prisma || {}));
        throw error;
    }
}

