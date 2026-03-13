"use client";

import React, { useEffect, useState, useMemo } from "react";
import AnimatedPagination from "../../Pagination/animatedPagination";
import { classNames } from "@/shared/lib/utils/formatting";
import TC23Template from "../templates/TC-23";
import SETemplate from "../templates/SE";
import NETemplate from "../templates/NE";
import ParentChildTemplate from "../templates/ParentChild";
import DichotomousTemplate from "../templates/Dichotomous";
import { LazyMathRenderer } from "@/shared/components/math/LazyMathRenderer";
import { getTemplateComponent } from "../templates/templateMap";
import { Checkbox } from "@/shared/components/ui/checkbox";
import { RadioGroup, RadioGroupItem } from "@/shared/components/ui/radio-group";
import { useQuestionStats } from "@/features/user-analytics/hooks/use-question-stats";
import Loading from "@/shared/components/feedback/loading";
import { Target, Activity } from "lucide-react";
import { useSubscription } from "@/shared/hooks/use-subscription";
import ProUpgradePrompt from "@/shared/components/marketing/ProUpgradePrompt";

const op = ["A", "B", "C", "D", "E", "F", "G", "H"];

// --- Interfaces ---

interface OptionData {
   optiontext: string;
   group?: string;
}

interface OptionsGridProps {
   type: string;
   options: Record<string, OptionData> | any[];
   isLongOptions: boolean;
   isAttempting: boolean;
   selectedOption: string | string[] | null;
   correctOption: string | string[] | undefined;
   handleOptionClick?: (optionText: string | string[]) => void;
   handleClear?: () => void;
   op: string[];
   text?: string;
   hideLabels?: boolean;
}

export interface QuestionProps {
   type: string;
   title: string;
   text: string;
   options: { [key: string]: { optiontext: string; group?: string } };
   selectedOption: string[];
   correctOption?: string[];
   handleOptionClick?: (option: string | string[]) => void;
   isLongOptions: boolean;
   handleClear?: () => void;
   handleClearAll?: () => void;
   handlePageChange?: (id: number) => void;
   questionIds?: (number | { [key: string]: number[] })[];
   questionId?: number;
   size?: number;
   showPagination?: boolean;
   showSolution?: boolean;
   solution?: any;
   options_type?: string | null;
   metadata?: any;
   localAttempts?: Map<number, string[]>;
   resultCorrectnessData?: Map<number, boolean>;
   isResultWindow?: boolean;
   tags?: string[];
   parentTags?: string[];
   hideLabels?: boolean;
   showTitle?: boolean;
   isLoading?: boolean;
}

// --- Helper Components & Functions ---

const processMathAndMarkdown = (text: string, partKey: string): React.JSX.Element => {
   const mathRegex = /\$([^$]+)\$/g;
   const parts: (string | React.JSX.Element)[] = [];
   let lastIndex = 0;
   let partIndex = 0;
   let match;
   while ((match = mathRegex.exec(text)) !== null) {
      if (match.index > lastIndex) parts.push(text.substring(lastIndex, match.index));
      parts.push(<LazyMathRenderer key={`${partKey}-math-${partIndex++}`} expression={match[1]} displayMode={false} className="inline mx-0.5" />);
      lastIndex = match.index + match[0].length;
   }
   if (lastIndex < text.length) parts.push(text.substring(lastIndex));
   if (parts.length === 0) parts.push(text);

   const processedParts = parts.map((part, idx) => {
      if (typeof part !== 'string') return part;
      const blankRegex = /_{2,}/g;
      const fragments: (string | React.JSX.Element)[] = [];
      let fragmentLastIndex = 0;
      let blankMatch;
      while ((blankMatch = blankRegex.exec(part)) !== null) {
         if (blankMatch.index > fragmentLastIndex) fragments.push(part.substring(fragmentLastIndex, blankMatch.index));
         fragments.push(<span key={`${partKey}-blank-${idx}-${blankMatch.index}`} className="inline-flex items-center justify-center min-w-14 h-[1.3rem] mx-1 bg-primary/3 border-b-2 border-primary/40 rounded-sm align-middle vertical-align-[-0.2em]" />);
         fragmentLastIndex = blankMatch.index + blankMatch[0].length;
      }
      if (fragmentLastIndex < part.length) fragments.push(part.substring(fragmentLastIndex));

      const subParts = fragments.flatMap((frag, fragIdx) => {
         if (typeof frag !== 'string') return [frag];
         const boldRegex = /(\*\*|__)(.*?)\1/g;
         const bolded: (string | React.JSX.Element)[] = [];
         let boldLastIndex = 0;
         let boldMatch;
         while ((boldMatch = boldRegex.exec(frag)) !== null) {
            if (boldMatch.index > boldLastIndex) bolded.push(frag.substring(boldLastIndex, boldMatch.index));
            bolded.push(<strong key={`${partKey}-bold-${idx}-${fragIdx}-${boldMatch.index}`} className="font-bold text-foreground">{boldMatch[2]}</strong>);
            boldLastIndex = boldMatch.index + boldMatch[0].length;
         }
         if (boldLastIndex < frag.length) bolded.push(frag.substring(boldLastIndex));
         return bolded;
      });
      return subParts.length > 0 ? <React.Fragment key={idx}>{subParts}</React.Fragment> : part;
   });
   return <>{processedParts}</>;
};

