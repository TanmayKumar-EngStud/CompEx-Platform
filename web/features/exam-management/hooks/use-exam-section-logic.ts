/**
 * Custom hook for exam section logic management
 *
 * Provides a clean interface for components to manage exam section state
 * and operations without directly accessing the service layer.
 */

import { useMemo, useCallback } from "react";
import { usePaginationStore } from "@/shared/stores/problems/pagination";
import { examSectionService } from "../services/exam-section-service";

export interface ExamSectionLogic {
   /** Array of section names for current exam */
   tabProperties: string[];
   /** Current exam name */
   examName: string;
   /** Current section name */
   sectionName: string;
   /** Switch to a different section */
   switchSection: (section: string) => void;
   /** Validate if a section is valid for current exam */
   isValidSection: (section: string) => boolean;
   /** Get default section for current exam */
   getDefaultSection: () => string;
}

/**
 * Hook for managing exam section logic
 *
 * @returns Object containing section state and control functions
 */
export function useExamSectionLogic(): ExamSectionLogic {
   const { examName, sectionName, setSectionName } = usePaginationStore();

   // Memoize tab properties to prevent unnecessary recalculations
   const tabProperties = useMemo(() => {
      return examSectionService.getTabPropertiesForExam(examName);
   }, [examName]);

   // Memoized function to switch sections with validation
   const switchSection = useCallback(
      (section: string) => {
         if (examSectionService.validateSectionForExam(examName, section)) {
            setSectionName(section);
         } else {
            console.warn(`Invalid section "${section}" for exam "${examName}"`);
         }
      },
      [examName, setSectionName]
   );

   // Memoized function to validate sections
   const isValidSection = useCallback(
      (section: string) => {
         return examSectionService.validateSectionForExam(examName, section);
      },
      [examName]
   );

   // Memoized function to get default section
   const getDefaultSection = useCallback(() => {
      return examSectionService.getDefaultSectionForExam(examName);
   }, [examName]);

   return {
      tabProperties,
      examName,
      sectionName,
      switchSection,
      isValidSection,
      getDefaultSection,
   };
}
