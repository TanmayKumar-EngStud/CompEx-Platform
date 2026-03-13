import React, { useState, useEffect } from "react";

interface SETemplateProps {
   isAttempting: boolean;
   options: { [key: string]: { optiontext: string } };
   selectedOptions: string[] | null;
   correctOptions?: string[];
   handleOptionClick?: (option: string[]) => void;
   isLongOptions: boolean;
}

const SETemplate: React.FC<SETemplateProps> = ({
   isAttempting,
   options,
   selectedOptions,
   correctOptions,
   handleOptionClick,
   isLongOptions,
}) => {
   const currentSelections = Array.isArray(selectedOptions) ? selectedOptions : [];
   const isLocked = currentSelections.length >= 2;

   const handleToggle = (optiontext: string) => {
      if (!isAttempting || !handleOptionClick) return;

      const isSelected = currentSelections.includes(optiontext);

      if (isSelected) {
         handleOptionClick(currentSelections.filter(opt => opt !== optiontext));
      } else if (!isLocked) {
         handleOptionClick([...currentSelections, optiontext]);
      }
   };

   const isCorrectOption = (optiontext: string) => {
      return correctOptions?.includes(optiontext);
   };

   return (
      <div className="mt-4 flex flex-col gap-2">
         <div className="text-xs font-bold mb-3 text-primary/60 uppercase tracking-widest flex items-center gap-2">
            <span className="size-1.5 rounded-full bg-primary/40" />
            Select TWO answer choices:
         </div>
         <div className="grid grid-cols-1 gap-3 max-w-2xl">
            {Object.entries(options).map(([key, { optiontext }], index) => {
               const isSelected = currentSelections.includes(optiontext);
               const isCorrect = isCorrectOption(optiontext);
               const op = ["A", "B", "C", "D", "E", "F", "G", "H"];

               return (
                  <div
                     key={key}
                     className={`p-4 border rounded-xl cursor-pointer transition-all duration-200
                        ${isLongOptions ? "text-sm" : "text-base"}
                        ${isAttempting
                           ? isSelected
                              ? "bg-primary/[0.03] border-primary ring-1 ring-primary/10"
                              : isLocked
                                 ? "bg-background border-border/40 opacity-40 cursor-default"
                                 : "bg-background border-border hover:border-primary/40 hover:bg-muted/20"
                           : isSelected
                              ? isCorrect
                                 ? "bg-green-50 dark:bg-green-900/20 border-green-500 text-green-700 dark:text-green-300"
                                 : "bg-red-50 dark:bg-red-900/20 border-red-500 text-red-700 dark:text-red-300"
                              : isCorrect
                                 ? "bg-green-50 dark:bg-green-900/20 border-green-500 text-green-700 dark:text-green-300"
                                 : "bg-background border-border opacity-60"
                        }
                        `}
                     onClick={() => handleToggle(optiontext)}
                  >
                     <div className="flex items-center gap-4">
                        <div className={`size-5 border rounded-md flex items-center justify-center transition-all duration-200 ${isSelected
                           ? "bg-primary border-primary scale-105"
                           : "border-border bg-background"
                           }`}>
                           {isSelected && (
                              <svg className="size-3.5 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={4}>
                                 <path strokeLinecap="round" strokeLinejoin="round" d="M5 13l4 4L19 7" />
                              </svg>
                           )}
                        </div>
                        <span className="flex-1 text-sm sm:text-base font-medium">
                           <span className="text-primary/40 font-bold mr-2">{op[index]}</span> {optiontext}
                        </span>
                     </div>
                  </div>
               );
            })}
         </div>
      </div>
   );
};

export default SETemplate;
