/**
 * Service for managing exam section business logic
 * 
 * Provides centralized logic for exam type section management including:
 * - Section validation and switching
 * - Default section selection
 * - Exam section configuration lookup
 */

import uiStrings from "@/app/dashboard/problems/config/ui-strings.json";

export interface ExamSectionConfig {
  examSections: Record<string, string[]>;
  defaultSections: Record<string, string>;
}

/**
 * Service for exam section business logic operations
 */
export const examSectionService = {
  /**
   * Get tab properties (sections) for a specific exam type
   * 
   * @param examName - The name of the exam (e.g., "GRE", "GMAT", "CAT")
   * @returns Array of section names for the exam
   */
  getTabPropertiesForExam: (examName: string): string[] => {
    const examSections = uiStrings.examSections as Record<string, string[]>;
    return examSections[examName] || ["quants", "verbal"];
  },

  /**
   * Get the default section for a specific exam type
   * 
   * @param examName - The name of the exam (e.g., "GRE", "GMAT", "CAT")
   * @returns Default section name for the exam
   */
  getDefaultSectionForExam: (examName: string): string => {
    const defaultSections = uiStrings.defaultSections as Record<string, string>;
    return defaultSections[examName] || "quants";
  },

  /**
   * Validate if a section is valid for a specific exam type
   * 
   * @param examName - The name of the exam
   * @param section - The section to validate
   * @returns True if the section is valid for the exam
   */
  validateSectionForExam: (examName: string, section: string): boolean => {
    const tabProperties = examSectionService.getTabPropertiesForExam(examName);
    return tabProperties.includes(section);
  },

  /**
   * Get all available exam types
   * 
   * @returns Array of exam type names
   */
  getAvailableExamTypes: (): string[] => {
    const examSections = uiStrings.examSections as Record<string, string[]>;
    return Object.keys(examSections);
  },

  /**
   * Get complete exam section configuration
   * 
   * @returns Complete configuration object with sections and defaults
   */
  getExamSectionConfig: (): ExamSectionConfig => {
    return {
      examSections: uiStrings.examSections as Record<string, string[]>,
      defaultSections: uiStrings.defaultSections as Record<string, string>
    };
  }
};