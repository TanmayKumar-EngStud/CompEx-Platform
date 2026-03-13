import { NextRequest, NextResponse } from "next/server";

/**
 * Performance metrics collection endpoint
 * 
 * Collects Web Vitals and other performance metrics from client-side
 * for analysis and monitoring purposes.
 */

interface PerformanceMetric {
   metric: string;
   value: number;
   id: string;
   url: string;
   timestamp: number;
   userAgent?: string;
   connection?: string;
}

interface MetricsResponse {
   success: boolean;
   message: string;
   metricsReceived: number;
}

/**
 * POST /api/metrics - Collect performance metrics
 * 
 * Request Body:
 * {
 *   metric: string,
 *   value: number,
 *   id: string,
 *   url: string,
 *   timestamp: number
 * }
 */
export async function POST(req: NextRequest): Promise<NextResponse<MetricsResponse>> {
   try {
      const body: PerformanceMetric = await req.json();
      
      // Validate required fields
      const requiredFields = ['metric', 'value', 'id', 'url', 'timestamp'];
      const missingFields = requiredFields.filter(field => !(field in body));
      
      if (missingFields.length > 0) {
         return NextResponse.json(
            {
               success: false,
               message: `Missing required fields: ${missingFields.join(', ')}`,
               metricsReceived: 0
            },
            { status: 400 }
         );
      }

      // Extract additional metadata
      const userAgent = req.headers.get('user-agent') || '';
      const enrichedMetric: PerformanceMetric = {
         ...body,
         userAgent,
         connection: req.headers.get('connection-type') || 'unknown',
      };

      // Log metric for development
      if (process.env.NODE_ENV === 'development') {
         console.log('📊 Performance Metric Received:', {
            metric: enrichedMetric.metric,
            value: Math.round(enrichedMetric.value * (enrichedMetric.metric === 'CLS' ? 1000 : 1)),
            url: enrichedMetric.url,
            rating: getMetricRating(enrichedMetric.metric, enrichedMetric.value),
         });
      }

      // TODO: Store metrics in database or send to monitoring service
      // Example database storage:
      // await storeMetricInDatabase(enrichedMetric);
      
      // TODO: Send to external monitoring service
      // await sendToMonitoringService(enrichedMetric);

      // For now, just acknowledge receipt
      return NextResponse.json({
         success: true,
         message: 'Metric received successfully',
         metricsReceived: 1
      });

   } catch (error) {
      console.error('Error processing performance metric:', error);
      return NextResponse.json(
         {
            success: false,
            message: 'Internal server error processing metric',
            metricsReceived: 0
         },
         { status: 500 }
      );
   }
}

/**
 * GET /api/metrics - Retrieve performance metrics summary
 * 
 * Query Parameters:
 * - timeframe: string - Time period (1h, 24h, 7d, 30d)
 * - metric: string - Specific metric to filter (CLS, FID, LCP, etc.)
 * - url: string - Filter by specific URL pattern
 */
export async function GET(req: NextRequest) {
   const searchParams = req.nextUrl.searchParams;
   const timeframe = searchParams.get('timeframe') || '24h';
   const metric = searchParams.get('metric');
   const url = searchParams.get('url');

   try {
      // TODO: Implement metrics retrieval from database
      // const metrics = await getMetricsFromDatabase({ timeframe, metric, url });

      // Mock response for now
      const mockMetrics = {
         summary: {
            timeframe,
            totalSamples: 0,
            averages: {
               CLS: 0,
               FID: 0,
               LCP: 0,
               FCP: 0,
               TTFB: 0,
            },
            ratings: {
               good: 0,
               needsImprovement: 0,
               poor: 0,
            }
         },
         message: 'Metrics endpoint implemented - database integration pending'
      };

      return NextResponse.json(mockMetrics);

   } catch (error) {
      console.error('Error retrieving metrics:', error);
      return NextResponse.json(
         { error: 'Internal server error retrieving metrics' },
         { status: 500 }
      );
   }
}

/**
 * Get performance rating based on metric thresholds
 */
function getMetricRating(metric: string, value: number): 'good' | 'needs-improvement' | 'poor' {
   const thresholds: Record<string, { good: number; poor: number }> = {
      CLS: { good: 0.1, poor: 0.25 },
      FID: { good: 100, poor: 300 },
      FCP: { good: 1800, poor: 3000 },
      LCP: { good: 2500, poor: 4000 },
      TTFB: { good: 800, poor: 1800 },
      INP: { good: 200, poor: 500 },
   };

   const threshold = thresholds[metric];
   if (!threshold) return 'good';

   if (value <= threshold.good) return 'good';
   if (value <= threshold.poor) return 'needs-improvement';
   return 'poor';
}