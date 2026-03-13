"use client";

import React, { useEffect, useRef, useState } from "react";
import { createPortal } from "react-dom";
import { motion, AnimatePresence } from "framer-motion";
import { TutorialStep } from "@/shared/configs/tutorial-steps";
import { Button } from "@/shared/components/ui/button";
import { cn } from "@/shared/lib/utils";
import { MousePointerClick } from "lucide-react";

interface TutorialTooltipProps {
    step: TutorialStep;
    currentIndex: number;
    totalSteps: number;
    onNext: () => void;
    onPrev: () => void;
    onSkip: () => void;
    targetRect: DOMRect | null;
    highlightPadding?: number;
}

export const TutorialTooltip: React.FC<TutorialTooltipProps> = ({
    step,
    currentIndex,
    totalSteps,
    onNext,
    onPrev,
    onSkip,
    targetRect,
    highlightPadding = 8,
}) => {
    const tooltipRef = useRef<HTMLDivElement>(null);
    const [position, setPosition] = useState<{ top: number; left: number }>({ top: -9999, left: -9999 });

    // Fixed-corner positions
    const fixedPositionStyle = (): React.CSSProperties | null => {
        if (!step.fixedPosition) return null;
        const margin = 20;
        switch (step.fixedPosition) {
            case "top-left":     return { top: margin, left: margin };
            case "top-right":    return { top: margin, right: margin };
            case "bottom-left":  return { bottom: margin, left: margin };
            // +96 clears the floating chat/action button that sits ~70px from bottom
            case "bottom-right": return { bottom: margin + 96, right: margin };
        }
    };

    useEffect(() => {
        // If using a fixed corner, no need to calculate position from targetRect
        if (step.fixedPosition) return;
        if (!targetRect || !tooltipRef.current) return;

        const tooltip = tooltipRef.current;
        const { width, height } = tooltip.getBoundingClientRect();
        const { top, left, right, bottom, width: tWidth, height: tHeight } = targetRect;
        const windowWidth = window.innerWidth;
        const windowHeight = window.innerHeight;

        const gap = 12;
        const hPad = highlightPadding;
        let pTop = 0;
        let pLeft = 0;

        const checkBounds = (t: number, l: number) => {
            return (
                t >= 12 &&
                l >= 12 &&
                t + height <= windowHeight - 12 &&
                l + width <= windowWidth - 12
            );
        };

        const place = (p: string) => {
            switch (p) {
                case "top":
                    pTop = top - hPad - gap - height;
                    pLeft = left + (tWidth / 2) - (width / 2);
                    break;
                case "bottom":
                    pTop = bottom + hPad + gap;
                    pLeft = left + (tWidth / 2) - (width / 2);
                    break;
                case "left":
                    pTop = top + (tHeight / 2) - (height / 2);
                    pLeft = left - hPad - gap - width;
                    break;
                case "right":
                    pTop = top + (tHeight / 2) - (height / 2);
                    pLeft = right + hPad + gap;
                    break;
            }
        };

        place(step.placement);

        if (!checkBounds(pTop, pLeft)) {
            const fallbackMap: Record<string, string> = {
                "top": "bottom",
                "bottom": "top",
                "left": "right",
                "right": "left"
            };
            place(fallbackMap[step.placement]);

            if (windowWidth < 768) {
                const padding = highlightPadding;
                if (bottom + height + padding > windowHeight) {
                    pTop = top - height - padding;
                } else {
                    pTop = bottom + padding;
                }
                pLeft = (windowWidth - width) / 2;
            }
        }

        // Final clamp
        if (pLeft < 12) pLeft = 12;
        if (pLeft + width > windowWidth - 12) pLeft = windowWidth - width - 12;
        if (pTop < 12) pTop = 12;
        if (pTop + height > windowHeight - 12) pTop = windowHeight - height - 12;

        setPosition({ top: pTop, left: pLeft });

    }, [targetRect, step.placement, step.title, step.description, step.fixedPosition, highlightPadding]);

    // Don't render if no position info and no fixed position
    if (!targetRect && !step.fixedPosition) return null;

    const isLastStep = currentIndex === totalSteps - 1;
    const fixed = fixedPositionStyle();

    const positionStyle: React.CSSProperties = fixed
        ? { ...fixed, position: "fixed" }
        : { top: position.top, left: position.left, position: "fixed" };

    const content = (
        <AnimatePresence>
            <motion.div
                ref={tooltipRef}
                key={`${currentIndex}-${step.title}`}
                initial={{ opacity: 0, y: 10, scale: 0.95 }}
                animate={{ opacity: 1, y: 0, scale: 1 }}
                exit={{ opacity: 0, scale: 0.95 }}
                transition={{ duration: 0.2 }}
                style={positionStyle}
                className="z-[201] bg-card text-card-foreground border border-border rounded-xl shadow-2xl p-5 w-[320px] max-w-[calc(100vw-32px)]"
            >
                <div className="flex items-center justify-between mb-2">
                    <span className="text-xs font-semibold text-primary uppercase tracking-wider">
                        Step {currentIndex + 1} of {totalSteps}
                    </span>
                    <button
                        onClick={onSkip}
                        className="text-xs text-muted-foreground hover:text-foreground transition-colors"
                    >
                        Skip Tour
                    </button>
                </div>

                <h3 className="font-bold text-lg mb-2">{step.title}</h3>
                <p className="text-sm text-muted-foreground mb-4 leading-relaxed">
                    {step.description}
                </p>

                {/* When user must take action, show a visual hint instead of buttons */}
                {step.noNextButton ? (
                    <div className="flex items-center gap-2 text-primary text-xs font-semibold animate-pulse">
                        <MousePointerClick className="w-4 h-4 flex-shrink-0" />
                        <span>Click to continue</span>
                    </div>
                ) : (
                    <div className="flex items-center justify-between mt-auto">
                        <div className="flex gap-1.5 ml-1">
                            {Array.from({ length: totalSteps }).map((_, idx) => (
                                <div
                                    key={idx}
                                    className={cn(
                                        "w-1.5 h-1.5 rounded-full transition-colors",
                                        idx === currentIndex
                                            ? "bg-primary scale-125"
                                            : "bg-muted"
                                    )}
                                />
                            ))}
                        </div>

                        <div className="flex gap-2">
                            {currentIndex > 0 && (
                                <Button
                                    variant="secondary"
                                    size="sm"
                                    onClick={onPrev}
                                >
                                    Prev
                                </Button>
                            )}
                            <Button
                                variant="default"
                                size="sm"
                                onClick={onNext}
                            >
                                {isLastStep ? "Finish" : "Next"}
                            </Button>
                        </div>
                    </div>
                )}
            </motion.div>
        </AnimatePresence>
    );

    if (typeof document === "undefined") return null;
    return createPortal(content, document.body);
};