const parseSolutionText = (text: string) => {
   if (!text) return [];
   // Handle both escaped and literal newlines
   const normalizedText = text.replace(/\\n/g, "\n");

   // Split by top-level HTML blocks. We look for <div...>...</div> or <svg...>...</svg>
   // This regex uses | to match either block type fully.
   const parts = normalizedText.split(/(<div[\s\S]*?<\/div>|<svg[\s\S]*?<\/svg>)/gi);
   const renderedElements: React.JSX.Element[] = [];

   parts.forEach((part, index) => {
      if (!part) return;
      const trimmed = part.trim();
      if (!trimmed) return;

      if (trimmed.toLowerCase().startsWith("<div") || trimmed.toLowerCase().startsWith("<svg")) {
         // Render the entire HTML block at once
         renderedElements.push(
            <div
               key={`html-${index}`}
               dangerouslySetInnerHTML={{ __html: part }}
               className="w-full overflow-x-auto my-4"
            />
         );
      } else {
         // Process normal text and math
         const paragraphs = part.split(/\n\s*\n/);
         paragraphs.forEach((paragraph, pIdx) => {
            const trimmedPara = paragraph.trim();
            if (!trimmedPara) return;

            const lines = paragraph.split("\n");
            const renderedLines = lines.map((line, lIdx) => {
               const trimmedLine = line.trim();
               if (!trimmedLine) return null;

               const isBullet = trimmedLine.startsWith("- ") || trimmedLine.startsWith("* ");
               const content = isBullet ? trimmedLine.substring(2) : line;
               const processedContent = processMathAndMarkdown(
                  content,
                  `text-${index}-${pIdx}-${lIdx}`
               );

               if (isBullet) {
                  return (
                     <div key={lIdx} className="flex gap-2 ml-4 my-1">
                        <span className="text-primary mt-1.5">•</span>
                        <span className="flex-1">{processedContent}</span>
                     </div>
                  );
               }
               return (
                  <div key={lIdx} className="mb-0.5">
                     {processedContent}
                  </div>
               );
            });

            renderedElements.push(
               <div key={`p-${index}-${pIdx}`} className="mb-4 leading-relaxed">
                  {renderedLines}
               </div>
            );
         });
      }
   });

   return renderedElements;
};

