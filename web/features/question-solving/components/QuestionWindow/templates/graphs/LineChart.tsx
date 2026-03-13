import React, { useState, useEffect } from "react";
import {
   LineChart,
   Line,
   XAxis,
   YAxis,
   CartesianGrid,
   Tooltip,
   Legend,
   ResponsiveContainer,
} from "recharts";
import { useTheme } from "next-themes";

interface LineChartTemplateProps {
   metadata: {
      description: string;
      graph: {
         data: any[];
         title: string;
         type: string;
         "x-axis": string;
         "y-axis": string;
      };
   };
}

const LineChartTemplate: React.FC<LineChartTemplateProps> = ({ metadata }) => {
   const { resolvedTheme } = useTheme();
   const [mounted, setMounted] = useState(false);

   useEffect(() => {
      setMounted(true);
   }, []);

   // Transform the data for recharts
   const transformedData = metadata.graph.data.map((item) => {
      const dataPoint: any = {
         name: item.x,
      };

      // Add values for each series
      item.series.forEach((series: any) => {
         dataPoint[series.name] = series.value;
      });

      return dataPoint;
   });

   // Get all series names
   const seriesNames = metadata.graph.data[0].series.map((s: any) => s.name);

   // Generate theme-aware colors for each series
   const colors =
      resolvedTheme === "dark"
         ? [
              "hsl(var(--chart-1))",
              "hsl(var(--chart-2))",
              "hsl(var(--chart-3))",
              "hsl(var(--chart-4))",
              "hsl(var(--chart-5))",
           ]
         : ["#8884d8", "#82ca9d", "#ffc658", "#ff7300", "#00C49F"];

   if (!mounted) {
      return (
         <div className="flex flex-col gap-4 w-full">
            <p className="text-sm text-muted-foreground">{metadata.description}</p>
            <div className="h-[400px] w-full bg-muted/10 rounded-md animate-pulse flex items-center justify-center">
               <span className="text-muted-foreground">Loading chart...</span>
            </div>
            <h3 className="text-center font-medium text-foreground">
               {metadata.graph.title}
            </h3>
         </div>
      );
   }

   return (
      <div className="flex flex-col gap-4 w-full">
         <p className="text-sm text-muted-foreground">{metadata.description}</p>
         <div className="h-[400px] w-full">
            <ResponsiveContainer width="100%" height="100%">
               <LineChart
                  data={transformedData}
                  margin={{
                     top: 20,
                     right: 30,
                     left: 20,
                     bottom: 20,
                  }}
               >
                  <CartesianGrid
                     strokeDasharray="3 3"
                     stroke={resolvedTheme === "dark" ? "#374151" : "#e5e7eb"}
                  />
                  <XAxis
                     dataKey="name"
                     label={{
                        value: metadata.graph["x-axis"],
                        position: "bottom",
                        style: {
                           fill:
                              resolvedTheme === "dark" ? "#f3f4f6" : "#1f2937",
                        },
                     }}
                     tick={{
                        fill: resolvedTheme === "dark" ? "#9ca3af" : "#4b5563",
                     }}
                  />
                  <YAxis
                     label={{
                        value: metadata.graph["y-axis"],
                        angle: -90,
                        position: "insideLeft",
                        style: {
                           fill:
                              resolvedTheme === "dark" ? "#f3f4f6" : "#1f2937",
                        },
                     }}
                     tick={{
                        fill: resolvedTheme === "dark" ? "#9ca3af" : "#4b5563",
                     }}
                  />
                  <Tooltip
                     contentStyle={{
                        backgroundColor:
                           resolvedTheme === "dark"
                              ? "rgba(31, 41, 55, 0.9)"
                              : "rgba(255, 255, 255, 0.9)",
                        border:
                           resolvedTheme === "dark"
                              ? "1px solid #374151"
                              : "1px solid #e2e8f0",
                        borderRadius: "6px",
                        color: resolvedTheme === "dark" ? "#f3f4f6" : "#1f2937",
                     }}
                     cursor={false}
                  />
                  <Legend
                     wrapperStyle={{
                        color: resolvedTheme === "dark" ? "#f3f4f6" : "#1f2937",
                     }}
                  />
                  {seriesNames.map((name: string, index: number) => (
                     <Line
                        key={name}
                        type="monotone"
                        dataKey={name}
                        stroke={colors[index % colors.length]}
                        activeDot={{ r: 8 }}
                        strokeWidth={2}
                     />
                  ))}
               </LineChart>
            </ResponsiveContainer>
         </div>
         <h3 className="text-center font-medium text-foreground">
            {metadata.graph.title}
         </h3>
      </div>
   );
};

export default LineChartTemplate;
