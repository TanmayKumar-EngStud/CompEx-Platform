"use client";
import React, { useState } from "react";
import { Hflow } from "@/shared/components/layouts/flows";
import { Tag } from "@/features/question-solving/hooks/(definitions)/tagDefinition";
// import { ProblemCategoriesSection } from "./problem-categories-section"; // Removed from main flow
import { ProblemsTableSection } from "./problems-table-section";
// import { PreferenceSettingsPanel } from "./preference-settings-panel"; // Moved to sidebar
import { ExamSectionPanel } from "@/features/exam-management/components/exam-section-panel";
// import { ProblemPageControls } from "./problem-page-controls"; // Not used in this layout update?
import { ProblemsSidebar } from "./problems-sidebar";

interface ProblemsPanelLayoutProps {
  tagData: {
    tagStatus: string;
    tagError: unknown;
    tagData: Tag[] | undefined;
  };
  problemData: {
    status: string;
    error: unknown;
    data: any;
    previousData: any;
    fullData?: any;
  };
  bookmarksEnabled: boolean;
  setBookmarksEnabled: (enabled: boolean) => void;
  showTimer: boolean;
  setShowTimer: React.Dispatch<React.SetStateAction<boolean>>;
  showDifficulty: boolean;
  setShowDifficulty: React.Dispatch<React.SetStateAction<boolean>>;
  questionTagsEnabled: boolean;
  setQuestionTagsEnabled: (enabled: boolean) => void;
  openQuestion: () => void;
  // calendar: React.ReactNode; // Removed
  onShuffle: (sectionId?: string) => void;
  isShuffling?: boolean;
}

const NullComponent = () => null;

export const ProblemsPanelLayout = React.memo(function ProblemsPanelLayout({
  tagData,
  problemData,
  bookmarksEnabled,
  setBookmarksEnabled,
  showTimer,
  setShowTimer,
  showDifficulty,
  setShowDifficulty,
  questionTagsEnabled,
  setQuestionTagsEnabled,
  openQuestion,
  // calendar, // Removed
  onShuffle,
  isShuffling = false,
}: ProblemsPanelLayoutProps) {
  const [isSidebarOpen, setIsSidebarOpen] = useState(true);

  return (
    <div className="flex w-full h-full">
      {/* Main Content Area */}
      <div className="flex-1 flex flex-col min-w-0 pr-4"> {/* Added pr-4 for spacing */}
        <ExamSectionPanel
          tagData={tagData}
          problemData={problemData}
          showDifficulty={showDifficulty}
          openQuestion={openQuestion}
          isShuffling={isShuffling}
          onShuffle={onShuffle}
          problemCategoriesComponent={NullComponent} // Hide categories in main area
          problemsTableComponent={ProblemsTableSection}
        />
      </div>

      {/* Right Sidebar (Navigation Window) */}
      <ProblemsSidebar
        isOpen={isSidebarOpen}
        setIsOpen={setIsSidebarOpen}
        tagData={tagData.tagData || []}
        bookmarksEnabled={bookmarksEnabled}
        setBookmarksEnabled={setBookmarksEnabled}
        showTimer={showTimer}
        setShowTimer={setShowTimer}
        showDifficulty={showDifficulty}
        setShowDifficulty={setShowDifficulty}
        questionTagsEnabled={questionTagsEnabled}
        setQuestionTagsEnabled={setQuestionTagsEnabled}
        onShuffle={onShuffle}
      />
    </div>
  );
});