const OptionsGrid: React.FC<OptionsGridProps> = ({
   type,
   options,
   isLongOptions,
   isAttempting,
   selectedOption,
   correctOption,
   handleOptionClick,
   handleClear,
   op,
   text,
   hideLabels,
}) => {
   if (type === "NE") {
      return (
         <NETemplate
            isAttempting={isAttempting}
            optionSelected={selectedOption?.[0] || ""}
            handleSetAnswer={handleOptionClick}
            correctAnswer={correctOption as string[]}
            handleClear={handleClear}
         />
      );
   } else if (type.startsWith("TC-") || type === "TC" || type === "GI") {
      return (
         <TC23Template
            isAttempting={isAttempting}
            options={options as any}
            selectedOptions={(selectedOption as string[]) || null}
            correctOptions={correctOption as string[]}
            handleOptionClick={handleOptionClick}
            isLongOptions={isLongOptions}
            text={text}
         />
      );
   } else if (type === "SE" || type === "Sentence Equivalence") {
      return (
         <SETemplate
            isAttempting={isAttempting}
            options={options as any}
            selectedOptions={(selectedOption as string[]) || null}
            correctOptions={correctOption as string[]}
            handleOptionClick={handleOptionClick}
            isLongOptions={isLongOptions}
         />
      );
   }

   const correctOptions = Array.isArray(correctOption) ? correctOption : [];
   const selectedOptions = Array.isArray(selectedOption) ? selectedOption : [];
   const isSingleCorrect = type !== "MCQ-Multi";

   if (isSingleCorrect) {
      const currentValue = selectedOptions.length > 0 ? selectedOptions[0] : "";
      const handleRadioChange = (value: string) => {
         if (isAttempting && handleOptionClick) {
            if (currentValue === value) {
               handleOptionClick([]);
            } else {
               handleOptionClick(value);
            }
         }
      };

      return (
         <RadioGroup
            value={currentValue}
            onValueChange={handleRadioChange}
            disabled={!isAttempting}
            className={`grid ${isLongOptions ? "grid-cols-1" : "grid-cols-2"} gap-3`}
         >
            {Object.entries(options).map(([key, value]) => {
               const optiontext = (value as any).optiontext;
               const isSelected = selectedOptions.includes(optiontext);
               const isCorrect = correctOptions.includes(optiontext);
               const handleSingleClick = (event: React.MouseEvent) => {
                  if (isAttempting && handleOptionClick) {
                     if (isSelected) {
                        event.preventDefault();
                        handleOptionClick([]);
                     }
                  }
               };

               return (
                  <label
                     key={key}
                     htmlFor={`single-option-${key}`}
                     className={`p-3 border rounded-lg cursor-pointer transition-all duration-200 block group ${isAttempting
                        ? isSelected
                           ? "bg-primary/10 border-primary text-foreground ring-1 ring-primary/20 shadow-xs"
                           : "bg-background border-border text-foreground hover:bg-muted/50 hover:border-muted-foreground/30"
                        : isSelected
                           ? isCorrect
                              ? "bg-green-100 dark:bg-green-900/30 border-green-500 text-foreground"
                              : "bg-red-100 dark:bg-red-900/30 border-red-500 text-foreground"
                           : isCorrect
                              ? "bg-green-100 dark:bg-green-900/30 border-green-500 text-foreground"
                              : "bg-background border-border text-foreground"
                        }`}
                     onClick={handleSingleClick}
                  >
                     <div className="flex items-center space-x-3">
                        <RadioGroupItem value={optiontext} id={`single-option-${key}`} disabled={!isAttempting} className="sr-only" />
                        <div className={`shrink-0 w-8 h-8 rounded-full border-2 flex items-center justify-center text-sm font-bold transition-all duration-300 ${isSelected
                           ? "bg-primary border-primary text-primary-foreground shadow-xs scale-110"
                           : "bg-background border-border text-muted-foreground/60 group-hover:border-primary/40"}`}>
                           {op[parseInt(key, 10)]}
                        </div>
                        <span className="flex-1 text-sm leading-relaxed font-medium">{optiontext.toString()}</span>
                     </div>
                  </label>
               );
            })}
         </RadioGroup>
      );
   }

   return (
      <div className={`grid ${isLongOptions ? "grid-cols-1" : "grid-cols-2"} gap-3`}>
         {Object.entries(options).map(([key, value]) => {
            const optiontext = (value as any).optiontext;
            const isSelected = selectedOptions.includes(optiontext);
            const isCorrect = correctOptions.includes(optiontext);
            const handleMultiSelect = (event?: React.MouseEvent) => {
               if (event) {
                  event.preventDefault();
                  event.stopPropagation();
               }
               if (isAttempting && handleOptionClick) {
                  let newSelectedOptions;
                  if (isSelected) {
                     newSelectedOptions = selectedOptions.filter((opt) => opt !== optiontext);
                  } else {
                     newSelectedOptions = [...selectedOptions, optiontext];
                  }
                  handleOptionClick(newSelectedOptions);
               }
            };

            const handleCheckboxChange = (checked: boolean) => {
               if (isAttempting && handleOptionClick) {
                  let newSelectedOptions;
                  if (checked) {
                     newSelectedOptions = [...selectedOptions, optiontext];
                  } else {
                     newSelectedOptions = selectedOptions.filter((opt) => opt !== optiontext);
                  }
                  handleOptionClick(newSelectedOptions);
               }
            };

            return (
               <div
                  key={key}
                  className={`p-3 border rounded-lg cursor-pointer transition-all duration-200 group ${isAttempting
                     ? isSelected
                        ? "bg-primary/10 border-primary text-foreground ring-1 ring-primary/20 shadow-xs"
                        : "bg-background border-border text-foreground hover:bg-muted/50 hover:border-muted-foreground/30"
                     : isSelected
                        ? isCorrect
                           ? "bg-green-100 dark:bg-green-900/30 border-green-500 text-foreground"
                           : "bg-red-100 dark:bg-red-900/30 border-red-500 text-foreground"
                        : isCorrect
                           ? "bg-green-100 dark:bg-green-900/30 border-green-500 text-foreground"
                           : "bg-background border-border text-foreground"
                     }`}
                  onClick={handleMultiSelect}
               >
                  <div className="flex items-center space-x-3">
                     <Checkbox id={`option-${key}`} checked={isSelected} disabled={!isAttempting} onCheckedChange={handleCheckboxChange} className="sr-only" />
                     <div className={`shrink-0 w-8 h-8 rounded-lg border-2 flex items-center justify-center text-sm font-bold transition-all duration-300 ${isSelected
                        ? "bg-primary border-primary text-primary-foreground shadow-xs scale-110"
                        : "bg-background border-border text-muted-foreground/60 group-hover:border-primary/40"}`}>
                        {op[parseInt(key, 10)]}
                     </div>
                     <label htmlFor={`option-${key}`} className={`flex-1 text-sm leading-relaxed font-medium ${isAttempting ? "cursor-pointer" : "cursor-default"}`}>
                        {optiontext.toString()}
                     </label>
                  </div>
               </div>
            );
         })}
      </div>
   );
};

