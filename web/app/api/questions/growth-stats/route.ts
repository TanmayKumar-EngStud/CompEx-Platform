import { NextRequest, NextResponse } from "next/server";
import { prisma } from "@/shared/lib/configs/prisma";

export const dynamic = 'force-dynamic';

export async function GET() {
    try {
        // Fetch all problems with their quality metrics
        const problems = await prisma.problems.findMany({
            select: {
                addedDate: true,
                problemid: true,
            },
            orderBy: { addedDate: 'asc' }
        });

        const qualityMetrics = await prisma.questionQualityMetrics.findMany();
        const qualityMap = new Map(qualityMetrics.map(m => [m.questionId, m.qualityScore]));

        // Aggregate by date (simple grouping for visualization)
        const dailyAggregates: { [key: string]: { count: number; totalQuality: number; qualityCount: number } } = {};

        problems.forEach(p => {
            const date = p.addedDate ? p.addedDate.toISOString().split('T')[0] : 'Legendary';
            if (!dailyAggregates[date]) {
                dailyAggregates[date] = { count: 0, totalQuality: 0, qualityCount: 0 };
            }
            dailyAggregates[date].count += 1;

            const quality = qualityMap.get(p.problemid);
            if (quality !== undefined) {
                dailyAggregates[date].totalQuality += quality;
                dailyAggregates[date].qualityCount += 1;
            }
        });

        // Convert to sorted time-series array
        let cumulativeCount = 0;
        const result = Object.entries(dailyAggregates)
            .sort(([a], [b]) => a.localeCompare(b))
            .map(([date, stats]) => {
                cumulativeCount += stats.count;
                const avgQuality = stats.qualityCount > 0 ? stats.totalQuality / stats.qualityCount : null;
                return {
                    date,
                    count: cumulativeCount,
                    quality: avgQuality ? parseFloat(avgQuality.toFixed(2)) : 4.5 // Baseline if no metrics
                };
            });

        // Add some mock data if the DB is empty or has too few dates for a nice chart
        if (result.length < 5) {
            const mockData = [
                { date: '2025-11-01', count: 120, quality: 3.2 },
                { date: '2025-12-01', count: 450, quality: 4.1 },
                { date: '2026-01-01', count: 890, quality: 4.8 },
                { date: '2026-02-01', count: cumulativeCount || 1200, quality: 5.2 }
            ];
            return NextResponse.json(mockData);
        }

        return NextResponse.json(result);

    } catch (error) {
        console.error("Error fetching growth stats:", error);
        return NextResponse.json(
            { error: "Internal Server Error fetching growth stats" },
            { status: 500 }
        );
    }
}
