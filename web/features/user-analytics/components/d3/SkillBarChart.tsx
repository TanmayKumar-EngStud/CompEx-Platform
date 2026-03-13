
"use client";

import React, { useEffect, useRef, useState } from 'react';
import * as d3 from 'd3';

interface SkillBarData {
    tag: string;
    section?: string;
    correct: number;
    incorrect: number;
    totalInBank: number;
}

interface SkillBarChartProps {
    data: SkillBarData[];
}

export const SkillBarChart: React.FC<SkillBarChartProps> = ({ data }) => {
    const headerSvgRef = useRef<SVGSVGElement>(null);
    const bodySvgRef = useRef<SVGSVGElement>(null);
    const footerSvgRef = useRef<SVGSVGElement>(null);
    const containerRef = useRef<HTMLDivElement>(null);
    const [dimensions, setDimensions] = useState({ width: 400 });

    useEffect(() => {
        if (!containerRef.current) return;
        const resizeObserver = new ResizeObserver((entries) => {
            const { width } = entries[0].contentRect;
            setDimensions({ width });
        });
        resizeObserver.observe(containerRef.current);
        return () => resizeObserver.disconnect();
    }, []);

    useEffect(() => {
        if (!bodySvgRef.current || !data) return;

        const processedData = [...data];
        const { width } = dimensions;
        const margin = { top: 10, right: 60, bottom: 0, left: 140 };
        const rowHeight = 38;
        const bodyHeight = processedData.length * rowHeight;

        // Common Scale
        const xMax = d3.max(data, d => d.totalInBank) || 0;
        const xRangeMax = xMax + 2;
        const xScale = d3.scaleLinear()
            .domain([0, xRangeMax])
            .range([margin.left, width - margin.right]);

        // Dynamic tick generation
        const tickCount = Math.min(xRangeMax, Math.max(2, Math.floor(width / 60)));
        const xTicks = xScale.ticks(tickCount)
            .filter(t => Number.isInteger(t));

        // 1. Header (Legend)
        const headerSvg = d3.select(headerSvgRef.current);
        headerSvg.selectAll("*").remove();
        const legend = headerSvg.append("g")
            .attr("transform", `translate(${margin.left}, 15)`);

        const legendItems = [
            { label: "Total", color: "rgba(229, 231, 235, 0.8)" },
            { label: "Correct", color: "rgba(16, 185, 129, 0.9)" },
            { label: "Incorrect", color: "rgba(239, 68, 68, 0.9)" }
        ];

        legendItems.forEach((item, i) => {
            const legG = legend.append("g")
                .attr("transform", `translate(${i * 85}, 0)`);
            legG.append("rect").attr("width", 10).attr("height", 10).attr("rx", 2).attr("fill", item.color);
            legG.append("text").attr("x", 15).attr("y", 9).attr("class", "text-[10px] fill-muted-foreground font-medium").text(item.label);
        });

        // 2. Body (Bars & Grid)
        const bodySvg = d3.select(bodySvgRef.current);
        bodySvg.selectAll("*").remove();
        const bodyG = bodySvg.append("g");

        // Vertical Grid
        bodyG.selectAll(".grid-line")
            .data(xTicks)
            .enter()
            .append("line")
            .attr("x1", d => xScale(d))
            .attr("x2", d => xScale(d))
            .attr("y1", 0)
            .attr("y2", bodyHeight)
            .attr("stroke", "rgba(156, 163, 175, 0.1)")
            .attr("stroke-dasharray", "2,2");

        const yScale = d3.scaleBand()
            .domain(processedData.map((d, i) => `${i}-${d.tag}`))
            .range([0, bodyHeight])
            .padding(0.3);

        processedData.forEach((d, i) => {
            const yPos = yScale(`${i}-${d.tag}`) || 0;
            const rowG = bodyG.append("g").attr("transform", `translate(0, ${yPos})`);
            const labelWidth = margin.left - 20;

            rowG.append("foreignObject")
                .attr("x", 10).attr("y", 0).attr("width", labelWidth).attr("height", yScale.bandwidth())
                .append("xhtml:div")
                .attr("style", `width: ${labelWidth}px; height: ${yScale.bandwidth()}px; display: flex; align-items: center; justify-content: flex-end; text-align: right;`)
                .html(`<div class="text-[10px] sm:text-[11px] font-semibold text-muted-foreground leading-tight px-1 overflow-hidden" style="display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical;">${d.tag}</div>`);

            const barG = rowG.append("g");
            barG.append("rect")
                .attr("x", margin.left).attr("y", 0).attr("width", xScale(d.totalInBank) - margin.left).attr("height", yScale.bandwidth())
                .attr("fill", "rgba(229, 231, 235, 0.4)").attr("rx", 4);

            const innerH = yScale.bandwidth() * 0.25;
            const center = yScale.bandwidth() / 2;
            barG.append("rect")
                .attr("x", margin.left).attr("y", center - innerH - 1).attr("width", Math.max(0, xScale(d.correct) - margin.left)).attr("height", innerH)
                .attr("fill", "rgba(16, 185, 129, 0.9)").attr("rx", 1);
            barG.append("rect")
                .attr("x", margin.left).attr("y", center + 1).attr("width", Math.max(0, xScale(d.incorrect) - margin.left)).attr("height", innerH)
                .attr("fill", "rgba(239, 68, 68, 0.9)").attr("rx", 1);

            barG.append("text")
                .attr("x", xScale(d.totalInBank) + 8).attr("y", center).attr("alignment-baseline", "middle").attr("class", "text-[10px] fill-muted-foreground font-bold")
                .text(`${d.correct + d.incorrect}/${d.totalInBank}`);
        });

        // 3. Footer (X-Axis)
        const footerSvg = d3.select(footerSvgRef.current);
        footerSvg.selectAll("*").remove();
        const xAxis = d3.axisBottom(xScale).tickValues(xTicks).tickFormat(d => d3.format("d")(d as number));
        footerSvg.append("g")
            .attr("transform", `translate(0, 5)`)
            .call(xAxis)
            .call(g => g.select(".domain").remove())
            .call(g => g.selectAll(".tick line").remove())
            .call(g => (g.selectAll(".tick text") as any).attr("class", "text-[10px] fill-muted-foreground"));

    }, [data, dimensions.width]);

    return (
        <div ref={containerRef} className="w-full flex flex-col relative group">
            <style jsx global>{`
                .skill-scrollbar::-webkit-scrollbar {
                    width: 6px;
                }
                .skill-scrollbar::-webkit-scrollbar-track {
                    background: transparent;
                }
                .skill-scrollbar::-webkit-scrollbar-thumb {
                    background: rgba(156, 163, 175, 0.05);
                    border-radius: 10px;
                    border: 2px solid transparent;
                    background-clip: content-box;
                }
                .group:hover .skill-scrollbar::-webkit-scrollbar-thumb {
                    background: rgba(156, 163, 175, 0.2);
                    background-clip: content-box;
                }
            `}</style>

            {/* Legend Stickied at Top */}
            <div className="z-10 bg-background/90 backdrop-blur-md sticky top-0 border-b border-muted/5 pb-1">
                <svg ref={headerSvgRef} width="100%" height={35} />
            </div>

            {/* Scrollable Body */}
            <div className="skill-scrollbar overflow-y-auto max-h-[320px] overflow-x-hidden pr-1 transition-all">
                <svg
                    ref={bodySvgRef}
                    width="100%"
                    height={data.length * 38}
                    viewBox={`0 0 ${dimensions.width} ${data.length * 38}`}
                />
            </div>

            {/* X-Axis Stickied at Bottom */}
            <div className="z-10 bg-background/90 backdrop-blur-md sticky bottom-0 mt-2 border-t border-muted/20 pt-1">
                <svg ref={footerSvgRef} width="100%" height={40} />
            </div>
        </div>
    );
};
