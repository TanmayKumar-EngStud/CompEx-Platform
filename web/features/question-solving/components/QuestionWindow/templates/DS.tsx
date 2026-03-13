// filepath: /Users/tanmaykumar/Desktop/compex/compex/app/ui/problems/questionfloatingwindow/Templates/DS.tsx
import React, { useEffect } from "react";

interface DSTemplateProps {
   text: string;
   metadata?: {
      passage?: string;
      statements?: string[];
   };
   questionDisplayfn: (text: string) => React.JSX.Element[];
}

const DSTemplate: React.FC<DSTemplateProps> = ({
   text,
   metadata,
   questionDisplayfn,
}) => {
   // Extremely robust extraction logic searching for passage/statements at multiple levels
   const extractData = () => {
      if (!metadata) return { passage: null, statements: [] };

      // Helper to check for fields in an object
      const findIn = (obj: any) => {
         if (!obj || typeof obj !== 'object') return null;
         const p = obj.passage || obj.para || obj.text || obj.Passage || obj.Para;
         const s = obj.statements || obj.Statements || obj.statement || obj.Statement;
         return (p || (s && Array.isArray(s))) ? { passage: p, statements: Array.isArray(s) ? s : (s ? [s] : []) } : null;
      };

      const meta = metadata as any;
      // Try different common nesting levels
      const searchPaths = [
         meta,
         meta.content,
         meta.metadata,
         Array.isArray(meta.metadata) ? meta.metadata[0] : null,
         meta.data,
      ];

      for (const path of searchPaths) {
         if (!path) continue;
         const found = findIn(path);
         if (found && (found.passage || found.statements.length > 0)) return found;
      }

      // Final fallback: if nothing else found, just check if metadata itself has the fields
      return {
         passage: meta.passage || meta.para,
         statements: meta.statements || []
      };
   };

   const { passage, statements } = extractData();

   return (
      <div className="flex flex-col w-full animate-in fade-in duration-500 max-w-4xl mx-auto space-y-1">
         {/* Context/Passage - Ultra Compact Integrated Style */}
         {passage && (
            <div className="pb-1 border-b border-border/10">
               <div className="text-[9px] font-bold text-primary/50 uppercase tracking-widest leading-none mb-0.5">Context</div>
               <div className="text-[14px] leading-tight text-foreground/80 italic font-medium">
                  {questionDisplayfn(passage)}
               </div>
            </div>
         )}

         {/* Question Stem */}
         <div className="text-[16px] font-bold text-foreground leading-snug py-0.5">
            {questionDisplayfn(text)}
         </div>

         {/* Statements Section - Ultra Direct Pure Style */}
         {statements.length > 0 && (
            <div className="flex flex-col gap-0.5 py-0.5">
               {statements.map((statement: string, idx: number) => (
                  <div
                     key={idx}
                     className="flex items-start gap-2"
                  >
                     <span className="text-[14px] text-primary/70 min-w-[90px] shrink-0 font-medium">
                        Statement ({idx + 1}):
                     </span>
                     <div className="text-[14px] leading-normal text-foreground/90 pt-0">
                        {questionDisplayfn(statement)}
                     </div>
                  </div>
               ))}
            </div>
         )}
      </div>
   );
};

export default DSTemplate;
