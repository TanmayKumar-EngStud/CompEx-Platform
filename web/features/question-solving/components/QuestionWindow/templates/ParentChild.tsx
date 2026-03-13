import React, { useEffect } from "react";
//calling main templates
import RCTemplate from "./RC";
import MSRTemplate from "./msr";
// specialized rendering engine
import { reDirectGraph } from "./specializedRenderers";
interface ParentChildTemplateProps {
   type: string;
   text: string;
   metadata: any;
}

const ParentChildTemplate: React.FC<ParentChildTemplateProps> = React.memo(({
   type,
   text,
   metadata,
}) => {
   const normalizedGlobalType = type?.toLowerCase();

   if (
      normalizedGlobalType === "rc" ||
      normalizedGlobalType === "reading comprehension" ||
      normalizedGlobalType === "cr" ||
      normalizedGlobalType === "critical reasoning"
   ) {
      return <RCTemplate metadata={metadata} />;
   }
   // Checking if the questions is of Type MSR
   if (
      (type && /msr/i.test(type)) ||
      metadata.content?.sources ||
      Object.keys(metadata).some((k) => /^Source\d+$/i.test(k)) ||
      (metadata.content && Object.keys(metadata.content).some((k) => /^Source\d+$/i.test(k)))
   ) {
      return <MSRTemplate metadata={metadata} />;
   }

   // Extract items from content - handle both array and object structures
   const renderItems = () => {
      // Priority 1: Use explicit content array/object if it exists
      if (metadata.content) {
         if (Array.isArray(metadata.content)) {
            return metadata.content.map((item: any, index: number) => (
               <div key={index}>{reDirectGraph(item?.type, item)}</div>
            ));
         }

         // If content is an object (e.g., {"graph": [...], "table": [...]})
         return Object.entries(metadata.content).map(([key, value]: [string, any], index: number) => {
            if (Array.isArray(value)) {
               // Filter out empty arrays to avoid redundant "Renderer not prepared" or empty charts
               return value.filter(item => item !== null).map((item: any, subIndex: number) => (
                  <div key={`${index}-${subIndex}`}>{reDirectGraph(item?.type || key, item)}</div>
               ));
            }
            if (value) return <div key={index}>{reDirectGraph(value?.type || key, value)}</div>;
            return null;
         });
      }

      // Priority 2: If no 'content' key, look for top-level keys like 'graph', 'table', 'passage'
      // This is common when parent metadata is merged directly into question.metadata
      const topLevelItems: React.ReactNode[] = [];
      const keysToProcess = ["graph", "table", "passage", "Passage", "para"];

      keysToProcess.forEach((key, idx) => {
         const value = metadata[key];
         if (!value) return;

         if (Array.isArray(value)) {
            value.forEach((item, i) => {
               topLevelItems.push(<div key={`${key}-${idx}-${i}`}>{reDirectGraph(item?.type || key, item)}</div>);
            });
         } else {
            // For TPA/singular structure: Inject sibling description if it exists
            // and the child doesn't have its own description
            let itemMetadata = value;
            if (typeof value === 'object' && value !== null && metadata.description && !value.description) {
               itemMetadata = { ...value, description: metadata.description };
            }

            topLevelItems.push(<div key={`${key}-${idx}`}>{reDirectGraph(value?.type || key, itemMetadata)}</div>);
         }
      });

      return topLevelItems.length > 0 ? topLevelItems : null;
   };

   // normal graphical question content:-
   return (
      <div className="flex flex-col gap-6 py-2">
         {metadata.title && (
            <div className="mb-2">
               <h2 className="text-xl font-bold text-foreground/90 tracking-tight">{metadata.title}</h2>
               {metadata.description && <p className="text-sm text-muted-foreground mt-1 leading-relaxed">{metadata.description}</p>}
            </div>
         )}
         <div className="flex flex-col gap-8">
            {renderItems()}
         </div>
      </div>
   );
});

export default ParentChildTemplate;
