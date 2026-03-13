/**
 * Truly lazy-loaded Bar Chart component
 * 
 * This component dynamically imports Recharts only when rendered
 */

import React, { useState, useEffect } from "react";
import { useTheme } from "next-themes";

interface BarChartTemplateProps {
   metadata: {
      description: string;
      graph: {
         data: Array<{ [key: string]: any }>;
         x_axis: string;
         y_axis: string;
      };
   };
}

const LazyBarChartDynamic: React.FC<BarChartTemplateProps> = ({ metadata }) => {
   const [RechartsComponents, setRechartsComponents] = useState<any>(null);
   const [loading, setLoading] = useState(true);
   const { theme } = useTheme();

   useEffect(() => {
      // Dynamically import Recharts only when this component renders
      import('recharts').then((recharts) => {
         setRechartsComponents({
            BarChart: recharts.BarChart,
            Bar: recharts.Bar,
            XAxis: recharts.XAxis,
            YAxis: recharts.YAxis,
            CartesianGrid: recharts.CartesianGrid,
            Tooltip: recharts.Tooltip,
            ResponsiveContainer: recharts.ResponsiveContainer,
         });
         setLoading(false);
      }).catch((error) => {
         console.error('Failed to load Recharts:', error);
         setLoading(false);
      });
   }, []);

   if (loading || !RechartsComponents) {
      return (
         <div className="flex items-center justify-center h-64 bg-gray-100 dark:bg-gray-800 rounded-lg">
            <div className="text-center">
               <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500 mx-auto mb-2"></div>
               <p className="text-gray-600 dark:text-gray-400">Loading bar chart...</p>
            </div>
         </div>
      );
   }

   const { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } = RechartsComponents;

   const data = metadata?.graph?.data || [];
   const xAxisKey = metadata?.graph?.x_axis || Object.keys(data[0] || {})[0];
   const yAxisKey = metadata?.graph?.y_axis || Object.keys(data[0] || {})[1];

   return (
      <div className="w-full">
         <h3 className="text-lg font-semibold mb-4 text-center">
            {metadata?.description || "Bar Chart"}
         </h3>
         <div style={{ width: "100%", height: 400 }}>
            <ResponsiveContainer>
               <BarChart data={data} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis 
                     dataKey={xAxisKey}
                     tick={{ fill: theme === "dark" ? "#e5e7eb" : "#374151" }}
                  />
                  <YAxis 
                     tick={{ fill: theme === "dark" ? "#e5e7eb" : "#374151" }}
                  />
                  <Tooltip 
                     contentStyle={{
                        backgroundColor: theme === "dark" ? "#1f2937" : "#ffffff",
                        border: `1px solid ${theme === "dark" ? "#374151" : "#d1d5db"}`,
                        borderRadius: "8px",
                        color: theme === "dark" ? "#e5e7eb" : "#374151"
                     }}
                  />
                  <Bar 
                     dataKey={yAxisKey} 
                     fill={theme === "dark" ? "#3b82f6" : "#2563eb"}
                     radius={[4, 4, 0, 0]}
                  />
               </BarChart>
            </ResponsiveContainer>
         </div>
      </div>
   );
};

export default LazyBarChartDynamic;