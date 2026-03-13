
"use client";

import React, { useEffect, useRef, useState } from 'react';
import * as d3 from 'd3';
import { clsx } from 'clsx';

interface DifficultyStat {
    difficulty: number;
    totalAttempts: number;
    correctAttempts: number;
    totalQuestionsInLevel: number;
}

interface TestTubeDonutProps {
    data: DifficultyStat[];
}

const colorMap: Record<number, string> = {
    1: "#3b82f6", // Blue
    2: "#10b981", // Emerald
    3: "#f59e0b", // Amber
    4: "#f97316", // Orange
    5: "#f43f5e", // Rose
};

const bgMap: Record<number, string> = {
    1: "bg-blue-500/10 text-blue-600 border-blue-200/50",
    2: "bg-emerald-500/10 text-emerald-600 border-emerald-200/50",
    3: "bg-amber-500/10 text-amber-600 border-amber-200/50",
    4: "bg-orange-500/10 text-orange-600 border-orange-200/50",
    5: "bg-rose-500/10 text-rose-600 border-rose-200/50",
};

export const TestTubeDonut: React.FC<TestTubeDonutProps> = ({ data }) => {
    const svgRef = useRef<SVGSVGElement>(null);
    const containerRef = useRef<HTMLDivElement>(null);
    const [containerWidth, setContainerWidth] = useState(300);

    const sortedData = useMemo(() => {
        return [1, 2, 3, 4, 5].map(lvl => {
            const found = data.find(d => d.difficulty === lvl);
            return found || { difficulty: lvl, totalAttempts: 0, correctAttempts: 0, totalQuestionsInLevel: 0 };
        });
    }, [data]);

    const totalQuestions = sortedData.reduce((acc, curr) => acc + curr.totalQuestionsInLevel, 0);
    const totalSolved = sortedData.reduce((acc, curr) => acc + curr.correctAttempts, 0);
    const totalAttempts = sortedData.reduce((acc, curr) => acc + curr.totalAttempts, 0);
    const overallAccuracy = totalAttempts > 0 ? (totalSolved / totalAttempts) * 100 : 0;

    useEffect(() => {
        if (containerRef.current) {
            const observer = new ResizeObserver((entries) => {
                if (entries[0]) setContainerWidth(entries[0].contentRect.width);
            });
            observer.observe(containerRef.current);
            return () => observer.disconnect();
        }
    }, []);

    const [isHovered, setIsHovered] = useState(false);

    useEffect(() => {
        if (!svgRef.current || !sortedData) return;

        const svg = d3.select(svgRef.current);
        svg.selectAll("*").remove();

        const width = 150;
        const height = 150;
        const radius = Math.min(width, height) / 2;
        const thickness = 6;
        const innerRadius = radius * 0.75;
        const outerRadius = innerRadius + thickness;

        const g = svg.append("g")
            .attr("transform", `translate(${width / 2},${height / 2})`);

        // Arc range: -130 to 130 degrees (open bottom)
        const startAngle = -Math.PI * 0.72;
        const endAngle = Math.PI * 0.72;
        const totalSpan = endAngle - startAngle;

        const totalQInBank = sortedData.reduce((acc, curr) => acc + curr.totalQuestionsInLevel, 1);

        // Calculate cumulative angles for segments
        let currentAngle = startAngle;

        sortedData.forEach((d) => {
            const segmentSpan = (d.totalQuestionsInLevel / totalQInBank) * totalSpan;
            const segmentEnd = currentAngle + segmentSpan;

            // Background segment
            const bgArc = d3.arc<any>()
                .innerRadius(innerRadius)
                .outerRadius(outerRadius)
                .startAngle(currentAngle)
                .endAngle(segmentEnd)
                .cornerRadius(4);

            g.append("path")
                .attr("d", bgArc(null))
                .attr("fill", colorMap[d.difficulty])
                .attr("opacity", 0.15);

            // Progress segment (Correct Attempts)
            if (d.correctAttempts > 0) {
                const progressSpan = (d.correctAttempts / d.totalQuestionsInLevel) * segmentSpan;
                const progressArc = d3.arc<any>()
                    .innerRadius(innerRadius)
                    .outerRadius(outerRadius)
                    .startAngle(currentAngle)
                    .endAngle(currentAngle + progressSpan)
                    .cornerRadius(4);

                g.append("path")
                    .attr("d", progressArc(null))
                    .attr("fill", colorMap[d.difficulty])
                    .attr("class", "transition-all duration-300");
            }

            // Small indicator dots at segment starts
            const dotAngle = currentAngle;
            const dotX = (innerRadius + thickness / 2) * Math.sin(dotAngle);
            const dotY = -(innerRadius + thickness / 2) * Math.cos(dotAngle);

            g.append("circle")
                .attr("cx", dotX)
                .attr("cy", dotY)
                .attr("r", 2.5)
                .attr("fill", colorMap[d.difficulty]);

            currentAngle = segmentEnd;
        });

        // Add a final dot at the very end
        const lastX = (innerRadius + thickness / 2) * Math.sin(endAngle);
        const lastY = -(innerRadius + thickness / 2) * Math.cos(endAngle);
        g.append("circle")
            .attr("cx", lastX)
            .attr("cy", lastY)
            .attr("r", 2.5)
            .attr("fill", colorMap[5]);

        // Center Area
        const center = g.append("g").attr("text-anchor", "middle");

        // Center text is handled by HTML overlay

        // Bottom footer text in the arc gap
        const footer = g.append("g")
            .attr("transform", `translate(0, ${innerRadius + 15})`)
            .attr("text-anchor", "middle");

        footer.append("text")
            .style("font-size", "10px")
            .style("font-weight", "600")
            .style("fill", "#94a3b8")
            .text(isHovered ? `${totalAttempts} Total Attempts` : `${totalAttempts - totalSolved} Incorrect`);

    }, [sortedData, containerWidth, isHovered, totalSolved, totalQuestions, overallAccuracy, totalAttempts]);

    return (
        <div
            ref={containerRef}
            className="w-full flex flex-col items-center cursor-default transition-all duration-300"
        >
            <div
                className="relative mb-2 flex items-center justify-center cursor-pointer"
                onMouseEnter={() => setIsHovered(true)}
                onMouseLeave={() => setIsHovered(false)}
            >
                <svg ref={svgRef} width={150} height={150}></svg>
                <div className="absolute inset-0 flex flex-col items-center justify-center pointer-events-none select-none">
                    <span className="text-4xl font-bold tracking-tighter tabular-nums text-foreground flex items-baseline">
                        {isHovered ? (
                            <>
                                {overallAccuracy % 1 === 0 ? overallAccuracy : overallAccuracy.toFixed(1)}
                                <span className="text-sm ml-1 font-semibold text-muted-foreground">%</span>
                            </>
                        ) : (
                            <>
                                {totalSolved}
                                <span className="text-sm ml-1 font-semibold text-muted-foreground">/{totalQuestions}</span>
                            </>
                        )}
                    </span>
                    <span className="text-xs font-bold text-muted-foreground uppercase tracking-widest mt-1">
                        {isHovered ? 'Accuracy' : (
                            <span className="flex items-center gap-1">
                                <span className="text-emerald-500">✓</span> Solved
                            </span>
                        )}
                    </span>
                </div>
            </div>

            <div className="w-fit space-y-0.5 px-4">
                {sortedData.map((d) => {
                    const incorrect = d.totalAttempts - d.correctAttempts;
                    return (
                        <div key={d.difficulty} className="flex items-center gap-6 group py-0.5">
                            <div className="flex items-center gap-4">
                                <div className={clsx(
                                    "w-6 h-6 flex items-center justify-center rounded-full border text-xs font-bold transition-all shadow-sm",
                                    bgMap[d.difficulty]
                                )}>
                                    {d.difficulty}
                                </div>
                                <div className="flex items-center font-mono text-sm tracking-tight w-[140px]">
                                    <span className="text-muted-foreground mr-1">[</span>
                                    <span
                                        className={clsx(
                                            "font-bold cursor-help",
                                            d.correctAttempts > 0 ? "text-green-500" : "text-gray-400"
                                        )}
                                        title="No. of correct attempts"
                                    >
                                        +{d.correctAttempts}
                                    </span>

                                    <span
                                        className={clsx(
                                            "font-bold ml-1.5 cursor-help",
                                            incorrect > 0 ? "text-red-500" : "text-gray-400"
                                        )}
                                        title="No. of incorrect attempts"
                                    >
                                        -{incorrect}
                                    </span>
                                    <span className="text-muted-foreground ml-1">]</span>
                                    <span
                                        className="font-bold ml-1"
                                        style={{ color: colorMap[d.difficulty] }}
                                    >
                                        /{d.totalQuestionsInLevel}
                                    </span>
                                </div>
                            </div>
                            <div className="text-[10px] font-bold text-muted-foreground bg-muted px-1.5 py-0.5 rounded">
                                {Math.round((d.totalAttempts / d.totalQuestionsInLevel) * 100 || 0)}%
                            </div>
                        </div>
                    );
                })}
            </div>
        </div>
    );
};

// Add missing useMemo import
import { useMemo } from 'react';
