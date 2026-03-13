"use client";

import React from "react";
import { useQuery } from "@tanstack/react-query";
import { useRouter } from "next/navigation";
import { usePaginationStore } from "@/shared/stores/problems/pagination";
import { useAttemptsStore } from "@/shared/stores/problems/attempts";
import { Card, CardContent, CardFooter, CardHeader, CardTitle } from "@/shared/components/ui/card";
import { Button } from "@/shared/components/ui/button";
import { Badge } from "@/shared/components/feedback/badge";
import { Skeleton } from "@/shared/components/ui/skeleton";
import { BarChart3, Trophy, Users, AlertCircle } from "lucide-react";
import { useTutorialStore } from "@/shared/stores/tutorial-store";

interface MockTestStats {
   attempts: number;
   highestScore: number;
   averageScore: number;
}

interface MockTest {
   id: number;
   title: string;
   date: string;
   difficulty: number; // 0-10 probably, assuming 1=Easy, 2=Med, 3=Hard for now
   questionCount: number;
   stats: MockTestStats;
   hasContent: boolean;
}

export const fetchMockTests = async (examName: string, userId: number) => {
   const params = new URLSearchParams({
      examName,
      userid: userId.toString()
   });

   const response = await fetch(`/api/mock?${params.toString()}`);
   if (!response.ok) {
      throw new Error("Failed to fetch mock tests");
   }
   return response.json();
};

export default function MockPage() {
   const { examName } = usePaginationStore();
   const { userId } = useAttemptsStore();

   const { data, isLoading, error } = useQuery({
      queryKey: ["mockTests", examName, userId],
      queryFn: () => fetchMockTests(examName, userId),
      staleTime: 0, // Always refetch
   });

   const { pageTours, startTour, isTourRunning } = useTutorialStore();

   React.useEffect(() => {
      if (!pageTours.mock && !isTourRunning && !isLoading && data?.mocks?.length > 0) {
         const timer = setTimeout(() => startTour("mock"), 1000);
         return () => clearTimeout(timer);
      }
   }, [pageTours.mock, isTourRunning, isLoading, data, startTour]);

   const router = useRouter();
   const mockTests: MockTest[] = data?.mocks || [];

   // Helper for difficulty badge
   const getDifficultyBadge = (level: number) => {
      if (level <= 3) return <Badge variant="secondary" className="bg-green-100 text-green-800 hover:bg-green-200">Easy</Badge>;
      if (level <= 7) return <Badge variant="secondary" className="bg-yellow-100 text-yellow-800 hover:bg-yellow-200">Medium</Badge>;
      return <Badge variant="secondary" className="bg-red-100 text-red-800 hover:bg-red-200">Hard</Badge>;
   };

   if (isLoading) {
      return (
         <div className="p-8 w-full">
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
               {[1, 2, 3].map((i) => (
                  <Skeleton key={i} className="h-[250px] w-full rounded-xl" />
               ))}
            </div>
         </div>
      );
   }

   if (error) {
      return (
         <div className="p-8 w-full flex justify-center items-center h-[50vh]">
            <div className="text-center space-y-3 text-red-500">
               <AlertCircle className="w-12 h-12 mx-auto" />
               <p>Failed to load mock tests. Please try again later.</p>
            </div>
         </div>
      );
   }

   if (mockTests.length === 0) {
      return (
         <div className="p-8 w-full flex flex-col justify-center items-center h-[60vh] text-center space-y-6">
            <div className="bg-muted/30 p-8 rounded-full">
               <Trophy className="w-16 h-16 text-muted-foreground/40" />
            </div>
            <div className="space-y-2">
               <h2 className="text-2xl font-bold tracking-tight text-foreground">Don&apos;t have mock papers right now</h2>
               <p className="text-muted-foreground max-w-sm mx-auto">
                  There are currently no active mock tests available for {examName}. Please check back later or explore practice problems.
               </p>
            </div>
            <Button variant="outline" onClick={() => window.location.href = '/dashboard/problems'}>
               Go to Practice
            </Button>
         </div>
      );
   }

   return (
      <div className="p-8 w-full space-y-8">
         <div className="flex flex-col gap-2" data-tour="mock-hero">
            <h1 className="text-3xl font-bold tracking-tight text-foreground">{examName} Mock Exams</h1>
            <p className="text-muted-foreground">Test your readiness with full-length curated mock papers.</p>
         </div>

         <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {mockTests.map((mock, ind) => (
               <Card
                  key={mock.id}
                  onClick={() => {
                     if (mock.questionCount === 0) return;
                     router.push(`/dashboard/mock/${mock.id}/attempt`);
                  }}
                  className="group transition-all duration-300 border-border/60 relative overflow-hidden cursor-pointer hover:shadow-xl hover:scale-[1.02] hover:border-primary/50"
                  data-tour={ind === 0 ? "mock-card-first" : undefined}
               >
                  <div className="absolute top-0 right-0 p-4 opacity-50 group-hover:opacity-100 transition-opacity">
                     {/* Optional decorative background Icon */}
                     <Trophy className="w-24 h-24 text-primary/5 absolute -top-4 -right-4 rotate-12" />
                  </div>

                  <CardHeader className="pb-3 z-10 relative">
                     <div className="flex justify-between items-start mb-2">
                        {getDifficultyBadge(mock.difficulty)}
                        <Badge variant="outline" className="text-xs font-mono">{mock.questionCount} Qs</Badge>
                     </div>
                     <CardTitle className="text-xl font-bold text-foreground">
                        {mock.title}
                     </CardTitle>
                  </CardHeader>

                  <CardContent className="pb-4 z-10 relative">
                     <div className="grid grid-cols-3 gap-2 py-4">
                        <div className="flex flex-col items-center justify-center p-2 rounded-lg bg-muted/20 border border-border/40">
                           <Users className="w-4 h-4 text-blue-500 mb-1" />
                           <span className="text-xs text-muted-foreground font-medium uppercase tracking-wide">Attempts</span>
                           <span className="text-sm font-bold">{mock.stats.attempts}</span>
                        </div>
                        <div className="flex flex-col items-center justify-center p-2 rounded-lg bg-muted/20 border border-border/40">
                           <Trophy className="w-4 h-4 text-yellow-500 mb-1" />
                           <span className="text-xs text-muted-foreground font-medium uppercase tracking-wide">Best</span>
                           <span className="text-sm font-bold">{mock.stats.highestScore}</span>
                        </div>
                        <div className="flex flex-col items-center justify-center p-2 rounded-lg bg-muted/20 border border-border/40">
                           <BarChart3 className="w-4 h-4 text-green-500 mb-1" />
                           <span className="text-xs text-muted-foreground font-medium uppercase tracking-wide">Avg</span>
                           <span className="text-sm font-bold">{mock.stats.averageScore}</span>
                        </div>
                     </div>
                  </CardContent>
               </Card>
            ))}
         </div>
      </div>
   );
}
