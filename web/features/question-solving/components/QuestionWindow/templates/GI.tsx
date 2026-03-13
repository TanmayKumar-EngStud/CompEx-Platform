import React, { useEffect } from "react";
import { reDirectGraph } from "./specializedRenderers";
interface GITemplateProps {
   metadata: any;
}

// Collected shared metadata extraction logic for all GI templates
export const extractGIMetadata = (data: any): { type: string; data: any }[] => {
   if (!data) return [];
   if (Array.isArray(data)) return data.flatMap(extractGIMetadata);

   const results: { type: string; data: any }[] = [];

   // Check wrappers FIRST. If we find valid content in wrappers, we prefer that over treating 'this' as a leaf.
   const wrapperKeys = ["Graph", "graph", "graphs", "Table", "table", "tables", "Passage", "passage", "para", "metadata", "Metadata"];
   let foundRenderableInWrappers = false;

   for (const key of wrapperKeys) {
      if (data[key]) {
         const nested = extractGIMetadata(data[key]);
         if (nested.length > 0) {
            foundRenderableInWrappers = true;
            // Apply implicit type if the child is generic
            const impliedType = key.toLowerCase().includes("graph") ? "graph" :
               (key.toLowerCase().includes("table") ? "table" :
                  (key.toLowerCase().includes("passage") || key === "para" ? "passage" : ""));

            if (impliedType) {
               nested.forEach(r => {
                  if (!r.type || r.type === "generic" || r.type === "graph") r.type = impliedType;
               });
            }
            results.push(...nested);
         }
      }
   }

   if (foundRenderableInWrappers) {
      return results;
   }

   // If NO wrappers found, check if this is a leaf node
   // If this object has a recognized type (other than generic), it's a leaf node
   if (data.type && data.type !== "generic" && data.type !== "graph" && data.type !== "GI") {
      results.push({ type: data.type, data });
      return results;
   }

   // If no valid nested content found, but this object HAS chart structure, it's a chart leaf
   if ((data.structure || data.data_format || data.bars || data.points || data.categories)) {
      results.push({ type: data.type || "graph", data });
   }

   return results;
};

import { useState } from "react";

// ... extractGIMetadata (lines 1-49 remain same, will import useState at top)

const PaginationControls: React.FC<{
   current: number;
   total: number;
   onNext: () => void;
   onPrev: () => void;
}> = ({ current, total, onNext, onPrev }) => {
   console.log("PaginationControls", { current, total });
   // if (total <= 1) return null; // Comment out to debug
   return (
      <div className="flex items-center justify-between mt-4 px-2 py-2 bg-gray-50 border border-gray-100 rounded-lg">
         <button
            onClick={onPrev}
            disabled={current === 0}
            className="px-3 py-1.5 text-xs font-medium text-gray-600 bg-white border border-gray-200 rounded hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
         >
            Previous
         </button>
         <span className="text-xs font-semibold text-gray-500">
            {current + 1} of {total}
         </span>
         <button
            onClick={onNext}
            disabled={current === total - 1}
            className="px-3 py-1.5 text-xs font-medium text-gray-600 bg-white border border-gray-200 rounded hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
         >
            Next
         </button>
      </div>
   );
};

const GITemplate: React.FC<GITemplateProps> = ({ metadata }) => {
   const combinedMetadata = extractGIMetadata(metadata).filter(m => m.data);
   const [currentIndex, setCurrentIndex] = useState(0);

   useEffect(() => {
      setCurrentIndex(0); // Reset on new metadata
   }, [metadata]);

   if (combinedMetadata.length === 0) return null;

   const m = combinedMetadata[currentIndex];
   const mtData = m.type === "table" ? { table: m.data } : (m.type === "passage" ? m.data : { graph: m.data });

   return (
      <div className="flex flex-col gap-6">
         <div className="transition-all duration-300">
            {reDirectGraph(m.type, mtData)}
         </div>
         <PaginationControls
            current={currentIndex}
            total={combinedMetadata.length}
            onNext={() => setCurrentIndex(i => Math.min(i + 1, combinedMetadata.length - 1))}
            onPrev={() => setCurrentIndex(i => Math.max(i - 1, 0))}
         />
      </div>
   );
};

interface GIQuestionProps {
   text: string;
   options: { [key: string]: { optiontext: string } };
   selectedOption: string[];
   correctOption?: string[];
   handleOptionClick?: (option: string | string[]) => void;
   isLongOptions: boolean;
   handleClear?: () => void;
   metadata: any;
   questionDisplayfn: (text: string) => React.JSX.Element[];
}

export const GIQuestion: React.FC<GIQuestionProps> = ({
   text,
   metadata,
   questionDisplayfn
}) => {
   const combinedMetadata = extractGIMetadata(metadata).filter(m => m.data);
   console.log("DEBUG: GIQuestion combinedMetadata", combinedMetadata); // DEBUG
   const [currentIndex, setCurrentIndex] = useState(0);

   useEffect(() => {
      setCurrentIndex(0);
   }, [metadata]);

   const currentItem = combinedMetadata[currentIndex];

   return (
      <div className="flex flex-col gap-6">
         {combinedMetadata.length > 0 && currentItem && (
            <div className="flex flex-col">
               <div className="transition-all duration-300">
                  {reDirectGraph(currentItem.type, currentItem.type === "table" ? { table: currentItem.data } : (currentItem.type === "passage" ? currentItem.data : { graph: currentItem.data }))}
               </div>
               <PaginationControls
                  current={currentIndex}
                  total={combinedMetadata.length}
                  onNext={() => setCurrentIndex(i => Math.min(i + 1, combinedMetadata.length - 1))}
                  onPrev={() => setCurrentIndex(i => Math.max(i - 1, 0))}
               />
            </div>
         )}

         <div className="text-base font-medium leading-relaxed text-foreground/90 bg-primary/[0.02] p-4 rounded-xl border border-primary/5 shadow-inner">
            {questionDisplayfn ? questionDisplayfn(text) : text}
         </div>
      </div>
   );
};

export default GITemplate;
