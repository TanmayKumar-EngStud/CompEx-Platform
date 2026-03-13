
import { NextRequest, NextResponse } from "next/server";
import { prisma } from "@/shared/lib/configs/prisma";
import { getUserIdFromRequest } from "@/shared/lib/utils/auth";

export async function GET(
    request: NextRequest,
    { params }: { params: Promise<{ id: string }> }
) {
    const { id } = await params;
    const mockId = parseInt(id);

    // Get secure userId from session cookie
    const userId = await getUserIdFromRequest(request);

    if (isNaN(mockId)) {
        return NextResponse.json({ error: "Invalid mock ID" }, { status: 400 });
    }

    try {
        const mockTest = await prisma.mocktests.findUnique({
            where: { mocktestid: mockId },
            include: {
                examtypes: true,
                mocksections: {
                    orderBy: { sectionnumber: "asc" },
                    include: {
                        sections: true,
                        problems: {
                            orderBy: { mockquestionnumber: "asc" },
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
                            orderBy: { mockquestionnumber: "asc" },
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

        // Check for existing official attempt
        let isFirstAttempt = true;
        if (userId) {
            const existingOfficialAttempt = await prisma.usermocktestattempts.findFirst({
                where: {
                    userid: userId,
                    mocktestid: mockId,
                    isofficialattempt: true
                }
            });
            isFirstAttempt = !existingOfficialAttempt;

            // 🛡️ ANTI-CHEAT: Register start time for official attempt immediately
            if (isFirstAttempt) {
                // Check if we already created an "In Progress" record in this session (e.g. on refresh)
                const inProgress = await prisma.usermocktestattempts.findFirst({
                    where: {
                        userid: userId,
                        mocktestid: mockId,
                        isofficialattempt: true,
                        endtime: null
                    }
                });

                if (!inProgress) {
                    await prisma.usermocktestattempts.create({
                        data: {
                            userid: userId,
                            mocktestid: mockId,
                            starttime: new Date(),
                            isofficialattempt: true,
                            totalscore: 0
                        }
                    });
                }
            }
        }

        // Process sections to flatten or structure as needed for the session
        // eslint-disable-next-line
        const processedSections = mockTest.mocksections.map((ms: any) => {
            interface RenderableItem {
                order: number;
                data: any;
            }

            const items: RenderableItem[] = [];

            // Add single problems (only those not part of a set)
            // eslint-disable-next-line
            ms.problems.filter((p: any) => !p.problemsSetId).forEach((p: any) => {
                items.push({
                    order: p.mockquestionnumber ?? 999,
                    data: {
                        ...p,
                        renderType: "single"
                    }
                });
            });

            // Add items from ProblemsSet
            // eslint-disable-next-line
            ms.ProblemsSet.forEach((ps: any) => {
                const parentContent = ps.content;
                const setType = ps.type;
                const setOrder = ps.mockquestionnumber ?? 999;

                // eslint-disable-next-line
                ps.problems.forEach((p: any, idx: number) => {
                    // For set items, we merge parent content into metadata
                    // so QuestionDisplay / ParentChildTemplate can find it.
                    const mergedMetadata = {
                        ...(p.metadata as any || {}),
                        problemsSetId: ps.problemsSetId,
                        content: parentContent,
                        setType: setType
                    };

                    items.push({
                        // If multiple questions in a set, we use set order + small increment
                        // to keep them together and in order.
                        order: setOrder + (idx * 0.01),
                        data: {
                            ...p,
                            metadata: mergedMetadata,
                            renderType: "set-item"
                        }
                    });
                });
            });

            // Sort by order
            items.sort((a, b) => a.order - b.order);

            return {
                mockSectionId: ms.mocksectionid,
                sectionName: ms.sections.name,
                sectionId: ms.sectionid,
                sectionNumber: ms.sectionnumber,
                items: items.map(i => i.data)
            };
        });

        return NextResponse.json({
            mockId: mockTest.mocktestid,
            examName: mockTest.examtypes?.name,
            examtypeid: mockTest.examtypeid,
            isFirstAttempt,
            sections: processedSections
        });

    } catch (error) {
        console.error("Error fetching mock session content:", error);
        return NextResponse.json({ error: "Internal Server Error" }, { status: 500 });
    }
}
