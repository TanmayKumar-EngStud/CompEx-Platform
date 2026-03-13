"use client";

import React, { useEffect, useRef, useState } from "react";
import { motion } from "framer-motion";

interface TutorialOverlayProps {
    targetRect: DOMRect | null;
    padding?: number;
    canInteract?: boolean;
}

export const TutorialOverlay: React.FC<TutorialOverlayProps> = ({
    targetRect,
    padding = 8,
    canInteract = false
}) => {
    const [windowSize, setWindowSize] = useState({ width: 0, height: 0 });
    // Ref to the full-screen SVG rect so we can temporarily disable its
    // pointer-events during elementFromPoint hit-testing.
    const svgRectRef = useRef<SVGRectElement>(null);

    useEffect(() => {
        const updateSize = () => {
            setWindowSize({
                width: window.innerWidth,
                height: window.innerHeight
            });
        };

        updateSize();
        window.addEventListener("resize", updateSize);
        return () => window.removeEventListener("resize", updateSize);
    }, []);

    if (!targetRect) return null;

    const pad = padding;
    const x = targetRect.left - pad;
    const y = targetRect.top - pad;
    const w = targetRect.width + (pad * 2);
    const h = targetRect.height + (pad * 2);

    return (
        <div className="fixed inset-0 z-[200] pointer-events-none">
            {/* SVG Mask Overlay */}
            <svg className="w-full h-full">
                <defs>
                    <mask id="tutorial-mask">
                        <rect x="0" y="0" width="100%" height="100%" fill="white" />
                        <motion.rect
                            initial={false}
                            animate={{ x, y, width: w, height: h }}
                            transition={{ type: "spring", stiffness: 300, damping: 30 }}
                            fill="black"
                            rx="8"
                        />
                    </mask>
                </defs>
                <rect
                    ref={svgRectRef}
                    x="0"
                    y="0"
                    width="100%"
                    height="100%"
                    fill="rgba(0,0,0,0.65)"
                    mask="url(#tutorial-mask)"
                    className="pointer-events-auto"
                />
            </svg>

            {/* Glow ring around the target */}
            <motion.div
                initial={false}
                animate={{
                    left: x,
                    top: y,
                    width: w,
                    height: h
                }}
                transition={{ type: "spring", stiffness: 300, damping: 30 }}
                className="absolute border-2 border-primary rounded-lg pointer-events-none"
                style={{
                    boxShadow: canInteract
                        ? "0 0 0 4px rgba(var(--primary-rgb), 0.2), 0 0 20px rgba(var(--primary-rgb), 0.4)"
                        : "0 0 15px rgba(var(--primary-rgb), 0.3)"
                }}
            />

            {/* Pulsing ring — only shown when user must click something */}
            {canInteract && (
                <motion.div
                    initial={false}
                    animate={{
                        left: x,
                        top: y,
                        width: w,
                        height: h
                    }}
                    transition={{ type: "spring", stiffness: 300, damping: 30 }}
                    className="absolute rounded-lg pointer-events-none"
                >
                    {/* Outer pulse ring */}
                    <motion.div
                        className="absolute inset-0 rounded-lg border-2 border-primary"
                        animate={{
                            scale: [1, 1.04, 1],
                            opacity: [0.8, 0.2, 0.8],
                        }}
                        transition={{
                            duration: 1.8,
                            repeat: Infinity,
                            ease: "easeInOut",
                        }}
                    />
                </motion.div>
            )}

            {/* Click-through area when canInteract — temporarily hides itself to dispatch real click */}
            {canInteract && (
                <motion.div
                    initial={false}
                    animate={{
                        left: x,
                        top: y,
                        width: w,
                        height: h
                    }}
                    transition={{ type: "spring", stiffness: 300, damping: 30 }}
                    className="absolute rounded-lg pointer-events-auto cursor-pointer"
                    onClick={(e) => {
                        const overlay = e.currentTarget as HTMLElement;
                        const svgRect = svgRectRef.current;

                        // Disable pointer-events on BOTH this div AND the full-screen
                        // SVG rect.  Without disabling the SVG rect, elementFromPoint
                        // returns it (it sits at the same z-level and covers the whole
                        // screen) instead of the actual page element underneath.
                        overlay.style.pointerEvents = "none";
                        if (svgRect) svgRect.style.pointerEvents = "none";

                        const realEl = document.elementFromPoint(e.clientX, e.clientY);

                        // Restore immediately after the synchronous hit-test.
                        overlay.style.pointerEvents = "";
                        if (svgRect) svgRect.style.pointerEvents = "";

                        if (!realEl || realEl === overlay) return;

                        // Use dispatchEvent instead of .click() because the
                        // underlying element might be an SVG node (e.g. a
                        // <polygon> from the polygonal card background) which
                        // does not expose a .click() method.  A bubbling
                        // MouseEvent is picked up by React's synthetic event
                        // system and will reach the nearest ancestor that has
                        // an onClick handler (e.g. the <tr> row or the card div).
                        realEl.dispatchEvent(
                            new MouseEvent("click", {
                                bubbles: true,
                                cancelable: true,
                                clientX: e.clientX,
                                clientY: e.clientY,
                            })
                        );
                    }}
                />
            )}
        </div>
    );
};
