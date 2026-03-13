"use client";

import React, { useMemo, useState, useCallback } from "react";
import { usePaginationStore } from "@/shared/stores/problems/pagination";
import { Tag } from "@/features/question-solving/hooks/(definitions)/tagDefinition";
import { motion, AnimatePresence } from "framer-motion";
import { ChevronDown, Hash } from "lucide-react";
import { cn } from "@/shared/lib/utils";

interface CategoryAccordionProps {
    tagData: Tag[];
}

export const CategoryAccordion: React.FC<CategoryAccordionProps> = React.memo(
    function CategoryAccordion({ tagData = [] }) {
        const {
            selectedTopics,
            setSelectedTopics,
            selectedThemes,
            setSelectedThemes,
            selectedTypes,
            setSelectedTypes,
        } = usePaginationStore();

        // Aggregate tags into categories
        const categories = useMemo(() => {
            const { sectionName } = usePaginationStore.getState();
            const isMixed = sectionName === "mixed";

            if (!Array.isArray(tagData)) return { topics: [], themes: [], types: [] };

            const topicMap = new Map<string, number>();
            const themeMap = new Map<string, number>();
            const typeMap = new Map<string, number>();

            tagData.forEach((tag) => {
                if (tag.topic && typeof tag.topic === "string" && tag.topic.trim() !== "") {
                    topicMap.set(tag.topic, (topicMap.get(tag.topic) || 0) + tag.count);
                }
                if (tag.theme && typeof tag.theme === "string" && tag.theme.trim() !== "") {
                    themeMap.set(tag.theme, (themeMap.get(tag.theme) || 0) + tag.count);
                }
                if (tag.type && typeof tag.type === "string" && tag.type.trim() !== "") {
                    typeMap.set(tag.type, (typeMap.get(tag.type) || 0) + tag.count);
                }
            });

            const shuffle = <T,>(array: T[]): T[] => {
                const newArr = [...array];
                for (let i = newArr.length - 1; i > 0; i--) {
                    const j = Math.floor(Math.random() * (i + 1));
                    [newArr[i], newArr[j]] = [newArr[j], newArr[i]];
                }
                return newArr;
            };

            const processList = (map: Map<string, number>) => {
                const list = Array.from(map.entries())
                    .map(([name, count]) => ({ name, count }))
                    .filter((t) => t.name && t.name.trim().length > 0);
                return isMixed ? shuffle(list) : list;
            };

            return {
                topics: processList(topicMap),
                themes: processList(themeMap),
                types: processList(typeMap),
            };
        }, [tagData]);

        const toggleSelection = useCallback((
            category: "topic" | "theme" | "type",
            name: string
        ) => {
            if (category === "topic") {
                setSelectedTopics(
                    selectedTopics.includes(name)
                        ? selectedTopics.filter((t) => t !== name)
                        : [...selectedTopics, name]
                );
            } else if (category === "theme") {
                setSelectedThemes(
                    selectedThemes.includes(name)
                        ? selectedThemes.filter((t) => t !== name)
                        : [...selectedThemes, name]
                );
            } else if (category === "type") {
                setSelectedTypes(
                    selectedTypes.includes(name)
                        ? selectedTypes.filter((t) => t !== name)
                        : [...selectedTypes, name]
                );
            }
        }, [selectedTopics, selectedThemes, selectedTypes, setSelectedTopics, setSelectedThemes, setSelectedTypes]);

        const hasAnySelection = selectedTopics.length > 0 || selectedThemes.length > 0 || selectedTypes.length > 0;

        const clearAllFilters = useCallback(() => {
            setSelectedTopics([]);
            setSelectedThemes([]);
            setSelectedTypes([]);
        }, [setSelectedTopics, setSelectedThemes, setSelectedTypes]);

        return (
            <div className="flex flex-col gap-3">
                <AnimatePresence>
                    {hasAnySelection && (
                        <motion.div
                            initial={{ opacity: 0, y: -10 }}
                            animate={{ opacity: 1, y: 0 }}
                            exit={{ opacity: 0, y: -10 }}
                            className="flex justify-end mb-1"
                        >
                            <button
                                onClick={clearAllFilters}
                                className="text-xs font-medium text-primary hover:text-primary/80 transition-colors flex items-center gap-1.5 px-2 py-1 rounded-md hover:bg-primary/5"
                            >
                                <span className="bg-primary/10 rounded-full w-4 h-4 flex items-center justify-center text-[10px]">
                                    {selectedTopics.length + selectedThemes.length + selectedTypes.length}
                                </span>
                                Clear filters
                            </button>
                        </motion.div>
                    )}
                </AnimatePresence>

                <AccordionSection
                    title="Question Types"
                    items={categories.types}
                    selectedItems={selectedTypes}
                    onToggle={(name) => toggleSelection("type", name)}
                    defaultOpen={true}
                />
                <AccordionSection
                    title="Topics"
                    items={categories.topics}
                    selectedItems={selectedTopics}
                    onToggle={(name) => toggleSelection("topic", name)}
                    defaultOpen={false}
                />
                <AccordionSection
                    title="Themes"
                    items={categories.themes}
                    selectedItems={selectedThemes}
                    onToggle={(name) => toggleSelection("theme", name)}
                    defaultOpen={false}
                />
            </div>
        );
    }
);

