import React, { useEffect, useState } from "react";
import { RadioGroup, RadioGroupItem } from "@/shared/components/ui/radio-group";

interface DichotomousTemplateProps {
    isAttempting: boolean;
    options: { [key: string]: { optiontext: string; group?: string } };
    selectedOption: string[];
    correctOption?: string[];
    handleOptionClick?: (option: string | string[]) => void;
    text?: string;
    [key: string]: any;
}

const DichotomousTemplate: React.FC<DichotomousTemplateProps> = ({
    isAttempting,
    options,
    selectedOption = [],
    correctOption = [],
    handleOptionClick,
    text,
}) => {
    const optionsArray = Object.values(options);

    // Use local state to track "Negative" selections because the parent only stores "Positive" ones.
    // This allows us to visually distinguish between "Unselected" and "Negative" in the UI.
    const [negativeSelections, setNegativeSelections] = useState<Set<string>>(new Set());

    if (optionsArray.length === 0) return null;

    // Extract headers from the options' group property or fallback to metadata
    const groupStr = optionsArray.find(o => o.group)?.group ||
        (optionsArray[0] as any)?.metadata?.group ||
        (options as any)?.metadata?.group ||
        "Positive/Negative";
    const [positiveLabel, negativeLabel] = groupStr.split("/");

    const handleSelection = (optiontext: string, isPositive: boolean) => {
        if (!isAttempting || !handleOptionClick) return;

        let newSelection = [...selectedOption];
        const newNegative = new Set(negativeSelections);

        if (isPositive) {
            if (!newSelection.includes(optiontext)) {
                newSelection.push(optiontext);
            }
            newNegative.delete(optiontext);
        } else {
            // Negative selection: Remove from positive list AND add to negative local state
            newSelection = newSelection.filter((opt) => opt !== optiontext);
            newNegative.add(optiontext);
        }

        setNegativeSelections(newNegative);
        handleOptionClick(newSelection);
    };

    return (
        <div className="space-y-1">
            {/* Render Question Text */}
            {text && (
                <div className="prose dark:prose-invert max-w-none mb-6">
                    <p className="text-foreground/90 leading-relaxed whitespace-pre-wrap">{text}</p>
                </div>
            )}

            <div className="mt-4 border border-border rounded-xl overflow-hidden bg-background shadow-sm">
                <table className="w-full text-sm border-collapse">
                    <thead>
                        <tr className="bg-muted/50 border-b border-slate-300 dark:border-slate-500/50">
                            <th className="px-6 py-3 text-center font-bold text-[10px] uppercase tracking-wider text-muted-foreground w-24 border-r border-slate-300 dark:border-slate-500/50">
                                {positiveLabel || "Positive"}
                            </th>
                            <th className="px-6 py-3 text-center font-bold text-[10px] uppercase tracking-wider text-muted-foreground w-24 border-r border-slate-300 dark:border-slate-500/50">
                                {negativeLabel || "Negative"}
                            </th>
                            <th className="px-6 py-4 text-left font-bold text-[10px] uppercase tracking-wider text-muted-foreground">
                                Options
                            </th>
                        </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-300 dark:divide-slate-500/50">
                        {optionsArray.map((option, index) => {
                            const isSelectedPositive = selectedOption.includes(option.optiontext);
                            const isActuallyCorrect = correctOption.includes(option.optiontext);
                            const isSelectedNegative = negativeSelections.has(option.optiontext);

                            // In non-attempting mode (review), we need to show correctness
                            // isSelectedPositive: user's choice
                            // isActuallyCorrect: true if this row's correct answer is the positive label

                            // Determine if we should show the negative radio as checked
                            // 1. If explicitly selected as negative (isSelectedNegative)
                            // 2. OR if we are in review mode (!isAttempting), checking logic:
                            //    If the user selected negative (not in selectedOption), visually show it checked?
                            //    Strictly speaking, the user's answer state is either Positive or Not Positive.
                            //    We can assume Not Positive = Negative for display in review mode.
                            const showNegativeChecked = isAttempting
                                ? isSelectedNegative
                                : !isSelectedPositive;

                            // Determine background colors for the cells
                            let positiveCellClass = "px-6 py-4 text-center transition-colors duration-200 border-r border-slate-200 dark:border-slate-700/50";
                            let negativeCellClass = "px-6 py-4 text-center transition-colors duration-200 border-r border-slate-200 dark:border-slate-700/50";

                            if (!isAttempting) {
                                // Positive Cell Logic
                                if (isActuallyCorrect) {
                                    // This is the correct answer -> Green
                                    positiveCellClass += " bg-emerald-100/60 dark:bg-emerald-500/10";
                                } else if (isSelectedPositive) {
                                    // User picked this but it's wrong -> Red
                                    positiveCellClass += " bg-rose-100/60 dark:bg-rose-500/10";
                                }

                                // Negative Cell Logic
                                if (!isActuallyCorrect) {
                                    // This is the correct answer -> Green
                                    negativeCellClass += " bg-emerald-100/60 dark:bg-emerald-500/10";
                                } else if (!isSelectedPositive) { // User picked negative (by not picking positive)
                                    // User picked this but it's wrong -> Red
                                    negativeCellClass += " bg-rose-100/60 dark:bg-rose-500/10";
                                }
                            }

                            return (
                                <tr key={index} className="hover:bg-muted/5 transition-colors group">
                                    <td className={positiveCellClass}>
                                        <div className="flex justify-center">
                                            <RadioGroup
                                                value={isSelectedPositive ? "positive" : ""}
                                                onValueChange={() => handleSelection(option.optiontext, true)}
                                                disabled={!isAttempting}
                                            >
                                                <RadioGroupItem
                                                    value="positive"
                                                    id={`positive-${index}`}
                                                    className={`size-5 border-2 transition-all duration-200 ${!isAttempting && isSelectedPositive
                                                        ? isActuallyCorrect
                                                            ? "border-emerald-600 text-emerald-600"
                                                            : "border-rose-600 text-rose-600"
                                                        : "border-primary/40 data-[state=checked]:border-primary data-[state=checked]:bg-primary"
                                                        }`}
                                                />
                                            </RadioGroup>
                                        </div>
                                    </td>
                                    <td className={negativeCellClass}>
                                        <div className="flex justify-center">
                                            <RadioGroup
                                                value={showNegativeChecked ? "negative" : ""}
                                                onValueChange={() => handleSelection(option.optiontext, false)}
                                                disabled={!isAttempting}
                                            >
                                                <RadioGroupItem
                                                    value="negative"
                                                    id={`negative-${index}`}
                                                    className={`size-5 border-2 transition-all duration-200 ${!isAttempting && !isSelectedPositive
                                                        ? !isActuallyCorrect
                                                            ? "border-emerald-600 text-emerald-600"
                                                            : "border-rose-600 text-rose-600"
                                                        : "border-primary/40 data-[state=checked]:border-primary data-[state=checked]:bg-primary"
                                                        }`}
                                                />
                                            </RadioGroup>
                                        </div>
                                    </td>
                                    <td className={`px-6 py-4 text-foreground/90 font-medium leading-relaxed`}>
                                        {option.optiontext}
                                    </td>
                                </tr>
                            );
                        })}
                    </tbody>
                </table>
            </div>
            <div className="mt-[5px] mb-[5px] px-1">
                <p className="text-[11px] text-muted-foreground italic font-medium">
                    Select one answer for each row.
                </p>
            </div>
        </div>
    );
};

export default DichotomousTemplate;
