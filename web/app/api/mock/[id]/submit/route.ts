
import { NextRequest, NextResponse } from "next/server";
import { prisma } from "@/shared/lib/configs/prisma";
import { getUserIdFromRequest } from "@/shared/lib/utils/auth";
import { parseTimeToSeconds } from "@/shared/lib/utils/formatting";

export async function POST(
    request: NextRequest,
    { params }: { params: Promise<{ id: string }> }
) {
    const { id } = await params;
    const mockId = parseInt(id);
    const body = await request.json();
    const { answers, timesTaken } = body;

    // Get secure userId from session cookie
    const userId = await getUserIdFromRequest(request);

    if (isNaN(mockId) || !userId) {
        return NextResponse.json({ error: "Unauthorized or invalid request data" }, { status: 401 });
    }

    try {
        // 1. Fetch mock test with all correct answers
        const mockTest = await prisma.mocktests.findUnique({
            where: { mocktestid: mockId },
            include: {
                mocksections: {
                    include: {
                        problems: {
                            include: {
                                problemoptions: true,
                                problemtags: {
                                    include: {
                                        tag_scopes: {
                                            include: {
                                                tags: true
                                            }
                                        }
                                    }
                                }
                            }
                        },
                        ProblemsSet: {
                            include: {
                                problems: {
                                    include: {
                                        problemoptions: true,
                                        problemtags: {
                                            include: {
                                                tag_scopes: {
                                                    include: {
                                                        tags: true
                                                    }
                                                }
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }
        });

        if (!mockTest) {
            return NextResponse.json({ error: "Mock test not found" }, { status: 404 });
        }

        // 2. Check for existing COMPLETED official attempt
        const completedOfficialAttempt = await prisma.usermocktestattempts.findFirst({
            where: {
                userid: userId,
                mocktestid: mockId,
                isofficialattempt: true,
                endtime: { not: null }
            }
        });

        const isFirstAttempt = !completedOfficialAttempt;

        // Find the "In Progress" official attempt if it exists
        const inProgressOfficial = await prisma.usermocktestattempts.findFirst({
            where: {
                userid: userId,
                mocktestid: mockId,
                isofficialattempt: true,
                endtime: null
            }
        });

        // 3. Process results
        const results: any[] = [];
        let totalScore = 0;
        const sectionScores: Map<number, number> = new Map();

        // eslint-disable-next-line
        mockTest.mocksections.forEach((ms: any) => {
            let sectionScore = 0;

            function transformProblem(p: any, mergedMetadata?: any) {
                const selected = answers[p.problemid] || [];
                // eslint-disable-next-line
                const correctOptions = p.problemoptions.filter((o: any) => o.iscorrect).map((o: any) => o.optiontext);

                const isCorrect = selected.length === correctOptions.length &&
                    selected.every((s: string) => correctOptions.includes(s));

                if (isCorrect) {
                    sectionScore++;
                    totalScore++;
                }

                return {
                    problemid: p.problemid,
                    type: p.type,
                    title: p.title,
                    text: p.text,
                    diagram: (p.metadata as any)?.diagram || null,
                    difficulty: p.difficulty || 3,
                    selectedoption: selected,
                    correctoption: correctOptions,
                    timetaken: formatTimeTaken(timesTaken[p.problemid] || 0),
                    solution: p.solution,
                    metadata: mergedMetadata || p.metadata,
                    options_type: p.options_type,
                    // eslint-disable-next-line
                    options: p.problemoptions.map((o: any) => ({
                        optiontext: o.optiontext,
                        group: o.group
                    })),
                    // eslint-disable-next-line
                    problemtags: p.problemtags.map((pt: any) => ({
                        tags: {
                            tagScopeId: pt.tagScopeId,
                            topic: pt.tag_scopes.tags.category === "Topic" ? pt.tag_scopes.tags.name : null,
                            theme: pt.tag_scopes.tags.category === "Theme" ? pt.tag_scopes.tags.name : null,
                            type: pt.tag_scopes.tags.category === "Type" ? pt.tag_scopes.tags.name : null,
                            name: pt.tag_scopes.tags.name
                        }
                    }))
                };
            }

            // Combine single problems and problems from sets
            // eslint-disable-next-line
            ms.problems.filter((p: any) => !p.problemsSetId).forEach((p: any) => {
                results.push(transformProblem(p));
            });

            // eslint-disable-next-line
            ms.ProblemsSet.forEach((ps: any) => {
                // eslint-disable-next-line
                ps.problems.forEach((p: any) => {
                    const mergedMetadata = {
                        ...(p.metadata as any || {}),
                        problemsSetId: ps.problemsSetId,
                        content: ps.content,
                        setType: ps.type
                    };
                    results.push(transformProblem(p, mergedMetadata));
                });
            });

            sectionScores.set(ms.sectionid, sectionScore);
        });

        // 4. Save to DB (Update in-progress official, or update existing official score)
        // eslint-disable-next-line
        await prisma.$transaction(async (tx: any) => {
            // LOCK: Acquire a row-level lock on the mock test record to prevent race conditions
            // This ensures that concurrent submissions for the same mock are serialized,
            // which is critical for accurate community aggregate calculations.
            await tx.$executeRaw`SELECT * FROM mocktests WHERE mocktestid = ${mockId} FOR UPDATE`;

            let attempt;

            if (isFirstAttempt && inProgressOfficial) {
                // Update the locked official attempt (first real submission)
                attempt = await tx.usermocktestattempts.update({
                    where: { attemptid: inProgressOfficial.attemptid },
                    data: {
                        endtime: new Date(),
                        totalscore: totalScore
                    }
                });
            } else if (completedOfficialAttempt) {
                // Retake: Update the existing official record ONLY if score is higher
                attempt = completedOfficialAttempt;
                const currentScore = Number(completedOfficialAttempt.totalscore);

                if (totalScore > currentScore) {
                    await tx.usermocktestattempts.update({
                        where: { attemptid: completedOfficialAttempt.attemptid },
                        data: { totalscore: totalScore }
                    });
                }

                // Delete old section scores for this attempt to prevent duplicates
                await tx.mocktestsectionscores.deleteMany({
                    where: { attemptid: attempt.attemptid }
                });
            } else {
                // Create a practice attempt (should not happen for official mocks but for safety)
                attempt = await tx.usermocktestattempts.create({
                    data: {
                        userid: userId,
                        mocktestid: mockId,
                        starttime: new Date(Date.now() - 3600000), // Placeholder
                        endtime: new Date(),
                        totalscore: totalScore,
                        isofficialattempt: false
                    }
                });
            }

            // 5. Update individual user attempts and real-time analytics
            for (const res of results) {
                const isCorrect = res.selectedoption.length === res.correctoption.length &&
                    res.selectedoption.every((s: string) => res.correctoption.includes(s));

                const timeInSeconds = parseTimeToSeconds(res.timetaken);

                const userAttempt = await tx.userattempts.create({
                    data: {
                        userid: userId,
                        problemid: res.problemid,
                        timetaken: res.timetaken,
                        iscorrect: isCorrect
                    }
                });

                // Link selected options
                const selectedOptionRecords = await tx.problemoptions.findMany({
                    where: {
                        problemid: res.problemid,
                        optiontext: { in: res.selectedoption }
                    }
                });

                for (const opt of selectedOptionRecords) {
                    await tx.userattempt_selectedoptions.create({
                        data: {
                            userattemptid: userAttempt.attemptid,
                            optionid: opt.optionid
                        }
                    });
                }

                // SYNC: Update user_tag_performance
                for (const pt of res.problemtags) {
                    const tagScopeId = pt.tags?.tagScopeId;
                    if (tagScopeId) {
                        await (tx as any).user_tag_performance.upsert({
                            where: {
                                userid_tagScopeId_is_mock: {
                                    userid: userId,
                                    tagScopeId: tagScopeId,
                                    is_mock: true
                                }
                            },
                            update: {
                                total_attempts: { increment: 1 },
                                total_correct: { increment: isCorrect ? 1 : 0 },
                                total_time_seconds: { increment: timeInSeconds }
                            },
                            create: {
                                userid: userId,
                                tagScopeId: tagScopeId,
                                is_mock: true,
                                total_attempts: 1,
                                total_correct: isCorrect ? 1 : 0,
                                total_time_seconds: timeInSeconds
                            }
                        });
                    }
                }

                // SYNC: Update user_difficulty_stats
                if (res.difficulty) {
                    await (tx as any).user_difficulty_stats.upsert({
                        where: {
                            userid_difficulty_is_mock: {
                                userid: userId,
                                difficulty: res.difficulty,
                                is_mock: true
                            }
                        },
                        update: {
                            total_attempts: { increment: 1 },
                            total_correct: { increment: isCorrect ? 1 : 0 },
                            total_time: { increment: timeInSeconds },
                            last_updated: new Date()
                        },
                        create: {
                            userid: userId,
                            difficulty: res.difficulty,
                            is_mock: true,
                            total_attempts: 1,
                            total_correct: isCorrect ? 1 : 0,
                            total_time: timeInSeconds,
                            last_updated: new Date()
                        }
                    });
                }
            }

            // 6. Update user_overall_performance (including time analysis)
            await (tx as any).user_overall_performance.upsert({
                where: {
                    userid_is_mock: {
                        userid: userId,
                        is_mock: true
                    }
                },
                update: {
                    total_attempts: { increment: results.length },
                    total_correct: { increment: totalScore },
                    total_incorrect: { increment: results.length - totalScore },
                    last_updated: new Date()
                },
                create: {
                    userid: userId,
                    is_mock: true,
                    total_attempts: results.length,
                    total_correct: totalScore,
                    total_incorrect: results.length - totalScore,
                    last_updated: new Date()
                }
            });

            // 7. Update community aggregates for O(1) fetch
            const allAttemptsForMock = await tx.usermocktestattempts.findMany({
                where: { mocktestid: mockId, endtime: { not: null } },
                select: { totalscore: true }
            });
            // eslint-disable-next-line
            const communityScores = allAttemptsForMock.map((a: any) => Number(a.totalscore || 0)).sort((a: any, b: any) => a - b);

            if (communityScores.length > 0) {
                const getQuartile = (arr: number[], q: number) => {
                    const pos = (arr.length - 1) * q;
                    const base = Math.floor(pos);
                    const rest = pos - base;
                    return arr[base + 1] !== undefined ? arr[base] + rest * (arr[base + 1] - arr[base]) : arr[base];
                };

                await (tx as any).mock_community_aggregates.upsert({
                    where: { mocktestid: mockId },
                    update: {
                        min_score: communityScores[0],
                        max_score: communityScores[communityScores.length - 1],
                        // eslint-disable-next-line
                        avg_score: communityScores.reduce((a: any, b: any) => a + b, 0) / communityScores.length,
                        q1: getQuartile(communityScores, 0.25),
                        median: getQuartile(communityScores, 0.5),
                        q3: getQuartile(communityScores, 0.75),
                        participants_count: communityScores.length,
                        last_updated: new Date()
                    },
                    create: {
                        mocktestid: mockId,
                        min_score: communityScores[0],
                        max_score: communityScores[communityScores.length - 1],
                        // eslint-disable-next-line
                        avg_score: communityScores.reduce((a: any, b: any) => a + b, 0) / communityScores.length,
                        q1: getQuartile(communityScores, 0.25),
                        median: getQuartile(communityScores, 0.5),
                        q3: getQuartile(communityScores, 0.75),
                        participants_count: communityScores.length,
                        last_updated: new Date()
                    }
                });

                // 8. Update user-specific ranking and percentile for this mock (O(1) fetch later)
                const userRank = communityScores.length - communityScores.lastIndexOf(Number(totalScore));
                const userPercentile = communityScores.length > 1
                    ? Math.round(((communityScores.length - userRank) / (communityScores.length - 1)) * 100)
                    : 100;

                await (tx as any).mocktestrankings.create({
                    data: {
                        userid: userId,
                        mocktestid: mockId,
                        rank: userRank,
                        totalscore: totalScore,
                        percentile: userPercentile,
                        rankingdate: new Date()
                    }
                });

                // Update score distribution
                const roundedScore = Math.round(totalScore);
                await (tx as any).mock_score_distribution_stats.upsert({
                    where: { mocktestid_score: { mocktestid: mockId, score: roundedScore } },
                    update: { frequency: { increment: 1 } },
                    create: { mocktestid: mockId, score: roundedScore, frequency: 1 }
                });
            }

            // Create individual section scores
            for (const [msId, score] of sectionScores) {
                await tx.mocktestsectionscores.create({
                    data: {
                        attemptid: attempt.attemptid,
                        sectionid: msId,
                        score: score
                    }
                });
            }
        });


        return NextResponse.json({
            results,
            totalScore,
            isFirstAttempt,
            mockId
        });

    } catch (error) {
        console.error("Error submitting mock exam:", error);
        return NextResponse.json({ error: "Internal Server Error" }, { status: 500 });
    }
}

function formatTimeTaken(ms: number): string {
    const totalSeconds = Math.floor(ms / 1000);
    const minutes = Math.floor(totalSeconds / 60);
    const seconds = totalSeconds % 60;

    if (minutes > 0) {
        return `${minutes} min ${seconds} sec`;
    }
    return `${seconds} sec`;
}
