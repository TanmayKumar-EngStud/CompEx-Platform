"use client";
import React, { useEffect } from "react";
import Navbar from "@/shared/components/layouts/navbar";
import { StreakProvider } from "@/shared/contexts/StreakContext";
import { usePathname } from "next/navigation";
import { useIdleXP } from "@/shared/hooks/use-idle-xp";

function DashboardContent({ children }: { children: React.ReactNode }) {
   const pathname = usePathname();
   const isAttemptPage = pathname.includes("/attempt") || pathname.includes("/session");

   // Reward pure presence
   useIdleXP();

   return (
      <div className="h-screen w-full overflow-auto bg-background">
         <div className="min-h-full flex flex-col w-full">
            {!isAttemptPage && (
               <Navbar />
            )}
            <main className={isAttemptPage ? "h-screen w-screen overflow-hidden fixed inset-0 z-50 bg-background" : "flex-1 w-full"}>
               {children}
            </main>
            {!isAttemptPage && (
               <footer className="w-full py-4 text-center text-xs text-muted-foreground/50 border-t border-border/30 bg-background/50 backdrop-blur-sm mt-auto">
                  © 2026 Compex. All Rights Reserved. Created by Tanmay Kumar
               </footer>
            )}
         </div>
      </div>
   );
}

import { TutorialProvider } from "@/shared/components/tutorial/TutorialProvider";
import { FirstLoginHandler } from "@/shared/components/tutorial/FirstLoginHandler";

export default function Layout({ children }: { children: React.ReactNode }) {
   return (
      <TutorialProvider>
         <FirstLoginHandler />
         <DashboardContent>{children}</DashboardContent>
      </TutorialProvider>
   );
}

