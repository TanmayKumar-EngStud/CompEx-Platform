"use client";

import React, { useState, useMemo } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
    BookOpen,
    ArrowRight,
    Zap,
    ChevronDown,
    Target,
    Layers
} from "lucide-react";
import { Button } from "@/shared/components/ui/button";
import { Card, CardContent } from "@/shared/components/ui/card";
import { usePaginationStore } from "@/shared/stores/problems/pagination";
import { useRouter } from "next/navigation";
import { ExploreTag } from "@/features/exploration/services/explore-queries";
import clsx from "clsx";
import { examSectionService } from "@/features/exam-management/services/exam-section-service";
import { useTutorialStore } from "@/shared/stores/tutorial-store";

interface ExplorePageClientProps {
    tags: ExploreTag[];
}

const containerVariants = {
    hidden: { opacity: 0 },
    show: {
        opacity: 1,
        transition: {
            staggerChildren: 0.05
        }
    }
};

const itemVariants = {
    hidden: { opacity: 0, scale: 0.95 },
    show: { opacity: 1, scale: 1 }
};



// const PRACTICE_METHODOLOGY = "Targeted practice is the most efficient way to isolate your conceptual gaps. Instead of drifting through random problem sets, mastering a specific Focused Topic or Question Type forces pattern recognition and sharpens your procedural speed. This 'deliberate practice' methodology ensures that once you sit for a full-length mock, your brain is already conditioned to recognize and execute solutions for every category—regardless of which exam you are taking.";

/* Polygonal Background Component - Replaces MagicBackground */
const PolygonalBackground = ({ name }: { name: string }) => {
    // Generate deterministic values based on tag name
    const seed = name.split("").reduce((acc, char) => acc + char.charCodeAt(0), 0);

    const getRandom = (index: number) => {
        const x = Math.sin(seed + index) * 10000;
        return x - Math.floor(x);
    };

    // Configuration
    const width = 100;
    const height = 100;
    const cols = 8;
    const rows = 4;
    const cellW = width / cols;
    const cellH = height / rows;

    // Generate grid points with jitter
    const points: [number, number][] = [];
    for (let y = 0; y <= rows; y++) {
        for (let x = 0; x <= cols; x++) {
            // Edges should stay on edges to fill space
            let px = x * cellW;
            let py = y * cellH;

            // Jitter internal points
            if (x > 0 && x < cols && y > 0 && y < rows) {
                const jitterX = (getRandom(y * cols + x) - 0.5) * cellW * 0.8;
                const jitterY = (getRandom(y * cols + x + 1000) - 0.5) * cellH * 0.8;
                px += jitterX;
                py += jitterY;
            }
            points.push([px, py]);
        }
    }

    // Generate triangles
    const triangles = [];
    let triIndex = 0;

    // Base color identity
    const baseHue = Math.floor(getRandom(999) * 360);
    const baseSat = 60 + Math.floor(getRandom(888) * 30); // 60-90%

    for (let y = 0; y < rows; y++) {
        for (let x = 0; x < cols; x++) {
            const i = y * (cols + 1) + x;

            // 4 points of the cell
            const p1 = points[i];             // Top-Left
            const p2 = points[i + 1];         // Top-Right
            const p3 = points[i + (cols + 1)]; // Bottom-Left
            const p4 = points[i + (cols + 1) + 1]; // Bottom-Right

            // We split quad into two triangles. 50% chance to split one way or another for variety
            const splitDir = getRandom(i * 33) > 0.5;

            const tT = (pts: number[][], offset: number) => {
                // Color variation
                const l = (40 + getRandom(offset + triIndex) * 50).toFixed(2);
                const a = (0.05 + getRandom(offset + triIndex + 50) * 0.2).toFixed(2);
                const h = (baseHue + (getRandom(offset + triIndex + 100) - 0.5) * 40).toFixed(2);

                triIndex++;
                return (
                    <polygon
                        key={`tri-${triIndex}`}
                        points={pts.map(p => p.map(c => c.toFixed(2)).join(",")).join(" ")}
                        fill={`hsla(${h}, ${baseSat}%, ${l}%, ${a})`}
                        stroke={`hsla(${h}, ${baseSat}%, ${l}%, ${Math.max(0, Number(a) - 0.1).toFixed(2)})`}
                        strokeWidth="0.5"
                    />
                );
            }

            if (splitDir) {
                // p1-p2-p4 & p1-p4-p3
                triangles.push(tT([p1, p2, p4], i));
                triangles.push(tT([p1, p4, p3], i + 1));
            } else {
                // p1-p2-p3 & p2-p4-p3
                triangles.push(tT([p1, p2, p3], i));
                triangles.push(tT([p2, p4, p3], i + 1));
            }
        }
    }

    return (
        <div className="absolute inset-0 z-0 overflow-hidden bg-background/50">
            <svg
                className="w-full h-full"
                viewBox={`0 0 ${width} ${height}`}
                preserveAspectRatio="none"
            >
                {triangles}
            </svg>
            {/* Soft Overlay to ensure text readability */}
            <div className="absolute inset-0 bg-gradient-to-t from-card via-card/80 to-transparent" />
        </div>
    );
};

