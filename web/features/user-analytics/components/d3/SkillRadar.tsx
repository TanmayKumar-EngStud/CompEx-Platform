
"use client";

import React, { useEffect, useRef, useState } from 'react';
import * as d3 from 'd3';

interface SkillRadarProps {
    data: { tag: string; accuracy: number; total: number }[];
}

export const SkillRadar: React.FC<SkillRadarProps> = ({ data }) => {
    const svgRef = useRef<SVGSVGElement>(null);
    const [containerWidth, setContainerWidth] = useState(400);

    const resizeObserver = useRef<ResizeObserver | null>(null);

    useEffect(() => {
        if (svgRef.current && svgRef.current.parentElement) {
            resizeObserver.current = new ResizeObserver((entries) => {
                const width = entries[0].contentRect.width;
                setContainerWidth(width);
            });
            resizeObserver.current.observe(svgRef.current.parentElement);
        }
        return () => {
            resizeObserver.current?.disconnect();
        }
    }, []);

    useEffect(() => {
        if (!svgRef.current || !data) return;

        const svg = d3.select(svgRef.current);
        svg.selectAll("*").remove();

        const width = containerWidth;
        const height = containerWidth; // Keep it square
        const margin = 40;
        const radius = Math.min(width, height) / 2 - margin;

        // Ensure at least 3 points for a proper polygon, pad if needed
        let processedData = [...data];
        if (processedData.length < 3) {
            // Pad with fake data for visualisation structure if less than 3 tags
            for (let i = processedData.length; i < 3; i++) {
                processedData.push({ tag: `Scale ${i + 1}`, accuracy: 0, total: 0 });
            }
        }

        const allAxis = processedData.map(d => d.tag);
        const total = allAxis.length;
        const angleSlice = Math.PI * 2 / total;

        // Scale
        const rScale = d3.scaleLinear()
            .range([0, radius])
            .domain([0, 100]); // Accuracy is 0-100%

        const g = svg.append("g")
            .attr("transform", `translate(${width / 2},${height / 2})`);

        // Filter for Glow
        const defs = svg.append("defs");
        const filter = defs.append("filter")
            .attr("id", "glow");
        filter.append("feGaussianBlur")
            .attr("stdDeviation", "2.5")
            .attr("result", "coloredBlur");
        const feMerge = filter.append("feMerge");
        feMerge.append("feMergeNode").attr("in", "coloredBlur");
        feMerge.append("feMergeNode").attr("in", "SourceGraphic");

        // Axis Grid
        const axisGrid = g.append("g").attr("class", "axisWrapper");

        // Levels (Circles or Polygons)
        const levels = 5;
        for (let j = 0; j < levels; j++) {
            const levelFactor = radius * ((j + 1) / levels);
            axisGrid.selectAll(".levels")
                .data([1]) // Dummy data
                .enter()
                .append("circle")
                .attr("r", levelFactor)
                .style("fill", "none")
                .style("stroke", "#374151") // gray-700
                .style("stroke-opacity", "0.5")
                .style("stroke-width", "0.5px");
        }

        // Axis Lines
        const axis = axisGrid.selectAll(".axis")
            .data(allAxis)
            .enter()
            .append("g")
            .attr("class", "axis");

        axis.append("line")
            .attr("x1", 0)
            .attr("y1", 0)
            .attr("x2", (d, i) => rScale(100) * Math.cos(angleSlice * i - Math.PI / 2))
            .attr("y2", (d, i) => rScale(100) * Math.sin(angleSlice * i - Math.PI / 2))
            .attr("class", "line")
            .style("stroke", "#4b5563") // gray-600
            .style("stroke-width", "1px");

        // Axis Labels
        axis.append("text")
            .attr("class", "legend")
            .style("font-size", "10px")
            .attr("text-anchor", "middle")
            .attr("dy", "0.35em")
            .attr("x", (d, i) => rScale(115) * Math.cos(angleSlice * i - Math.PI / 2))
            .attr("y", (d, i) => rScale(115) * Math.sin(angleSlice * i - Math.PI / 2))
            .text(d => d)
            .style("fill", "#9ca3af"); // gray-400


        // The Radar Chart blob
        const radarLine = d3.lineRadial<{ tag: string, accuracy: number }>()
            .radius(d => rScale(d.accuracy))
            .angle((d, i) => i * angleSlice)
            .curve(d3.curveLinearClosed);

        // Draw the blob
        g.append("path")
            .datum(processedData)
            .attr("class", "radarArea")
            .attr("d", radarLine)
            .style("fill", "rgba(16, 185, 129, 0.2)") // emerald-500 with opacity
            .style("fill-opacity", 0.7)
            .style("stroke", "#10b981") // emerald-500
            .style("stroke-width", 2)
            .style("filter", "url(#glow)");

        // Draw circles at vertices
        g.selectAll(".radarCircle")
            .data(processedData)
            .enter().append("circle")
            .attr("class", "radarCircle")
            .attr("r", 4)
            .attr("cx", (d, i) => rScale(d.accuracy) * Math.cos(angleSlice * i - Math.PI / 2))
            .attr("cy", (d, i) => rScale(d.accuracy) * Math.sin(angleSlice * i - Math.PI / 2))
            .style("fill", "#10b981")
            .style("fill-opacity", 0.8);

    }, [data, containerWidth]);

    return (
        <div className="w-full h-full flex flex-col items-center justify-center bg-card rounded-xl border border-border p-4">
            <h3 className="text-lg font-semibold mb-2 self-start">Skill Breakdown</h3>
            <div className="flex-1 w-full flex items-center justify-center">
                <svg ref={svgRef} width="100%" height="300" style={{ maxWidth: '400px', maxHeight: '400px' }}></svg>
            </div>
        </div>
    );
};
