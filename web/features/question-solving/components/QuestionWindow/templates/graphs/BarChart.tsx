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

interface BarChartTemplateProps {
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

const BarChartTemplate: React.FC<BarChartTemplateProps> = ({ metadata }) => {
   const { resolvedTheme } = useTheme();
   const [mounted, setMounted] = useState(false);

   useEffect(() => {
      setMounted(true);
   }, []);

   // Transform the data for recharts
   const chartData = metadata.graph.data.map((item) => ({
      name: item.label,
      value: item.value,
   }));

   // Theme-aware bar color
   const barColor =
      resolvedTheme === "dark" ? "hsl(var(--chart-1))" : "#60A5FA";

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
                        value: metadata.graph["x-axis"],
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
                  <Bar dataKey="value" fill={barColor} />
               </BarChart>
            </ResponsiveContainer>
         </div>
         <h3 className="text-center font-medium mb-4 text-foreground">
            {metadata.graph.title}
         </h3>
      </div>
   );
};

export default BarChartTemplate;
