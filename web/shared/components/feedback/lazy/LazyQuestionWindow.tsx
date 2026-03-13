"use client";

import { lazy, Suspense } from "react";
import { ContentSkeleton } from "../SkeletonLoaders";

const QuestionWindowComponent = lazy(() => import("@/features/question-solving/components/QuestionWindow/questionwindow"));

export const LazyQuestionWindow = (props: any) => (
    <Suspense
        fallback={
            <div className="fixed inset-0 flex items-center justify-center bg-black/50 backdrop-blur-sm z-50">
                <div className="relative bg-background p-6 shadow-xl rounded-lg w-11/12 max-w-5xl h-5/6 select-none overflow-hidden border border-border">
                    <ContentSkeleton rows={8} className="h-full p-4" />
                </div>
            </div>
        }
    >
        <QuestionWindowComponent {...props} />
    </Suspense>
);

export default LazyQuestionWindow;
