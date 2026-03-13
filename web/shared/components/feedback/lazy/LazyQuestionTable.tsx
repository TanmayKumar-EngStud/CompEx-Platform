"use client";

import { lazy, Suspense } from "react";
import { QuestionTableSkeleton } from "../SkeletonLoaders";

const QuestionTableComponent = lazy(() => import("@/features/question-solving/components/question-table/question-table"));

export const LazyQuestionTable = (props: any) => (
    <Suspense fallback={<QuestionTableSkeleton />}>
        <QuestionTableComponent {...props} />
    </Suspense>
);

export default LazyQuestionTable;
