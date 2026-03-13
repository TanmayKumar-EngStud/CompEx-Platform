import { prisma } from "@/shared/lib/configs/prisma";

/**
 * Service for calculating question stats from user attempts
 */

import { QuestionStats } from "../types/stats";

/**
 * Converts "X min Y sec" or "X sec" to total seconds
 */
function parseTimeToSeconds(timeStr: string | null): number {
    if (!timeStr) return 0;
    let seconds = 0;
    if (timeStr.includes("min")) {
        const parts = timeStr.split(" ");
        const minIndex = parts.findIndex((p) => p === "min");
        const secIndex = parts.findIndex((p) => p === "sec");
        if (minIndex > 0) seconds += parseInt(parts[minIndex - 1]) * 60;
        if (secIndex > 0 && secIndex !== minIndex + 1) {
            seconds += parseInt(parts[secIndex - 1]);
        }
    } else if (timeStr.includes("sec")) {
        const match = timeStr.match(/(\d+)\s*sec/);
        if (match) seconds = parseInt(match[1]);
    }
    return seconds;
}

/**
 * Converts total seconds back to "X min Y sec" or "X sec"
 */
function formatSecondsToTime(totalSeconds: number): string {
    if (totalSeconds >= 60) {
        const mins = Math.floor(totalSeconds / 60);
        const secs = Math.round(totalSeconds % 60);
        return secs > 0 ? `${mins} min ${secs} sec` : `${mins} min`;
    }
    return `${Math.round(totalSeconds)} sec`;
}

/**
 * Fetches statistics for a specific question based on user attempts
 * 
 * @param problemId - The ID of the question
 * @returns Promise resolving to QuestionStats or null if no correct attempts
 */
export async function getQuestionStats(problemId: number): Promise<QuestionStats | null> {
    const correctAttempts = await prisma.userattempts.findMany({
        where: {
            problemid: problemId,
            iscorrect: true,
        },
        select: {
            timetaken: true,
        },
    });

    if (correctAttempts.length === 0) {
        return null;
    }

    const timesInSeconds = correctAttempts
        // eslint-disable-next-line
        .map((a: any) => parseTimeToSeconds(a.timetaken))
        // eslint-disable-next-line
        .filter((t: any) => t > 0);

    if (timesInSeconds.length === 0) {
        return null;
    }

    // eslint-disable-next-line
    const totalSeconds = timesInSeconds.reduce((sum: any, t: any) => sum + t, 0);
    const averageSeconds = totalSeconds / timesInSeconds.length;
    const bestSeconds = Math.min(...timesInSeconds);

    return {
        averageTime: formatSecondsToTime(averageSeconds),
        bestTime: formatSecondsToTime(bestSeconds),
        totalSolves: correctAttempts.length,
    };
}
