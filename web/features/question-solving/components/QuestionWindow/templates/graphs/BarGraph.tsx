import React, { useState, useEffect } from "react";
import {
   BarChart,
   Bar,
   XAxis,
   YAxis,
   CartesianGrid,
   Tooltip,
   ResponsiveContainer,
} from "recharts";
import { useTheme } from "next-themes";

interface BarGraphTemplateProps {
   metadata: any;
}

const BarGraphTemplate: React.FC<BarGraphTemplateProps> = ({ metadata }) => {
   const { resolvedTheme } = useTheme();
   const [mounted, setMounted] = useState(false);

   useEffect(() => {
      setMounted(true);
   }, []);

   const chartData = metadata.graph.data.data.map(
      (value: number, index: number) => ({
         name: metadata.graph.data["x-axis"][index],
         value: value,
      })
   );

   // Theme-aware colors
   const barColor =
      resolvedTheme === "dark" ? "hsl(var(--chart-1))" : "#4299e1";

   if (!mounted) {
      return (
         <div className="flex flex-col gap-4 w-full">
            <p className="text-sm text-muted-foreground">{metadata.description}</p>
            <div className="h-[300px] w-full bg-muted/10 rounded-md animate-pulse flex items-center justify-center">
               <span className="text-muted-foreground">Loading chart...</span>
            </div>
            <h3 className="text-center font-medium mb-4 text-foreground">
               {metadata.graph.title}
            </h3>
         </div>
      );
   }

   return (
      <div className="flex flex-col gap-4 w-full">
         <p className="text-sm text-muted-foreground">{metadata.description}</p>
         <div className="h-[300px] w-full">
            <ResponsiveContainer width="100%" height="100%">
               <BarChart
                  data={chartData}
                  margin={{
                     top: 20,
                     right: 30,
                     left: 20,
                     bottom: 30,
                  }}
               >
                  <CartesianGrid
                     strokeDasharray="3 3"
                     stroke={resolvedTheme === "dark" ? "#374151" : "#e5e7eb"}
                  />
                  <XAxis
                     dataKey="name"
                     label={{
                        value: metadata.graph.data.xAxis,
                        position: "bottom",
                        offset: 0,
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
                     ticks={metadata.graph.data["y-axis"]}
                     label={{
                        value: metadata.graph.data.yAxis,
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
                  <Bar dataKey="value" fill={barColor} />
               </BarChart>
            </ResponsiveContainer>
         </div>
         <h3 className="text-center font-medium text-foreground">
            {metadata.graph.data.title}
         </h3>
      </div>
   );
};

export default BarGraphTemplate;
