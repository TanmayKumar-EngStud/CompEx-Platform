import React, { useState, useEffect } from "react";
import {
   PieChart,
   Pie,
   Cell,
   ResponsiveContainer,
   Tooltip,
   Legend,
} from "recharts";
import { useTheme } from "next-themes";

interface PieChartDataItem {
   label: string;
   color: string; // We'll keep the interface but ignore this value
   value: number;
}

interface PieChartTemplateProps {
   metadata: {
      description: string;
      graph: {
         data: PieChartDataItem[];
         title: string;
         type: string;
      };
   };
}

const RADIAN = Math.PI / 180;
const renderCustomizedLabel = ({
   cx,
   cy,
   midAngle,
   innerRadius,
   outerRadius,
   percent,
   name,
   value,
}: any) => {
   const radius = innerRadius + (outerRadius - innerRadius) * 0.5;
   const x = cx + radius * Math.cos(-midAngle * RADIAN);
   const y = cy + radius * Math.sin(-midAngle * RADIAN);

   return (
      <>
         <text
            x={x}
            y={y}
            fill="white"
            textAnchor={x > cx ? "start" : "end"}
            dominantBaseline="central"
            className="text-sm font-medium"
         >
            {`${(percent * 100).toFixed(0)}%`}
         </text>
      </>
   );
};

const PieChartTemplate: React.FC<PieChartTemplateProps> = ({ metadata }) => {
   const { resolvedTheme } = useTheme();
   const [mounted, setMounted] = useState(false);

   useEffect(() => {
      setMounted(true);
   }, []);

   // Theme-aware colors
   const COLORS =
      resolvedTheme === "dark"
         ? [
              "hsl(var(--chart-1))",
              "hsl(var(--chart-2))",
              "hsl(var(--chart-3))",
              "hsl(var(--chart-4))",
              "hsl(var(--chart-5))",
              "#4B5563",
              "#2DD4BF",
              "#FB923C",
              "#818CF8",
              "#F87171",
           ]
         : [
              "#60A5FA", // Blue
              "#34D399", // Emerald
              "#A78BFA", // Purple
              "#F472B6", // Pink
              "#FBBF24", // Amber
              "#4B5563", // Gray
              "#2DD4BF", // Teal
              "#FB923C", // Orange
              "#818CF8", // Indigo
              "#F87171", // Red
           ];

   // Transform the data but use our custom colors instead of the provided ones
   const chartData = metadata.graph.data.map((item) => ({
      name: item.label,
      value: item.value,
   }));

   if (!mounted) {
      return (
         <div className="flex flex-col gap-4 w-full">
            <p className="text-sm text-muted-foreground">{metadata.description}</p>
            <div className="h-[400px] w-full bg-muted/10 rounded-md animate-pulse flex items-center justify-center">
               <span className="text-muted-foreground">Loading chart...</span>
            </div>
            <h3 className="text-center font-medium mb-9 text-foreground">
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
               <PieChart margin={{ top: 5, right: 5, bottom: 5, left: 5 }}>
                  <Pie
                     data={chartData}
                     cx="50%"
                     cy="50%"
                     labelLine={false}
                     label={renderCustomizedLabel}
                     outerRadius={150}
                     dataKey="value"
                  >
                     {chartData.map((entry, index) => (
                        <Cell
                           key={`cell-${index}`}
                           fill={COLORS[index % COLORS.length]}
                           stroke={
                              resolvedTheme === "dark" ? "#1f2937" : "#fff"
                           }
                           strokeWidth={2}
                        />
                     ))}
                  </Pie>
                  <Tooltip
                     formatter={(value: number, label: string) => [
                        `${value}% - ${label}`,
                        "Distribution",
                     ]}
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
                        padding: "8px",
                        margin: "0",
                        color: resolvedTheme === "dark" ? "#f3f4f6" : "#1f2937",
                     }}
                     itemStyle={{
                        padding: "2px 0",
                     }}
                     cursor={false}
                  />
                  <Legend
                     layout="horizontal"
                     verticalAlign="bottom"
                     align="center"
                     wrapperStyle={{
                        paddingTop: "20px",
                        color: resolvedTheme === "dark" ? "#f3f4f6" : "#1f2937",
                     }}
                  />
               </PieChart>
            </ResponsiveContainer>
         </div>
         <h3 className="text-center font-medium mb-9 text-foreground">
            {metadata.graph.title}
         </h3>
      </div>
   );
};

export default PieChartTemplate;
