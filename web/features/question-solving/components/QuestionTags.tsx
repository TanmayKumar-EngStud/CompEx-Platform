import React from "react";
import { useTheme } from "next-themes";
import { classNames, truncateBrackets } from "@/shared/lib/utils/formatting";

interface QuestionTagsProps {
   tags: string[];
   className?: string;
}

/**
 * Component to display question tags with consistent colors
 * Uses the same color system as the tag filter components for consistency
 */
export const QuestionTags: React.FC<QuestionTagsProps> = ({ tags, className = "" }) => {
   const { resolvedTheme } = useTheme();

   if (!tags || tags.length === 0) {
      return null;
   }

   return (
      <div className={classNames("flex flex-wrap gap-1.5", className)}>
         {tags.map((tagName, index) => (
            <span
               key={`${tagName}-${index}`}
               className="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium transition-all duration-200 border border-border bg-muted/50 text-muted-foreground hover:bg-muted"
            >
               {truncateBrackets(tagName)}
            </span>
         ))}
      </div>
   );
};

export default QuestionTags;