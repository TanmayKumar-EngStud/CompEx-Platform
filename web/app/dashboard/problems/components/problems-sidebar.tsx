"use client";

import React from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Settings2, X, ChevronLeft, ChevronRight } from "lucide-react";
import { Button } from "@/shared/components/ui/button";
import { CategoryAccordion } from "./category-accordion";
import { PreferenceSettingsPanel } from "./preference-settings-panel";
import { Tag } from "@/features/question-solving/hooks/(definitions)/tagDefinition";

interface ProblemsSidebarProps {
    isOpen: boolean;
    setIsOpen: (isOpen: boolean) => void;

    // Data for Categories
    tagData: Tag[];

    // Props for Settings
    bookmarksEnabled: boolean;
    setBookmarksEnabled: (enabled: boolean) => void;
    showTimer: boolean;
    setShowTimer: React.Dispatch<React.SetStateAction<boolean>>;
    showDifficulty: boolean;
    setShowDifficulty: React.Dispatch<React.SetStateAction<boolean>>;
    questionTagsEnabled: boolean;
    setQuestionTagsEnabled: (enabled: boolean) => void;
    onShuffle: (sectionId?: string) => void;
}

export function ProblemsSidebar({
    isOpen,
    setIsOpen,
    tagData,
    bookmarksEnabled,
    setBookmarksEnabled,
    showTimer,
    setShowTimer,
    showDifficulty,
    setShowDifficulty,
    questionTagsEnabled,
    setQuestionTagsEnabled,
    onShuffle,
}: ProblemsSidebarProps) {

    return (
        <>
            {/* Toggle Button (Fixed on the right edge when closed) */}
            <AnimatePresence>
                {!isOpen && (
                    <motion.div
                        initial={{ opacity: 0, x: 20 }}
                        animate={{ opacity: 1, x: 0 }}
                        exit={{ opacity: 0, x: 20 }}
                        transition={{ duration: 0.2 }}
                        className="fixed right-0 top-1/2 -translate-y-1/2 z-40"
                    >
                        <Button
                            variant="outline"
                            size="icon"
                            className="h-12 w-8 rounded-l-xl rounded-r-none border-r-0 shadow-md bg-background hover:bg-muted"
                            onClick={() => setIsOpen(true)}
                            title="Open Filters & Settings"
                            data-tour="problems-filters"
                        >
                            <ChevronLeft className="h-4 w-4" />
                        </Button>
                    </motion.div>
                )}
            </AnimatePresence>

            {/* Sidebar Container */}
            <motion.div
                initial={{ width: 0, opacity: 0 }}
                animate={{
                    width: isOpen ? 320 : 0,
                    opacity: isOpen ? 1 : 0
                }}
                transition={{ type: "spring", stiffness: 300, damping: 30 }}
                className="h-[calc(100vh-9rem)] border-l bg-card overflow-hidden flex-shrink-0 sticky top-4 rounded-l-2xl border-y border-l shadow-sm my-4"
            >
                <div className="h-full w-[320px] flex flex-col">
                    {/* Header */}
                    <div className="flex items-center justify-between p-4 border-b">
                        <div className="flex items-center gap-2">
                            <Settings2 className="h-5 w-5 text-muted-foreground" />
                            <h2 className="font-semibold text-lg">Filters & Settings</h2>
                        </div>
                        <Button
                            variant="ghost"
                            size="icon"
                            className="h-8 w-8"
                            onClick={() => setIsOpen(false)}
                        >
                            <ChevronRight className="h-5 w-5" />
                        </Button>
                    </div>

                    {/* Scrollable Content */}
                    <div className="flex-1 overflow-y-auto p-4 space-y-8 no-scrollbar">
                        {/* Problem Categories */}
                        <section>
                            <h3 className="text-sm font-medium text-muted-foreground mb-3 uppercase tracking-wider">
                                Problem Categories
                            </h3>
                            <CategoryAccordion tagData={tagData} />
                        </section>

                        {/* Settings */}
                        <section>
                            <PreferenceSettingsPanel
                                bookmarksEnabled={bookmarksEnabled}
                                setBookmarksEnabled={setBookmarksEnabled}
                                showTimer={showTimer}
                                setShowTimer={setShowTimer}
                                showDifficulty={showDifficulty}
                                setShowDifficulty={setShowDifficulty}
                                questionTagsEnabled={questionTagsEnabled}
                                setQuestionTagsEnabled={setQuestionTagsEnabled}
                                onShuffle={onShuffle}
                            />
                        </section>
                    </div>
                </div>
            </motion.div>
        </>
    );
}
