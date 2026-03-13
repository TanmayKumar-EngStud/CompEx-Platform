"use client";

import { lazy, Suspense } from "react";
import { TagSectionSkeleton } from "../SkeletonLoaders";

const TagSectionComponent = lazy(() => import("@/features/exam-management/components/tag-properties"));

export const LazyTagSection = (props: any) => (
    <Suspense fallback={<TagSectionSkeleton />}>
        <TagSectionComponent {...props} />
    </Suspense>
);

export default LazyTagSection;