interface AccordionSectionProps {
    title: string;
    items: { name: string; count: number }[];
    selectedItems: string[];
    onToggle: (name: string) => void;
    defaultOpen?: boolean;
}

const TagRow = ({
    name,
    count,
    isActive,
    onClick
}: {
    name: string;
    count: number;
    isActive: boolean;
    onClick: () => void
}) => (
    <div
        onClick={onClick}
        className={cn(
            "flex items-center justify-between px-3 py-2.5 rounded-md transition-all cursor-pointer text-sm group border-l-2",
            isActive
                ? "bg-primary/5 text-primary border-primary font-semibold shadow-sm"
                : "hover:bg-muted/70 text-muted-foreground hover:text-foreground border-transparent border-l-muted/30"
        )}
    >
        <div className="flex items-center gap-2 overflow-hidden">
            {!isActive && <Hash className="h-3 w-3 opacity-30 group-hover:opacity-100 transition-opacity" />}
            <span className="truncate">{name}</span>
        </div>
        <span className={cn(
            "ml-2 px-1.5 py-0.5 rounded text-[10px] font-bold min-w-[28px] text-center transition-colors",
            isActive ? "bg-primary text-primary-foreground" : "bg-muted text-muted-foreground group-hover:bg-primary/20 group-hover:text-primary"
        )}>
            {count}
        </span>
    </div>
);

const AccordionSection = ({
    title,
    items,
    selectedItems,
    onToggle,
    defaultOpen = false,
}: AccordionSectionProps) => {
    const [isOpen, setIsOpen] = useState(defaultOpen);

    if (items.length === 0) return null;

    return (
        <div className="border border-border/50 rounded-xl overflow-hidden bg-card/30 backdrop-blur-sm">
            <button
                onClick={() => setIsOpen(!isOpen)}
                className="w-full flex items-center justify-between p-4 bg-muted/20 hover:bg-muted/40 transition-colors text-sm font-semibold"
            >
                <div className="flex items-center gap-2">
                    <span className="bg-primary/10 text-primary w-1.5 h-1.5 rounded-full" />
                    <span>{title} <span className="text-muted-foreground/60 font-normal ml-1">({items.length})</span></span>
                </div>
                <motion.div
                    animate={{ rotate: isOpen ? 180 : 0 }}
                    transition={{ duration: 0.2 }}
                >
                    <ChevronDown className="h-4 w-4 text-muted-foreground/50" />
                </motion.div>
            </button>

            <AnimatePresence initial={false}>
                {isOpen && (
                    <motion.div
                        initial={{ height: 0, opacity: 0 }}
                        animate={{ height: "auto", opacity: 1 }}
                        exit={{ height: 0, opacity: 0 }}
                        transition={{ duration: 0.25, ease: "circOut" }}
                    >
                        <div className="px-2 py-3 border-t border-border/50 bg-background/20">
                            <div className="flex flex-col gap-0.5">
                                {items.map((item, idx) => (
                                    <TagRow
                                        key={`${title}-${idx}`}
                                        name={item.name}
                                        count={item.count}
                                        isActive={selectedItems.includes(item.name)}
                                        onClick={() => onToggle(item.name)}
                                    />
                                ))}
                            </div>
                        </div>
                    </motion.div>
                )}
            </AnimatePresence>
        </div>
    );
};
