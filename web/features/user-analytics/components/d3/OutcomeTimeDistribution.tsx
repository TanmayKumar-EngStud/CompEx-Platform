"use client";

import React, { useEffect, useRef } from 'react';
import * as d3 from 'd3';
import { Clock, CheckCircle2, XCircle } from 'lucide-react';

interface TimeMetrics {
    min: number;
    max: number;
    avg: number;
}

interface TimeAnalysisData {
    user: {
        correct: TimeMetrics;
        incorrect: TimeMetrics;
    };
    community: {
        correct: TimeMetrics;
        incorrect: TimeMetrics;
    };
    correctCount: number;
    incorrectCount: number;
}

interface Props {
    data?: TimeAnalysisData;
}

export function OutcomeTimeDistribution({ data }: Props) {
    const svgRef = useRef<SVGSVGElement>(null);

    const hasData = data && (data.correctCount > 0 || data.incorrectCount > 0);

    useEffect(() => {
        if (!svgRef.current || !hasData || !data) return;

        const margin = { top: 40, right: 30, bottom: 50, left: 50 };
        const width = 450 - margin.left - margin.right;
        const height = 300 - margin.top - margin.bottom;

        const svg = d3.select(svgRef.current);
        svg.selectAll("*").remove();

        const g = svg.append("g")
            .attr("transform", `translate(${margin.left},${margin.top})`);

        // Prepare Data for Grouped Bars
        const groups = ['Correct', 'Incorrect'];
        const subGroups = ['User', 'Community'];

        // Helper to ensure stats object is never null
        const safeStats = (stats: any) => stats || { min: 0, max: 0, avg: 0 };

        const chartData = [
            {
                group: 'Correct',
                User: safeStats(data.user?.correct),
                Community: safeStats(data.community?.correct),
                color: '#22c55e'
            },
            {
                group: 'Incorrect',
                User: safeStats(data.user?.incorrect),
                Community: safeStats(data.community?.incorrect),
                color: '#ef4444'
            }
        ];

        // Scales
        const x0 = d3.scaleBand()
            .domain(groups)
            .rangeRound([0, width])
            .paddingInner(0.2);

        const x1 = d3.scaleBand()
            .domain(subGroups)
            .rangeRound([0, x0.bandwidth()])
            .padding(0.1);

        const maxVal = d3.max([
            data.user.correct.max || 0, data.user.incorrect.max || 0,
            data.community.correct.max || 0, data.community.incorrect.max || 0
        ]) || 60;

        const y = d3.scaleLinear()
            .domain([0, maxVal * 1.1])
            .range([height, 0]);

        // Draw Axes
        g.append("g")
            .attr("transform", `translate(0,${height})`)
            .call(d3.axisBottom(x0).tickSize(0))
            .call(g => g.select(".domain").attr("stroke-opacity", 0.2))
            .selectAll("text")
            .style("font-weight", "600")
            .style("font-size", "12px")
            .attr("dy", "1em");

        g.append("g")
            .call(d3.axisLeft(y).ticks(5).tickFormat(d => `${d}s`))
            .call(g => g.select(".domain").remove())
            .call(g => g.selectAll(".tick line").attr("x2", width).attr("stroke-opacity", 0.05));

        // Draw Groups
        const groupG = g.selectAll(".group")
            .data(chartData)
            .enter()
            .append("g")
            .attr("transform", d => `translate(${x0(d.group)},0)`);

        // Draw Bars and Whiskers
        subGroups.forEach((sub) => {
            // WHISKER: Min to Max line
            groupG.append("line")
                .attr("x1", d => x1(sub)! + x1.bandwidth() / 2)
                .attr("x2", d => x1(sub)! + x1.bandwidth() / 2)
                .attr("y1", d => y((d as any)[sub].min))
                .attr("y2", d => y((d as any)[sub].max))
                .attr("stroke", "hsl(var(--foreground))")
                .attr("stroke-width", 1)
                .attr("stroke-dasharray", "2,2")
                .attr("opacity", 0.4);

            // Min cap
            groupG.append("line")
                .attr("x1", d => x1(sub)! + x1.bandwidth() * 0.3)
                .attr("x2", d => x1(sub)! + x1.bandwidth() * 0.7)
                .attr("y1", d => y((d as any)[sub].min))
                .attr("y2", d => y((d as any)[sub].min))
                .attr("stroke", "hsl(var(--foreground))")
                .attr("opacity", 0.4);

            // Max cap
            groupG.append("line")
                .attr("x1", d => x1(sub)! + x1.bandwidth() * 0.3)
                .attr("x2", d => x1(sub)! + x1.bandwidth() * 0.7)
                .attr("y1", d => y((d as any)[sub].max))
                .attr("y2", d => y((d as any)[sub].max))
                .attr("stroke", "hsl(var(--foreground))")
                .attr("opacity", 0.4);

            // BAR: Height is Average
            groupG.append("rect")
                .attr("x", d => x1(sub)!)
                .attr("y", d => y((d as any)[sub].avg))
                .attr("width", x1.bandwidth())
                .attr("height", d => height - y((d as any)[sub].avg))
                .attr("fill", d => sub === 'User' ? d.color : '#94a3b8')
                .attr("rx", 4)
                .attr("opacity", sub === 'User' ? 0.9 : 0.6);

            // Value label for Average
            groupG.append("text")
                .attr("x", d => x1(sub)! + x1.bandwidth() / 2)
                .attr("y", d => y((d as any)[sub].avg) - 5)
                .attr("text-anchor", "middle")
                .style("font-size", "10px")
                .style("font-weight", "700")
                .style("fill", (d: any) => sub === 'User' ? (d as any).color : 'currentColor')
                .text((d: any) => `${(d as any)[sub].avg}s`);
        });

        // Legend
        const legend = g.append("g")
            .attr("transform", `translate(${width - 100}, -25)`);

        legend.append("rect").attr("width", 10).attr("height", 10).attr("fill", "#64748b").attr("rx", 2);
        legend.append("text").attr("x", 15).attr("y", 9).text("Community").style("font-size", "10px").attr("fill", "muted-foreground");

        legend.append("rect").attr("y", 15).attr("width", 10).attr("height", 10).attr("fill", "#22c55e").attr("rx", 2);
        legend.append("text").attr("x", 15).attr("y", 24).text("Your Average").style("font-size", "10px").attr("fill", "muted-foreground");

    }, [data, hasData]);

    return (
        <div className="w-full h-full flex flex-col">
            <div className="mb-2">
                <h4 className="text-base font-bold tracking-tight flex items-center gap-2">
                    <Clock className="w-4 h-4 text-muted-foreground" />
                    Time vs. Outcome
                </h4>
                <p className="text-xs text-muted-foreground">
                    Compare your speed metrics against the community benchmark.
                </p>
            </div>

            <div className="flex-1 flex items-center justify-center min-h-[300px]">
                {!hasData || !data ? (
                    <div className="text-center text-muted-foreground text-sm">
                        No attempt data available.
                    </div>
                ) : (
                    <div className="w-full flex justify-center">
                        <svg ref={svgRef} width={450} height={300} className="overflow-visible" />
                    </div>
                )}
            </div>

            {hasData && data && (
                <div className="mt-4 space-y-3">
                    <div className="grid grid-cols-2 gap-3">
                        {/* Correct Section */}
                        <div className="bg-green-500/5 border border-green-500/10 rounded-lg p-3">
                            <div className="flex items-center gap-1.5 text-green-700 dark:text-green-400 font-bold text-sm mb-2">
                                <CheckCircle2 className="w-4 h-4" /> Correct
                            </div>
                            <div className="grid grid-cols-2 gap-4 text-[10px]">
                                <div>
                                    <p className="text-muted-foreground uppercase tracking-wider font-bold mb-1">Your Stats</p>
                                    <p>Avg: <span className="font-bold text-green-600 dark:text-green-400">{data.user.correct.avg}s</span></p>
                                    <p className="text-muted-foreground">Range: {data.user.correct.min}s - {data.user.correct.max}s</p>
                                </div>
                                <div>
                                    <p className="text-muted-foreground uppercase tracking-wider font-bold mb-1">Community</p>
                                    <p>Avg: <span className="font-bold">{data.community.correct.avg}s</span></p>
                                    <p className="text-muted-foreground">Range: {data.community.correct.min}s - {data.community.correct.max}s</p>
                                </div>
                            </div>
                        </div>

                        {/* Incorrect Section */}
                        <div className="bg-red-500/5 border border-red-500/10 rounded-lg p-3">
                            <div className="flex items-center gap-1.5 text-red-700 dark:text-red-400 font-bold text-sm mb-2">
                                <XCircle className="w-4 h-4" /> Incorrect
                            </div>
                            <div className="grid grid-cols-2 gap-4 text-[10px]">
                                <div>
                                    <p className="text-muted-foreground uppercase tracking-wider font-bold mb-1">Your Stats</p>
                                    <p>Avg: <span className="font-bold text-red-600 dark:text-green-400">{data.user.incorrect.avg}s</span></p>
                                    <p className="text-muted-foreground">Range: {data.user.incorrect.min}s - {data.user.incorrect.max}s</p>
                                </div>
                                <div>
                                    <p className="text-muted-foreground uppercase tracking-wider font-bold mb-1">Community</p>
                                    <p>Avg: <span className="font-bold">{data.community.incorrect.avg}s</span></p>
                                    <p className="text-muted-foreground">Range: {data.community.incorrect.min}s - {data.community.incorrect.max}s</p>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
}

