
"use client";

import React, { useEffect, useRef, useState } from 'react';
import * as d3 from 'd3';

interface TrendChartProps {
    data: { date: string; accuracy: number; submissions: number }[];
}

export const TrendChart: React.FC<TrendChartProps> = ({ data }) => {
    const svgRef = useRef<SVGSVGElement>(null);
    const [containerWidth, setContainerWidth] = useState(600);
    const containerRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        if (containerRef.current) {
            const observer = new ResizeObserver((entries) => {
                setContainerWidth(entries[0].contentRect.width);
            });
            observer.observe(containerRef.current);
            return () => observer.disconnect();
        }
    }, []);

    useEffect(() => {
        if (!svgRef.current || !data || data.length === 0) return;

        const svg = d3.select(svgRef.current);
        svg.selectAll("*").remove();

        const margin = { top: 20, right: 30, bottom: 30, left: 40 };
        const width = containerWidth - margin.left - margin.right;
        const height = 300 - margin.top - margin.bottom;

        const g = svg.append("g")
            .attr("transform", `translate(${margin.left},${margin.top})`);

        // Scales
        const parseDate = d3.timeParse("%Y-%m-%d");
        const parsedData = data.map(d => ({
            ...d,
            parsedDate: parseDate(d.date) as Date
        }));

        const x = d3.scaleTime()
            .domain(d3.extent(parsedData, d => d.parsedDate) as [Date, Date])
            .range([0, width]);

        const y = d3.scaleLinear()
            .domain([0, 100])
            .range([height, 0]);

        // Gradients
        const defs = svg.append("defs");
        const gradient = defs.append("linearGradient")
            .attr("id", "areaGradient")
            .attr("x1", "0%")
            .attr("y1", "0%")
            .attr("x2", "0%")
            .attr("y2", "100%");
        gradient.append("stop").attr("offset", "0%").attr("stop-color", "#3b82f6").attr("stop-opacity", 0.6); // blue-500
        gradient.append("stop").attr("offset", "100%").attr("stop-color", "#3b82f6").attr("stop-opacity", 0);

        // Gridlines
        const yAxisGrid = d3.axisLeft(y).tickSize(-width).tickFormat(() => "").ticks(5);
        g.append("g").attr("class", "grid")
            .call(yAxisGrid)
            .style("stroke-opacity", 0.1)
            .style("stroke-dasharray", "3,3")
            .select(".domain").remove();

        // Area Generator
        const area = d3.area<{ parsedDate: Date; accuracy: number }>()
            .x(d => x(d.parsedDate))
            .y0(height)
            .y1(d => y(d.accuracy))
            .curve(d3.curveMonotoneX);

        // Line Generator
        const line = d3.line<{ parsedDate: Date; accuracy: number }>()
            .x(d => x(d.parsedDate))
            .y(d => y(d.accuracy))
            .curve(d3.curveMonotoneX);

        // Draw Area
        g.append("path")
            .datum(parsedData)
            .attr("fill", "url(#areaGradient)")
            .attr("d", area);

        // Draw Line
        g.append("path")
            .datum(parsedData)
            .attr("fill", "none")
            .attr("stroke", "#3b82f6")
            .attr("stroke-width", 2)
            .attr("d", line);

        // Draw Dots
        g.selectAll(".dot")
            .data(parsedData)
            .enter().append("circle")
            .attr("class", "dot")
            .attr("cx", d => x(d.parsedDate))
            .attr("cy", d => y(d.accuracy))
            .attr("r", 3)
            .attr("fill", "#2563eb") // blue-600
            .append("title")
            .text(d => `${d.date}: ${d.accuracy}% (${d.submissions} submissions)`);

        // Axes
        g.append("g")
            .attr("transform", `translate(0,${height})`)
            .call(d3.axisBottom(x).ticks(5))
            .attr("color", "#6b7280"); // gray-500

        g.append("g")
            .call(d3.axisLeft(y).ticks(5))
            .attr("color", "#6b7280");

    }, [data, containerWidth]);

    return (
        <div ref={containerRef} className="w-full bg-card rounded-xl border border-border p-4">
            <h3 className="text-lg font-semibold mb-2">Accuracy Trend</h3>
            <svg ref={svgRef} width={containerWidth} height={300}></svg>
        </div>
    );
};
