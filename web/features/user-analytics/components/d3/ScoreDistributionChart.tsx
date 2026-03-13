
"use client";

import React, { useEffect, useRef } from 'react';
import * as d3 from 'd3';

interface DistributionPoint {
    score: number;
    frequency: number;
}

interface Props {
    data: DistributionPoint[];
    userScore: number;
}

export function ScoreDistributionChart({ data, userScore }: Props) {
    const svgRef = useRef<SVGSVGElement>(null);

    useEffect(() => {
        if (!svgRef.current || !data || data.length === 0) return;

        const margin = { top: 40, right: 30, bottom: 50, left: 60 };
        const width = 500 - margin.left - margin.right;
        const height = 280 - margin.top - margin.bottom;

        const svg = d3.select(svgRef.current);
        svg.selectAll("*").remove();

        const g = svg.append("g")
            .attr("transform", `translate(${margin.left},${margin.top})`);

        // Scales
        // Calculate dynamic domains
        const allScores = data.map(d => d.score);
        const minScore = Math.min(...allScores, userScore);
        const maxScore = Math.max(...allScores, userScore);

        // Add padding to the domain (e.g., 5% on each side)
        const scoreRange = maxScore - minScore || 1; // Prevent division by zero
        const xPadding = scoreRange * 0.05;

        const xScale = d3.scaleLinear()
            .domain([minScore - xPadding, maxScore + xPadding])
            .range([0, width]);

        const maxFreq = d3.max(data, d => d.frequency) || 0;
        const yScale = d3.scaleLinear()
            .domain([0, maxFreq * 1.1]) // 10% top padding
            .range([height, 0]);

        // Gradient for the distribution
        const defs = svg.append("defs");
        const gradient = defs.append("linearGradient")
            .attr("id", "dist-gradient")
            .attr("x1", "0%").attr("y1", "0%")
            .attr("x2", "0%").attr("y2", "100%");

        gradient.append("stop")
            .attr("offset", "0%")
            .attr("stop-color", "#10b981")
            .attr("stop-opacity", 0.4);

        gradient.append("stop")
            .attr("offset", "100%")
            .attr("stop-color", "#10b981")
            .attr("stop-opacity", 0);

        // Area generator for the "Bell Curve" effect
        const area = d3.area<DistributionPoint>()
            .x(d => xScale(d.score))
            .y0(height)
            .y1(d => yScale(d.frequency))
            .curve(d3.curveBasis);

        const line = d3.line<DistributionPoint>()
            .x(d => xScale(d.score))
            .y(d => yScale(d.frequency))
            .curve(d3.curveBasis);

        // Add glow effect for the line
        defs.append("filter")
            .attr("id", "glow")
            .append("feGaussianBlur")
            .attr("stdDeviation", "2")
            .attr("result", "coloredBlur");

        // Draw Distribution Area
        g.append("path")
            .datum(data)
            .attr("fill", "url(#dist-gradient)")
            .attr("d", area);

        // Draw Distribution Line
        g.append("path")
            .datum(data)
            .attr("fill", "none")
            .attr("stroke", "#10b981")
            .attr("stroke-width", 2.5)
            .attr("d", line);

        // Community Average Marker
        const avgScore = d3.mean(data, d => d.score) || 0;
        const avgX = xScale(avgScore);

        g.append("line")
            .attr("x1", avgX).attr("y1", 0)
            .attr("x2", avgX).attr("y2", height)
            .attr("stroke", "hsl(var(--muted-foreground))")
            .attr("stroke-width", 1)
            .attr("stroke-dasharray", "2,2")
            .attr("opacity", 0.5);

        g.append("text")
            .attr("x", avgX)
            .attr("y", -5)
            .attr("text-anchor", "middle")
            .attr("fill", "hsl(var(--muted-foreground))")
            .style("font-size", "9px")
            .style("font-weight", "500")
            .text("AVG");

        // User Position Marker
        const userX = xScale(userScore);

        // Vertical line for user
        g.append("line")
            .attr("x1", userX).attr("y1", 0)
            .attr("x2", userX).attr("y2", height)
            .attr("stroke", "#064e3b")
            .attr("stroke-width", 2)
            .attr("stroke-dasharray", "4,2");

        // Circle at the point
        // Find approximate y for userScore by interpolating or just finding nearest
        const nearestPoint = data.reduce((prev, curr) =>
            Math.abs(curr.score - userScore) < Math.abs(prev.score - userScore) ? curr : prev
        );
        const userY = yScale(nearestPoint.frequency);

        g.append("circle")
            .attr("cx", userX)
            .attr("cy", userY)
            .attr("r", 6)
            .attr("fill", "#10b981")
            .attr("stroke", "white")
            .attr("stroke-width", 2)
            .attr("filter", "drop-shadow(0 2px 4px rgba(0,0,0,0.2))");

        // "You" Label
        g.append("text")
            .attr("x", userX)
            .attr("y", -10)
            .attr("text-anchor", "middle")
            .attr("fill", "#064e4b")
            .style("font-size", "10px")
            .style("font-weight", "bold")
            .text("YOU");

        // Axes
        g.append("g")
            .attr("transform", `translate(0,${height})`)
            .call(d3.axisBottom(xScale).ticks(10)); // More granular ticks

        // Add X-axis label
        g.append("text")
            .attr("x", width / 2)
            .attr("y", height + 35)
            .attr("text-anchor", "middle")
            .style("font-size", "10px")
            .text("Mock Score");

        // Y-Axis
        g.append("g")
            .call(d3.axisLeft(yScale).ticks(5));

        // Y-Axis Label
        g.append("text")
            .attr("transform", "rotate(-90)")
            .attr("y", 0 - margin.left + 15)
            .attr("x", 0 - (height / 2))
            .attr("dy", "1em")
            .style("text-anchor", "middle")
            .style("font-size", "10px")
            .style("fill", "hsl(var(--muted-foreground))")
            .text("Frequency");

        // Horizontal Grid
        g.append("g")
            .attr("class", "grid")
            .attr("opacity", 0.05)
            .call(d3.axisLeft(yScale).tickSize(-width).tickFormat(() => ""));

    }, [data, userScore]);

    return (
        <div className="w-full h-full flex flex-col items-center">
            <div className="self-start mb-4">
                <h4 className="text-sm font-semibold">Community Score Distribution</h4>
                <p className="text-xs text-muted-foreground mt-1">
                    Compare your latest mock score against the entire community. Identify where you stand on the bell curve.
                </p>
            </div>
            <div className="relative w-full overflow-hidden bg-primary/[0.01] rounded-2xl border border-primary/5 p-4 flex justify-center">
                <svg ref={svgRef} width={500} height={280} className="max-w-full text-muted-foreground" />
            </div>
        </div>
    );
}