const StaticPaginationSection: React.FC<{
   showSolution: boolean;
   showPagination: boolean;
   questionIds?: (number | { [key: string]: number[] })[];
   questionId?: number;
   handlePageChange?: (id: number) => void;
   size?: number;
   handleClear?: () => void;
   handleClearAll?: () => void;
   localAttempts?: Map<number, string[]>;
   resultCorrectnessData?: Map<number, boolean>;
   isResultWindow?: boolean;
}> = React.memo(
   ({
      showSolution,
      showPagination,
      questionIds,
      questionId,
      handlePageChange,
      size,
      handleClear,
      handleClearAll,
      localAttempts,
      resultCorrectnessData,
      isResultWindow = false,
   }) => {
      return (
         <div className="mt-1 border-t pt-1 pb-2 bg-background">
            <div className={classNames("flex flex-col gap-1", !showSolution ? "items-center" : "", isResultWindow ? "items-center" : "")}>
               <div className={classNames("w-full flex gap-3", isResultWindow ? "justify-center" : "items-center justify-between")}>
                  {showPagination && questionIds && questionId !== undefined && handlePageChange && size && (
                     <div className={isResultWindow ? "" : "flex-1"}>
                        <AnimatedPagination
                           questionIds={questionIds}
                           currentQuestionId={questionId}
                           onPageChange={handlePageChange}
                           windowSize={size || 9}
                           localAttempts={localAttempts}
                           resultCorrectnessData={resultCorrectnessData}
                           isResultWindow={isResultWindow}
                        />
                     </div>
                  )}
                  {handleClear && !isResultWindow && (
                     <button onClick={handleClear} className="shrink-0 px-3 py-1 bg-muted hover:bg-muted/80 text-foreground text-sm font-semibold rounded-md border border-border transition-all duration-200 hover:shadow-xs">
                        Clear
                     </button>
                  )}
                  {handleClearAll && !isResultWindow && (
                     <button onClick={handleClearAll} className="shrink-0 px-3 py-1 bg-muted hover:bg-muted/80 text-foreground text-sm font-semibold rounded-md border border-border transition-all duration-200 hover:shadow-xs">
                        Clear All
                     </button>
                  )}
               </div>
            </div>
         </div>
      );
   }
);

