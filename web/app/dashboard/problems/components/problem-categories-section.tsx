"use client";
import React from "react";
import { LazyTagSection as Section } from "@/shared/components/feedback/lazy/LazyTagSection";
import SmartDataLoader from "@/shared/components/feedback/SmartDataLoader";
import { TagSectionSkeleton } from "@/shared/components/feedback/SkeletonLoaders";
import { Tag } from "@/features/question-solving/hooks/(definitions)/tagDefinition";
import { usePaginationStore } from "@/shared/stores/problems/pagination";
import { useUIStore } from "@/shared/stores/problems/ui-state";
import uiStrings from "../config/ui-strings.json";

interface ProblemCategoriesSectionProps {
  tagData: {
    tagStatus: string;
    tagError: unknown;
    tagData: Tag[] | undefined;
  };
}

export function ProblemCategoriesSection({
  tagData,
}: ProblemCategoriesSectionProps) {
  const { sectionName } = usePaginationStore();
  const { displaySolvedQuestions, setDisplaySolvedQuestions: setDisplaySolvedQuestionsStore } = useUIStore();

  // Create a React-compatible setter function
  const setDisplaySolvedQuestions = React.useCallback((value: React.SetStateAction<boolean>) => {
    if (typeof value === 'function') {
      setDisplaySolvedQuestionsStore(value(displaySolvedQuestions));
    } else {
      setDisplaySolvedQuestionsStore(value);
    }
  }, [displaySolvedQuestions, setDisplaySolvedQuestionsStore]);

  return (
    <div className="flex flex-col gap-[5px]">
      <h1 className="text-2xl tracking-tight mb-4">
        {uiStrings.headers.problemCategories}
      </h1>

      <SmartDataLoader
        status={tagData.tagStatus as any}
        data={tagData.tagData}
        error={tagData.tagError}
        loader={<TagSectionSkeleton />}
        loadingMessage={uiStrings.messages.loadingCategories}
        emptyComponent={
          <div className="text-center py-8 text-muted-foreground">
            {uiStrings.messages.noCategoriesAvailable}
          </div>
        }
        className="min-h-[120px]"
        suppressLoadingWhenDataExists={true}
        dataKey={`tags-${sectionName}-${tagData.tagStatus}`}
      >
        {(data) => (
          <Section
            tagData={data}
            displaySolvedQuestions={displaySolvedQuestions}
            setDisplaySolvedQuestions={setDisplaySolvedQuestions}
          />
        )}
      </SmartDataLoader>
    </div>
  );
}