const SectionAccordion = ({ title, children, defaultOpen = true }: { title: string, children: React.ReactNode, defaultOpen?: boolean }) => {
    const [isOpen, setIsOpen] = useState(defaultOpen);

    return (
        <div className="space-y-4">
            <button
                onClick={() => setIsOpen(!isOpen)}
                className="flex items-center justify-between w-full group py-3 px-4 rounded-xl bg-card/40 border border-border/40 hover:bg-card/60 transition-all"
            >
                <div className="flex items-center gap-3">
                    <div className="w-1.5 h-6 rounded-full bg-primary/40 group-hover:bg-primary transition-colors" />
                    <h3 className="text-xl font-bold tracking-tight">{title}</h3>
                </div>
                <ChevronDown className={clsx("w-5 h-5 text-muted-foreground transition-transform duration-300", isOpen && "rotate-180")} />
            </button>
            <AnimatePresence>
                {isOpen && (
                    <motion.div
                        initial={{ height: 0, opacity: 0 }}
                        animate={{ height: "auto", opacity: 1 }}
                        exit={{ height: 0, opacity: 0 }}
                        transition={{ duration: 0.3, ease: "easeInOut" }}
                        className="overflow-hidden"
                    >
                        <div className="pt-2 pb-6">
                            {children}
                        </div>
                    </motion.div>
                )}
            </AnimatePresence>
        </div>
    );
};

