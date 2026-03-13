"use client";
import React from "react";
import Tab from "./tab";
import Panel from "./panel";
import { usePaginationStore } from "@/shared/stores/problems/pagination";
import { useProblemsStore } from "@/shared/stores/problems/cache";
import { usePaginationCacheStore } from "@/features/question-solving/stores/pagination-cache.store";
import { useNavigationStore } from "@/shared/stores/problems/navigation";
import { motion, AnimatePresence } from "framer-motion";
import { Shuffle, Sparkles, Dice5, X } from "lucide-react";
import { clsx } from "clsx";

interface PanelParentProps {
   children: React.ReactNode[];
   titles: string[];
   defaultIndex?: number;
   onShuffle?: (sectionId?: string) => void;
   isShuffling?: boolean;
}

const PanelParent = ({
   children,
   titles,
   defaultIndex = 0,
   onShuffle,
   isShuffling = false,
}: PanelParentProps) => {
   const {
      sectionName,
      sectionIndex,
      setSectionName,
      setSectionIndex,
      setPage,
      examName,
   } = usePaginationStore();

   const { clearProblems } = useProblemsStore();
   const { clearCache } = usePaginationCacheStore();
   const { setStart } = useNavigationStore();

   const handleTabClick = (index: number, title: string) => {
      if (title === sectionName) return;

      console.log(`🎯 Tab clicked: ${title}. Resetting section state.`);

      // Reset ALL stores immediately to prevent stale data display
      clearProblems();
      clearCache();
      setStart(-1);

      setPage(1);
      setSectionName(title);
      setSectionIndex(index);
   };

   const handleShuffleAction = async () => {
      if (!onShuffle) return;

      // If already in mixed mode, "undo" it by going to the first section
      if (sectionName === "mixed") {
         const firstSection = titles[0] || "quants";
         setPage(1);
         setSectionName(firstSection);
         setSectionIndex(0);
         return;
      }

      // Set section to mixed to fetch all questions
      setPage(1);
      setSectionName("mixed");

      const targetSectionId = `${examName}-mixed`;

      // Trigger shuffle for the mixed section
      onShuffle(targetSectionId);
   };

   return (
      <div className="space-y-6">
         <div className="flex items-center justify-between gap-4 bg-card/30 p-2 rounded-xl border border-border/40 backdrop-blur-sm">
            <div
               data-tour="section-tabs"
               className="relative flex flex-1 rounded-lg bg-muted/50 p-1 gap-1 flex-nowrap overflow-x-auto no-scrollbar"
            >
               <AnimatePresence>
                  {sectionName === "mixed" && (
                     <motion.div
                        layoutId="mixed-highlighter"
                        className="absolute inset-1 bg-background rounded-md shadow-sm z-0 border border-primary/10"
                        initial={{ opacity: 0, scaleX: 0.95 }}
                        animate={{ opacity: 1, scaleX: 1 }}
                        exit={{ opacity: 0, scaleX: 0.95 }}
                        transition={{ type: "spring", bounce: 0, duration: 0.4 }}
                     />
                  )}
               </AnimatePresence>

               {titles.map((title, index) => {
                  const isMixed = sectionName === "mixed";
                  const isActive = title === sectionName;

                  return (
                     <React.Fragment key={index}>
                        {index > 0 && isMixed && (
                           <div className="flex items-center px-1 z-10 shrink-0">
                              <motion.span
                                 initial={{ opacity: 0, scale: 0 }}
                                 animate={{ opacity: 1, scale: 1 }}
                                 className="text-primary/60 font-black text-xs"
                              >
                                 +
                              </motion.span>
                           </div>
                        )}
                        <Tab
                           onClick={() => handleTabClick(index, title)}
                           on={isActive && !isMixed}
                           className={clsx(
                              "transition-all duration-300",
                              isMixed && "bg-transparent shadow-none z-10 text-foreground font-bold"
                           )}
                        >
                           <span className="capitalize">{title}</span>
                        </Tab>
                     </React.Fragment>
                  );
               })}
            </div>

            {onShuffle && (
               <motion.button
                  whileHover={{ scale: 1.02, x: 2 }}
                  whileTap={{ scale: 0.98 }}
                  onClick={handleShuffleAction}
                  disabled={isShuffling}
                  className={clsx(
                     "relative group flex items-center justify-center w-10 h-10 rounded-lg font-bold transition-all duration-300 overflow-hidden",
                     sectionName === "mixed"
                        ? "bg-primary text-primary-foreground shadow-[0_0_20px_rgba(var(--primary-rgb),0.3)]"
                        : "bg-secondary hover:bg-secondary/80 text-secondary-foreground border border-border/40"
                  )}
               >
                  {/* Background Glow for Shuffling State */}
                  <AnimatePresence>
                     {isShuffling && (
                        <motion.div
                           initial={{ opacity: 0 }}
                           animate={{ opacity: 1 }}
                           exit={{ opacity: 0 }}
                           className="absolute inset-0 bg-gradient-to-r from-primary via-blue-400 to-primary bg-[length:200%_auto] animate-gradient"
                        />
                     )}
                  </AnimatePresence>

                  <div className="relative z-10 flex items-center justify-center">
                     <AnimatePresence mode="wait">
                        <motion.div
                           key={isShuffling ? "shuffling" : sectionName === "mixed" ? "mixed" : "normal"}
                           initial={{ opacity: 0, scale: 0.5, rotate: -45 }}
                           animate={{ opacity: 1, scale: 1, rotate: 0 }}
                           exit={{ opacity: 0, scale: 0.5, rotate: 45 }}
                           transition={{ duration: 0.2, ease: "easeInOut" }}
                        >
                           <motion.div
                              animate={isShuffling ? { rotate: 360 } : {}}
                              transition={isShuffling ? { repeat: Infinity, duration: 1, ease: "linear" } : {}}
                           >
                              {isShuffling ? (
                                 <Dice5 className="w-5 h-5" />
                              ) : sectionName === "mixed" ? (
                                 <X className="w-5 h-5 text-primary-foreground" />
                              ) : (
                                 <Shuffle className="w-5 h-5" />
                              )}
                           </motion.div>
                        </motion.div>
                     </AnimatePresence>



                     {!isShuffling && (
                        <AnimatePresence>
                           <motion.div
                              initial={{ opacity: 0, scale: 0 }}
                              whileHover={{ opacity: 1, scale: 1 }}
                              className="absolute -top-1 -right-1"
                           >
                              <Sparkles className="w-3 h-3 text-yellow-400 animate-pulse" />
                           </motion.div>
                        </AnimatePresence>
                     )}
                  </div>
               </motion.button>
            )}
         </div>

         <motion.div
            key={sectionName}
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.3 }}
         >
            <Panel active={true}>{children[sectionIndex] || children[0]}</Panel>
         </motion.div>
      </div>
   );
};

export default PanelParent;
