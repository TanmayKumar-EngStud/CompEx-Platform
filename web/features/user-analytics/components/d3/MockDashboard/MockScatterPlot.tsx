
"use client";

import React, { useEffect, useRef } from 'react';
import * as d3 from 'd3';


interface MockData {
    userScore: number;
    difficulty: number;
    mockId: number;
    communityStats?: {
        min: number;
        max: number;
        avg: number;
        q1: number;
        median: number;
        q3: number;
    };
}

interface Props {
    data: MockData[];
}

export function MockScatterPlot({ data }: Props) {
    const svgRef = useRef<SVGSVGElement>(null);

    useEffect(() => {
        if (!svgRef.current || !data || data.length === 0) return;

        const margin = { top: 30, right: 30, bottom: 60, left: 60 };
        const width = 500 - margin.left - margin.right;
        const height = 340 - margin.top - margin.bottom;

        const svg = d3.select(svgRef.current);
        svg.selectAll("*").remove();

        const g = svg.append("g")
            .attr("transform", `translate(${margin.left},${margin.top})`);

        // Aggregating Community Data by Difficulty
        const difficultyLevels = [1, 2, 3, 4, 5];
        const aggregatedData = difficultyLevels.map(level => {
            const levelMocks = data.filter(d => d.difficulty === level);
            if (levelMocks.length === 0) return null;

            return {
                difficulty: level,
                commMin: d3.min(levelMocks, d => d.communityStats?.min ?? 0)!,
                commMax: d3.max(levelMocks, d => d.communityStats?.max ?? 0)!,
                commAvg: d3.mean(levelMocks, d => d.communityStats?.avg ?? 0)!
            };
        }).filter(d => d !== null) as { difficulty: number, commMin: number, commMax: number, commAvg: number }[];

        // Scales
        const xScale = d3.scaleLinear()
            .domain([0.5, 5.5])
            .range([0, width]);

        // Calculate Y scale domain based on both user and community scores
        const allScores: number[] = [];
        data.forEach(d => {
            allScores.push(d.userScore);
            if (d.communityStats) {
                allScores.push(d.communityStats.min, d.communityStats.max);
            }
        });

        const yScale = d3.scaleLinear()
            .domain([Math.max(0, d3.min(allScores)! * 0.8), d3.max(allScores)! * 1.1])
            .range([height, 0]);

        // Colors for difficulty
        const diffColors: Record<number, string> = {
            1: "#3b82f6", 2: "#10b981", 3: "#f59e0b", 4: "#f97316", 5: "#f43f5e"
        };

        // Grid lines
        g.append("g")
            .attr("opacity", 0.03)
            .call(d3.axisLeft(yScale).tickSize(-width).tickFormat(() => ""));

        g.append("g")
            .attr("opacity", 0.03)
            .attr("transform", `translate(0,${height})`)
            .call(d3.axisBottom(xScale).ticks(5).tickSize(-height).tickFormat(() => ""));

        // 1. Draw Community Area (Min-Max)
        if (aggregatedData.length > 1) {
            const areaGenerator = d3.area<{ difficulty: number, commMin: number, commMax: number }>()
                .x(d => xScale(d.difficulty))
                .y0(d => yScale(d.commMin))
                .y1(d => yScale(d.commMax))
                .curve(d3.curveMonotoneX);

            g.append("path")
                .datum(aggregatedData)
                .attr("fill", "hsl(var(--primary))")
                .attr("opacity", 0.08)
                .attr("d", areaGenerator);
        }

        // 2. Draw Community Average Line
        if (aggregatedData.length > 1) {
            const lineGenerator = d3.line<{ difficulty: number, commAvg: number }>()
                .x(d => xScale(d.difficulty))
                .y(d => yScale(d.commAvg))
                .curve(d3.curveMonotoneX);

            g.append("path")
                .datum(aggregatedData)
                .attr("fill", "none")
                .attr("stroke", "hsl(var(--primary))")
                .attr("stroke-width", 1.5)
                .attr("stroke-dasharray", "4,4")
                .attr("opacity", 0.4)
                .attr("d", lineGenerator);
        }

        // Axes
        g.append("g")
            .attr("transform", `translate(0,${height})`)
            .style("font-size", "10px")
            .style("color", "hsl(var(--muted-foreground))")
            .call(d3.axisBottom(xScale).ticks(5).tickFormat(d => `L${d}`));

        g.append("g")
            .style("font-size", "10px")
            .style("color", "hsl(var(--muted-foreground))")
            .call(d3.axisLeft(yScale).ticks(10));

        // Axis Label
        g.append("text")
            .attr("x", width / 2)
            .attr("y", height + 35)
            .attr("text-anchor", "middle")
            .style("font-size", "10px")
            .style("fill", "hsl(var(--muted-foreground))")
            .text("Difficulty Level");

        // Scatter points
        const dots = g.selectAll(".dot")
            .data(data)
            .enter()
            .append("circle")
            .attr("cx", d => xScale(d.difficulty))
            .attr("cy", d => yScale(d.userScore))
            .attr("r", 5)
            .attr("fill", d => diffColors[d.difficulty] || "#94a3b8")
            .attr("stroke", "white")
            .attr("stroke-width", 1.5)
            .attr("filter", "drop-shadow(0px 2px 4px rgba(0,0,0,0.1))")
            .attr("opacity", 1);

        dots.append("title")
            .text(d => `Mock ${d.mockId}\nYour Score: ${d.userScore}\nCommunity Avg: ${Math.round(d.communityStats?.avg ?? 0)}\nDifficulty: L${d.difficulty}`);

    }, [data]);

    return (
        <div className="w-full h-full flex flex-col items-center">
            <div className="self-start mb-4">
                <h4 className="text-sm font-semibold">Difficulty vs Score Stability</h4>
                <p className="text-xs text-muted-foreground mt-1">
                    Analyze how your performance varies across different difficulty levels (L1-L5).
                    Consistent variance indicates stable mastery.
                </p>
            </div>

            <div className="relative w-full overflow-hidden bg-primary/[0.01] rounded-2xl border border-primary/5 p-4 flex flex-col items-center">
                <svg ref={svgRef} width={500} height={340} className="max-w-full" />

                {/* Custom Legend */}
                <div className="flex gap-6 mt-2 pt-4 border-t border-primary/5 w-full justify-center">
                    <div className="flex items-center gap-2">
                        <div className="w-3 h-3 bg-primary/10 border border-primary/20 rounded-sm"></div>
                        <span className="text-[10px] text-muted-foreground">Community Range</span>
                    </div>
                    <div className="flex items-center gap-2">
                        <div className="w-6 h-0 border-t border-dashed border-primary/40"></div>
                        <span className="text-[10px] text-muted-foreground">Community Avg</span>
                    </div>
                    <div className="flex items-center gap-2">
                        <div className="w-2.5 h-2.5 rounded-full bg-emerald-500 shadow-sm"></div>
                        <span className="text-[10px] text-muted-foreground">Your Score</span>
                    </div>
                </div>
            </div>
        </div>
    );
}
