
"use client";

import React, { useEffect, useRef } from 'react';
import * as d3 from 'd3';

interface TrendData {
    date: string | Date;
    percentile: number;
}

interface Props {
    data: TrendData[];
}

export function PercentileTrendChart({ data }: Props) {
    const svgRef = useRef<SVGSVGElement>(null);

    useEffect(() => {
        if (!svgRef.current || !data || data.length === 0) return;

        const margin = { top: 30, right: 20, bottom: 40, left: 50 };
        const width = 450 - margin.left - margin.right;
        const height = 280 - margin.top - margin.bottom;

        const svg = d3.select(svgRef.current);
        svg.selectAll("*").remove();

        const g = svg.append("g")
            .attr("transform", `translate(${margin.left},${margin.top})`);

        // Prepare data
        const sortedData = [...data]
            .filter(d => d.date !== null)
            .sort((a, b) => new Date(a.date).getTime() - new Date(b.date).getTime());

        if (sortedData.length === 0) return;

        // Scales
        const xScale = d3.scaleTime()
            .domain(d3.extent(sortedData, d => new Date(d.date)) as [Date, Date])
            .range([0, width]);

        const yScale = d3.scaleLinear()
            .domain([0, 100])
            .range([height, 0]);

        // Gradient for the area
        const defs = svg.append("defs");
        const gradient = defs.append("linearGradient")
            .attr("id", "percentile-gradient")
            .attr("x1", "0%").attr("y1", "0%")
            .attr("x2", "0%").attr("y2", "100%");

        gradient.append("stop")
            .attr("offset", "0%")
            .attr("stop-color", "#3b82f6")
            .attr("stop-opacity", 0.2);

        gradient.append("stop")
            .attr("offset", "100%")
            .attr("stop-color", "#3b82f6")
            .attr("stop-opacity", 0);

        // Grid Lines
        g.append("g")
            .attr("class", "grid")
            .attr("opacity", 0.05)
            .call(d3.axisLeft(yScale).tickSize(-width).tickFormat(() => ""));

        // Area generator
        const area = d3.area<TrendData>()
            .x(d => xScale(new Date(d.date)))
            .y0(height)
            .y1(d => yScale(d.percentile))
            .curve(d3.curveMonotoneX);

        // Line generator
        const line = d3.line<TrendData>()
            .x(d => xScale(new Date(d.date)))
            .y(d => yScale(d.percentile))
            .curve(d3.curveMonotoneX);

        // Add Area
        g.append("path")
            .datum(sortedData)
            .attr("fill", "url(#percentile-gradient)")
            .attr("d", area);

        // Add Line
        g.append("path")
            .datum(sortedData)
            .attr("fill", "none")
            .attr("stroke", "#3b82f6")
            .attr("stroke-width", 2.5)
            .attr("d", line);

        // Axes
        g.append("g")
            .attr("transform", `translate(0,${height})`)
            .call(d3.axisBottom(xScale).ticks(5).tickFormat(d3.timeFormat("%b %d") as any));

        g.append("g")
            .call(d3.axisLeft(yScale).ticks(5).tickFormat(d => `${d}%`));

        // Interaction Dots
        g.selectAll(".dot")
            .data(sortedData)
            .enter()
            .append("circle")
            .attr("cx", d => xScale(new Date(d.date)))
            .attr("cy", d => yScale(d.percentile))
            .attr("r", 4)
            .attr("fill", "white")
            .attr("stroke", "#3b82f6")
            .attr("stroke-width", 2)
            .style("cursor", "pointer");

    }, [data]);

    return (
        <div className="w-full h-full flex flex-col items-center">
            <div className="self-start mb-4">
                <h4 className="text-sm font-semibold">Percentile Progression</h4>
                <p className="text-xs text-muted-foreground mt-1">
                    Track your relative performance over time. An upward trend indicates you are outpacing the competition.
                </p>
            </div>
            <div className="relative w-full overflow-hidden bg-primary/[0.01] rounded-2xl border border-primary/5 p-4 flex justify-center">
                <svg ref={svgRef} width={450} height={280} className="max-w-full text-muted-foreground" />
            </div>
        </div>
    );
}
