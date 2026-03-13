"use client";

import React, { useEffect, useState, useCallback, useRef } from "react";
import { usePathname, useRouter } from "next/navigation";
import { useTutorialStore } from "@/shared/stores/tutorial-store";
import { tours } from "@/shared/configs/tutorial-steps";
import { TutorialOverlay } from "./TutorialOverlay";
import { TutorialTooltip } from "./TutorialTooltip";

export const TutorialProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
    const pathname = usePathname();
    const router = useRouter();
    const {
        activeTour,
        activeStep,
        isTourRunning,
        nextStep,
        prevStep,
        endTour,
        completePageTour,
        completeGlobalTour
    } = useTutorialStore();

    const [targetRect, setTargetRect] = useState<DOMRect | null>(null);
    // Track previous pathname to detect navigation
    const prevPathnameRef = useRef<string>(pathname);

    const tour = activeTour ? tours[activeTour] : null;
    const step = tour ? tour.steps[activeStep] : null;

    // Helper to find element with retry
    const findElement = useCallback(async (selector: string, timeout = 5000) => {
        const start = Date.now();

        return new Promise<Element | null>((resolve) => {
            const check = () => {
                const el = document.querySelector(selector);
                if (el) {
                    resolve(el);
                    return;
                }
                if (Date.now() - start > timeout) {
                    resolve(null);
                    return;
                }
                requestAnimationFrame(check);
            };
            check();
        });
    }, []);

    // Auto-advance when pathname matches advanceOnNavigate prefix
    useEffect(() => {
        if (!isTourRunning || !step?.advanceOnNavigate) return;
        // Only trigger when pathname actually changed
        if (pathname === prevPathnameRef.current) return;
        prevPathnameRef.current = pathname;

        if (pathname.startsWith(step.advanceOnNavigate)) {
            // Small delay to let the new page render
            const timer = setTimeout(() => nextStep(), 600);
            return () => clearTimeout(timer);
        }
    }, [pathname, isTourRunning, step, nextStep]);

    // Keep prevPathnameRef in sync even when tour isn't running
    useEffect(() => {
        prevPathnameRef.current = pathname;
    }, [pathname]);

    // Auto-advance when advanceOnSelector appears in DOM
    useEffect(() => {
        if (!isTourRunning || !step?.advanceOnSelector) return;

        let stopped = false;
        const selector = step.advanceOnSelector;

        const poll = () => {
            if (stopped) return;
            const el = document.querySelector(selector);
            if (el) {
                // Element found — advance after a short delay so the user can see it
                setTimeout(() => {
                    if (!stopped) nextStep();
                }, 400);
                return;
            }
            setTimeout(poll, 200);
        };

        poll();
        return () => { stopped = true; };
    }, [isTourRunning, activeTour, activeStep, step, nextStep]);

    // Locate target element and update rect
    useEffect(() => {
        if (!isTourRunning || !step) {
            setTargetRect(null);
            return;
        }

        // If this step has noOverlay we still need targetRect for tooltip positioning
        // but skip it for fixed-position tooltips
        if (step.noOverlay && step.fixedPosition) {
            setTargetRect(null);
            return;
        }

        let isMounted = true;
        let cleanupEvents: (() => void) | undefined;

        const locateTarget = async () => {
            setTargetRect(null);

            // Navigate to required route first
            if (step.route && pathname !== step.route) {
                router.push(step.route);
                return;
            }

            // Wait for target element
            const el = await findElement(step.target);

            if (!isMounted) return;

            if (el) {
                el.scrollIntoView({ behavior: 'smooth', block: 'center' });

                const updateRect = () => {
                    if (isMounted) setTargetRect(el.getBoundingClientRect());
                };

                setTimeout(updateRect, 100);
                setTimeout(updateRect, 500);

                window.addEventListener('resize', updateRect);
                window.addEventListener('scroll', updateRect, true);

                cleanupEvents = () => {
                    window.removeEventListener('resize', updateRect);
                    window.removeEventListener('scroll', updateRect, true);
                };
            } else {
                console.warn(`Tutorial target not found: ${step.target}`);
            }
        };

        locateTarget();

        return () => {
            isMounted = false;
            if (cleanupEvents) cleanupEvents();
        };
    }, [isTourRunning, activeTour, activeStep, pathname, step, findElement, router]);

    const handleNext = () => {
        if (!tour) return;
        if (activeStep < tour.steps.length - 1) {
            nextStep();
        } else {
            // Finished
            if (activeTour === "welcome") {
                completeGlobalTour();
            } else if (
                activeTour === "explore" ||
                activeTour === "problems" ||
                activeTour === "mock" ||
                activeTour === "profile"
            ) {
                completePageTour(activeTour);
            }
            endTour();
        }
    };

    const showOverlay = isTourRunning && step && !step.noOverlay && targetRect;
    const showTooltip = isTourRunning && step && (targetRect || step.fixedPosition);

    return (
        <>
            {children}
            {showOverlay && (
                <TutorialOverlay
                    targetRect={targetRect}
                    padding={step.highlightPadding}
                    canInteract={step.canInteract}
                />
            )}
            {showTooltip && (
                <TutorialTooltip
                    step={step}
                    currentIndex={activeStep}
                    totalSteps={tour?.steps.length || 0}
                    onNext={handleNext}
                    onPrev={prevStep}
                    onSkip={endTour}
                    targetRect={targetRect}
                    highlightPadding={step.highlightPadding ?? 8}
                />
            )}
        </>
    );
};
