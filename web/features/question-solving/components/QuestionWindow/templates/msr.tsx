import React, { useState, useMemo } from "react";
import { reDirectGraph } from "./specializedRenderers";

interface MSRTemplateProps {
   metadata: any;
}

const MSRTemplate: React.FC<MSRTemplateProps> = ({ metadata }) => {
   const [activeTabIdx, setActiveTabIdx] = useState(0);

   // Normalize sources from metadata
   const sources = useMemo(() => {
      // Priority 1: Check for explicit source keys (Source1, Source2, etc.)
      let sourceKeys = Object.keys(metadata)
         .filter((key) => /^Source\d+$/i.test(key));

      if (sourceKeys.length > 0) {
         return sourceKeys.sort((a, b) => {
            const numA = parseInt(a.replace(/\D/g, "")) || 0;
            const numB = parseInt(b.replace(/\D/g, "")) || 0;
            return numA - numB;
         }).map((key) => ({
            id: key,
            tabTitle: key.replace(/([a-z])(\d+)/i, "$1 $2"),
            ...metadata[key],
         }));
      }

      // Priority 1.5: Check for SourceX keys inside metadata.content
      if (metadata.content && typeof metadata.content === "object" && !Array.isArray(metadata.content)) {
         sourceKeys = Object.keys(metadata.content)
            .filter((key) => /^Source\d+$/i.test(key));

         if (sourceKeys.length > 0) {
            return sourceKeys.sort((a, b) => {
               const numA = parseInt(a.replace(/\D/g, "")) || 0;
               const numB = parseInt(b.replace(/\D/g, "")) || 0;
               return numA - numB;
            }).map((key) => ({
               id: key,
               tabTitle: key.replace(/([a-z])(\d+)/i, "$1 $2"),
               ...metadata.content[key],
            }));
         }
      }

      // Priority 2: Check for metadata.content.sources array
      if (Array.isArray(metadata.content?.sources)) {
         return metadata.content.sources.map((s: any, idx: number) => ({
            ...s,
            tabTitle: s.title || `Source ${idx + 1}`,
         }));
      }

      return [];
   }, [metadata]);

   if (sources.length === 0) {
      return (
         <div className="p-8 border border-dashed border-border/60 rounded-2xl bg-muted/5 text-center">
            <p className="text-muted-foreground">
               No sources available for this MSR question.
            </p>
         </div>
      );
   }

   const activeSource = sources[activeTabIdx];

   const renderSourceContent = (source: any) => {
      // Robust content extraction: 
      // 1. If source object has a key that matches the source ID (e.g. Source1: {Source1: {...}}), unwrap it.
      let normalizedSource = source;
      if (source.id && source[source.id] && typeof source[source.id] === "object") {
         normalizedSource = { ...source, ...source[source.id] };
      }

      // 2. Extract renderable entries (exclude utility keys)
      const entries = Object.entries(normalizedSource).filter(
         ([key]) => !["id", "tabTitle", "source_info", "title", "content", normalizedSource.id].includes(key)
      );

      // Handle old format nested 'content'
      let finalEntries = [...entries];
      if (normalizedSource.content && typeof normalizedSource.content === "object" && !Array.isArray(normalizedSource.content)) {
         finalEntries = [...finalEntries, ...Object.entries(normalizedSource.content)];
      }

      if (finalEntries.length === 0) return null;

      return finalEntries.map(([key, value], idx) => {
         if (!value) return null;

         // Map common keys to standard types for reDirectGraph
         let type = key;
         const lowKey = key.toLowerCase();
         if (lowKey === "para" || lowKey === "passages" || lowKey === "text" || lowKey === "passage")
            type = "passage";
         if (lowKey === "graph" || lowKey === "chart" || lowKey === "figure") type = "graph";
         if (lowKey === "table" || lowKey === "data_table") type = "table";

         // Special case: if the value is an object and has a recognizable type/structure, use that
         if (typeof value === "object" && !Array.isArray(value)) {
            const val = value as any;
            if (val.type || val.structure || val.graph || val.table || val.para || val.passage) {
               // Let reDirectGraph handle the inner object
               return (
                  <div
                     key={idx}
                     className="animate-in fade-in slide-in-from-bottom-2 duration-500"
                  >
                     {reDirectGraph(val.type || type, val)}
                  </div>
               );
            }
         }

         return (
            <div
               key={idx}
               className="animate-in fade-in slide-in-from-bottom-2 duration-500"
            >
               {reDirectGraph(type, value)}
            </div>
         );
      });
   };

   return (
      <div className="flex flex-col gap-4 w-full h-full">
         <div className="flex flex-col gap-6 py-2">
            <div className="flex flex-col gap-3">
               <div className="flex items-center gap-2">
                  <span className="px-2 py-0.5 rounded bg-primary/10 text-primary text-[10px] font-bold uppercase tracking-wider whitespace-nowrap">
                     MSR Context
                  </span>
                  <div className="h-px flex-grow bg-border/40" />
               </div>
               <h2 className="text-xl font-extrabold text-foreground tracking-tight leading-tight">
                  {metadata.title || "Departmental Analysis"}
               </h2>
               {metadata.description && (
                  <p className="text-sm text-muted-foreground leading-relaxed italic border-l-2 border-primary/20 pl-4">
                     {metadata.description}
                  </p>
               )}
            </div>
         </div>

         {/* Premium Segmented Navigation at the TOP */}
         <div className="flex p-1.5 bg-background/50 backdrop-blur-sm rounded-xl gap-1 w-full shadow-sm border border-border/50 sticky top-0 z-10">
            {sources.map((source: any, idx: number) => (
               <button
                  key={idx}
                  onClick={() => setActiveTabIdx(idx)}
                  className={`flex-1 px-3 py-2 text-sm font-bold rounded-lg transition-all duration-200 ${activeTabIdx === idx
                     ? "bg-primary text-primary-foreground shadow-md scale-[1.02]"
                     : "text-muted-foreground hover:text-foreground hover:bg-muted/50"
                     }`}
               >
                  {source.tabTitle}
               </button>
            ))}
         </div>

         <div className="flex flex-col gap-6 px-1">
            {/* Source Content Area */}
            <div className="flex flex-col gap-6 min-h-[300px]">
               {activeSource.source_info && (
                  <div className="flex items-start gap-3 p-4 bg-primary/[0.03] border-l-4 border-primary/40 rounded-r-xl">
                     <div className="text-xs text-muted-foreground leading-relaxed italic">
                        {activeSource.source_info}
                     </div>
                  </div>
               )}

               <div className="flex flex-col gap-6">
                  {renderSourceContent(activeSource)}
               </div>
            </div>
         </div>
      </div>
   );
};

export default MSRTemplate;
