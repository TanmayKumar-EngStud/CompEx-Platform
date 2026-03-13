import React, { useState, useEffect } from "react";
import {
   ScatterChart,
   Scatter,
   XAxis,
   YAxis,
   CartesianGrid,
   ResponsiveContainer,
   Label,
   Tooltip,
} from "recharts";
import { useTheme } from "next-themes";

interface ScatterPlotTemplateProps {
   metadata: {
      description: string;
      graph: any;
   };
}

const ScatterPlotTemplate: React.FC<ScatterPlotTemplateProps> = ({
   metadata,
}) => {
   const { resolvedTheme } = useTheme();
   const [mounted, setMounted] = useState(false);

   useEffect(() => {
      setMounted(true);
   }, []);

   // Transform the data into the format Recharts expects
   const chartData = metadata.graph.data.map((point: any) => ({
      x: point.x,
      y: point.y,
   }));

   // Theme-aware colors
   const dotColor =
      resolvedTheme === "dark" ? "hsl(var(--chart-1))" : "#8884d8";

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
               <ScatterChart
                  margin={{
                     top: 20,
                     right: 60,
                     left: 60,
                     bottom: 40,
                  }}
               >
                  <CartesianGrid
                     strokeDasharray="3 3"
                     stroke={resolvedTheme === "dark" ? "#374151" : "#e5e7eb"}
                  />
                  <XAxis
                     type="number"
                     dataKey="x"
                     tick={{
                        fill: resolvedTheme === "dark" ? "#9ca3af" : "#4b5563",
                     }}
                  >
                     <Label
                        value={metadata.graph.xAxis || metadata.graph["x-axis"]}
                        position="bottom"
                        offset={20}
                        style={{
                           fill:
                              resolvedTheme === "dark" ? "#f3f4f6" : "#1f2937",
                        }}
                     />
                  </XAxis>
                  <YAxis
                     type="number"
                     dataKey="y"
                     tick={{
                        fill: resolvedTheme === "dark" ? "#9ca3af" : "#4b5563",
                     }}
                  >
                     <Label
                        value={metadata.graph.yAxis || metadata.graph["y-axis"]}
                        angle={-90}
                        position="insideBottomLeft"
                        offset={0}
                        style={{
                           fill:
                              resolvedTheme === "dark" ? "#f3f4f6" : "#1f2937",
                        }}
                     />
                  </YAxis>
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
                  <Scatter data={chartData} fill={dotColor} shape="circle" />
               </ScatterChart>
            </ResponsiveContainer>
         </div>
         <h3 className="text-center font-medium mb-9 text-foreground">
            {metadata.graph.title}
         </h3>
      </div>
   );
};

export default ScatterPlotTemplate;
