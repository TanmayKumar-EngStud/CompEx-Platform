import { lazy, Suspense } from "react";
import { ChartSkeleton } from "@/shared/components/feedback/ChartSkeleton";

/**
 * Lazy-loaded chart components for optimal bundle size
 * 
 * These components are loaded on-demand to reduce initial bundle size.
 * Recharts is a heavy library (~400KB) so we only load chart types as needed.
 */

// Lazy load all chart components
export const LazyBarChart = lazy(() => import("./BarChart"));
export const LazyBarGraph = lazy(() => import("./BarGraph"));
export const LazyGroupedBarChart = lazy(() => import("./GroupedBarChart"));
export const LazyLineChart = lazy(() => import("./LineChart"));
export const LazyLineGraph = lazy(() => import("./LineGraph"));
export const LazyPieChart = lazy(() => import("./PieChart"));
export const LazyScatterPlot = lazy(() => import("./ScatterPlot"));
export const LazyStackedBarChart = lazy(() => import("./StackedBarChart"));

/**
 * Chart component props interface
 */
interface ChartComponentProps {
   data?: any;
   width?: number;
   height?: number;
   [key: string]: any;
}

/**
 * Wrapper component for lazy-loaded charts with consistent loading states
 */
interface LazyChartWrapperProps extends ChartComponentProps {
   ChartComponent: React.LazyExoticComponent<React.ComponentType<any>>;
   fallbackText?: string;
}

function LazyChartWrapper({ 
   ChartComponent, 
   fallbackText = "Loading chart...",
   ...props 
}: LazyChartWrapperProps) {
   return (
      <Suspense fallback={<ChartSkeleton text={fallbackText} />}>
         <ChartComponent {...props} />
      </Suspense>
   );
}

// Convenient wrapper components with loading states
export function LazyBarChartWithSuspense(props: ChartComponentProps) {
   return (
      <LazyChartWrapper
         ChartComponent={LazyBarChart}
         fallbackText="Loading bar chart..."
         {...props}
      />
   );
}

export function LazyBarGraphWithSuspense(props: ChartComponentProps) {
   return (
      <LazyChartWrapper
         ChartComponent={LazyBarGraph}
         fallbackText="Loading bar graph..."
         {...props}
      />
   );
}

export function LazyGroupedBarChartWithSuspense(props: ChartComponentProps) {
   return (
      <LazyChartWrapper
         ChartComponent={LazyGroupedBarChart}
         fallbackText="Loading grouped bar chart..."
         {...props}
      />
   );
}

export function LazyLineChartWithSuspense(props: ChartComponentProps) {
   return (
      <LazyChartWrapper
         ChartComponent={LazyLineChart}
         fallbackText="Loading line chart..."
         {...props}
      />
   );
}

export function LazyLineGraphWithSuspense(props: ChartComponentProps) {
   return (
      <LazyChartWrapper
         ChartComponent={LazyLineGraph}
         fallbackText="Loading line graph..."
         {...props}
      />
   );
}

export function LazyPieChartWithSuspense(props: ChartComponentProps) {
   return (
      <LazyChartWrapper
         ChartComponent={LazyPieChart}
         fallbackText="Loading pie chart..."
         {...props}
      />
   );
}

export function LazyScatterPlotWithSuspense(props: ChartComponentProps) {
   return (
      <LazyChartWrapper
         ChartComponent={LazyScatterPlot}
         fallbackText="Loading scatter plot..."
         {...props}
      />
   );
}

export function LazyStackedBarChartWithSuspense(props: ChartComponentProps) {
   return (
      <LazyChartWrapper
         ChartComponent={LazyStackedBarChart}
         fallbackText="Loading stacked bar chart..."
         {...props}
      />
   );
}

/**
 * Chart type enum for dynamic chart selection
 */
export enum ChartType {
   BAR_CHART = "BarChart",
   BAR_GRAPH = "BarGraph", 
   GROUPED_BAR_CHART = "GroupedBarChart",
   LINE_CHART = "LineChart",
   LINE_GRAPH = "LineGraph",
   PIE_CHART = "PieChart",
   SCATTER_PLOT = "ScatterPlot",
   STACKED_BAR_CHART = "StackedBarChart"
}

/**
 * Dynamic chart component selector
 * 
 * Renders the appropriate chart component based on chart type.
 * Only loads the specific chart component needed.
 * 
 * @param chartType - Type of chart to render
 * @param props - Props to pass to the chart component
 * @returns JSX element for the selected chart
 */
export function DynamicChart({ 
   chartType, 
   ...props 
}: { chartType: ChartType } & ChartComponentProps) {
   switch (chartType) {
      case ChartType.BAR_CHART:
         return <LazyBarChartWithSuspense {...props} />;
      case ChartType.BAR_GRAPH:
         return <LazyBarGraphWithSuspense {...props} />;
      case ChartType.GROUPED_BAR_CHART:
         return <LazyGroupedBarChartWithSuspense {...props} />;
      case ChartType.LINE_CHART:
         return <LazyLineChartWithSuspense {...props} />;
      case ChartType.LINE_GRAPH:
         return <LazyLineGraphWithSuspense {...props} />;
      case ChartType.PIE_CHART:
         return <LazyPieChartWithSuspense {...props} />;
      case ChartType.SCATTER_PLOT:
         return <LazyScatterPlotWithSuspense {...props} />;
      case ChartType.STACKED_BAR_CHART:
         return <LazyStackedBarChartWithSuspense {...props} />;
      default:
         return <ChartSkeleton text="Unsupported chart type" />;
   }
}