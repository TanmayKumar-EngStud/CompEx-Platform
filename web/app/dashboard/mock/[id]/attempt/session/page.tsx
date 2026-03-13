"use client";

import React, { useState, useEffect } from "react";
import { useParams, useRouter } from "next/navigation";
import { Button } from "@/shared/components/ui/button";
import { Timer as TimerIcon, ArrowLeft, ArrowRight, CheckCircle2, AlertCircle } from "lucide-react";
import { motion } from "framer-motion";
import QuestionDisplay from "@/features/question-solving/components/QuestionWindow/QuestionDisplay/questionDisplay";
import Loading from "@/shared/components/feedback/loading";
import { useTimerStore } from "@/features/user-analytics/hooks/timerDefinition";
import { useResultData } from "@/features/user-analytics/hooks/resultWindowDefinitions";
import { useAttemptsStore } from "@/shared/stores/problems/attempts";
import { LazyResultWindow, preloadResultWindow } from "@/shared/components/feedback/lazy/LazyResultWindow";

interface MockSessionData {
    mockId: number;
    examName: string;
    sections: Array<{
        mockSectionId: number;
        sectionName: string;
        sectionId: number;
        sectionNumber: number;
        items: any[];
    }>;
    isFirstAttempt: boolean;
}

export default function MockSessionPage() {
    const params = useParams();
    const router = useRouter();
    const mockId = params.id;

    const [sessionData, setSessionData] = useState<MockSessionData | null>(null);
    const [loading, setLoading] = useState(true);
    const [currentSectionIndex, setCurrentSectionIndex] = useState(0);
    const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
    const [sectionTimeRemaining, setSectionTimeRemaining] = useState(0);
    const [answers, setAnswers] = useState<Map<number, string[]>>(new Map());
    const [showResults, setShowResults] = useState(false);
    const [submitting, setSubmitting] = useState(false);
    const [showConfirmModal, setShowConfirmModal] = useState(false);

    const { switchQuestion, recordOptionSelectedTime, getElapsedTime, clearAllTimers, currentQuestionId } = useTimerStore();
    const { setResultData } = useResultData();
    const { userId, addAttempt, resetAttempt } = useAttemptsStore();

    const formatTime = (seconds: number) => {
        const mins = Math.floor(seconds / 60);
        const secs = seconds % 60;
        return `${mins}:${secs.toString().padStart(2, "0")}`;
    };

    const handleSubmitExam = React.useCallback(async () => {
        if (!sessionData || submitting) return;
        setSubmitting(true);

        try {
            // Collect all times from timer store
            const timesTaken: Record<number, number> = {};
            const allProblemIds: number[] = sessionData.sections.flatMap(s => s.items.map(i => i.problemid));

            allProblemIds.forEach(id => {
                timesTaken[id] = getElapsedTime(id);
            });

            const res = await fetch(`/api/mock/${mockId}/submit`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    answers: Object.fromEntries(answers),
                    timesTaken
                })
            });

            const data = await res.json();
            if (data.error) throw new Error(data.error);

            // Clean up anti-cheat storage
            localStorage.removeItem(`mock_${mockId}_expiry`);
            localStorage.removeItem(`mock_${mockId}_section`);

            // Populate stores for ResultWindow
            setResultData(data.results);

            // Sync with AttemptsStore for persistence/consistency
            resetAttempt();
            data.results.forEach((r: any) => {
                addAttempt({
                    problemId: r.problemid,
                    option: r.selectedoption,
                    timetaken: r.timetaken,
                    partialcorrectnessscore: null
                });
            });

            setShowResults(true);
        } catch (err) {
            console.error("Error submitting exam:", err);
            alert("Failed to submit exam. Please try again.");
        } finally {
            setSubmitting(false);
        }
    }, [sessionData, submitting, mockId, answers, getElapsedTime, setResultData, resetAttempt, addAttempt]);

    const handleFinishSection = React.useCallback(async () => {
        if (!sessionData) return;

        if (currentSectionIndex < sessionData.sections.length - 1) {
            // Move to next section
            const nextSectionIndex = currentSectionIndex + 1;
            const nextSection = sessionData.sections[nextSectionIndex];
            const nextQuestionId = nextSection.items[0].problemid;

            switchQuestion(currentQuestionId, nextQuestionId);

            // Re-initialize timer for next section
            const duration = 20 * 60;
            const expiry = Date.now() + duration * 1000;
            localStorage.setItem(`mock_${mockId}_expiry`, expiry.toString());
            localStorage.setItem(`mock_${mockId}_section`, nextSectionIndex.toString());

            setCurrentSectionIndex(nextSectionIndex);
            setCurrentQuestionIndex(0);
            setSectionTimeRemaining(duration);
        } else {
            // End exam
            await handleSubmitExam();
        }
    }, [sessionData, currentSectionIndex, currentQuestionId, switchQuestion, handleSubmitExam, mockId]);

    const goToNextQuestion = React.useCallback(() => {
        if (!sessionData) return;
        const currentSection = sessionData.sections[currentSectionIndex];
        const currentQuestion = currentSection.items[currentQuestionIndex];
        if (currentQuestionIndex < currentSection.items.length - 1) {
            const nextId = currentSection.items[currentQuestionIndex + 1].problemid;
            switchQuestion(currentQuestion.problemid, nextId);
            setCurrentQuestionIndex(prev => prev + 1);
        } else {
            handleFinishSection();
        }
    }, [sessionData, currentSectionIndex, currentQuestionIndex, switchQuestion, handleFinishSection]);

    const goToPrevQuestion = React.useCallback(() => {
        if (!sessionData) return;
        const currentSection = sessionData.sections[currentSectionIndex];
        const currentQuestion = currentSection.items[currentQuestionIndex];
        if (currentQuestionIndex > 0) {
            const prevId = currentSection.items[currentQuestionIndex - 1].problemid;
            switchQuestion(currentQuestion.problemid, prevId);
            setCurrentQuestionIndex(prev => prev - 1);
        }
    }, [sessionData, currentSectionIndex, currentQuestionIndex, switchQuestion]);

    useEffect(() => {
        preloadResultWindow();
        const fetchSession = async () => {
            try {
                const res = await fetch(`/api/mock/${mockId}/session`);
                const data = await res.json();
                if (data.error) throw new Error(data.error);
                setSessionData(data);

                // --- TIMER PERSISTENCE CORE ---
                const savedExpiry = localStorage.getItem(`mock_${mockId}_expiry`);
                const savedSection = localStorage.getItem(`mock_${mockId}_section`);

                let initialSection = 0;
                let initialTime = 20 * 60;

                const now = Date.now();
                const expiry = savedExpiry ? parseInt(savedExpiry) : 0;
                const isActiveSession = savedExpiry && savedSection && expiry > now;

                if (isActiveSession) {
                    // Valid in-progress session — resume from saved section with remaining time
                    initialSection = parseInt(savedSection!);
                    initialTime = Math.floor((expiry - now) / 1000);
                } else {
                    // No saved state OR timer has expired → always start fresh from section 0.
                    // Clear any stale localStorage so a previous timed-out attempt doesn't
                    // bleed into the new session (this was causing the Verbal section to
                    // appear instead of the first Quants section).
                    localStorage.removeItem(`mock_${mockId}_expiry`);
                    localStorage.removeItem(`mock_${mockId}_section`);

                    const freshExpiry = now + initialTime * 1000;
                    localStorage.setItem(`mock_${mockId}_expiry`, freshExpiry.toString());
                    localStorage.setItem(`mock_${mockId}_section`, "0");
                }

                setCurrentSectionIndex(initialSection);
                setSectionTimeRemaining(initialTime);

                // Start timer for the appropriate question
                if (data.sections?.[initialSection]?.items?.[0]) {
                    switchQuestion(null, data.sections[initialSection].items[0].problemid);
                }
            } catch (err) {
                console.error("Failed to load mock session:", err);
            } finally {
                setLoading(false);
            }
        };
        fetchSession();

        // 🛡️ ANTI-CHEAT: Navigation Guard
        const handleBeforeUnload = (e: BeforeUnloadEvent) => {
            if (!showResults) {
                e.preventDefault();
                e.returnValue = "Are you sure you want to leave? Your exam progress might be lost.";
                return e.returnValue;
            }
        };
        window.addEventListener("beforeunload", handleBeforeUnload);

        return () => {
            clearAllTimers();
            window.removeEventListener("beforeunload", handleBeforeUnload);
        };
    }, [mockId, clearAllTimers, switchQuestion, showResults]);

    // Timer logic for the SECTION
    useEffect(() => {
        if (!sessionData || sectionTimeRemaining <= 0 || showResults) return;

        const interval = setInterval(() => {
            setSectionTimeRemaining(prev => {
                if (prev <= 1) {
                    clearInterval(interval);
                    handleFinishSection();
                    return 0;
                }
                return prev - 1;
            });
        }, 1000);

        return () => clearInterval(interval);
    }, [sessionData, sectionTimeRemaining, showResults, handleFinishSection]);

    // 🛡️ ANTI-CHEAT: Keyboard Blocking & Navigation
    useEffect(() => {
        const handleKeyDown = (e: KeyboardEvent) => {
            // Block Refresh Shortcuts
            if ((e.ctrlKey || e.metaKey) && e.key === "r") {
                e.preventDefault();
                return;
            }
            if (e.key === "F5") {
                e.preventDefault();
                return;
            }

            // Don't navigate if user is typing in an input or textarea
            const target = e.target as HTMLElement;
            if (target.tagName === "INPUT" || target.tagName === "TEXTAREA" || target.isContentEditable) {
                return;
            }

            if (e.key === "ArrowRight") {
                goToNextQuestion();
            } else if (e.key === "ArrowLeft") {
                goToPrevQuestion();
            }
        };

        window.addEventListener("keydown", handleKeyDown);
        return () => window.removeEventListener("keydown", handleKeyDown);
    }, [goToNextQuestion, goToPrevQuestion]);

    // 🛡️ ANTI-CHEAT: Back Button Trap
    useEffect(() => {
        if (showResults) return;

        // Push a state so there's always something to 'pop' before leaving the page
        window.history.pushState(null, "", window.location.href);

        const handlePopState = () => {
            // Immediately push again to stay on current page
            window.history.pushState(null, "", window.location.href);
            // Show confirmation instead of leaving
            setShowConfirmModal(true);
        };

        window.addEventListener("popstate", handlePopState);
        return () => window.removeEventListener("popstate", handlePopState);
    }, [showResults]);

    const currentSection = sessionData?.sections[currentSectionIndex];
    const currentQuestion = currentSection?.items[currentQuestionIndex];

    const { totalQuestions, currentProgressCount } = React.useMemo(() => {
        if (!sessionData) return { totalQuestions: 0, currentProgressCount: 0 };
        const total = sessionData.sections.reduce((acc, s) => acc + s.items.length, 0);
        const completedInPrev = sessionData.sections
            .slice(0, currentSectionIndex)
            .reduce((acc, s) => acc + s.items.length, 0);
        return {
            totalQuestions: total,
            currentProgressCount: completedInPrev + currentQuestionIndex + 1
        };
    }, [sessionData, currentSectionIndex, currentQuestionIndex]);

    const progressPercent = totalQuestions > 0 ? (currentProgressCount / totalQuestions) * 100 : 0;

    const transformedOptions = React.useMemo(() => {
        if (!currentQuestion) return null;
        return currentQuestion.problemoptions?.reduce((acc: any, option: any, index: number) => {
            acc[index.toString()] = {
                optiontext: option.optiontext,
                group: option.group,
            };
            return acc;
        }, {});
    }, [currentQuestion]);

    const handleOptionClick = React.useCallback((option: string | string[]) => {
        if (!currentQuestion) return;
        const newOption = Array.isArray(option) ? option : [option];
        setAnswers(prev => {
            const next = new Map(prev);
            next.set(currentQuestion.problemid, newOption);
            return next;
        });
        recordOptionSelectedTime(currentQuestion.problemid);
    }, [currentQuestion, recordOptionSelectedTime]);

    const isLongOptions = React.useMemo(() =>
        transformedOptions && Object.values(transformedOptions).some((opt: any) => opt.optiontext?.length > 50)
        , [transformedOptions]);

    const currentSelectedOption = React.useMemo(() =>
        (currentQuestion && answers.get(currentQuestion.problemid)) || [],
        [answers, currentQuestion]);

    if (showResults) {
        return (
            <div className="h-screen w-screen bg-background overflow-hidden flex flex-col">
                <LazyResultWindow
                    isFullPage={true}
                    closeButtonText="Back to Mock section"
                    onClose={() => router.push("/dashboard/mock")}
                />
            </div>
        );
    }

    if (loading) return <div className="h-screen w-screen flex items-center justify-center bg-background"><Loading message="Loading your mock exam..." /></div>;
    if (!sessionData) return <div className="h-screen w-screen flex items-center justify-center bg-background">Error loading mock data. Please go back and try again.</div>;

    if (!currentSection || !currentQuestion) return (
        <div className="h-screen w-screen flex flex-col items-center justify-center bg-background gap-4 text-center p-8">
            <AlertCircle className="w-16 h-16 text-muted-foreground/40" />
            <h2 className="text-2xl font-bold">No Questions Available</h2>
            <p className="text-muted-foreground max-w-md">
                This mock paper doesn&apos;t have any questions assigned yet.
                Please check back later or try a different mock paper.
            </p>
            <Button variant="outline" onClick={() => router.push('/dashboard/mock')}>
                Back to Mock Exams
            </Button>
        </div>
    );

    return (
        <div className="h-screen w-screen bg-background flex flex-col overflow-hidden font-sans">
            {submitting && (
                <div className="fixed inset-0 z-[100] bg-background/80 backdrop-blur-sm flex items-center justify-center">
                    <Loading message="Finalizing your score..." />
                </div>
            )}

            {/* Header */}
            <header className="h-16 border-b flex items-center justify-between px-8 bg-card shadow-sm z-10 shrink-0">
                <div className="flex items-center gap-6">
                    <div className="flex flex-col">
                        <span className="text-[10px] uppercase font-bold text-muted-foreground tracking-widest leading-none mb-1">Section {currentSectionIndex + 1} of {sessionData.sections.length}</span>
                        <h2 className="text-sm font-bold tracking-tight">{currentSection.sectionName}</h2>
                    </div>
                    <div className="h-8 w-px bg-border mx-2" />
                    <div className="flex flex-col">
                        <span className="text-[10px] uppercase font-bold text-muted-foreground tracking-widest leading-none mb-1">Question</span>
                        <h2 className="text-sm font-bold tracking-tight">{currentQuestionIndex + 1} of {currentSection.items.length}</h2>
                    </div>
                </div>

                <div className="flex items-center gap-6">
                    <div className={`flex items-center gap-2 px-4 py-2 rounded-lg border ${sectionTimeRemaining < 60 ? "bg-red-50 border-red-200 text-red-600 animate-pulse" : "bg-muted/50 border-border"}`}>
                        <TimerIcon className="w-4 h-4" />
                        <span className="text-lg font-mono font-bold leading-none">{formatTime(sectionTimeRemaining)}</span>
                    </div>

                    <Button
                        variant="outline"
                        size="sm"
                        className="text-xs font-bold gap-2 text-muted-foreground hover:text-foreground border-dashed"
                        onClick={() => setShowConfirmModal(true)}
                    >
                        End Early
                    </Button>
                </div>
            </header>

            {/* Global Progress Bar */}
            <div className="h-1 w-full bg-muted shrink-0 overflow-hidden">
                <motion.div
                    className="h-full bg-primary"
                    initial={{ width: 0 }}
                    animate={{ width: `${progressPercent}%` }}
                    transition={{ duration: 0.5, ease: "easeOut" }}
                />
            </div>

            {/* Confirmation Modal */}
            {showConfirmModal && (
                <div className="fixed inset-0 z-[110] bg-black/60 backdrop-blur-sm flex items-center justify-center p-4">
                    <div className="bg-card border border-border rounded-2xl shadow-2xl max-w-md w-full overflow-hidden animate-in fade-in zoom-in duration-200">
                        <div className="p-8">
                            <div className="w-12 h-12 bg-amber-100 dark:bg-amber-900/30 rounded-full flex items-center justify-center mb-6">
                                <TimerIcon className="w-6 h-6 text-amber-600 dark:text-amber-400" />
                            </div>
                            <h3 className="text-xl font-bold mb-2">End Exam Early?</h3>
                            <p className="text-muted-foreground leading-relaxed">
                                {sessionData?.isFirstAttempt
                                    ? "As this is your first attempt, this partial attempt will be used to estimate your official score for this paper."
                                    : "Are you sure you want to end this exam? Your current progress will be saved."
                                }
                            </p>
                        </div>
                        <div className="bg-muted/50 p-6 flex flex-col sm:flex-row gap-3 justify-end">
                            <Button
                                variant="ghost"
                                onClick={() => setShowConfirmModal(false)}
                                className="font-semibold"
                            >
                                Cancel
                            </Button>
                            <Button
                                onClick={() => {
                                    setShowConfirmModal(false);
                                    handleSubmitExam();
                                }}
                                className="bg-primary hover:bg-primary/90 font-bold px-8"
                            >
                                Confirm & Submit
                            </Button>
                        </div>
                    </div>
                </div>
            )}

            {/* Question Content */}
            <main className="flex-grow min-h-0 overflow-hidden bg-background relative flex flex-col">
                <QuestionDisplay
                    key={currentQuestion.problemid}
                    type={currentQuestion.type || "unknown"}
                    title={currentQuestion.title}
                    text={currentQuestion.text}
                    options_type={currentQuestion.options_type}
                    options={transformedOptions}
                    selectedOption={currentSelectedOption}
                    handleOptionClick={handleOptionClick}
                    questionId={currentQuestion.problemid}
                    metadata={currentQuestion.metadata}
                    showPagination={false}
                    size={11}
                    isLongOptions={isLongOptions}
                />
            </main>

            {/* Footer Navigation */}
            < footer className="h-20 border-t bg-card/50 flex items-center justify-between px-12 shrink-0" >
                <Button
                    variant="ghost"
                    disabled={currentQuestionIndex === 0}
                    onClick={goToPrevQuestion}
                    className="gap-2 font-bold uppercase tracking-tighter"
                >
                    <ArrowLeft className="w-4 h-4" />
                    Previous
                </Button>

                <div className="hidden md:flex flex-col items-center gap-0.5 opacity-40 hover:opacity-100 transition-opacity duration-500">
                    <div className="flex items-center gap-1.5">
                        <span className="px-1.5 py-0.5 rounded border border-foreground/20 text-[10px] font-bold">←</span>
                        <span className="text-[10px] uppercase font-black tracking-widest">Navigation</span>
                        <span className="px-1.5 py-0.5 rounded border border-foreground/20 text-[10px] font-bold">→</span>
                    </div>
                    <p className="text-[9px] font-medium text-muted-foreground">Use arrow keys for smoother navigation</p>
                </div>

                <div className="flex items-center gap-4">
                    {currentQuestionIndex === currentSection.items.length - 1 ? (
                        <Button
                            onClick={handleFinishSection}
                            className="bg-primary hover:bg-primary/90 px-8 py-6 text-sm font-bold rounded-xl gap-2 shadow-lg shadow-primary/20"
                        >
                            {currentSectionIndex === sessionData.sections.length - 1 ? "Finish Exam" : "Finish Section"}
                            <CheckCircle2 className="w-5 h-5" />
                        </Button>
                    ) : (
                        <Button
                            onClick={goToNextQuestion}
                            className="bg-primary hover:bg-primary/90 px-8 py-6 text-sm font-bold rounded-xl gap-2 shadow-lg shadow-primary/20"
                        >
                            Next Question
                            <ArrowRight className="w-5 h-5" />
                        </Button>
                    )}
                </div>
            </footer >
        </div >
    );
}