export default function ExplorePageClient({ tags }: ExplorePageClientProps) {
    const router = useRouter();
    const {
        examName,
        setSelectedTopics,
        setSelectedTypes,
        setExamName,
        setSectionName,
        setSectionIndex
    } = usePaginationStore();

    const { pageTours, startTour, isTourRunning, isFirstLogin, activeTour, activeStep } = useTutorialStore();

    // Auto-trigger tour if not completed (skip if first-login modal is still showing)
    React.useEffect(() => {
        if (!pageTours.explore && !isTourRunning && !isFirstLogin) {
            const timer = setTimeout(() => startTour("explore"), 800);
            return () => clearTimeout(timer);
        }
    }, [pageTours.explore, isTourRunning, isFirstLogin, startTour]);

    // Tutorial step-1 card cycling: highlight each topic card one by one so
    // users clearly see they should click a card.
    const isTutorialStep1 = isTourRunning && activeTour === "explore" && activeStep === 0;
    const [tutorialCardIdx, setTutorialCardIdx] = React.useState(0);

    // Filter tags by selected exam
    const currentExamTags = useMemo(() => {
        return tags.filter(t => t.examName.toLowerCase() === examName.toLowerCase());
    }, [tags, examName]);

    // Group tags by section and category
    const groupedData = useMemo(() => {
        const sections: Record<string, { topics: ExploreTag[], types: ExploreTag[] }> = {};

        currentExamTags.forEach(tag => {
            if (!sections[tag.sectionName]) {
                sections[tag.sectionName] = { topics: [], types: [] };
            }
            if (tag.category === "topic") {
                sections[tag.sectionName].topics.push(tag);
            } else if (tag.category === "type") {
                sections[tag.sectionName].types.push(tag);
            }
        });

        return sections;
    }, [currentExamTags]);

    const handleStartPractice = (tag: ExploreTag) => {
        // 1. Set Exam Name (Resets everything)
        setExamName(tag.examName);

        // 2. Find Canonical Section Name & Index
        // This ensures case safety and correct tab index
        const validSections = examSectionService.getTabPropertiesForExam(tag.examName);
        const sectionIndex = validSections.findIndex(
            (s: string) => s.toLowerCase() === tag.sectionName.toLowerCase()
        );

        if (sectionIndex !== -1) {
            const canonicalName = validSections[sectionIndex];
            setSectionName(canonicalName); // Sets canonical name ("verbal" vs "Verbal")
            setSectionIndex(sectionIndex); // Sets correct index (1 vs 0)
        } else {
            // Fallback if not found in config, use tag's name
            setSectionName(tag.sectionName);
            console.warn(`Section ${tag.sectionName} not found in config for ${tag.examName}`);
        }

        // 3. Set Filters (After section/exam reset)
        if (tag.category === "topic") {
            setSelectedTopics([tag.name]);
            setSelectedTypes([]);
        } else {
            setSelectedTypes([tag.name]);
            setSelectedTopics([]);
        }

        router.push(`/dashboard/explore/${encodeURIComponent(tag.name)}`);
    };

    const sectionNames = Object.keys(groupedData);

    // Total topic cards across all sections (used for cycling highlight wrap-around)
    const totalTopicCards = useMemo(() => {
        return sectionNames.reduce((sum, s) => sum + groupedData[s].topics.length, 0);
    }, [sectionNames, groupedData]);

    // Cycle the highlighted card index while tutorial step 1 is active
    React.useEffect(() => {
        if (!isTutorialStep1 || totalTopicCards === 0) {
            setTutorialCardIdx(0);
            return;
        }
        const interval = setInterval(() => {
            setTutorialCardIdx(prev => (prev + 1) % totalTopicCards);
        }, 900);
        return () => clearInterval(interval);
    }, [isTutorialStep1, totalTopicCards]);

    // Global topic index counter — reset each render, incremented while mapping sections.
    // Declared here (not inside JSX) so it's properly scoped to a single render call.
    let _topicCounter = 0;

    return (
        <div className="max-w-7xl mx-auto px-6 py-12 space-y-16">
            {/* Hero Section */}
            <header className="text-center space-y-8" data-tour="explore-hero">
                <div className="space-y-4">
                    <motion.div
                        initial={{ opacity: 0, scale: 0.9 }}
                        animate={{ opacity: 1, scale: 1 }}
                        className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-primary/10 text-primary text-xs font-bold uppercase tracking-wider"
                    >
                        <Zap className="w-3 h-3" />
                        Targeted Practice
                    </motion.div>
                    <motion.h1
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        className="text-5xl font-extrabold tracking-tight sm:text-6xl"
                    >
                        Explore <span className="text-primary italic">{examName}</span> Modules
                    </motion.h1>
                    {/* <motion.p
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: 0.1 }}
                        className="text-lg text-muted-foreground max-w-3xl mx-auto italic font-medium leading-relaxed bg-muted/30 p-8 rounded-2xl border border-border/40"
                    >
                        &quot;{PRACTICE_METHODOLOGY}&quot;
                    </motion.p> */}
                </div>
            </header>

            {/* Topics Section */}
            <section className="space-y-12" data-tour="explore-topics">
                <div className="flex items-center gap-4 border-b border-border/40 pb-4">
                    <div className="p-2 rounded-lg bg-primary/10 text-primary">
                        <Target className="w-6 h-6" />
                    </div>
                    <div>
                        <h2 className="text-3xl font-bold tracking-tight">Focused Topics</h2>
                        <p className="text-sm text-muted-foreground">Isolate concept-specific gaps for {examName}</p>
                    </div>
                </div>

                <div className="max-w-5xl text-muted-foreground leading-relaxed -mt-4">
                    <p>
                        Focused topics allow you to drill down into the core mathematical and verbal concepts that appear across the exam.
                        By mastering these individual modules like <strong>Algebra</strong>, <strong>Geometry</strong>, or <strong>Critical Reasoning</strong>,
                        you build a library of mental models that make complex, multi-concept problems easier to solve on test day.
                    </p>
                </div>

                <div className="space-y-6">
                    {sectionNames.map((section, idx) => (
                        <SectionAccordion key={section} title={section.toUpperCase()} defaultOpen={idx === 0}>
                            <motion.div
                                variants={containerVariants}
                                initial="hidden"
                                animate="show"
                                className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4"
                            >
                                {groupedData[section].topics.map((topic, index) => {
                                    const cardGlobalIdx = _topicCounter++;
                                    const isTutorialHighlighted = isTutorialStep1 && cardGlobalIdx === tutorialCardIdx;
                                    return (
                                        <motion.div key={`${topic.tagid}-${topic.examName}-${topic.sectionName}-${topic.category}`} variants={itemVariants} className="h-full">
                                            <div
                                                className={clsx(
                                                    "group relative overflow-hidden rounded-xl border bg-card transition-all duration-300 h-full min-h-[160px] flex flex-col cursor-pointer shadow-sm",
                                                    isTutorialHighlighted
                                                        ? "border-primary shadow-[0_0_0_3px_rgba(var(--primary-rgb),0.35),0_0_24px_rgba(var(--primary-rgb),0.3)] scale-[1.03] z-10"
                                                        : "border-border/40 hover:border-primary/50 hover:shadow-md"
                                                )}
                                                onClick={() => handleStartPractice(topic)}
                                                data-tour={idx === 0 && index === 0 ? "explore-card-first" : undefined}
                                            >
                                                {/* Full Card Background Animation */}
                                                <PolygonalBackground name={topic.name} />
                                                {/* Overlay Content */}
                                                <div className="relative z-10 p-5 flex flex-col h-full bg-gradient-to-b from-transparent via-card/5 to-card/20">
                                                    {/* Top: Title */}
                                                    <h4 className="text-xl font-bold leading-tight group-hover:text-primary transition-colors mb-auto pr-2">
                                                        {topic.name}
                                                    </h4>

                                                    {/* Bottom: Action & Heatmapped Count */}
                                                    <div className="flex items-end justify-between w-full pt-6 border-t border-border/10 mt-4">
                                                        <div className="flex items-center gap-2 text-muted-foreground group-hover:text-primary transition-colors">
                                                            <span className="text-[10px] font-bold uppercase tracking-wider">Train</span>
                                                            <ArrowRight className="w-3.5 h-3.5 transform group-hover:translate-x-1 transition-transform" />
                                                        </div>

                                                        <div
                                                            className="px-3 py-1.5 rounded-lg text-lg font-bold text-primary border border-primary/20 backdrop-blur-md"
                                                            style={{
                                                                backgroundColor: `rgba(var(--primary-rgb), ${Math.min(Math.max(topic.count / 60, 0.10), 0.5)})`
                                                            }}
                                                        >
                                                            {topic.count} Qs
                                                        </div>
                                                    </div>
                                                </div>
                                            </div>
                                        </motion.div>
                                    );
                                })}
                                {groupedData[section].topics.length === 0 && (
                                    <p className="text-muted-foreground italic text-sm py-4">No specific topics available for this section.</p>
                                )}
                            </motion.div>
                        </SectionAccordion>
                    ))}
                </div>
            </section>

            {/* Question Types Section */}
            <section className="space-y-12 pb-24">
                <div className="flex items-center gap-4 border-b border-border/40 pb-4">
                    <div className="p-2 rounded-lg bg-primary/10 text-primary">
                        <Layers className="w-6 h-6" />
                    </div>
                    <div>
                        <h2 className="text-3xl font-bold tracking-tight">Question Types</h2>
                        <p className="text-sm text-muted-foreground">Master {examName} solving strategies by format</p>
                    </div>
                </div>

                <div className="max-w-5xl text-muted-foreground leading-relaxed -mt-4">
                    <p>
                        Every exam has unique question formats designed to test different cognitive abilities.
                        Practicing by <strong>Question Type</strong> helps you master the specific logic and timing required for formats like &nbsp;
                        <strong>Data Sufficiency</strong>, <strong>Sentence Equivalence</strong>, or <strong>Numerical Entry</strong>.
                        Solving by type ensures you are never surprised by the delivery of a problem.
                    </p>
                </div>

                <div className="space-y-6">
                    {sectionNames.map((section, idx) => (
                        <SectionAccordion key={section} title={section.toUpperCase()} defaultOpen={idx === 0}>
                            <motion.div
                                variants={containerVariants}
                                initial="hidden"
                                animate="show"
                                className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4"
                            >
                                {groupedData[section].types.map((type) => (
                                    <motion.div key={`${type.tagid}-${type.examName}-${type.sectionName}-${type.category}`} variants={itemVariants} className="h-full">
                                        <div
                                            className="group relative overflow-hidden rounded-xl border border-border/30 bg-card hover:border-primary/50 transition-all cursor-pointer shadow-sm border-l-4 border-l-primary/20 hover:border-l-primary h-full min-h-[160px] flex flex-col"
                                            onClick={() => handleStartPractice(type)}
                                        >
                                            <PolygonalBackground name={type.name} />

                                            <div className="relative z-10 p-5 flex flex-col h-full justify-between">
                                                <div className="space-y-1">
                                                    <h4 className="text-lg font-bold group-hover:text-primary transition-colors">{type.name}</h4>
                                                    <p className="text-[10px] text-muted-foreground uppercase tracking-widest font-bold opacity-60">Accuracy & Speed focus</p>
                                                </div>

                                                <div className="flex items-end justify-between w-full pt-6">
                                                    <div className="flex items-center gap-2 text-muted-foreground group-hover:text-primary transition-colors opacity-0 group-hover:opacity-100 transition-opacity">
                                                        <span className="text-[10px] font-bold uppercase tracking-wider">Train</span>
                                                        <ArrowRight className="w-3.5 h-3.5" />
                                                    </div>

                                                    <div
                                                        className="px-3 py-1.5 rounded-lg text-lg font-bold text-primary border border-primary/20 backdrop-blur-sm"
                                                        style={{
                                                            backgroundColor: `rgba(var(--primary-rgb), ${Math.min(Math.max(type.count / 60, 0.10), 0.5)})`
                                                        }}
                                                    >
                                                        {type.count} Qs
                                                    </div>
                                                </div>
                                            </div>
                                        </div>
                                    </motion.div>
                                ))}
                                {groupedData[section].types.length === 0 && (
                                    <p className="text-muted-foreground italic text-sm py-4">No question types available for this section.</p>
                                )}
                            </motion.div>
                        </SectionAccordion>
                    ))}
                </div>
            </section>
        </div>
    );
}
