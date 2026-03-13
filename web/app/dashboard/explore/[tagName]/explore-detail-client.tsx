"use client";

import React, { useEffect, useMemo } from "react";
import { useRouter } from "next/navigation";
import { motion } from "framer-motion";
import {
    ArrowLeft,
    Play,
    Shuffle,
    Zap,
    BookOpen,
    Target,
    Layers
} from "lucide-react";
import { Button } from "@/shared/components/ui/button";
import { usePaginationStore } from "@/shared/stores/problems/pagination";
import { usePaginationCacheStore } from "@/features/question-solving/stores/pagination-cache.store";
import { usePaginatedProblems } from "@/features/question-solving/hooks/(pagination)/fetchProblems";
import { useAttemptsStore } from "@/shared/stores/problems/attempts";
import { useProblemsStore } from "@/shared/stores/problems/cache";
import { useNavigationStore } from "@/shared/stores/problems/navigation";
import { useUIStore } from "@/shared/stores/problems/ui-state";
import { ProblemsTableSection } from "../../problems/components/problems-table-section";
import { LazyQuestionWindow } from "@/shared/components/feedback/lazy/LazyQuestionWindow";
import { LazyResultWindow } from "@/shared/components/feedback/lazy/LazyResultWindow";
import { useProblemsPageState } from "../../problems/hooks/use-problems-page-state";
import { useQuestionWindowControls } from "../../problems/hooks/use-question-window-controls";
import { ExploreTag } from "@/features/exploration/services/explore-queries";
import { examSectionService } from "@/features/exam-management/services/exam-section-service";

interface ExploreDetailClientProps {
    tag: ExploreTag;
}

/* Polygonal Background Component - Consistent with main explore page */
const HeaderBackground = ({ name }: { name: string }) => {
    const seed = name.split("").reduce((acc, char) => acc + char.charCodeAt(0), 0);
    const getRandom = (index: number) => {
        const x = Math.sin(seed + index) * 10000;
        return x - Math.floor(x);
    };

    const width = 100;
    const height = 100;
    const cols = 12;
    const rows = 3;
    const cellW = width / cols;
    const cellH = height / rows;

    const points: [number, number][] = [];
    for (let y = 0; y <= rows; y++) {
        for (let x = 0; x <= cols; x++) {
            let px = x * cellW;
            let py = y * cellH;
            if (x > 0 && x < cols && y > 0 && y < rows) {
                px += (getRandom(y * cols + x) - 0.5) * cellW * 0.8;
                py += (getRandom(y * cols + x + 1000) - 0.5) * cellH * 0.8;
            }
            points.push([px, py]);
        }
    }

    const triangles = [];
    const baseHue = Math.floor(getRandom(999) * 360);

    for (let y = 0; y < rows; y++) {
        for (let x = 0; x < cols; x++) {
            const i = y * (cols + 1) + x;
            const p1 = points[i];
            const p2 = points[i + 1];
            const p3 = points[i + (cols + 1)];
            const p4 = points[i + (cols + 1) + 1];
            const splitDir = getRandom(i * 33) > 0.5;

            const renderTri = (pts: number[][], offset: number) => {
                const l = (70 + getRandom(offset) * 20).toFixed(2);
                const a = (0.1 + getRandom(offset + 50) * 0.1).toFixed(2);
                const h = (baseHue + (getRandom(offset + 100) - 0.5) * 30).toFixed(2);

                return (
                    <polygon
                        key={`${offset}-${triangles.length}`}
                        points={pts.map(p => p.map(c => c.toFixed(2)).join(",")).join(" ")}
                        fill={`hsla(${h}, 70%, ${l}%, ${a})`}
                    />
                );
            };

            if (splitDir) {
                triangles.push(renderTri([p1, p2, p4], i));
                triangles.push(renderTri([p1, p4, p3], i + 1));
            } else {
                triangles.push(renderTri([p1, p2, p3], i));
                triangles.push(renderTri([p2, p4, p3], i + 1));
            }
        }
    }

    return (
        <div className="absolute inset-0 z-0 overflow-hidden bg-muted/20">
            <svg className="w-full h-full" viewBox="0 0 100 100" preserveAspectRatio="none">
                {triangles}
            </svg>
            <div className="absolute inset-0 bg-gradient-to-b from-transparent to-background" />
        </div>
    );
};

