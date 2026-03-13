
import React from "react";
import { Input } from "@/shared/components/ui/input";

interface NETemplateProps {
    isAttempting: boolean;
    optionSelected: string;
    handleSetAnswer?: (answer: string[]) => void;
    correctAnswer?: string[];
    handleClear?: () => void;
}

const NETemplate: React.FC<NETemplateProps> = ({
    isAttempting,
    optionSelected,
    handleSetAnswer,
    correctAnswer,
    handleClear
}) => {
    const isCorrect = correctAnswer?.includes(optionSelected);

    return (
        <div className="mt-8 flex flex-col gap-4 max-w-sm">
            <div className="text-xs font-bold text-primary/60 uppercase tracking-widest flex items-center gap-2">
                <span className="size-1.5 rounded-full bg-primary/40" />
                Enter your answer:
            </div>

            <div className="relative group">
                <Input
                    type="text"
                    disabled={!isAttempting}
                    value={optionSelected}
                    onChange={(e) => handleSetAnswer?.([e.target.value])}
                    className={`h-14 text-lg font-mono border-2 transition-all duration-200 
                        ${isAttempting
                            ? "bg-background border-border hover:border-primary/40 focus:border-primary"
                            : isCorrect
                                ? "bg-green-50 dark:bg-green-900/20 border-green-500 text-green-700 dark:text-green-300 disabled:opacity-100"
                                : "bg-red-50 dark:bg-red-900/20 border-red-500 text-red-700 dark:text-red-300 disabled:opacity-100"
                        }`}
                    placeholder="Type value..."
                />
                {!isAttempting && !isCorrect && correctAnswer && (
                    <div className="mt-2 text-sm font-medium text-green-600 dark:text-green-400 flex items-center gap-2">
                        <span className="text-xs uppercase font-bold text-primary/40">Correct Answer:</span>
                        {correctAnswer.join(", ")}
                    </div>
                )}
            </div>

            {isAttempting && handleClear && optionSelected && (
                <button
                    onClick={handleClear}
                    className="text-xs font-bold text-muted-foreground hover:text-foreground transition-colors w-fit underline decoration-dashed underline-offset-4"
                >
                    Clear answer
                </button>
            )}
        </div>
    );
};

export default NETemplate;
