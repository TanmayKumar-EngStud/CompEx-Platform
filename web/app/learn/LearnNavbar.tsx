"use client";

import Navbar from "@/shared/components/layouts/navbar";
import { StreakProvider } from "@/shared/contexts/StreakContext";

export default function LearnNavbar() {
    return (
        <StreakProvider>
            <Navbar />
        </StreakProvider>
    );
}
