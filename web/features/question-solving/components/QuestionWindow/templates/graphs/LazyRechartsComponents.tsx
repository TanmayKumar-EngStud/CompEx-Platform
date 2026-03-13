/**
 * Lazy-loaded Recharts components
 * 
 * This file creates truly lazy-loaded chart components by dynamically importing
 * Recharts only when needed. This prevents Recharts from being bundled in the main chunk.
 */

import React, { lazy, Suspense, ComponentType } from 'react';
import { ChartSkeleton } from "@/shared/components/feedback/ChartSkeleton";

// Define interfaces for chart props
interface ChartProps {
  metadata: any;
  [key: string]: any;
}

// Create a higher-order component for truly lazy loading
function createLazyChartComponent(chartType: string) {
  return function LazyChartWrapper(props: ChartProps) {
    return (
      <Suspense fallback={<ChartSkeleton text={`Loading ${chartType.toLowerCase()}...`} />}>
        <DynamicChartRenderer chartType={chartType} {...props} />
      </Suspense>
    );
  };
}

// Dynamic chart renderer that imports everything at runtime
const DynamicChartRenderer = React.memo(({ chartType, ...props }: { chartType: string } & ChartProps) => {
  const [ChartComponent, setChartComponent] = React.useState<ComponentType<any> | null>(null);
  const [loading, setLoading] = React.useState(true);
  const [error, setError] = React.useState<string | null>(null);

  React.useEffect(() => {
    let mounted = true;

    const loadChart = async () => {
      try {
        // Import chart implementation dynamically
        const chartModule = await import(`./Dynamic${chartType}`);
        
        if (mounted) {
          setChartComponent(() => chartModule.default);
          setLoading(false);
        }
      } catch (err) {
        console.error(`Failed to load ${chartType}:`, err);
        if (mounted) {
          setError(`Failed to load ${chartType}`);
          setLoading(false);
        }
      }
    };

    loadChart();

    return () => {
      mounted = false;
    };
  }, [chartType]);

  if (loading) {
    return <ChartSkeleton text={`Loading ${chartType.toLowerCase()}...`} />;
  }

  if (error || !ChartComponent) {
    return (
      <div className="flex items-center justify-center h-64 bg-red-50 dark:bg-red-900/20 rounded-lg">
        <p className="text-red-600 dark:text-red-400">
          {error || `Failed to load ${chartType}`}
        </p>
      </div>
    );
  }

  return <ChartComponent {...props} />;
});

// Create lazy-loaded chart components
export const LazyBarChartWithRecharts = createLazyChartComponent('BarChart');
export const LazyBarGraphWithRecharts = createLazyChartComponent('BarGraph');
export const LazyGroupedBarChartWithRecharts = createLazyChartComponent('GroupedBarChart');
export const LazyLineChartWithRecharts = createLazyChartComponent('LineChart');
export const LazyLineGraphWithRecharts = createLazyChartComponent('LineGraph');
export const LazyPieChartWithRecharts = createLazyChartComponent('PieChart');
export const LazyScatterPlotWithRecharts = createLazyChartComponent('ScatterPlot');
export const LazyStackedBarChartWithRecharts = createLazyChartComponent('StackedBarChart');

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
 * Dynamic chart component selector with true lazy loading
 * 
 * Only loads Recharts when a chart is actually rendered
 */
export function DynamicChartWithRecharts({ 
  chartType, 
  ...props 
}: { chartType: ChartType } & ChartProps) {
  switch (chartType) {
    case ChartType.BAR_CHART:
      return <LazyBarChartWithRecharts {...props} />;
    case ChartType.BAR_GRAPH:
      return <LazyBarGraphWithRecharts {...props} />;
    case ChartType.GROUPED_BAR_CHART:
      return <LazyGroupedBarChartWithRecharts {...props} />;
    case ChartType.LINE_CHART:
      return <LazyLineChartWithRecharts {...props} />;
    case ChartType.LINE_GRAPH:
      return <LazyLineGraphWithRecharts {...props} />;
    case ChartType.PIE_CHART:
      return <LazyPieChartWithRecharts {...props} />;
    case ChartType.SCATTER_PLOT:
      return <LazyScatterPlotWithRecharts {...props} />;
    case ChartType.STACKED_BAR_CHART:
      return <LazyStackedBarChartWithRecharts {...props} />;
    default:
      return <ChartSkeleton text="Unsupported chart type" />;
  }
}