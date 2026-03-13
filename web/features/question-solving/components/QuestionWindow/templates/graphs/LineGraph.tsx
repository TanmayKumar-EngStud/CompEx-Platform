import React from "react";
import {
   LineChart,
   Line,
   XAxis,
   YAxis,
   CartesianGrid,
   Tooltip,
   ResponsiveContainer,
   Label,
} from "recharts";
import { useTheme } from "next-themes";

interface LineGraphData {
   data: {
      label: string;
      value: number[];
   }[];
   "x-axis": string[];
   "y-axis": number[];
   title: string;
   xAxis: string;
   yAxis: string;
}

interface LineGraphTemplateProps {
   metadata: {
      description: string;
      graph: {
         data: LineGraphData;
         type: string;
      };
   };
}

const LineGraphTemplate: React.FC<LineGraphTemplateProps> = ({ metadata }) => {
   const { resolvedTheme } = useTheme();

   // Transform the data into the format Recharts expects
   const chartData = metadata.graph.data.data.map((value, index) => ({
      name: value.label,
      value: value,
   }));

   // Theme-aware colors
   const lineColor =
      resolvedTheme === "dark" ? "hsl(var(--chart-1))" : "#8884d8";
   const dotFill = resolvedTheme === "dark" ? "hsl(var(--chart-1))" : "#8884d8";
   const dotStroke = resolvedTheme === "dark" ? "#1f2937" : "#FFFFFF";

   return (
      <div className="flex flex-col gap-4 w-full">
         <p className="text-sm text-muted-foreground">{metadata.description}</p>
         <div className="h-[400px] w-full">
            <ResponsiveContainer width="100%" height="100%">
               <LineChart
                  data={chartData}
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
                     dataKey="name"
                     tick={{
                        fill: resolvedTheme === "dark" ? "#9ca3af" : "#666",
                     }}
                  >
                     <Label
                        value={metadata.graph.data.xAxis}
                        position="bottom"
                        offset={20}
                        style={{
                           fill:
                              resolvedTheme === "dark" ? "#f3f4f6" : "#1f2937",
                        }}
                     />
                  </XAxis>
                  <YAxis
                     domain={[0, "auto"]}
                     ticks={metadata.graph.data["y-axis"]}
                     tick={{
                        fill: resolvedTheme === "dark" ? "#9ca3af" : "#666",
                     }}
                  >
                     <Label
                        value={metadata.graph.data.yAxis}
                        angle={-90}
                        position="insideLeft"
                        offset={0}
                        style={{
                           fill:
                              resolvedTheme === "dark" ? "#f3f4f6" : "#1f2937",
                        }}
                     />
                  </YAxis>
                  <Tooltip
                     formatter={(value: number) => [`${value} USD`, "Expenses"]}
                     labelFormatter={(label) => `Month: ${label}`}
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
                  <Line
                     type="monotone"
                     dataKey="value"
                     stroke={lineColor}
                     strokeWidth={2}
                     dot={{
                        fill: dotFill,
                        stroke: dotStroke,
                        strokeWidth: 2,
                        r: 4,
                     }}
                     activeDot={{
                        fill: dotFill,
                        stroke: dotStroke,
                        strokeWidth: 2,
                        r: 6,
                     }}
                  />
               </LineChart>
            </ResponsiveContainer>
         </div>
         <h3 className="text-center font-medium mb-9 text-foreground">
            {metadata.graph.data.title}
         </h3>
      </div>
   );
};

export default LineGraphTemplate;
