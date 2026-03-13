import React, { useState, useEffect } from "react";
import {
   BarChart,
   Bar,
   XAxis,
   YAxis,
   CartesianGrid,
   Tooltip,
   Legend,
   ResponsiveContainer,
} from "recharts";
import { useTheme } from "next-themes";

interface StackedBarChartTemplateProps {
   metadata: any;
}

const StackedBarChartTemplate: React.FC<StackedBarChartTemplateProps> = ({
   metadata,
}) => {
   const { resolvedTheme } = useTheme();
   const [mounted, setMounted] = useState(false);

   useEffect(() => {
      setMounted(true);
   }, []);

   // Transform the data for recharts
   const categories = metadata.graph.data.map((item: any) => item.category);
   const strategicPillars = metadata.graph.data[0].values.map(
      (item: any) => item.strategic_pillar
   );

   // Create data structure for stacked bar chart
   const chartData = strategicPillars.map((pillar: string, index: number) => {
      const dataPoint: any = {
         name: pillar,
      };

      // Add values for each team/category
      metadata.graph.data.forEach((team: any) => {
         dataPoint[team.category] = team.values[index].value;
      });

      return dataPoint;
   });

   // Generate theme-aware colors for bars
   const COLORS =
      resolvedTheme === "dark"
         ? [
              "hsl(var(--chart-1))",
              "hsl(var(--chart-2))",
              "hsl(var(--chart-3))",
              "hsl(var(--chart-4))",
              "hsl(var(--chart-5))",
              "#4B5563",
           ]
         : ["#60A5FA", "#34D399", "#A78BFA", "#F472B6", "#FBBF24", "#4B5563"];

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
                  <Legend
                     wrapperStyle={{
                        color: resolvedTheme === "dark" ? "#f3f4f6" : "#1f2937",
                     }}
                  />
                  {categories.map((category: string, index: number) => (
                     <Bar
                        key={category}
                        dataKey={category}
                        stackId="a"
                        fill={COLORS[index % COLORS.length]}
                     />
                  ))}
               </BarChart>
            </ResponsiveContainer>
         </div>
         <h3 className="text-center font-medium mb-4 text-foreground">
            {metadata.graph.title}
         </h3>
      </div>
   );
};

export default StackedBarChartTemplate;
