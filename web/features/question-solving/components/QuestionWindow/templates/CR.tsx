import React, { useEffect } from "react";

interface CRTemplateProps {
   text: string;
   metadata?: any;
}

const CRTemplate: React.FC<CRTemplateProps> = ({ text, metadata }) => {
   const getPassages = () => {
      if (!metadata) return [];

      const content = metadata.content || metadata;
      const rawPassages = content.passages || content.Passage || content.para || content.text || [];
      return Array.isArray(rawPassages) ? rawPassages : [rawPassages];
   };

   const passages = getPassages().filter(p => p !== undefined && p !== null);

   return (
      <div className="flex flex-col gap-4">
         {passages.length > 0 && (
            <div className="flex flex-col gap-4">
               {passages.map((passage: any, index: number) => {
                  const content = typeof passage === "string" ? passage : (passage?.para || passage?.text || "");
                  return (
                     <p
                        key={index}
                        className="font-serif text-[16px] leading-[1.8] text-foreground/90 antialiased"
                     >
                        {content}
                     </p>
                  );
               })}
            </div>
         )}
         <div className="mt-2">
            <span dangerouslySetInnerHTML={{ __html: text }} />
         </div>
      </div>
   );
};

export default CRTemplate;
