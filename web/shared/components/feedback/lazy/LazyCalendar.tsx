"use client";

import { lazy, Suspense } from "react";
import { CalendarSkeleton } from "@/shared/components/feedback/SkeletonLoaders";

const CalendarComponent = lazy(() => import("@/shared/components/ui/calendar"));

export const LazyCalendar = (props: any) => (
    <Suspense fallback={<CalendarSkeleton />}>
        <CalendarComponent {...props} />
    </Suspense>
);

export default LazyCalendar;
