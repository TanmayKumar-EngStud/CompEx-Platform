import React from "react";

interface RCTemplateProps {
   metadata: {
      problemsSetId?: number;
      content?: any;
      title?: string;
      [key: string]: any;
   };
}

const RCTemplate: React.FunctionComponent<RCTemplateProps> = ({ metadata }) => {
   const getPassages = () => {
      const content = metadata.content || metadata;
      if (!content) return [];

      const rawPassages = content.passages || content.Passage || content.para || content.text || [];
      return Array.isArray(rawPassages) ? rawPassages : [rawPassages];
   };

   const passages = getPassages().filter(p => p !== undefined && p !== null);

   if (passages.length > 0) {
      return (
         <div className="flex flex-col gap-4">
            {metadata.title && <h2 className="text-xl font-bold text-foreground/90">{metadata.title}</h2>}
            <div className="flex flex-col gap-6">
               {passages.map((passage, index) => {
                  const text = typeof passage === "string" ? passage : (passage?.para || passage?.text || "");
                  return (
                     <div
                        key={index}
                        className="font-serif text-[16px] leading-[1.8] text-foreground/90 antialiased selection:bg-primary/20"
                        dangerouslySetInnerHTML={{
                           __html: text,
                        }}
                     />
                  );
               })}
            </div>
         </div>
      );
   } else {
      return <div className="text-muted-foreground italic text-sm p-4">Passage content not found.</div>;
   }
};

export default RCTemplate;
