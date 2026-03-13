"use client";
import React, { useEffect, useState } from "react";
import { usePaginationStore } from "@/shared/stores/problems/pagination";
import uiStrings from "../config/ui-strings.json";

interface ExamSectionTabsProps {
   children: React.ReactNode;
}

export function ExamSectionTabs({ children }: ExamSectionTabsProps) {
   const [tabProperties, setTabProperties] = useState(["quants", "verbal"]);
   const { examName, sectionName, setSectionName } = usePaginationStore();

   useEffect(() => {
      const examSections = uiStrings.examSections as Record<string, string[]>;
      const defaultSections = uiStrings.defaultSections as Record<
         string,
         string
      >;

      if (examName in examSections) {
         const sections = examSections[examName];
         setTabProperties(sections);

         // Set default section if current section is not valid for this exam
         if (!sections.includes(sectionName)) {
            setSectionName(defaultSections[examName]);
         }
      }
   }, [examName, sectionName, setSectionName]);

   return (
      <div>
         {React.Children.map(children, (child, index) => {
            if (index < tabProperties.length) {
               return child;
            }
            return null;
         })}
      </div>
   );
}
