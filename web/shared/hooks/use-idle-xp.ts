"use client";

import { useEffect } from "react";
import { useAttemptsStore } from "@/shared/stores/problems/attempts";

export const useIdleXP = () => {
    const { userId } = useAttemptsStore();

    useEffect(() => {
        if (!userId || userId === 0) return;

        // Grant initial awareness reward
        const grantReward = async () => {
            try {
                await fetch(`/api/rewards/idle?userId=${userId}`);
                console.log("🧘 Awareness XP authenticated.");
            } catch (error) {
                console.error("Failed to authenticate presence", error);
            }
        };

        // Every 5 minutes of presence
        const interval = setInterval(grantReward, 5 * 60 * 1000);
        grantReward();

        return () => clearInterval(interval);
    }, [userId]);
};
