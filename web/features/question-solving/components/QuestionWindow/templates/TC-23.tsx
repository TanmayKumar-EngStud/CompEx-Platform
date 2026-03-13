import React, { useEffect, useState } from "react";
import { RadioGroup, RadioGroupItem } from "@/shared/components/ui/radio-group";

interface TC23TemplateProps {
   isAttempting: boolean;
   options: { [key: string]: { optiontext: string; group: string } } | any;
   selectedOptions: string[] | null;
   correctOptions?: string[];
   handleOptionClick?: (option: string[]) => void;
   isLongOptions: boolean;
   text?: string;
}

const TC23Template: React.FC<TC23TemplateProps> = ({
   isAttempting,
   options,
   selectedOptions,
   correctOptions,
   handleOptionClick,
   isLongOptions,
   text = "",
}) => {
   // Robust grouping logic for GRE Text Completion and Graphic Interpretation
   const groupedOptionsData = React.useMemo(() => {
      const allOptionsRaw = Object.values(options);
      if (allOptionsRaw.length === 0) return [];

      // 0. Handle already grouped options (common in GI or advanced metadata)
      // Check if the first item is an array or if the options object is actually an array of objects
      if (Array.isArray(options)) {
         return options.map((group: any) => {
            if (Array.isArray(group)) return group;
            if (typeof group === 'object' && group !== null) {
               return Object.entries(group).map(([key, val]) => ({
                  optiontext: typeof val === 'string' ? val : (val as any).optiontext || val,
                  group: key
               }));
            }
            return [group];
         });
      }

      const allOptions = allOptionsRaw;

      // 1. Attempt to group by the 'group' property if it provides meaningful separation
      const uniqueGroups = Array.from(new Set(allOptions.map(opt => (opt as any).group).filter(Boolean)));

      if (uniqueGroups.length > 1) {
         // Sort groups naturally (1, 2, 3...) to ensure correct Blank order
         uniqueGroups.sort((a, b) => String(a).localeCompare(String(b), undefined, { numeric: true }));
         return uniqueGroups.map(g => allOptions.filter((opt: any) => opt.group === g));
      }

      // If we have exactly one distinct group value, this is definitively a single-blank
      // question (TC-1). Skip all option-count fallbacks to avoid showing 2 columns for
      // TC-1 questions that happen to have 6 options (e.g. group="blank 1" with 6 choices).
      if (uniqueGroups.length === 1) {
         return [allOptions];
      }

      // 2. Count blanks in text to determine number of columns
      const blankMatch = text.match(/_{2,}/g);
      const blankCount = blankMatch ? blankMatch.length : 1;

      // 3. Split by detected blank count if uniform distribution is likely
      if (blankCount > 1 && allOptions.length % blankCount === 0) {
         const itemsPerGroup = allOptions.length / blankCount;
         const result = [];
         for (let i = 0; i < blankCount; i++) {
            result.push(allOptions.slice(i * itemsPerGroup, (i + 1) * itemsPerGroup));
         }
         return result;
      }

      // 4. Default GRE-style fallbacks
      if (allOptions.length === 9) {
         return [allOptions.slice(0, 3), allOptions.slice(3, 6), allOptions.slice(6, 9)];
      }
      if (allOptions.length === 6) {
         return [allOptions.slice(0, 3), allOptions.slice(3, 6)];
      }
      if (allOptions.length === 8) {
         return [allOptions.slice(0, 4), allOptions.slice(4, 8)];
      }

      // Default: Single column
      return [allOptions];
   }, [options, text]);

   const [selectedSubOptions, setSelectedSubOptions] = useState<{
      optiontext: string;
      group: string;
      groupIndex: number;
   }[]>([]);

   useEffect(() => {
      if (
         (!selectedOptions || selectedOptions.length === 0) &&
         selectedSubOptions &&
         selectedSubOptions.length > 0
      ) {
         setSelectedSubOptions([]);
      } else {
         if (selectedOptions && groupedOptionsData) {
            let count = 0;
            for (let i = 0; i < selectedSubOptions.length; i++) {
               if (selectedOptions.includes(selectedSubOptions[i].optiontext)) {
                  count++;
               }
            }
            if (count !== selectedOptions.length) {
               let addSelectedOptions: {
                  optiontext: string;
                  group: string;
                  groupIndex: number;
               }[] = [];
               for (let i = 0; i < selectedOptions.length; i++) {
                  for (let j = 0; j < groupedOptionsData.length; j++) {
                     for (let k = 0; k < groupedOptionsData[j].length; k++) {
                        if (
                           selectedOptions[i] ===
                           groupedOptionsData[j][k].optiontext
                        ) {
                           addSelectedOptions.push({
                              optiontext: selectedOptions[i],
                              group: groupedOptionsData[j][k].group,
                              groupIndex: j,
                           });
                           break;
                        }
                     }
                  }
               }
               setSelectedSubOptions(addSelectedOptions);
            }
         }
      }
   }, [selectedOptions, groupedOptionsData]);

   const handleSubOptionClicking = (
      optiontext: string,
      group: string,
      groupIndex: number
   ) => {
      let tempSelectedSubOptions = [...selectedSubOptions];
      let isOptionAdded = false;
      for (let i = 0; i < tempSelectedSubOptions.length; i++) {
         if (tempSelectedSubOptions[i].groupIndex === groupIndex) {
            tempSelectedSubOptions[i].group = group;
            tempSelectedSubOptions[i].optiontext = optiontext;
            isOptionAdded = true;
            break;
         }
      }
      if (!isOptionAdded) {
         tempSelectedSubOptions.push({
            optiontext,
            group,
            groupIndex,
         });
      }
      setSelectedSubOptions(tempSelectedSubOptions);
      if (handleOptionClick) {
         const selectionArray = tempSelectedSubOptions.map((opt) => opt.optiontext);
         handleOptionClick(selectionArray);
      }
   };

   function checkIfSelected(optiontext: string) {
      if (selectedOptions && Array.isArray(selectedOptions)) {
         return selectedOptions.includes(optiontext);
      } else {
         return false;
      }
   }

   function isCorrectOption(optiontext: string) {
      return correctOptions?.includes(optiontext);
   }

   // Option labels for A-I format
   const op = ["A", "B", "C", "D", "E", "F", "G", "H", "I"];

   return (
      <div className={`grid mt-6 bg-background ${
            groupedOptionsData.length === 3 ? "grid-cols-3 gap-6" :
            groupedOptionsData.length === 2 ? "grid-cols-2 gap-8" :
            "grid-cols-1 gap-4 max-w-md"
         }`}>
         {groupedOptionsData &&
            groupedOptionsData.map((columnOptions, groupIndex) => {
               const selectedOpt = selectedSubOptions?.find(opt => opt.groupIndex === groupIndex);
               const currentGroupSelection = selectedOpt ? `${groupIndex}::${selectedOpt.optiontext}` : "";

               const handleRadioChange = (value: string) => {
                  if (isAttempting) {
                     const actualText = value.includes('::') ? value.split('::').slice(1).join('::') : value;

                     if (currentGroupSelection === value) {
                        const newSubOptions = selectedSubOptions.filter(
                           opt => opt.groupIndex !== groupIndex
                        );
                        setSelectedSubOptions(newSubOptions);
                        if (handleOptionClick) {
                           handleOptionClick(newSubOptions.map(opt => opt.optiontext));
                        }
                     } else {
                        const groupData = columnOptions.find(
                           item => item.optiontext === actualText
                        );
                        if (groupData) {
                           handleSubOptionClicking(actualText, groupData.group, groupIndex);
                        }
                     }
                  }
               };

               return (
                  <div key={groupIndex} className="flex flex-col rounded-xl bg-muted/30 overflow-hidden">
                     <div className="px-4 py-3 font-semibold text-xs text-center uppercase tracking-widest text-muted-foreground/70">
                        Blank {groupIndex + 1}
                     </div>
                     <div className="px-2 pb-3 flex-grow">
                        <RadioGroup
                           value={currentGroupSelection}
                           onValueChange={handleRadioChange}
                           disabled={!isAttempting}
                           className="flex flex-col gap-0.5"
                        >
                           {columnOptions.map(
                              ({ optiontext, group }, index) => {
                                 const isSelected = currentGroupSelection === `${groupIndex}::${optiontext}`;
                                 const isCorrect = isCorrectOption(optiontext);

                                 // Continuous labelling calculation
                                 let labelIndex = index;
                                 for (let i = 0; i < groupIndex; i++) {
                                    labelIndex += groupedOptionsData[i].length;
                                 }

                                 const handleSingleClick = (event: React.MouseEvent) => {
                                    if (isAttempting) {
                                       if (isSelected) {
                                          event.preventDefault();
                                          const newSubOptions = selectedSubOptions.filter(
                                             opt => opt.groupIndex !== groupIndex
                                          );
                                          setSelectedSubOptions(newSubOptions);
                                          if (handleOptionClick) {
                                             handleOptionClick(newSubOptions.map(opt => opt.optiontext));
                                          }
                                       }
                                    }
                                 };

                                 return (
                                    <label
                                       key={index}
                                       htmlFor={`tc23-option-${groupIndex}-${index}`}
                                       className={`px-3 py-2.5 cursor-pointer transition-all duration-200 block rounded-lg mx-1 mb-1 ${isAttempting
                                          ? isSelected
                                             ? "bg-primary/10 text-primary font-medium ring-1 ring-primary/30"
                                             : "hover:bg-muted/60"
                                          : isSelected
                                             ? isCorrect
                                                ? "bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-300"
                                                : "bg-red-100 dark:bg-red-900/30 text-red-700 dark:text-red-300"
                                             : isCorrect
                                                ? "bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-300"
                                                : ""
                                          }`}
                                       onClick={handleSingleClick}
                                    >
                                       <div className="flex items-center space-x-3">
                                          <RadioGroupItem
                                             value={`${groupIndex}::${optiontext}`}
                                             id={`tc23-option-${groupIndex}-${index}`}
                                             disabled={!isAttempting}
                                             className="size-4"
                                          />
                                          <span className="flex-1 text-sm">
                                             <span className="font-bold mr-1">({op[labelIndex]})</span>
                                             {optiontext}
                                          </span>
                                       </div>
                                    </label>
                                 );
                              }
                           )}
                        </RadioGroup>
                     </div>
                  </div>
               );
            })}
      </div>
   );
};

export default TC23Template;