// --- Main Component ---

const QuestionDisplay: React.FC<QuestionProps> = React.memo(
   ({
      type,
      title,
      text,
      options_type,
      options,
      selectedOption,
      correctOption,
      handleOptionClick,
      isLongOptions,
      handleClear,
      handleClearAll,
      handlePageChange,
      questionIds,
      questionId,
      size,
      showPagination = false,
      showSolution = false,
      solution,
      metadata,
      localAttempts,
      resultCorrectnessData,
      isResultWindow = false,
      tags = [],
      parentTags = [],
      hideLabels = false,
      showTitle = true,
      isLoading = false,
   }) => {
      const [isAttempting, setIsAttempting] = useState(true);
      const { stats, isLoading: statsLoading } = useQuestionStats(isResultWindow ? questionId : undefined);
      const { isPro, isLoading: subscriptionLoading } = useSubscription();

      const normalizedType = useMemo(() => {
         const t = type?.toLowerCase().trim() || "";
         const optType = options_type?.toLowerCase().trim() || "";
         // Collect all tag names for fallback detection
         const allTagNames = [...(tags || []), ...(parentTags || [])].map(s => s.toLowerCase());

         // 1. Graphic Interpretation
         if (t === "gi" || t === "graphic interpretation" || t.includes("graphic")) return "GI";

         // 2. Sentence Equivalence - check type, options_type, and tags
         if (t === "se" || t === "sentence equivalence" || t.includes("sentence eq")) return "SE";

         // 3. Reading Comprehension
         if (t === "rc" || t === "reading comprehension") return "RC";

         // 4. Critical Reasoning
         if (t === "cr" || t === "critical reasoning") return "CR";

         // 5. Data Sufficiency
         if (t === "ds" || t === "data sufficiency") return "DS";

         // 6. Table Analysis
         if (t === "ta" || t === "table analysis") return "TA";

         // 7. Multi-Source Reasoning
         if (t === "msr" || t === "multi-source reasoning") return "MSR";

         // 8. Two-Part Analysis
         if (t === "tpa" || t === "two-part analysis") return "TPA";

         // 9. Numeric Entry
         if (t === "ne" || t === "numeric entry" || t === "numerical entry" || t.includes("numeric")) return "NE";

         // 10. Dichotomous (special check for various synonyms)
         const isDichotomous =
            t.includes("dichotomous") ||
            t.includes("binary") ||
            t.includes("yes/no") ||
            t.includes("inference vs conflict") ||
            optType === "dichotomous";

         if (isDichotomous) return "DICHOTOMOUS";

         // Helper: determine TC variant from option count
         const detectTCVariant = () => {
            const optCount = Object.keys(options || {}).length;
            // Also check if options have group values for more accurate detection
            const groups = new Set(
               Object.values(options || {})
                  .map((opt: any) => opt.group)
                  .filter(Boolean)
            );
            if (groups.size > 0) {
               // Group count = number of blanks
               if (groups.size === 1) return "TC-1";
               if (groups.size === 2) return "TC-2";
               return "TC-3";
            }
            // Fallback: infer from option count
            if (optCount <= 5) return "TC-1";
            if (optCount === 6) return "TC-2";
            return "TC-3";
         };

         // 11. Text Completion (TC)
         // Check explicit type OR options_type="blank" (DB often stores "Multiple Choice" for TC)
         if (t === "tc" || t === "text completion" || t.startsWith("tc-") || optType === "blank") {
            if (t.startsWith("tc-")) return t.toUpperCase();
            return detectTCVariant();
         }

         // 12. Tag-based fallback: DB often stores "Multiple Choice" as a generic type,
         // but the actual question type is indicated in the tags.
         if (t === "multiple choice" || t === "mcq" || t === "") {
            // Check tags for Sentence Equivalence
            if (allTagNames.some(tag => tag.includes("sentence equivalence"))) return "SE";
            // Check tags for Text Completion
            if (allTagNames.some(tag => tag.includes("text completion"))) return detectTCVariant();
            // Check tags for Graphic Interpretation
            if (allTagNames.some(tag => tag.includes("graphic interpretation"))) return "GI";
            // Check tags for Reading Comprehension
            if (allTagNames.some(tag => tag.includes("reading comprehension"))) return "RC";
            // Check tags for Critical Reasoning
            if (allTagNames.some(tag => tag.includes("critical reasoning"))) return "CR";
            // Check tags for Data Sufficiency
            if (allTagNames.some(tag => tag.includes("data sufficiency"))) return "DS";
         }

         return type;
      }, [type, options, options_type, tags, parentTags]);

      const computedCorrectOption = useMemo(() => {
         if (correctOption && correctOption.length > 0) return correctOption;

         // Fallback for NE questions if correctOption isn't explicitly provided
         if (normalizedType === "NE" && options) {
            return Object.values(options)
               .filter((opt: any) => opt.iscorrect)
               .map((opt: any) => opt.optiontext);
         }
         return correctOption;
      }, [correctOption, normalizedType, options]);

      useEffect(() => {
         if (solution) setIsAttempting(false);
      }, [solution]);

      const Template = getTemplateComponent(normalizedType);

      const staticLayout = useMemo(() => {
         const isSplitLayout =
            (metadata && "problemsSetId" in metadata) ||
            normalizedType === "RC" ||
            normalizedType === "CR" ||
            normalizedType === "MSR" ||
            normalizedType === "TPA";

         return {
            hasParentChild: !!isSplitLayout,
            widthClass:
               normalizedType === "RC" ||
                  normalizedType === "CR" ||
                  isSplitLayout
                  ? "w-1/3"
                  : "w-full",
         };
      }, [normalizedType, metadata]);

      const questionContent = useMemo(() => {
         if (metadata) {
            if ((normalizedType === "RC" || normalizedType === "CR") && staticLayout.hasParentChild) {
               return (
                  <div>
                     <h3 className="font-medium mb-2"><b>Question:</b></h3>
                     {parseSolutionText(text)}
                  </div>
               );
            } else {
               return (
                  <Template
                     text={text}
                     metadata={metadata}
                     options={options}
                     selectedOption={selectedOption}
                     correctOption={computedCorrectOption}
                     handleOptionClick={handleOptionClick}
                     isLongOptions={isLongOptions}
                     questionDisplayfn={parseSolutionText}
                     handleClear={handleClear}
                     isAttempting={isAttempting}
                  />
               );
            }
         } else {
            return (
               <>
                  <b>Question:</b>
                  {parseSolutionText(text)}
               </>
            );
         }
      }, [normalizedType, text, metadata, options, selectedOption, computedCorrectOption, handleOptionClick, isLongOptions, handleClear, Template, isAttempting]);

      return (
         <div className="grow min-h-0 flex flex-col overflow-hidden">
            <div className="grow min-h-0 flex flex-row bg-background">
               {staticLayout.hasParentChild && (
                  <div className={`w-1/2 grow min-h-0 border-r border-border/40 overflow-y-auto ${isResultWindow ? 'scrollbar-thumb-primary/30' : 'scrollbar-thin scrollbar-thumb-primary/10'} hover:scrollbar-thumb-primary/20 bg-background/50 p-8 lg:p-12 ${isResultWindow ? 'pb-24' : ''}`}>
                     <ParentChildTemplate
                        type={normalizedType}
                        text={text}
                        metadata={metadata}
                     />
                  </div>
               )}
               <div className={`grow min-h-0 overflow-y-auto ${isResultWindow ? "scrollbar-thumb-primary/30" : "scrollbar-thin scrollbar-thumb-primary/10"} hover:scrollbar-thumb-primary/20 ${staticLayout.hasParentChild ? "w-1/2" : "w-full"} p-8 lg:p-12 ${isResultWindow ? "pb-24" : ""}`}>
                  <div className="max-w-3xl mx-auto">
                     {title && !hideLabels && showTitle && (
                        <div className="mb-6">
                           <h1 className="text-2xl md:text-3xl font-black tracking-tight text-foreground/90 leading-tight">
                              {title}
                           </h1>
                           <div className="h-1.5 w-16 bg-primary/20 rounded-full mt-3" />
                        </div>
                     )}

                     <div className="mb-8 min-h-[100px] flex flex-col">
                        {!hideLabels && (
                           <div className="flex items-center gap-2 mb-4">
                              <span className="text-[10px] uppercase font-bold text-primary/60 tracking-[0.2em]">Question</span>
                              <div className="h-px flex-1 bg-primary/5" />
                           </div>
                        )}
                        {isLoading ? (
                           <div className="grow flex items-center justify-center py-12">
                              <Loading message="Fetching question details..." size="md" />
                           </div>
                        ) : (
                           <div className="text-foreground/90 font-medium leading-[1.8] text-[17px] antialiased">
                              {questionContent}
                           </div>
                        )}
                     </div>

                     {!isLoading && (parentTags.length > 0 || tags.length > 0) && (
                        <div className="flex flex-wrap gap-2 px-1 mb-1">
                           {parentTags.map((tag: string, i: number) => (
                              <span
                                 key={`p-${i}`}
                                 className="text-[11px] px-2.5 py-1 bg-primary/20 text-primary rounded-full border border-primary/20 font-bold tracking-tight shadow-xs transition-colors hover:bg-primary/30 cursor-default"
                              >
                                 {tag}
                              </span>
                           ))}
                           {tags.map((tag: string, i: number) => (
                              <span
                                 key={`c-${i}`}
                                 className="text-[11px] px-2.5 py-1 bg-primary/5 text-primary/70 rounded-full border border-primary/10 font-semibold tracking-tight shadow-xs transition-colors hover:bg-primary/10 cursor-default"
                              >
                                 {tag}
                              </span>
                           ))}
                        </div>
                     )}

                     {!isLoading && (
                        <>
                           {(() => {
                              let displayOptions = options;
                              if (normalizedType === "GI" && metadata?.options) {
                                 displayOptions = Array.isArray(metadata.options) && Array.isArray(metadata.options[0])
                                    ? metadata.options[0]
                                    : metadata.options;
                              }

                              if (normalizedType === "DICHOTOMOUS" || options_type?.toLowerCase() === "dichotomous") {
                                 return (
                                    <div className="px-1 shrink-0 pb-1">
                                       <DichotomousTemplate
                                          isAttempting={isAttempting}
                                          options={displayOptions}
                                          selectedOption={selectedOption || []}
                                          correctOption={computedCorrectOption || []}
                                          handleOptionClick={handleOptionClick}
                                       />
                                    </div>
                                 );
                              }

                              return (
                                 <div className="px-1 shrink-0 pb-1 mt-6">
                                    {!hideLabels && (
                                       <div className="flex items-center gap-3 mb-5 px-1">
                                          <div className="h-6 w-1 bg-primary rounded-full" />
                                          <span className="text-[10px] uppercase font-bold text-primary tracking-[0.2em] opacity-80">Selection Options</span>
                                          <div className="h-px flex-1 bg-primary/5" />
                                       </div>
                                    )}
                                    <div className="px-1 shrink-0 pb-1">
                                       <OptionsGrid
                                          type={normalizedType}
                                          options={displayOptions}
                                          isLongOptions={isLongOptions}
                                          isAttempting={isAttempting}
                                          selectedOption={selectedOption}
                                          correctOption={computedCorrectOption}
                                          handleOptionClick={handleOptionClick}
                                          handleClear={handleClear}
                                          op={op}
                                          text={text}
                                          hideLabels={hideLabels}
                                       />
                                    </div>
                                 </div>
                              );
                           })()}
                        </>
                     )}

                     {showSolution && solution && (
                        <>
                           {/* Temporarily removing subscription gate for AI Coach Solutions */}
                           <div className="w-full mt-10 p-6 bg-primary/5 border border-primary/20 rounded-2xl shadow-xs relative overflow-hidden group">
                              <div className="absolute top-0 right-0 w-32 h-32 bg-primary/5 rounded-full -mr-16 -mt-16 blur-3xl group-hover:bg-primary/10 transition-colors duration-500" />
                              <h3 className="text-base font-bold text-primary mb-5 flex items-center gap-3">
                                 <div className="p-2 bg-primary text-primary-foreground rounded-xl shadow-xs">
                                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                       <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0012 18.75c-1.03 0-1.9-.4-2.593-1.003L8.86 17.25zm4.562-7.823L11.31 11.414" />
                                    </svg>
                                 </div>
                                 AI Coach Solution
                              </h3>
                              <div className="space-y-4 text-foreground/90 text-[15px] leading-relaxed relative z-10">
                                 {(() => {
                                    // solution is Json? from Prisma — can be string, object, array, or null
                                    if (typeof solution === 'string') {
                                       if (solution.trim()) return parseSolutionText(solution);
                                    }

                                    if (Array.isArray(solution)) {
                                       const joined = solution
                                          .map((s: any) => typeof s === 'string' ? s : JSON.stringify(s))
                                          .join('\n');
                                       if (joined.trim()) return parseSolutionText(joined);
                                    }

                                    if (solution && typeof solution === 'object') {
                                       // Try common keys in the JSON object
                                       const obj = solution as Record<string, any>;
                                       const textContent =
                                          obj.explanation || obj.solution || obj.text ||
                                          obj.content || obj.answer || obj.steps;

                                       if (typeof textContent === 'string' && textContent.trim()) {
                                          return parseSolutionText(textContent);
                                       }

                                       if (Array.isArray(textContent)) {
                                          const stepsText = textContent
                                             .map((s: any, i: number) => typeof s === 'string' ? `${i + 1}. ${s}` : JSON.stringify(s))
                                             .join('\n');
                                          if (stepsText.trim()) return parseSolutionText(stepsText);
                                       }

                                       // Last resort: stringify the entire object
                                       const allValues = Object.values(obj)
                                          .filter(v => v !== null && v !== undefined)
                                          .map(v => typeof v === 'string' ? v : JSON.stringify(v))
                                          .join('\n\n');
                                       if (allValues.trim()) return parseSolutionText(allValues);
                                    }

                                    return (
                                       <div className="flex items-center gap-2 text-muted-foreground italic py-2">
                                          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                             <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                                          </svg>
                                          No detailed explanation available for this question.
                                       </div>
                                    );
                                 })()}
                              </div>
                           </div>
                        </>
                     )}


                     {isResultWindow && stats && !statsLoading && (
                        <div className="px-6 py-5 mt-10 bg-primary/5 border border-primary/20 rounded-2xl flex items-center justify-between shadow-xs">
                           <div className="flex items-center gap-8">
                              <div className="flex items-center gap-3">
                                 <div className="p-2.5 bg-amber-100 dark:bg-amber-900/40 rounded-xl">
                                    <Target size={18} className="text-amber-600" />
                                 </div>
                                 <div>
                                    <p className="text-[10px] font-bold text-muted-foreground uppercase tracking-widest">Global Avg. Time</p>
                                    <p className="text-[15px] font-black text-foreground">{stats.averageTime}</p>
                                 </div>
                              </div>
                              <div className="w-px h-10 bg-border/60" />
                              <div className="flex items-center gap-3">
                                 <div className="p-2.5 bg-emerald-100 dark:bg-emerald-900/40 rounded-xl">
                                    <Activity size={18} className="text-emerald-600" />
                                 </div>
                                 <div>
                                    <p className="text-[10px] font-bold text-muted-foreground uppercase tracking-widest">Fastest Solve</p>
                                    <p className="text-[15px] font-black text-foreground">{stats.bestTime}</p>
                                 </div>
                              </div>
                           </div>
                           <div className="text-right">
                              <p className="text-[10px] font-bold text-muted-foreground uppercase tracking-widest">Global Solves</p>
                              <p className="text-lg font-black text-primary">{stats.totalSolves}</p>
                           </div>
                        </div>
                     )}
                  </div>
               </div>
            </div >

            <div className="shrink-0 bg-background border-t">
               <StaticPaginationSection
                  showSolution={showSolution}
                  showPagination={showPagination}
                  questionIds={questionIds}
                  questionId={questionId}
                  handlePageChange={handlePageChange}
                  size={size}
                  handleClear={handleClear}
                  handleClearAll={handleClearAll}
                  localAttempts={localAttempts}
                  resultCorrectnessData={resultCorrectnessData}
                  isResultWindow={isResultWindow}
               />
            </div>
         </div >
      );
   }
);

export default QuestionDisplay;
