"use client";

import { lazy, Suspense } from "react";
import { ContentSkeleton } from "../SkeletonLoaders";

const ResultWindowComponent = lazy(() => import("@/features/user-analytics/components/result-window/resultWindow"));

export const LazyResultWindow = (props: any) => {
    const isFullPage = props.isFullPage;
    return (
        <Suspense
            fallback={
                isFullPage ? (
                    <div className="h-screen w-screen bg-background p-8 flex flex-col items-center">
                        <div className="w-full max-w-5xl space-y-8 animate-pulse">
                            <div className="h-10 bg-muted rounded-xl w-1/3 mx-auto" />
                            <div className="grid grid-cols-4 gap-4">
                                {[1, 2, 3, 4].map(i => <div key={i} className="h-32 bg-muted rounded-2xl" />)}
                            </div>
                            <div className="h-96 bg-muted rounded-2xl w-full" />
                        </div>
                    </div>
                ) : (
                    <div className="fixed inset-0 flex items-center justify-center bg-black/50 backdrop-blur-sm z-50">
                        <div className="relative bg-background p-6 shadow-xl rounded-lg w-11/12 max-w-5xl h-5/6 select-none overflow-hidden border border-border">
                            <ContentSkeleton rows={8} className="h-full p-4" />
                        </div>
                    </div>
                )
            }
        >
            <ResultWindowComponent {...props} />
        </Suspense>
    );
};

// Export preloader for ResultWindow to avoid blinks on submit
export const preloadResultWindow = () => {
    import("@/features/user-analytics/components/result-window/resultWindow").catch(console.error);
};

export default LazyResultWindow;
