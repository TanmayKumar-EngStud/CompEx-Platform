/**
 * Exam Section Panel
 * Force Rebuild
 */
/** Extracted from problems-panel-layout.tsx for better organization and reusability.
 */

"use client";
import React from "react";
import PanelParent from "@/features/exam-management/components/parent-panel";
import { Hflow } from "@/shared/components/layouts/flows";
import { Tag } from "@/features/question-solving/hooks/(definitions)/tagDefinition";
import { useExamSectionLogic } from "@/features/exam-management/hooks/use-exam-section-logic";

export interface ExamSectionPanelProps {
  /** Tag data for problem categories */
  tagData: {
    tagStatus: string;
    tagError: unknown;
    tagData: Tag[] | undefined;
  };
  /** Problem data for the table section */
  problemData: {
    status: string;
    error: unknown;
    data: any;
    previousData: any;
    fullData?: any;
  };
  /** Settings and controls */
  showDifficulty: boolean;
  openQuestion: () => void;
  onShuffle?: (sectionId?: string) => void;
  isShuffling?: boolean;
  /** Content components to render in each tab */
  problemCategoriesComponent: React.ComponentType<{
    tagData: {
      tagStatus: string;
      tagError: unknown;
      tagData: Tag[] | undefined;
    };
  }>;
  problemsTableComponent: React.ComponentType<{
    problemData: {
      status: string;
      error: unknown;
      data: any;
      previousData: any;
      fullData?: any;
    };
    showDifficulty: boolean;
    openQuestion: () => void;
    isShuffling?: boolean;
  }>;
}

/**
 * Main exam section panel component with tab navigation
 * 
 * Renders exam-specific tabs with problem categories and problems table
 * for each section (e.g., Quants, Verbal for GRE).
 */
export const ExamSectionPanel = React.memo(function ExamSectionPanel({
  tagData,
  problemData,
  showDifficulty,
  openQuestion,
  isShuffling = false,
  onShuffle,
  problemCategoriesComponent: ProblemCategoriesComponent,
  problemsTableComponent: ProblemsTableComponent,
}: ExamSectionPanelProps) {
  const { tabProperties } = useExamSectionLogic();

  return (
    <PanelParent titles={tabProperties} onShuffle={onShuffle} isShuffling={isShuffling}>
      {tabProperties.map((_, index) => (
        <ExamSectionTabContent
          key={index}
          tagData={tagData}
          problemData={problemData}
          showDifficulty={showDifficulty}
          openQuestion={openQuestion}
          isShuffling={isShuffling}
          ProblemCategoriesComponent={ProblemCategoriesComponent}
          ProblemsTableComponent={ProblemsTableComponent}
        />
      ))}
    </PanelParent>
  );
});

interface ExamSectionTabContentProps {
  tagData: ExamSectionPanelProps['tagData'];
  problemData: ExamSectionPanelProps['problemData'];
  showDifficulty: boolean;
  openQuestion: () => void;
  isShuffling?: boolean;
  ProblemCategoriesComponent: ExamSectionPanelProps['problemCategoriesComponent'];
  ProblemsTableComponent: ExamSectionPanelProps['problemsTableComponent'];
}

/**
 * Content for each exam section tab
 * 
 * Contains the problem categories section and problems table section
 * for the specific exam section (e.g., Quants tab content).
 */
const ExamSectionTabContent = React.memo(function ExamSectionTabContent({
  tagData,
  problemData,
  showDifficulty,
  openQuestion,
  isShuffling = false,
  ProblemCategoriesComponent,
  ProblemsTableComponent,
}: ExamSectionTabContentProps) {
  return (
    <div>
      <ProblemCategoriesComponent
        tagData={tagData}
      />

      <ProblemsTableComponent
        problemData={problemData}
        showDifficulty={showDifficulty}
        openQuestion={openQuestion}
        isShuffling={isShuffling}
      />
    </div>
  );
});