/**
 * Dynamic Chart Renderer using D3.js
 * 
 * Replaces Recharts with D3 for "minimalistic consistent professional design"
 * and full control over label visibility.
 */

import React, { useEffect, useRef, useMemo, useState } from 'react';
import * as d3 from 'd3';
import { ChartSkeleton } from "@/shared/components/feedback/ChartSkeleton";

interface ChartProps {
  type: string;
  metadata: any;
}

const DynamicChartRenderer: React.FC<ChartProps> = ({ type, metadata }) => {
  const svgRef = useRef<SVGSVGElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);
  const [dimensions, setDimensions] = useState({ width: 600, height: 400 });
  const [hoveredIndex, setHoveredIndex] = useState<number | null>(null);

  // --- 1. Data Normalization ---
  const { chartType, data, config } = useMemo(() => {
    // Normalize: if metadata.graph is an array (some GI questions wrap charts in an array),
    // unwrap the first element so all downstream logic sees a plain object.
    const normalizedMeta = Array.isArray(metadata?.graph)
      ? { ...metadata, graph: metadata.graph[0] }
      : metadata;

    const rawType = (normalizedMeta?.type || normalizedMeta?.graph?.type || type || "").toLowerCase().replace(/_/g, " ");
    const structure = normalizedMeta?.structure || normalizedMeta?.graph?.structure || normalizedMeta?.metadata?.structure || normalizedMeta?.Graph?.structure || {};
    let dataFormat =
      structure?.data_format ||
      normalizedMeta?.graph?.data_format ||
      normalizedMeta?.metadata?.data_format ||
      normalizedMeta?.graph ||
      normalizedMeta?.metadata ||
      normalizedMeta ||
      {};

    // Handle nested data object (common in MSR)
    if (dataFormat.data && !dataFormat.series && !dataFormat.bars && !dataFormat.categories) {
      dataFormat = { ...dataFormat, ...dataFormat.data };
    }

    let resolvedType = rawType;
    if (resolvedType === "graph" || resolvedType === "chart" || resolvedType === "generic" || !resolvedType) {
      if (Array.isArray(dataFormat?.bars)) resolvedType = "bar chart";
      else if (Array.isArray(dataFormat?.points)) resolvedType = "scatter chart";
      else if (Array.isArray(dataFormat?.segments)) resolvedType = "pie chart";
      else if (Array.isArray(dataFormat?.series)) resolvedType = "line chart";
      else if (Array.isArray(dataFormat?.categories) || Array.isArray(dataFormat?.labels)) resolvedType = "bar chart";
      else resolvedType = "bar chart";
    }

    // Standardize Data
    let standardizedData: any[] = [];
    let keys: string[] = [];
    let colors = dataFormat?.colors || ["#000000"];
    let detectedXKey = "";
    let detectedYKey = "";

    const normalizePoint = (obj: any) => {
      if (typeof obj !== 'object' || obj === null) return { x: obj, y: obj };
      const objKeys = Object.keys(obj);
      if (objKeys.length === 0) return { x: "", y: 0 };

      // Use explicit x/y/label/value if they exist, otherwise use positional
      const xK = objKeys.find(k => k === 'x' || k === 'label' || k === 'category' || k === 'year') || objKeys[0];
      const yK = objKeys.find(k => k === 'y' || k === 'value' || k === 'volume' || k === 'amount') || objKeys[1] || objKeys[0];

      if (!detectedXKey) detectedXKey = xK;
      if (!detectedYKey) detectedYKey = yK;

      return {
        label: obj[xK],
        value: obj[yK],
        x: obj[xK],
        y: obj[yK],
        ...obj
      };
    };

    // Professional Palette
    const palette = ["#264653", "#2a9d8f", "#e9c46a", "#f4a261", "#e76f51", "#780000", "#03045e", "#0077b6", "#00b4d8", "#90e0ef"];
    if (!dataFormat?.colors) colors = palette;

    // Handle different data formats
    if (Array.isArray(dataFormat?.bars)) {
      standardizedData = dataFormat.bars.map(normalizePoint);
    } else if (Array.isArray(dataFormat?.points)) {
      standardizedData = dataFormat.points.map(normalizePoint);
    } else if (Array.isArray(dataFormat?.segments)) {
      standardizedData = dataFormat.segments;
    } else if (Array.isArray(dataFormat?.series)) {
      // Multi-series or single series in 'series' format
      keys = dataFormat.series.map((s: any) => s.name || s.label || `Series ${keys.length + 1}`);

      // If categories are missing, try to infer them from the first series
      let categories = dataFormat.categories;
      if (!Array.isArray(categories) && dataFormat.series.length > 0) {
        const firstSeries = dataFormat.series[0];
        const vals = firstSeries.values || firstSeries.data || firstSeries.points || [];
        categories = vals.map((d: any, i: number) => {
          const norm = normalizePoint(d);
          return norm.x !== undefined ? norm.x : `Point ${i + 1}`;
        });
      }

      if (Array.isArray(categories)) {
        standardizedData = categories.map((cat: any, i: number) => {
          const item: any = { label: cat.toString() };
          dataFormat.series.forEach((s: any) => {
            const key = s.name || s.label || "Value";
            const vals = s.values || s.data || s.points || [];
            if (vals[i] !== undefined) {
              const norm = normalizePoint(vals[i]);
              item[key] = norm.y;
            } else {
              item[key] = 0;
            }
          });
          return item;
        });

        if (dataFormat.series[0]?.color || dataFormat.series[0]?.line_color) {
          colors = dataFormat.series.map((s: any) => s.color || s.line_color).filter(Boolean);
          if (colors.length === 0) colors = palette;
        }
      } else {
        // Fallback for points-based series (single series)
        const rawData = dataFormat.series[0]?.values || dataFormat.series[0]?.data || dataFormat.series[0]?.points || [];
        standardizedData = rawData.map(normalizePoint);
      }
    } else if (Array.isArray(dataFormat?.categories) && dataFormat.categories.length > 0 && typeof dataFormat.categories[0] === 'object') {
      // categories is an array of objects like [{category: "A", value: 10}] — normalize directly
      standardizedData = dataFormat.categories.map(normalizePoint);
    } else if (Array.isArray(dataFormat?.values) && (Array.isArray(dataFormat?.categories) || Array.isArray(dataFormat?.labels))) {
      const labelArray = dataFormat.categories || dataFormat.labels;
      standardizedData = labelArray.map((cat: string, i: number) => ({
        label: cat,
        value: dataFormat.values[i]
      }));
    } else if (Array.isArray(dataFormat?.structure?.data)) {
      // data nested inside structure (e.g. metadata.graph.structure.data)
      standardizedData = dataFormat.structure.data.map(normalizePoint);
    } else if (Array.isArray(normalizedMeta?.graph?.data)) {
      // Direct data array fallback (Standard Recharts style)
      standardizedData = normalizedMeta.graph.data.map(normalizePoint);
    }

    // Axis Label Inference
    let xLabel = structure?.x_axis?.label;
    if (!xLabel && detectedXKey && detectedXKey !== 'x' && detectedXKey !== 'label') {
      xLabel = detectedXKey.charAt(0).toUpperCase() + detectedXKey.slice(1);
    }
    if (!xLabel) xLabel = "Category";

    let yLabel = structure?.y_axis?.label;
    if (!yLabel && detectedYKey && detectedYKey !== 'y' && detectedYKey !== 'value') {
      yLabel = detectedYKey.charAt(0).toUpperCase() + detectedYKey.slice(1);
    }
    if (!yLabel) yLabel = "Value";

    return {
      chartType: resolvedType,
      data: standardizedData,
      config: {
        title: structure?.title || normalizedMeta?.title || normalizedMeta?.graph?.title,
        xLabel,
        yLabel,
        colors,
        keys, // For stacked/grouped/line
        yRange: structure?.y_axis?.range,
        xRange: structure?.x_axis?.range,
        innerRadius: dataFormat?.inner_radius || 0
      }
    };
  }, [type, metadata]);

  // Extract Legend Items for HTML Rendering
  const legendItems = useMemo(() => {
    const isPie = chartType.includes("pie") || chartType.includes("donut");
    const isBar = chartType.includes("bar");

    if (isPie || (isBar && config.keys.length <= 1)) {
      return data.map((d, i) => ({
        label: d.label,
        color: config.colors[i % config.colors.length]
      }));
    }
    if (config.keys.length > 1) {
      return config.keys.map((key, i) => ({
        label: key,
        color: config.colors[i % config.colors.length]
      }));
    }
    return [];
  }, [chartType, data, config]);


  // --- 2. Resize Handler ---
  useEffect(() => {
    const handleResize = () => {
      if (containerRef.current) {
        setDimensions({
          width: containerRef.current.clientWidth,
          height: 400 // Fixed height for consistency
        });
      }
    };
    window.addEventListener('resize', handleResize);
    handleResize();
    return () => window.removeEventListener('resize', handleResize);
  }, []);


  // --- 3. D3 Drawing Logic ---
  useEffect(() => {
    if (!svgRef.current || !data.length) return;

    const svg = d3.select(svgRef.current);
    svg.selectAll("*").remove(); // Clear previous

    const { width, height } = dimensions;
    const margin = { top: 10, right: 60, bottom: 40, left: 40 };

    const isPie = chartType.includes("pie") || chartType.includes("donut");
    const isBar = chartType.includes("bar");
    const isCategorical = isPie || isBar;

    const contentWidth = width - margin.left - margin.right;
    const contentHeight = height - margin.top - margin.bottom;

    // Use a tighter vertical area for categorical charts to minimize gap
    const adjustedHeight = isCategorical ? Math.min(contentHeight * 0.8, contentWidth * 0.8) : contentHeight;

    const g = svg.append("g").attr("transform", `translate(${margin.left},${margin.top})`);

    // Helper for theme-aware colors
    const isDark = document.documentElement.classList.contains('dark');
    const labelColor = isDark ? "#94a3b8" : "#475569"; // slate-400 : slate-600
    const titleColor = isDark ? "#f1f5f9" : "#0f172a"; // slate-100 : slate-900
    const gridColorUnit = isDark ? "rgba(255,255,255,0.1)" : "rgba(0,0,0,0.1)";
    const gridColorNonUnit = isDark ? "rgba(255,255,255,0.05)" : "rgba(0,0,0,0.05)";

    const tooltip = d3.select(containerRef.current).select(".d3-tooltip");
    const showTooltip = (event: any, title: string, items: { name: string, value: any, color?: string }[]) => {
      const [xPos, yPos] = d3.pointer(event, containerRef.current);
      const containerWidth = containerRef.current?.clientWidth || 0;

      const content = `
        <div class="flex flex-col gap-1.5 min-w-[140px]">
          <div class="font-bold text-foreground border-b border-border/50 pb-1.5 mb-1.5">${title}</div>
          <div class="flex flex-col gap-1.5">
            ${items.map(item => `
              <div class="flex items-center justify-between gap-4">
                <div class="flex items-center gap-2">
                  ${item.color ? `<div class="w-2.5 h-2.5 rounded-[2px]" style="background-color: ${item.color}"></div>` : ""}
                  <span class="text-muted-foreground whitespace-nowrap">${item.name}:</span>
                </div>
                <span class="font-bold text-foreground">${item.value}</span>
              </div>
            `).join("")}
          </div>
        </div>
      `;

      // Offset values
      let left = xPos + 15;
      let top = yPos - 35;

      // Prevent clipping at right edge
      if (left > containerWidth - 180) {
        left = xPos - 190;
      }

      tooltip
        .style("opacity", 1)
        .html(content)
        .style("left", left + "px")
        .style("top", top + "px");
    };
    const hideTooltip = () => tooltip.style("opacity", 0);

    const getTooltipItems = (d: any) => {
      if (config.keys.length > 0) {
        return config.keys.map((key, i) => ({
          name: key,
          value: d[key],
          color: config.colors[i % config.colors.length]
        }));
      }
      return [{ name: config.yLabel || "Value", value: d.value || d.y, color: config.colors[0] }];
    };

    // Grid Helpers
    const drawGrids = (xScale: any, yScale: any) => {
      if (isPie) return;

      // Horizontal Grids
      const yTicks = yScale.ticks(10);
      g.append("g")
        .attr("class", "grid-y")
        .selectAll("line")
        .data(yTicks)
        .enter().append("line")
        .attr("x1", 0)
        .attr("x2", contentWidth)
        .attr("y1", (d: any) => yScale(d))
        .attr("y2", (d: any) => yScale(d))
        .attr("stroke", gridColorUnit)
        .attr("stroke-width", 1)
        .attr("stroke-dasharray", "4 4"); // Dashed for unit grids

      // Vertical Grids (if applicable)
      if (xScale.ticks) {
        const xTicks = xScale.ticks(10);
        g.append("g")
          .attr("class", "grid-x")
          .selectAll("line")
          .data(xTicks)
          .enter().append("line")
          .attr("x1", (d: any) => xScale(d))
          .attr("x2", (d: any) => xScale(d))
          .attr("y1", 0)
          .attr("y2", contentHeight)
          .attr("stroke", gridColorNonUnit)
          .attr("stroke-width", 1)
          .attr("stroke-dasharray", "4 4"); // Dotted for non-unit/minor grids
      }
    };

    // Axis Label Helper
    const drawAxisLabels = () => {
      if (isPie || isBar) return;

      // X Label
      g.append("text")
        .attr("x", contentWidth / 2)
        .attr("y", adjustedHeight + 45) // Based on margin.bottom = 60
        .attr("text-anchor", "middle")
        .style("font-size", "11px")
        .style("font-weight", "600")
        .style("fill", labelColor)
        .text(config.xLabel);

      // Y Label
      g.append("text")
        .attr("transform", "rotate(-90)")
        .attr("x", -contentHeight / 2)
        .attr("y", -45) // Based on margin.left = 60
        .attr("text-anchor", "middle")
        .style("font-size", "11px")
        .style("font-weight", "600")
        .style("fill", labelColor)
        .text(config.yLabel);
    };

    // --- Draw Functions ---

    // BAR CHART (Vertical)
    const drawBarChart = () => {
      const x = d3.scaleBand()
        .domain(data.map(d => d.label))
        .range([0, contentWidth])
        .padding(0.3);

      let yDomain = [0, d3.max(data, (d: any) => d.value) as number];
      if (config.yRange) yDomain = config.yRange;

      const y = d3.scaleLinear()
        .domain(yDomain)
        .range([adjustedHeight, 0]).nice();

      drawGrids(x, y);

      g.selectAll(".bar")
        .data(data)
        .enter().append("rect")
        .attr("x", (d: any) => x(d.label)!)
        .attr("y", (d: any) => y(d.value))
        .attr("width", x.bandwidth())
        .attr("height", (d: any) => adjustedHeight - y(d.value))
        .attr("fill", (d, i) => config.colors[i % config.colors.length])
        .attr("stroke", (d, i) => i === hoveredIndex ? "#FFD700" : "none")
        .attr("stroke-width", (d, i) => i === hoveredIndex ? 2 : 0)
        .style("filter", (d, i) => i === hoveredIndex ? "drop-shadow(0 0 3px rgba(255, 215, 0, 0.5))" : "none")
        .attr("rx", 2)
        .on("mouseover", (event: any, d: any) => {
          const i = data.indexOf(d);
          setHoveredIndex(i);
          showTooltip(event, d.label, getTooltipItems(d));
        })
        .on("mouseout", () => {
          setHoveredIndex(null);
          hideTooltip();
        });

      g.append("g")
        .attr("transform", `translate(0,${adjustedHeight})`)
        .call(d3.axisBottom(x).tickFormat(() => "")) // Hide labels
        .attr("color", labelColor);

      g.append("g")
        .call(d3.axisLeft(y).ticks(5))
        .attr("color", labelColor)
        .selectAll("text")
        .style("font-size", "10px");

      drawAxisLabels();
    };

    // HORIZONTAL BAR CHART
    const drawHorizontalBarChart = () => {
      const y = d3.scaleBand()
        .domain(data.map(d => d.label))
        .range([0, adjustedHeight])
        .padding(0.3);

      const x = d3.scaleLinear()
        .domain([0, d3.max(data, (d: any) => d.value) as number])
        .range([0, contentWidth]).nice();

      drawGrids(x, y);

      g.selectAll(".bar")
        .data(data)
        .enter().append("rect")
        .attr("x", 0)
        .attr("y", (d: any) => y(d.label)!)
        .attr("width", (d: any) => x(d.value))
        .attr("height", y.bandwidth())
        .attr("fill", (d, i) => config.colors[i % config.colors.length])
        .attr("stroke", (d, i) => i === hoveredIndex ? "#FFD700" : "none")
        .attr("stroke-width", (d, i) => i === hoveredIndex ? 2 : 0)
        .style("filter", (d, i) => i === hoveredIndex ? "drop-shadow(0 0 3px rgba(255, 215, 0, 0.5))" : "none")
        .attr("rx", 2)
        .on("mouseover", (event: any, d: any) => {
          const i = data.indexOf(d);
          setHoveredIndex(i);
          showTooltip(event, d.label, getTooltipItems(d));
        })
        .on("mouseout", () => {
          setHoveredIndex(null);
          hideTooltip();
        });

      g.append("g")
        .call(d3.axisLeft(y).tickFormat(() => "")) // Hide labels on y-axis for horizontal bars too
        .attr("color", labelColor);

      g.append("g")
        .attr("transform", `translate(0,${adjustedHeight})`)
        .call(d3.axisBottom(x).ticks(5))
        .attr("color", labelColor)
        .selectAll("text")
        .style("font-size", "10px");

      drawAxisLabels();
    };

    // LINE CHART
    const drawLineChart = () => {
      const isNumericalX =
        metadata?.structure?.x_axis?.type === 'numerical' ||
        metadata?.graph?.structure?.x_axis?.type === 'numerical';

      const isCategoricalX =
        metadata?.structure?.x_axis?.type === 'categorical' ||
        metadata?.graph?.structure?.x_axis?.type === 'categorical';

      // 1. Setup Scales
      let x: any;
      const xData = data.map(d => d.label || d.x);

      if (isNumericalX && !isCategoricalX) {
        const xExtent = d3.extent(data, d => parseFloat(d.label || d.x)) as [number, number];
        const xPadding = (xExtent[1] - xExtent[0]) * 0.05 || 1;
        x = d3.scaleLinear()
          .domain([xExtent[0] - xPadding, xExtent[1] + xPadding])
          .range([0, contentWidth]).nice();
      } else {
        // Categorical or default to Points
        x = d3.scalePoint()
          .domain(xData.map(d => d.toString()))
          .range([0, contentWidth])
          .padding(0.2);
      }

      let yMax = 0;
      if (config.keys && config.keys.length > 0) {
        data.forEach((d: any) => {
          config.keys.forEach(k => {
            const val = parseFloat(d[k]);
            if (!isNaN(val)) yMax = Math.max(yMax, val);
          });
        });
      } else {
        yMax = d3.max(data, (d: any) => d.y || d.value) as number;
      }

      const y = d3.scaleLinear()
        .domain([0, yMax * 1.1])
        .range([adjustedHeight, 0]).nice();

      drawGrids(x, y);

      // 2. Draw Lines & Points
      const keys = config.keys.length > 0 ? config.keys : ["Value"];

      keys.forEach((key, i) => {
        const seriesColor = config.colors[i % config.colors.length];

        const line = d3.line<any>()
          .x(d => x((d.label || d.x).toString()))
          .y(d => y(config.keys.length > 0 ? d[key] : (d.y || d.value)));

        // Path
        g.append("path")
          .datum(data)
          .attr("fill", "none")
          .attr("stroke", seriesColor)
          .attr("stroke-width", 2.5)
          .attr("stroke-linejoin", "round")
          .attr("stroke-linecap", "round")
          .attr("d", line);

        // Dots
        g.selectAll(`.dot-${i}`)
          .data(data)
          .enter().append("circle")
          .attr("cx", (d: any) => x((d.label || d.x).toString()))
          .attr("cy", (d: any) => y(config.keys.length > 0 ? d[key] : (d.y || d.value)))
          .attr("r", 4.5)
          .attr("fill", seriesColor)
          .attr("stroke", isDark ? "#1e293b" : "#fff")
          .attr("stroke-width", 1.5)
          .on("mouseover", (event: any, d: any) => showTooltip(event, (d.label || d.x).toString(), getTooltipItems(d)))
          .on("mouseout", hideTooltip);
      });

      // 3. Axes
      const xAxis = d3.axisBottom(x);
      if (isNumericalX && !isCategoricalX) {
        (xAxis as d3.Axis<any>).tickFormat(d3.format("d")); // No commas for years/integers
      }

      g.append("g")
        .attr("transform", `translate(0,${adjustedHeight})`)
        .call(xAxis)
        .attr("color", labelColor)
        .selectAll("text")
        .style("font-size", "10px");

      g.append("g")
        .call(d3.axisLeft(y).ticks(5))
        .attr("color", labelColor)
        .selectAll("text")
        .style("font-size", "10px");

      // Legend removed from SVG

      drawAxisLabels();
    };

    // AREA CHART
    const drawAreaChart = () => {
      const xExtent = d3.extent(data, (d: any) => d.x) as [number, number];
      const yExtent = d3.extent(data, (d: any) => d.y) as [number, number];

      const xRange = xExtent[1] - xExtent[0];
      const yRange = yExtent[1] - yExtent[0];
      const xPadding = xRange * 0.1 || 1;
      const yPadding = yRange * 0.1 || 1;

      const x = d3.scaleLinear().domain([Math.max(0, xExtent[0] - xPadding), xExtent[1] + xPadding]).range([0, contentWidth]).nice();
      const y = d3.scaleLinear().domain([Math.max(0, yExtent[0] - yPadding), yExtent[1] + yPadding]).range([adjustedHeight, 0]).nice();

      drawGrids(x, y);

      const area = d3.area<any>()
        .x(d => x(d.x))
        .y0(adjustedHeight)
        .y1(d => y(d.y));

      g.append("path")
        .datum(data)
        .attr("fill", config.colors[0])
        .attr("fill-opacity", isDark ? 0.3 : 0.2)
        .attr("d", area);

      const line = d3.line<any>()
        .x(d => x(d.x))
        .y(d => y(d.y));

      g.append("path")
        .datum(data)
        .attr("fill", "none")
        .attr("stroke", config.colors[0])
        .attr("stroke-width", 2)
        .attr("d", line);

      // Dots for tooltips
      g.selectAll(".dot")
        .data(data)
        .enter().append("circle")
        .attr("cx", (d: any) => x(d.x))
        .attr("cy", (d: any) => y(d.y))
        .attr("r", 5)
        .attr("fill", config.colors[0])
        .attr("stroke", isDark ? "#1e293b" : "#fff")
        .attr("stroke-width", 1.5)
        .style("opacity", 0) // Hidden until hover or just keep it invisible for hover area
        .on("mouseover", (event: any, d: any) => showTooltip(event, (d.label || d.x).toString(), getTooltipItems(d)))
        .on("mouseout", hideTooltip)
        .transition().duration(500).style("opacity", 1);

      g.append("g").attr("transform", `translate(0,${adjustedHeight})`).call(d3.axisBottom(x)).attr("color", labelColor);
      g.append("g").call(d3.axisLeft(y)).attr("color", labelColor);

      drawAxisLabels();
    };

    // SCATTER CHART
    const drawScatterChart = () => {
      const xExt = d3.extent(data, (d: any) => d.x) as [number, number];
      const yExt = d3.extent(data, (d: any) => d.y) as [number, number];
      const xP = (xExt[1] - xExt[0]) * 0.1 || 1;
      const yP = (yExt[1] - yExt[0]) * 0.1 || 1;

      const x = d3.scaleLinear().domain([Math.max(0, xExt[0] - xP), xExt[1] + xP]).range([0, contentWidth]).nice();
      const y = d3.scaleLinear().domain([Math.max(0, yExt[0] - yP), yExt[1] + yP]).range([adjustedHeight, 0]).nice();

      drawGrids(x, y);

      g.selectAll("dot")
        .data(data)
        .enter()
        .append("circle")
        .attr("cx", (d: any) => x(d.x))
        .attr("cy", (d: any) => y(d.y))
        .attr("r", 5)
        .style("fill", config.colors[0])
        .style("opacity", 0.75)
        .style("stroke", isDark ? "#1e293b" : "#fff")
        .on("mouseover", (event: any, d: any) => showTooltip(event, "Data Point", [{ name: "X", value: d.x }, { name: "Y", value: d.y, color: config.colors[0] }]))
        .on("mouseout", hideTooltip);

      g.append("g").attr("transform", `translate(0,${adjustedHeight})`).call(d3.axisBottom(x)).attr("color", labelColor);
      g.append("g").call(d3.axisLeft(y)).attr("color", labelColor);

      drawAxisLabels();
    };

    // PIE CHART
    const drawPieChart = () => {
      const radius = Math.min(contentWidth, adjustedHeight) / 2;
      const pieG = g.append("g").attr("transform", `translate(${contentWidth / 2},${adjustedHeight / 2})`);

      const pie = d3.pie<any>().value((d: any) => d.value);
      const arc = d3.arc<any>()
        .innerRadius(chartType.includes("donut") ? radius * 0.6 : 0)
        .outerRadius(radius)
        .padAngle(0.02)
        .cornerRadius(4);

      const arcs = pieG.selectAll("arc")
        .data(pie(data))
        .enter()
        .append("g")
        .attr("class", "arc");

      arcs.append("path")
        .attr("d", arc)
        .attr("fill", (d, i) => config.colors[i % config.colors.length])
        .attr("stroke", (d, i) => i === hoveredIndex ? "#FFD700" : (isDark ? "#1e293b" : "#fff"))
        .style("stroke-width", (d, i) => i === hoveredIndex ? "2.5px" : "1px")
        .style("filter", (d, i) => i === hoveredIndex ? "drop-shadow(0 0 4px rgba(255, 215, 0, 0.6))" : "none")
        .on("mouseover", (event: any, d: any) => {
          setHoveredIndex(d.index);
          showTooltip(event, d.data.label, [{ name: "Value", value: d.data.value, color: config.colors[d.index % config.colors.length] }]);
        })
        .on("mouseout", () => {
          setHoveredIndex(null);
          hideTooltip();
        });

      // Legend removed from SVG
    };

    // STACKED BAR CHART
    const drawStackedBarChart = () => {
      if (!config.keys.length) return;

      const x = d3.scaleBand()
        .domain(data.map(d => d.label))
        .range([0, contentWidth])
        .padding(0.3);

      const stackedData = d3.stack().keys(config.keys)(data);
      const yMax = d3.max(stackedData, layer => d3.max(layer, d => d[1])) as number;
      const y = d3.scaleLinear().domain([0, yMax]).range([adjustedHeight, 0]).nice();

      drawGrids(x, y);

      const color = d3.scaleOrdinal().domain(config.keys).range(config.colors) as unknown as d3.ScaleOrdinal<string, string>;

      g.selectAll("g.layer")
        .data(stackedData)
        .enter().append("g")
        .attr("fill", (d) => color(d.key))
        .selectAll("rect")
        .data(d => d)
        .enter().append("rect")
        .attr("x", (d: any) => x(d.data.label)!)
        .attr("y", d => y(d[1]))
        .attr("height", d => y(d[0]) - y(d[1]))
        .attr("width", x.bandwidth())
        .attr("rx", 1)
        .on("mouseover", (event: any, d: any) => showTooltip(event, d.data.label, getTooltipItems(d.data)))
        .on("mouseout", hideTooltip);

      g.append("g").attr("transform", `translate(0,${adjustedHeight})`).call(d3.axisBottom(x).tickFormat(() => "")).attr("color", labelColor);
      g.append("g").call(d3.axisLeft(y)).attr("color", labelColor);

      drawAxisLabels();
    };

    if (chartType.includes("horizontal")) drawHorizontalBarChart();
    else if (chartType.includes("bar") && config.keys.length > 0) drawStackedBarChart();
    else if (chartType.includes("bar")) drawBarChart();
    else if (chartType.includes("line")) drawLineChart();
    else if (chartType.includes("scatter")) drawScatterChart();
    else if (chartType.includes("pie") || chartType.includes("donut")) drawPieChart();
    else if (chartType.includes("area")) drawAreaChart();
    else drawBarChart();

  }, [chartType, data, config, dimensions]);


  return (
    <div ref={containerRef} className="w-full relative p-6 bg-card rounded-xl border border-border shadow-sm">
      <div
        className="d3-tooltip absolute bg-popover/95 backdrop-blur-sm text-popover-foreground text-[11px] font-medium px-2.5 py-1.5 rounded-lg shadow-xl border border-border pointer-events-none opacity-0 transition-opacity z-[100]"
      />
      <div className="flex flex-col items-center w-full">
        <svg
          ref={svgRef}
          width={dimensions.width}
          height={(chartType.includes("pie") || chartType.includes("donut") || chartType.includes("bar")) ? 280 : dimensions.height}
          className="max-w-full overflow-visible"
        />

        {legendItems.length > 0 && (
          <div className="mt-2 grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-x-6 gap-y-1.5 w-full pt-3 border-t border-border/40">
            {legendItems.map((item, i) => (
              <div
                key={i}
                className={`flex items-center gap-2 group cursor-default transition-opacity ${hoveredIndex !== null && hoveredIndex !== i ? 'opacity-40' : 'opacity-100'}`}
                onMouseEnter={() => setHoveredIndex(i)}
                onMouseLeave={() => setHoveredIndex(null)}
              >
                <div
                  className={`size-1.5 rounded-[1px] flex-shrink-0 shadow-sm transition-all ${hoveredIndex === i ? 'scale-125 ring-2 ring-[#FFD700]/30' : ''}`}
                  style={{ backgroundColor: item.color }}
                />
                <span className={`text-[9px] font-bold transition-colors truncate uppercase tracking-tight ${hoveredIndex === i ? 'text-foreground' : 'text-muted-foreground/70'}`} title={item.label}>
                  {item.label}
                </span>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default DynamicChartRenderer;