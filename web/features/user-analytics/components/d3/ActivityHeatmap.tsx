"use client";

import React, { useEffect, useRef, useState } from 'react';
import * as d3 from 'd3';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/shared/components/ui/card";

interface ActivityHeatmapProps {
    data: { date: string; count: number }[];
    joinDate?: string;
}

export const ActivityHeatmap: React.FC<ActivityHeatmapProps> = ({ data, joinDate }) => {
    const svgRef = useRef<SVGSVGElement>(null);
    const [containerWidth, setContainerWidth] = useState(800);

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

        const parseDate = d3.timeParse("%Y-%m-%d");
        const formatDay = d3.timeFormat("%w");
        const formatWeek = d3.timeFormat("%b");
        const formatDate = d3.timeFormat("%Y-%m-%d");
        const formatMonth = d3.timeFormat("%b");

        // Date Range Logic
        const today = new Date();
        const futureDate = new Date(today);
        futureDate.setMonth(today.getMonth() + 6); // +6 months window

        const startDate = joinDate ? new Date(joinDate) : new Date(today.getFullYear() - 1, today.getMonth(), today.getDate());

        // Ensure start date is valid and strictly before today
        if (isNaN(startDate.getTime()) || startDate >= today) {
            startDate.setFullYear(today.getFullYear() - 1);
        }

        const dateRange = d3.timeDays(startDate, futureDate);

        // Dynamic Sizing Logic
        const totalWeeks = d3.timeWeek.count(startDate, futureDate) + 2;
        const paddingLeft = 30;
        const availableWidth = containerWidth - paddingLeft - 20;

        // Calculate optimal day size to fill width, with a minimum fallback
        const calculatedDaySize = Math.floor(availableWidth / totalWeeks);
        const daySize = Math.max(calculatedDaySize, 14);
        const cellMargin = 3; // Slightly larger margin for larger cells
        const cellSize = daySize - cellMargin;
        const yearHeight = daySize * 7 + 20; // 7 days + padding
        const dataMap = new Map(data.map(d => [d.date, d.count]));

        const processedData = dateRange.map(date => {
            const dateStr = formatDate(date);
            return {
                date: date,
                str: dateStr,
                count: dataMap.get(dateStr) || 0,
                day: +formatDay(date),
                week: +d3.timeWeek.count(startDate, date), // Count weeks from start date
                isFuture: date > today
            };
        });

        // Color scale
        const maxCount = d3.max(data, d => d.count) || 5;
        // GitHub-like solid colors
        const colorScale = d3.scaleLinear<string>()
            .domain([0, maxCount])
            .range(["#9be9a8", "#216e39"]);

        const width = containerWidth;
        const height = yearHeight + 30; // Extra space for labels
        const totalContentWidth = daySize * totalWeeks + paddingLeft;

        svg.attr("width", width)
            .attr("height", height)
            .attr("viewBox", `0 0 ${Math.max(width, totalContentWidth)} ${height}`)
            .style("font-family", "sans-serif")
            .style("font-size", "10px");

        const g = svg.append("g")
            .attr("transform", `translate(${paddingLeft}, 20)`); // Padding

        // Draw cells
        g.selectAll("rect")
            .data(processedData)
            .join("rect")
            .attr("width", cellSize)
            .attr("height", cellSize)
            .attr("x", d => d.week * daySize)
            .attr("y", d => d.day * daySize)
            .attr("fill", d => {
                if (d.isFuture) return "none";
                // Use solid theme color for empty cells (GitHub style)
                // WRAPPING VARS IN HSL() IS CRITICAL FOR TAILWIND VARS
                // Using --border for empty cells as it has better contrast than secondary
                return d.count === 0 ? "hsl(var(--border))" : colorScale(d.count);
            })
            .attr("opacity", 1)

            // For future days, use dashed stroke
            .attr("stroke", d => d.isFuture ? "hsl(var(--muted-foreground))" : "none")
            .attr("stroke-width", d => d.isFuture ? 1 : 0)
            .attr("stroke-opacity", d => d.isFuture ? 0.3 : 0)
            .attr("stroke-line", d => d.isFuture ? "2,2" : "none")

            .attr("rx", 2)
            .attr("ry", 2)
            .append("title")
            .text(d => `${d.str}: ${d.count} submissions`);

        // Month labels
        const months = d3.timeMonths(startDate, futureDate);
        g.selectAll("text.month")
            .data(months)
            .join("text")
            .attr("class", "month")
            .attr("x", d => d3.timeWeek.count(startDate, d) * daySize)
            .attr("y", -5)
            .text(formatMonth)
            .attr("fill", "hsl(var(--muted-foreground))")
            .style("font-size", "10px");

        // Day labels
        const days = ["Mon", "Wed", "Fri"];
        g.selectAll("text.day")
            .data(days)
            .join("text")
            .attr("class", "day")
            .attr("x", -5)
            .attr("y", (d, i) => (1 + i * 2) * daySize + 8) // align with Mon, Wed, Fri rows (1, 3, 5)
            .attr("text-anchor", "end")
            .text(d => d)
            .attr("fill", "hsl(var(--muted-foreground))")
            .style("font-size", "10px");

    }, [data, containerWidth, joinDate]);

    return (
        <Card className="w-full h-full flex flex-col border-primary/5">
            <CardHeader className="pb-2">
                <CardTitle className="text-base">Activity Heatmap</CardTitle>
                <CardDescription className="text-xs">Daily Problems Submission Intensity</CardDescription>
            </CardHeader>
            <CardContent className="flex-1 flex items-center justify-center overflow-hidden p-0 pb-2 px-4">
                <svg ref={svgRef} className="w-full h-auto"></svg>
            </CardContent>
        </Card>
    );
};