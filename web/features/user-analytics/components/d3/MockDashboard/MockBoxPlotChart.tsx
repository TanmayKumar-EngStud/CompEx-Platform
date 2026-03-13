
"use client";

import React, { useEffect, useRef } from 'react';
import * as d3 from 'd3';

interface MockData {
    mockId: number;
    date: string;
    userScore: number;
    difficulty: number;
    rank: number;
    totalParticipants: number;
    percentile: number;
    communityStats: {
        min: number;
        max: number;
        q1: number;
        median: number;
        q3: number;
    };
}

interface Props {
    data: MockData[];
}

export function MockBoxPlotChart({ data }: Props) {
    const svgRef = useRef<SVGSVGElement>(null);

    useEffect(() => {
        if (!svgRef.current || !data || data.length === 0) return;

        const margin = { top: 30, right: 30, bottom: 40, left: 50 };
        const width = 450 - margin.left - margin.right;
        const height = 320 - margin.top - margin.bottom;

        const svg = d3.select(svgRef.current);
        svg.selectAll("*").remove();

        const g = svg.append("g")
            .attr("transform", `translate(${margin.left},${margin.top})`);

        // Scales
        const xScale = d3.scalePoint()
            .domain(data.map((_, i) => i.toString()))
            .range([0, width])
            .padding(0.5);

        const allScores = data.flatMap(d => {
            if (!d.communityStats) return [d.userScore];
            return [d.communityStats.min, d.communityStats.max, d.userScore];
        });
        const yScale = d3.scaleLinear()
            .domain([d3.min(allScores)! * 0.95, d3.max(allScores)! * 1.05])
            .range([height, 0]);

        // Add Grid Lines
        // Horizontal Grid
        g.append("g")
            .attr("class", "grid")
            .attr("opacity", 0.05)
            .call(d3.axisLeft(yScale).tickSize(-width).tickFormat(() => ""));

        // Vertical Grid
        g.append("g")
            .attr("class", "grid")
            .attr("opacity", 0.05)
            .attr("transform", `translate(0,${height})`)
            .call(d3.axisBottom(xScale).tickSize(-height).tickFormat(() => ""));

        // Colors for difficulty
        const diffColors: Record<number, string> = {
            1: "#3b82f6", // blue-500
            2: "#10b981", // emerald-500
            3: "#f59e0b", // amber-500
            4: "#f97316", // orange-500
            5: "#f43f5e"  // rose-500
        };

        // Axes
        const xAxis = g.append("g")
            .attr("transform", `translate(0,${height})`)
            .call(d3.axisBottom(xScale).tickFormat((_, i) => `M${data[i].mockId}`));

        xAxis.selectAll("text")
            .attr("transform", "rotate(-30)")
            .style("text-anchor", "end")
            .style("font-size", "9px");

        // X-axis label
        xAxis.append("text")
            .attr("x", width / 2)
            .attr("y", 35)
            .attr("fill", "currentColor")
            .style("font-size", "10px")
            .style("font-weight", "600")
            .text("Mocks");

        const yAxis = g.append("g")
            .call(d3.axisLeft(yScale).ticks(5));

        // Y-axis label
        yAxis.append("text")
            .attr("transform", "rotate(-90)")
            .attr("y", -35)
            .attr("x", -height / 2)
            .attr("fill", "currentColor")
            .attr("text-anchor", "middle")
            .style("font-size", "10px")
            .style("font-weight", "600")
            .text("Score");

        // Arrowhead definition
        svg.append("defs").append("marker")
            .attr("id", "arrowhead")
            .attr("viewBox", "0 -5 10 10")
            .attr("refX", 8)
            .attr("refY", 0)
            .attr("markerWidth", 5)
            .attr("markerHeight", 5)
            .attr("orient", "auto")
            .append("path")
            .attr("d", "M0,-5L10,0L0,5")
            .attr("fill", "currentColor");

        // Draw Box Plots (Candlesticks) - High Visibility Design
        data.forEach((d, i) => {
            const x = xScale(i.toString())!;
            const stats = d.communityStats || { min: 0, max: 0, q1: 0, median: 0, q3: 0 };

            // If no participants, skip community metrics
            if (stats.max === 0 && stats.min === 0) return;

            // Trend logic for coloring (User score progression)
            const isDown = i > 0 && d.userScore < data[i - 1].userScore;
            const trendColor = isDown ? "#ef4444" : "#22c55e";
            const commColor = "hsl(var(--muted-foreground))";

            // 1. WICK: Main vertical range line (Min to Max)
            g.append("line")
                .attr("x1", x).attr("x2", x)
                .attr("y1", yScale(stats.min))
                .attr("y2", yScale(stats.max))
                .attr("stroke", commColor)
                .attr("stroke-width", 1)
                .attr("stroke-dasharray", "2,2")
                .attr("opacity", 0.4);

            // Min/Max caps for the wick
            const capWidth = 6;
            [stats.min, stats.max].forEach(val => {
                g.append("line")
                    .attr("x1", x - capWidth / 2).attr("x2", x + capWidth / 2)
                    .attr("y1", yScale(val)).attr("y2", yScale(val))
                    .attr("stroke", commColor)
                    .attr("opacity", 0.4);
            });

            // 2. BODY: Interquartile Range (Q1 to Q3)
            const boxWidth = 14;
            const boxHeight = Math.abs(yScale(stats.q1) - yScale(stats.q3));

            if (boxHeight > 0.5) { // Only draw if there's a visible range
                g.append("rect")
                    .attr("x", x - boxWidth / 2)
                    .attr("y", yScale(stats.q3))
                    .attr("width", boxWidth)
                    .attr("height", boxHeight)
                    .attr("fill", "hsl(var(--primary))")
                    .attr("opacity", 0.08)
                    .attr("stroke", "hsl(var(--primary))")
                    .attr("stroke-width", 0.5)
                    .attr("stroke-opacity", 0.2)
                    .attr("rx", 2);
            }

            // 3. MEDIAN: The community center point
            g.append("line")
                .attr("x1", x - boxWidth / 2)
                .attr("x2", x + boxWidth / 2)
                .attr("y1", yScale(stats.median))
                .attr("y2", yScale(stats.median))
                .attr("stroke", "hsl(var(--primary))")
                .attr("opacity", 0.5)
                .attr("stroke-width", 1.5);
        });

        // Line connecting user scores (drawing segments for trend coloring)
        for (let i = 1; i < data.length; i++) {
            const x1 = xScale((i - 1).toString())!;
            const y1 = yScale(data[i - 1].userScore);
            const x2 = xScale(i.toString())!;
            const y2 = yScale(data[i].userScore);

            const isDown = data[i].userScore < data[i - 1].userScore;
            const color = isDown ? "#f43f5e" : "#10b981"; // Using more vibrant rose/emerald

            // Add a subtle drop shadow to the line
            g.append("line")
                .attr("x1", x1).attr("y1", y1)
                .attr("x2", x2).attr("y2", y2)
                .attr("stroke", "black")
                .attr("stroke-width", 2)
                .attr("opacity", 0.05)
                .attr("transform", "translate(0, 2)");

            const segment = g.append("line")
                .attr("x1", x1).attr("y1", y1)
                .attr("x2", x2).attr("y2", y2)
                .attr("stroke", color)
                .attr("stroke-width", 2.5)
                .attr("stroke-linecap", "round")
                .attr("opacity", 0.9);

            if (i === data.length - 1) {
                // Style arrowhead for the segment
                segment.attr("marker-end", "url(#arrowhead)");
            }
        }

        // User Score Markers
        const dots = g.selectAll(".dot")
            .data(data)
            .enter()
            .append("circle")
            .attr("class", "dot")
            .attr("cx", (_, i) => xScale(i.toString())!)
            .attr("cy", d => yScale(d.userScore))
            .attr("r", 5.5)
            .attr("fill", d => diffColors[d.difficulty] || "#94a3b8")
            .attr("stroke", "white")
            .attr("stroke-width", 2.5)
            .style("cursor", "pointer")
            .attr("filter", "drop-shadow(0 2px 4px rgba(0,0,0,0.15))")
            .on("mouseover", function () {
                d3.select(this).transition().duration(200).attr("r", 7.5);
            })
            .on("mouseout", function () {
                d3.select(this).transition().duration(200).attr("r", 5.5);
            });

        // Tooltips
        dots.append("title")
            .text(d => `Mock ID: ${d.mockId}\nDate: ${new Date(d.date).toLocaleDateString()}\nScore: ${d.userScore}\nDifficulty: L${d.difficulty}\nRank: ${d.rank}/${d.totalParticipants}\nPercentile: ${d.percentile}%`);

    }, [data]);

    return (
        <div className="w-full h-full flex flex-col items-center">
            <div className="w-full flex justify-between items-start mb-4">
                <h4 className="text-sm font-semibold">Mock Performance Progression</h4>

                {/* How to read Legend */}
                <div className="bg-muted/30 p-2 rounded-lg border text-[10px] space-y-1 max-w-[200px]">
                    <div className="font-bold border-bottom mb-1 opacity-70 uppercase tracking-tighter">How to read</div>
                    <div className="flex items-center gap-2">
                        <div className="w-1 h-3 bg-foreground/40" />
                        <span><span className="font-bold">Wick:</span> Community Score Range</span>
                    </div>
                    <div className="flex items-center gap-2">
                        <div className="w-2 h-2 bg-foreground/10 border" />
                        <span><span className="font-bold">Body:</span> 25th-75th Percentile</span>
                    </div>
                    <div className="flex items-center gap-2">
                        <div className="w-2 h-2 rounded-full border border-foreground/40" />
                        <span><span className="font-bold">Dot:</span> Your Score (Colored by Difficulty)</span>
                    </div>
                </div>
            </div>

            <div className="relative w-full overflow-x-auto">
                <svg ref={svgRef} width={800} height={320} className="max-w-full text-muted-foreground" />
            </div>

            <div className="flex flex-wrap justify-between w-full mt-4 items-center gap-4">
                <div className="flex gap-4 text-xs opacity-70">
                    <div className="flex items-center gap-1"><div className="w-3 h-3 rounded-full bg-[#3b82f6]"></div> L1</div>
                    <div className="flex items-center gap-1"><div className="w-3 h-3 rounded-full bg-[#10b981]"></div> L2</div>
                    <div className="flex items-center gap-1"><div className="w-3 h-3 rounded-full bg-[#f59e0b]"></div> L3</div>
                    <div className="flex items-center gap-1"><div className="w-3 h-3 rounded-full bg-[#f97316]"></div> L4</div>
                    <div className="flex items-center gap-1"><div className="w-3 h-3 rounded-full bg-[#f43f5e]"></div> L5</div>
                </div>
                <div className="flex gap-4 text-[11px] font-medium">
                    <div className="flex items-center gap-1.5"><div className="w-2 h-0.5 bg-[#22c55e]"></div> Score Improvement</div>
                    <div className="flex items-center gap-1.5"><div className="w-2 h-0.5 bg-[#ef4444]"></div> Score Decline</div>
                </div>
            </div>
        </div>
    );
}
