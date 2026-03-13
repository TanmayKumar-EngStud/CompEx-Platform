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

interface GroupedBarChartTemplateProps {
   metadata: any;
}

const GroupedBarChartTemplate: React.FC<GroupedBarChartTemplateProps> = ({
   metadata,
}) => {
   const { resolvedTheme } = useTheme();
   const [mounted, setMounted] = useState(false);

   useEffect(() => {
      setMounted(true);
   }, []);

   // Transform the data for recharts
   const chartData: any[] = [];
   const years: string[] = [];

   // Extract all years from the first data item
   if (metadata.graph?.data?.length > 0) {
      const firstItem = metadata.graph.data[0];
      // Get all keys except 'category'
      Object.keys(firstItem).forEach((key) => {
         if (key !== "category" && !isNaN(parseInt(key))) {
            years.push(key);
         }
      });
   }

   // Transform data into the format recharts expects
   metadata.graph.data.forEach((item: any) => {
      const dataPoint: any = {
         name: item.category,
      };

      // Add each year's value
      years.forEach((year) => {
         dataPoint[year] = item[year];
      });

      chartData.push(dataPoint);
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
           ]
         : ["#60A5FA", "#34D399", "#A78BFA", "#F472B6", "#FBBF24"];

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
                     formatter={(value) => [`${value}%`, "Return"]}
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
                  {years.map((year, index) => (
                     <Bar
                        key={year}
                        dataKey={year}
                        name={`${year}`}
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

export default GroupedBarChartTemplate;