export default function ExploreDetailClient({ tag }: ExploreDetailClientProps) {
    const router = useRouter();
    const {
        examName,
        sectionName,
        setSelectedTopics,
        setSelectedTypes,
        setExamName,
        setSectionName,
        setSectionIndex,
        setPage
    } = usePaginationStore();

    const { userId } = useAttemptsStore();
    const { clearProblems } = useProblemsStore();
    const { ensurePreferencesInitialized } = useUIStore();
    const {
        initializeService,
        shuffleQuestions,
        clearCache,
        isShuffling: cacheIsShuffling
    } = usePaginationCacheStore();
    const { setStart } = useNavigationStore();

    const [isLocalShuffling, setIsLocalShuffling] = React.useState(false);
    const pageState = useProblemsPageState();
    const windowControls = useQuestionWindowControls();
    const problemData = usePaginatedProblems();

    // Sync Store with URL Tag on mount
    useEffect(() => {
        // Only set if different to avoid infinite loops or unnecessary resets
        const isAlreadySet =
            examName === tag.examName &&
            sectionName === tag.sectionName &&
            (tag.category === "topic" ? true : true); // We'll just set it to be sure

        console.log("🎯 Training Mode Initializing for:", tag.name);

        // 1. Set Exam & Section
        setExamName(tag.examName);
        const validSections = examSectionService.getTabPropertiesForExam(tag.examName);
        const sectionIndex = validSections.findIndex((s: string) => s.toLowerCase() === tag.sectionName.toLowerCase());

        if (sectionIndex !== -1) {
            setSectionName(validSections[sectionIndex]);
            setSectionIndex(sectionIndex);
        } else {
            setSectionName(tag.sectionName);
        }

        // 2. Set Specific Filter
        if (tag.category === "topic") {
            setSelectedTopics([tag.name]);
            setSelectedTypes([]);
        } else {
            setSelectedTypes([tag.name]);
            setSelectedTopics([]);
        }

        // 3. Reset Pagination & Cache
        setPage(1);
        clearProblems();
        clearCache();
        setStart(-1);

        // 4. Initialize Service
        initializeService({}, userId);
        ensurePreferencesInitialized();

    }, [
        tag,
        userId,
        examName,
        sectionName,
        setExamName,
        setSectionName,
        setSectionIndex,
        setSelectedTopics,
        setSelectedTypes,
        setPage,
        clearProblems,
        clearCache,
        setStart,
        initializeService,
        ensurePreferencesInitialized
    ]);

    const handleShuffle = async () => {
        setIsLocalShuffling(true);
        try {
            await shuffleQuestions();
        } finally {
            setIsLocalShuffling(false);
        }
    };

    const handleStartTraining = () => {
        windowControls.handleOpenQuestionWindow(pageState.setIsQuestionWindowOpen);
    };

    const isShuffling = isLocalShuffling || cacheIsShuffling;

    return (
        <div className="flex flex-col min-h-screen">
            {/* Header / Hero */}
            <header className="relative pt-12 pb-8 px-6 border-b border-border/40 overflow-hidden">
                <HeaderBackground name={tag.name} />
                <div className="max-w-7xl mx-auto relative z-10 space-y-6">
                    <Button
                        variant="ghost"
                        size="sm"
                        className="gap-2 -ml-2 text-muted-foreground hover:text-foreground"
                        onClick={() => router.push("/dashboard/explore")}
                    >
                        <ArrowLeft className="w-4 h-4" />
                        Back to Modules
                    </Button>

                    <div className="flex flex-col md:flex-row md:items-end justify-between gap-6">
                        <div className="space-y-2">
                            <div className="flex items-center gap-2">
                                <div className="px-2 py-0.5 rounded-full bg-primary/10 text-[10px] font-bold text-primary border border-primary/20 uppercase tracking-wider">
                                    {tag.examName} • {tag.sectionName}
                                </div>
                                <div className="px-2 py-0.5 rounded-full bg-muted text-[10px] font-bold text-muted-foreground border border-border uppercase tracking-wider">
                                    {tag.category}
                                </div>
                            </div>
                            <h1 className="text-4xl font-extrabold tracking-tight">{tag.name}</h1>
                            <p className="text-muted-foreground max-w-2xl">
                                Targeted training session for master of {tag.name.toLowerCase()}.
                                Complete the questions below to improve your pattern recognition and solving speed.
                            </p>
                        </div>

                        <div className="flex items-center gap-3">
                            <Button
                                variant="outline"
                                size="lg"
                                className="gap-2 font-bold"
                                onClick={handleShuffle}
                                disabled={isShuffling}
                            >
                                <Shuffle className={`w-4 h-4 ${isShuffling ? 'animate-spin' : ''}`} />
                                Shuffle
                            </Button>
                            <Button
                                size="lg"
                                className="gap-2 font-bold px-8 shadow-lg shadow-primary/20"
                                onClick={handleStartTraining}
                            >
                                <Play className="w-4 h-4 fill-current" />
                                Start Training
                            </Button>
                        </div>
                    </div>
                </div>
            </header>

            {/* Main Content */}
            <main className="flex-1 max-w-7xl mx-auto w-full px-6 py-8">
                <div className="bg-card/50 rounded-2xl border border-border/40 p-6 md:p-8 shadow-sm">
                    <ProblemsTableSection
                        problemData={problemData}
                        showDifficulty={true}
                        openQuestion={() => windowControls.handleOpenQuestionWindow(pageState.setIsQuestionWindowOpen)}
                        isShuffling={isShuffling}
                    />
                </div>
            </main>

            {/* Modals */}
            {pageState.isResultWindowOpen &&
                (windowControls.hasValidAttempts ||
                    pageState.pendingLocalAttempts) && (
                    <LazyResultWindow
                        onClose={() =>
                            windowControls.handleCloseResultWindow(
                                pageState.setIsResultWindowOpen,
                                pageState.setPendingLocalAttempts
                            )
                        }
                        localAttempts={pageState.pendingLocalAttempts}
                        hideLabels={true}
                    />
                )}

            {pageState.isQuestionWindowOpen && (
                <LazyQuestionWindow
                    onClose={() =>
                        windowControls.handleCloseQuestionWindow(
                            pageState.setIsQuestionWindowOpen
                        )
                    }
                    onFinish={(localAttempts: Map<number, any>) =>
                        windowControls.handleFinishSession(
                            pageState.setIsQuestionWindowOpen,
                            pageState.setIsResultWindowOpen,
                            pageState.setPendingLocalAttempts,
                            localAttempts || new Map()
                        )
                    }
                    showTimer={true}
                    hideLabels={true}
                />
            )}
        </div>
    );
}
