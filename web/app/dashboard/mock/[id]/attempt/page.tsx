"use client";

import React from "react";
import { useParams, useRouter } from "next/navigation";
import { useAttemptsStore } from "@/shared/stores/problems/attempts";
import { usePaginationStore } from "@/shared/stores/problems/pagination";
import { Button } from "@/shared/components/ui/button";
import { Card, CardContent, CardFooter, CardHeader, CardTitle } from "@/shared/components/ui/card";
import {
    Clock,
    AlertCircle,
    CheckCircle2,
    Info,
    ArrowRight,
    ShieldAlert,
    Timer
} from "lucide-react";
import { Badge } from "@/shared/components/feedback/badge";

export default function MockAttemptInstructionPage() {
    const params = useParams();
    const router = useRouter();
    const { examName } = usePaginationStore();
    const mockId = params.id;

    // Exam specific information
    const getExamDuration = () => {
        if (examName?.toUpperCase() === "GRE") {
            return "1 hour 28 minutes";
        }
        if (examName?.toUpperCase() === "GMAT") {
            return "2 hours 15 minutes";
        }
        return "2 hours";
    };

    const getExamFormat = () => {
        if (examName?.toUpperCase() === "GRE") {
            return "Verbal Reasoning and Quantitative Reasoning (Writing Assessment excluded).";
        }
        if (examName?.toUpperCase() === "GMAT") {
            return "Quantitative Reasoning, Verbal Reasoning, and Data Insights sections.";
        }
        return "Standardized testing format.";
    };

    const handleBeginExam = () => {
        // Always clear any stale session state so the exam starts fresh from section 1.
        // Without this, a previous incomplete/timed-out session's localStorage would
        // cause the exam to resume mid-way (e.g. Section 4) instead of section 1.
        localStorage.removeItem(`mock_${mockId}_expiry`);
        localStorage.removeItem(`mock_${mockId}_section`);
        router.push(`/dashboard/mock/${mockId}/attempt/session`);
    };

    return (
        <div className="h-screen w-screen bg-background overflow-hidden flex flex-col font-sans">
            <div className="flex-grow flex flex-col p-8 md:p-12 space-y-10 overflow-auto max-w-6xl mx-auto w-full">

                {/* Minimalist Header */}
                <div className="flex flex-col md:flex-row justify-between items-start md:items-end gap-4 border-b pb-8 shrink-0">
                    <div className="space-y-2">
                        <p className="text-xs font-medium text-muted-foreground uppercase tracking-widest">Mock Examination #{mockId}</p>
                        <h1 className="text-3xl font-bold tracking-tight text-foreground">
                            {examName} Instructions
                        </h1>
                    </div>
                    <div className="flex items-center gap-6 text-sm font-medium">
                        <div className="flex flex-col items-end">
                            <span className="text-[10px] text-muted-foreground uppercase font-bold tracking-wider">Total Duration</span>
                            <span className="text-base">{getExamDuration()}</span>
                        </div>
                    </div>
                </div>

                {/* Main Content Grid */}
                <div className="grid grid-cols-1 md:grid-cols-3 gap-12">

                    {/* Left & Middle Columns: Structure & Preparation */}
                    <div className="md:col-span-2 space-y-10">

                        {/* Section Detail Section */}
                        <section className="space-y-4">
                            <h2 className="text-lg font-semibold flex items-center gap-2">
                                <Timer className="w-5 h-5 text-primary" />
                                Exam Structure
                            </h2>
                            <div className="rounded-xl border bg-card overflow-hidden">
                                <table className="w-full text-sm">
                                    <thead className="bg-muted/50">
                                        <tr>
                                            <th className="px-4 py-3 text-left font-medium text-muted-foreground">Section Type</th>
                                            <th className="px-4 py-3 text-left font-medium text-muted-foreground">Count</th>
                                            <th className="px-4 py-3 text-right font-medium text-muted-foreground">Time Per Section</th>
                                        </tr>
                                    </thead>
                                    <tbody className="divide-y">
                                        {examName?.toUpperCase() === "GRE" ? (
                                            <>
                                                <tr>
                                                    <td className="px-4 py-3 font-medium">Quantitative Reasoning</td>
                                                    <td className="px-4 py-3">2 Sections</td>
                                                    <td className="px-4 py-3 text-right text-muted-foreground">21m - 26m</td>
                                                </tr>
                                                <tr>
                                                    <td className="px-4 py-3 font-medium">Verbal Reasoning</td>
                                                    <td className="px-4 py-3">2 Sections</td>
                                                    <td className="px-4 py-3 text-right text-muted-foreground">18m - 23m</td>
                                                </tr>
                                            </>
                                        ) : (
                                            <>
                                                <tr>
                                                    <td className="px-4 py-3 font-medium">Quantitative / Verbal / Data</td>
                                                    <td className="px-4 py-3">3 Sections</td>
                                                    <td className="px-4 py-3 text-right text-muted-foreground">45 minutes</td>
                                                </tr>
                                            </>
                                        )}
                                    </tbody>
                                </table>
                            </div>
                            <p className="text-xs text-muted-foreground italic">
                                Note: Each section has a hard deadline. Unsaved progress will be lost if the timer expires.
                            </p>
                        </section>

                        {/* Physical Requirements Section */}
                        <section className="space-y-4">
                            <h2 className="text-lg font-semibold flex items-center gap-2">
                                <ShieldAlert className="w-5 h-5 text-primary" />
                                Preparation Requirements
                            </h2>
                            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                                <div className="p-4 rounded-xl border bg-muted/20 flex gap-4">
                                    <span className="text-xl">🧮</span>
                                    <div>
                                        <p className="text-sm font-bold">Physical Calculator</p>
                                        <p className="text-xs text-muted-foreground">We recommend having a physical calculator ready for quick computations.</p>
                                    </div>
                                </div>
                                <div className="p-4 rounded-xl border bg-muted/20 flex gap-4">
                                    <span className="text-xl">📝</span>
                                    <div>
                                        <p className="text-sm font-bold">Rough Work Sheets</p>
                                        <p className="text-xs text-muted-foreground">Keep blank paper and a pen handy for diagrams and scratch work.</p>
                                    </div>
                                </div>
                            </div>
                        </section>

                        {/* Standard Procedures */}
                        <section className="space-y-4">
                            <h2 className="text-lg font-semibold">General Procedures</h2>
                            <ul className="grid grid-cols-1 sm:grid-cols-2 gap-x-8 gap-y-3">
                                {[
                                    "Stable internet connection required.",
                                    "Browser tabs must not be switched.",
                                    "No pauses allowed once started.",
                                    "Ensure power supply for the duration."
                                ].map((step, i) => (
                                    <li key={i} className="flex gap-3 text-sm text-foreground/80">
                                        <CheckCircle2 className="w-4 h-4 text-green-500 shrink-0 mt-0.5" />
                                        {step}
                                    </li>
                                ))}
                            </ul>
                        </section>
                    </div>

                    {/* Right Column: Score Policy & Actions */}
                    <div className="space-y-8 flex flex-col justify-between">
                        <section className="p-6 rounded-2xl border bg-destructive/5 border-destructive/20 dark:bg-destructive/30 space-y-4">
                            <h3 className="text-sm font-bold text-destructive flex items-center gap-2 uppercase tracking-tighter">
                                <AlertCircle className="w-4 h-4" />
                                Attempt & Scoring Policy
                            </h3>
                            <div className="space-y-3 text-sm leading-relaxed text-foreground/80">
                                <p>
                                    Practice attempts are unlimited. However, <strong className="text-foreground font-bold">only the first attempt</strong> is recorded in your performance history.
                                </p>
                                <p className="text-xs font-medium italic text-muted-foreground/80">
                                    A partial or empty start is still considered an attempt.
                                </p>
                            </div>
                        </section>

                        <div className="space-y-4">
                            <Button
                                size="lg"
                                className="w-full py-6 text-base font-bold rounded-xl shadow-sm hover:translate-y-[-1px] transition-all"
                                onClick={handleBeginExam}
                            >
                                Start Mock Exam
                            </Button>

                            <Button
                                variant="outline"
                                className="w-full text-xs font-medium py-2 text-muted-foreground hover:text-foreground"
                                onClick={() => router.push("/dashboard/mock")}
                            >
                                ← Return to Dashboard
                            </Button>
                        </div>

                        <p className="text-[10px] text-muted-foreground/60 text-center">
                            Standardised Assessment Portal<br />
                            v2.1.0 • CompEx Platform
                        </p>
                    </div>
                </div>
            </div>
        </div>
    );
}
