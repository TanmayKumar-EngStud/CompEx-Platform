
"use client";

import React, { useEffect, useRef, useState } from 'react';
import * as d3 from 'd3';

interface DifficultyStats {
    total: number;
    correct: number;
}

interface DifficultyPieProps {
    data: {
        easy: DifficultyStats;
        medium: DifficultyStats;
        hard: DifficultyStats;
    };
}

export const DifficultyPie: React.FC<DifficultyPieProps> = ({ data }) => {
    const svgRef = useRef<SVGSVGElement>(null);
    const [containerWidth, setContainerWidth] = useState(300);
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
        if (!svgRef.current || !data) return;

        const svg = d3.select(svgRef.current);
        svg.selectAll("*").remove();

        const width = containerWidth;
        const height = 200;
        const radius = Math.min(width, height) / 2;

        const g = svg.append("g")
            .attr("transform", `translate(${width / 2},${height / 2})`);

        const pieData = [
            { label: "Easy", value: data.easy.total, color: "#22c55e" }, // green-500
            { label: "Med", value: data.medium.total, color: "#eab308" }, // yellow-500
            { label: "Hard", value: data.hard.total, color: "#ef4444" }  // red-500
        ].filter(d => d.value > 0);

        if (pieData.length === 0) {
            g.append("text")
                .attr("text-anchor", "middle")
                .text("No Data")
                .attr("fill", "#6b7280");
            return;
        }

        const pie = d3.pie<{ label: string; value: number; color: string }>()
            .value(d => d.value)
            .sort(null);

        const arc = d3.arc<d3.PieArcDatum<{ label: string; value: number; color: string }>>()
            .innerRadius(radius * 0.6)
            .outerRadius(radius * 0.9);

        // Draw Arcs
        g.selectAll("path")
            .data(pie(pieData))
            .enter()
            .append("path")
            .attr("d", arc)
            .attr("fill", d => d.data.color)
            .attr("stroke", "white")
            .style("stroke-width", "2px")
            .append("title")
            .text(d => `${d.data.label}: ${d.data.value} attempted`);

        // Center Text (Total)
        const totalSolved = data.easy.total + data.medium.total + data.hard.total;
        g.append("text")
            .attr("text-anchor", "middle")
            .attr("dy", "-0.2em")
            .style("font-size", "20px")
            .style("font-weight", "bold")
            .text(totalSolved);

        g.append("text")
            .attr("text-anchor", "middle")
            .attr("dy", "1.2em")
            .style("font-size", "12px")
            .text("Solved")
            .attr("fill", "#6b7280");

    }, [data, containerWidth]);

    return (
        <div ref={containerRef} className="bg-card rounded-xl border border-border p-4 flex flex-col items-center">
            <h3 className="text-lg font-semibold mb-2 self-start">Difficulty</h3>
            <div className="flex-1 flex items-center justify-center w-full">
                <svg ref={svgRef} width={containerWidth} height={200}></svg>
            </div>
            <div className="flex gap-4 mt-2 text-xs text-muted-foreground w-full justify-around">
                <div className="text-green-500 font-medium">Easy: {data.easy.total}</div>
                <div className="text-yellow-500 font-medium">Med: {data.medium.total}</div>
                <div className="text-red-500 font-medium">Hard: {data.hard.total}</div>
            </div>
        </div>
    );
};
