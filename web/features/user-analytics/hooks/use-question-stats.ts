import { useState, useEffect } from "react";
import { QuestionStats } from "../types/stats";

/**
 * Hook for lazy fetching question statistics
 * 
 * @param problemId - The ID of the question to fetch stats for
 * @returns Object containing stats, loading state, and error
 */
export function useQuestionStats(problemId: number | undefined) {
    const [stats, setStats] = useState<QuestionStats | null>(null);
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        if (!problemId) {
            setStats(null);
            return;
        }

        const fetchStats = async () => {
            setIsLoading(true);
            setError(null);
            try {
                const response = await fetch(`/api/problems/${problemId}/stats`);
                if (!response.ok) {
                    throw new Error("Failed to fetch statistics");
                }
                const data = await response.json();
                setStats(data);
            } catch (err) {
                console.error("Error fetching question stats:", err);
                setError(err instanceof Error ? err.message : "An unknown error occurred");
            } finally {
                setIsLoading(false);
            }
        };

        fetchStats();
    }, [problemId]);

    return { stats, isLoading, error };
}
