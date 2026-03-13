"use client";

import { useEffect, useState } from "react";
import { AccountSettingsModal } from "@/shared/components/interactive/AccountSettingsModal";
import { useTutorialStore } from "@/shared/stores/tutorial-store";

export function FirstLoginHandler() {
    const { isFirstLogin, setFirstLogin, startTour, globalTourCompleted } = useTutorialStore();
    const [showSettings, setShowSettings] = useState(false);
    const [userId, setUserId] = useState<number>(0);
    const [currentUser, setCurrentUser] = useState<any>(null);

    useEffect(() => {
        // Fetch current user details to pass to modal
        // We only trigger if isFirstLogin is true
        if (!isFirstLogin) return;

        const fetchUser = async () => {
            try {
                const res = await fetch("/api/auth/me");
                if (res.ok) {
                    const data = await res.json();
                    setUserId(data.userid);
                    setCurrentUser({
                        username: data.username,
                        email: data.email,
                        image_url: data.image_url
                    });
                    setShowSettings(true);
                }
            } catch (error) {
                console.error("Failed to fetch user for onboarding", error);
            }
        };

        fetchUser();
    }, [isFirstLogin]);

    const handleSettingsClose = () => {
        setShowSettings(false);
        setFirstLogin(false);

        // Start the welcome tour after settings modal closes
        if (!globalTourCompleted) {
            // Small delay to let the modal close animation finish
            setTimeout(() => {
                startTour("welcome");
            }, 500);
        }
    };

    if (!showSettings || !currentUser) return null;

    return (
        <AccountSettingsModal
            userId={userId}
            currentUser={currentUser}
            isOpen={showSettings}
            onClose={handleSettingsClose}
            onUpdate={() => {
                // Refresh user data if needed, or just continue
            }}
            isFirstLogin={true}
        />
    );
}
