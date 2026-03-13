"use client";

import React, { useEffect, useRef } from 'react';
import * as d3 from 'd3';

interface SectionData {
    name: string;
    count: number;
}

interface Props {
    data: SectionData[];
}

export function SectionDistributionDonut({ data }: Props) {
    const svgRef = useRef<SVGSVGElement>(null);

    useEffect(() => {
        if (!svgRef.current || !data || data.length === 0) return;

        const width = 200;
        const height = 120; // Semi-circle height
        const radius = Math.min(width, height * 2) / 2 - 10;

        const svg = d3.select(svgRef.current);
        svg.selectAll("*").remove();

        const g = svg.append("g")
            .attr("transform", `translate(${width / 2}, ${height - 10})`); // Center bottom

        const color = d3.scaleOrdinal()
            .domain(data.map(d => d.name))
            .range(["#3b82f6", "#10b981", "#f59e0b", "#ef4444"]);

        const pie = d3.pie<SectionData>()
            .startAngle(-Math.PI / 2)
            .endAngle(Math.PI / 2)
            .value(d => d.count)
            .sort(null);

        const arc = d3.arc<d3.PieArcDatum<SectionData>>()
            .innerRadius(radius * 0.6)
            .outerRadius(radius)
            .cornerRadius(4);

        // const hoverArc = d3.arc<d3.PieArcDatum<SectionData>>()
        //     .innerRadius(radius * 0.6)
        //     .outerRadius(radius * 1.1)
        //     .cornerRadius(4);

        const arcs = g.selectAll("arc")
            .data(pie(data))
            .enter()
            .append("g")
            .attr("class", "arc");

        // Paths
        arcs.append("path")
            .attr("fill", d => color(d.data.name) as string)
            .attr("d", arc)
            .attr("stroke", "hsl(var(--card))")
            .style("stroke-width", "2px")
            .attr("opacity", 0.9);

    }, [data]);

    // Calculate total for percentages
    const total = data.reduce((sum, d) => sum + d.count, 0);

    return (
        <div className="flex items-center h-full">
            {/* Chart */}
            <div className="flex-shrink-0 relative flex items-end justify-center pb-2">
                <svg ref={svgRef} width={200} height={120} className="overflow-visible" />
                <div className="absolute bottom-4 left-1/2 -translate-x-1/2 text-center">
                    <span className="text-2xl font-bold">{total}</span>
                    <span className="block text-[10px] text-muted-foreground uppercase tracking-wider">Attempts</span>
                </div>
            </div>

            {/* Legend */}
            <div className="flex flex-col gap-2 ml-4">
                {data.map((d, i) => {
                    const colors = ["bg-blue-500", "bg-emerald-500", "bg-amber-500", "bg-red-500"];
                    const percent = total > 0 ? Math.round((d.count / total) * 100) : 0;

                    return (
                        <div key={d.name} className="flex items-center gap-2 text-xs">
                            <span className={`w-2 h-2 rounded-full ${colors[i % colors.length]}`} />
                            <span className="capitalize font-medium text-muted-foreground">{d.name}</span>
                            <span className="font-bold ml-auto">{percent}%</span>
                        </div>
                    );
                })}
            </div>
        </div>
    );
}
