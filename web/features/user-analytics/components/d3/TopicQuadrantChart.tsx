
"use client";

import React, { useEffect, useRef } from 'react';
import * as d3 from 'd3';
import { Target } from 'lucide-react';

interface TopicData {
    tag: string;
    section: string;
    accuracy: number;
    avgTime: number;
    attemptCount: number;
}

interface Props {
    data: TopicData[];
}

export function TopicQuadrantChart({ data }: Props) {
    const svgRef = useRef<SVGSVGElement>(null);

    useEffect(() => {
        if (!svgRef.current || !data || data.length === 0) return;

        // Filter out topics with 0 attempts
        const filteredData = data.filter(d => d.attemptCount > 0);
        if (filteredData.length === 0) return;

        const margin = { top: 40, right: 30, bottom: 50, left: 50 };
        const width = 400 - margin.left - margin.right;
        const height = 300 - margin.top - margin.bottom;

        const svg = d3.select(svgRef.current);
        svg.selectAll("*").remove();

        const g = svg.append("g")
            .attr("transform", `translate(${margin.left},${margin.top})`);

        // Scales
        const xScale = d3.scaleLinear()
            .domain([0, (d3.max(filteredData, d => d.avgTime) || 60) * 1.1])
            .range([0, width]);

        const yScale = d3.scaleLinear()
            .domain([0, 100])
            .range([height, 0]);

        // Quadrant lines (Medians or fixed points)
        const avgAccuracy = 70; // or d3.median(filteredData, d => d.accuracy)
        const avgTime = d3.median(filteredData, d => d.avgTime) || 60;

        // Draw Rects for Quadrants
        const quadrants = [
            { name: "Rush Zone", x: 0, y: 0, w: xScale(avgTime), h: yScale(avgAccuracy), color: "#fef2f2" }, // Top Left (Fast but Inaccurate)
            { name: "Mastery", x: 0, y: 0, w: xScale(avgTime), h: yScale(avgAccuracy), color: "#f0fdf4" }, // Bottom Left? Wait.
        ];

        // Let's just draw lines
        g.append("line")
            .attr("x1", xScale(avgTime)).attr("y1", 0)
            .attr("x2", xScale(avgTime)).attr("y2", height)
            .attr("stroke", "#e2e8f0").attr("stroke-dasharray", "4");

        g.append("line")
            .attr("x1", 0).attr("y1", yScale(avgAccuracy))
            .attr("x2", width).attr("y2", yScale(avgAccuracy))
            .attr("stroke", "#e2e8f0").attr("stroke-dasharray", "4");

        // Labels for Quadrants - Positioned at the bottom of their respective areas to fill white space
        const quadPadding = 8;
        const labels = [
            { text: "MASTERY", x: quadPadding, y: yScale(avgAccuracy) - quadPadding, anchor: "start", color: "#22c55e" },
            { text: "OVER-INVESTED", x: width - quadPadding, y: yScale(avgAccuracy) - quadPadding, anchor: "end", color: "#3b82f6" },
            { text: "RUSHED", x: quadPadding, y: height - quadPadding, anchor: "start", color: "#ef4444" },
            { text: "CRITICAL", x: width - quadPadding, y: height - quadPadding, anchor: "end", color: "#f59e0b" }
        ];

        g.selectAll(".q-label")
            .data(labels)
            .enter()
            .append("text")
            .attr("x", d => d.x)
            .attr("y", d => d.y)
            .attr("text-anchor", d => d.anchor)
            .attr("fill", d => d.color)
            .style("font-size", "12px")
            .style("font-weight", "900")
            .style("letter-spacing", "0.02em")
            .style("opacity", 0.5)
            .style("pointer-events", "none")
            .text(d => d.text);

        // Axes
        g.append("g")
            .attr("transform", `translate(0,${height})`)
            .call(d3.axisBottom(xScale).ticks(5).tickFormat(d => `${d}s`))
            .call(g => g.select(".domain").attr("stroke-opacity", 0.2))
            .selectAll("text")
            .style("font-size", "10px");

        g.append("g")
            .call(d3.axisLeft(yScale).ticks(5).tickFormat(d => `${d}%`))
            .call(g => g.select(".domain").attr("stroke-opacity", 0.2))
            .selectAll("text")
            .style("font-size", "10px");

        // Axis Titles
        g.append("text")
            .attr("x", width / 2)
            .attr("y", height + 35)
            .attr("text-anchor", "middle")
            .style("font-size", "10px")
            .style("font-weight", "bold")
            .style("fill", "hsl(var(--muted-foreground))")
            .style("opacity", 0.8)
            .text("Average Time per Question (Seconds)");

        // Points
        const dots = g.selectAll(".dot")
            .data(filteredData)
            .enter()
            .append("circle")
            .attr("class", d => `dot topic-${d.tag.replace(/\s+/g, '-')}`)
            .attr("cx", d => xScale(d.avgTime))
            .attr("cy", d => yScale(d.accuracy))
            .attr("r", d => Math.sqrt(d.attemptCount) * 2.5 + 4)
            .attr("fill", d => {
                if (d.accuracy >= avgAccuracy && d.avgTime <= avgTime) return "#22c55e"; // Mastery
                if (d.accuracy >= avgAccuracy) return "#3b82f6"; // Over-Invested
                if (d.avgTime <= avgTime) return "#ef4444"; // Rushed
                return "#f59e0b"; // Critical
            })
            .attr("opacity", 0.9)
            .attr("stroke", "white")
            .attr("stroke-width", 2)
            .style("filter", "drop-shadow(0 2px 4px rgba(0,0,0,0.1))")
            .style("cursor", "pointer")
            .on("mouseover", function (event, d) {
                const radius = Math.sqrt(d.attemptCount) * 2.5 + 4;
                d3.select(this)
                    .transition().duration(200)
                    .attr("opacity", 1)
                    .attr("r", radius * 1.3);
            })
            .on("mouseout", function (event, d) {
                const radius = Math.sqrt(d.attemptCount) * 2.5 + 4;
                d3.select(this)
                    .transition().duration(200)
                    .attr("opacity", 0.9)
                    .attr("r", radius);
            });

        dots.append("title")
            .text(d => `${d.tag}\nSection: ${d.section}\nAccuracy: ${d.accuracy}%\nAvg Time: ${d.avgTime || 0}s\nAttempts: ${d.attemptCount}`);

    }, [data]);



    // Calculate distributions for the bottom stats grid
    const analytics = React.useMemo(() => {
        if (!data) return null;
        const filtered = data.filter(d => d.attemptCount > 0);
        const avgTime = d3.median(filtered, d => d.avgTime) || 60;
        const avgAccuracy = 70;

        return {
            masteryCount: filtered.filter(d => d.accuracy >= avgAccuracy && d.avgTime <= avgTime).length,
            overInvestedCount: filtered.filter(d => d.accuracy >= avgAccuracy && d.avgTime > avgTime).length,
            rushedCount: filtered.filter(d => d.accuracy < avgAccuracy && d.avgTime <= avgTime).length,
            criticalCount: filtered.filter(d => d.accuracy < avgAccuracy && d.avgTime > avgTime).length,
            medianTime: Math.round(avgTime)
        };
    }, [data]);

    // Ensure we have enough data (at least 2 points) to draw a meaningful chart
    const hasData = data && data.filter(d => d.attemptCount > 0).length >= 2;

    return (
        <div className="w-full h-full flex flex-col">
            <div className="w-full mb-6">
                <h4 className="text-base font-bold tracking-tight">Efficiency vs. Mastery</h4>
                <p className="text-xs text-muted-foreground">Identifying performance hotspots across all topics.</p>
            </div>

            <div className="relative w-full flex-1 flex items-center justify-center min-h-[300px]">
                {!hasData ? (
                    <div className="flex flex-col items-center justify-center text-center p-8 bg-muted/10 rounded-2xl border-2 border-dashed border-border/50 w-full h-[280px]">
                        <div className="w-16 h-16 rounded-full bg-primary/5 flex items-center justify-center mb-4">
                            <Target className="w-8 h-8 text-primary/40" />
                        </div>
                        <p className="text-sm font-medium text-muted-foreground max-w-[250px]">
                            Need at least 2 active topics to generate quadrant analysis. Solve more problems!
                        </p>
                    </div>
                ) : (
                    <div className="w-full overflow-hidden flex justify-center">
                        <svg ref={svgRef} width={400} height={300} className="max-w-full text-muted-foreground overflow-visible" />
                    </div>
                )}
            </div>

            {hasData && analytics && (
                <div className="mt-6">
                    <div className="grid grid-cols-2 gap-2 mb-4">
                        <div className="bg-green-500/[0.03] border border-green-500/10 rounded-lg p-2.5">
                            <div className="flex items-center justify-between mb-1">
                                <span className="text-[10px] font-bold text-green-600 dark:text-green-400 uppercase tracking-wider">Mastery</span>
                                <span className="text-xs font-black">{analytics.masteryCount}</span>
                            </div>
                            <p className="text-[9px] text-muted-foreground leading-tight">Fast & Accurate topics.</p>
                        </div>
                        <div className="bg-blue-500/[0.03] border border-blue-500/10 rounded-lg p-2.5">
                            <div className="flex items-center justify-between mb-1">
                                <span className="text-[10px] font-bold text-blue-600 dark:text-blue-400 uppercase tracking-wider">Over-Invested</span>
                                <span className="text-xs font-black">{analytics.overInvestedCount}</span>
                            </div>
                            <p className="text-[9px] text-muted-foreground leading-tight">Accurate but slow.</p>
                        </div>
                        <div className="bg-red-500/[0.03] border border-red-500/10 rounded-lg p-2.5">
                            <div className="flex items-center justify-between mb-1">
                                <span className="text-[10px] font-bold text-red-600 dark:text-red-400 uppercase tracking-wider">Rushed</span>
                                <span className="text-xs font-black">{analytics.rushedCount}</span>
                            </div>
                            <p className="text-[9px] text-muted-foreground leading-tight">Fast but error-prone.</p>
                        </div>
                        <div className="bg-amber-500/[0.03] border border-amber-500/10 rounded-lg p-2.5">
                            <div className="flex items-center justify-between mb-1">
                                <span className="text-[10px] font-bold text-amber-600 dark:text-amber-400 uppercase tracking-wider">Critical</span>
                                <span className="text-xs font-black">{analytics.criticalCount}</span>
                            </div>
                            <p className="text-[9px] text-muted-foreground leading-tight">Slow & Inaccurate.</p>
                        </div>
                    </div>

                    <div className="px-2 text-[10px] text-muted-foreground italic flex items-center gap-2">
                        <div className="w-1.5 h-1.5 rounded-full bg-primary/20"></div>
                        Median Speed Benchmark: {analytics.medianTime}s per question.
                    </div>
                </div>
            )}
        </div>
    );
}
