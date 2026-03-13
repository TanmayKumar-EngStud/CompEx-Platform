/**
 * Chart skeleton loading component
 * 
 * Provides a consistent loading state for chart components
 * while heavy libraries like Recharts are being loaded.
 */

interface ChartSkeletonProps {
   /**
    * Text to display while loading
    */
   text?: string;
   /**
    * Width of the skeleton chart area
    */
   width?: number;
   /**
    * Height of the skeleton chart area
    */
   height?: number;
   /**
    * Additional CSS classes
    */
   className?: string;
}

export function ChartSkeleton({ 
   text = "Loading chart...", 
   width = 400, 
   height = 300,
   className = ""
}: ChartSkeletonProps) {
   return (
      <div 
         className={`flex flex-col items-center justify-center bg-gray-50 dark:bg-gray-800 rounded-lg border-2 border-dashed border-gray-300 dark:border-gray-600 ${className}`}
         style={{ width, height }}
         role="status"
         aria-label={text}
      >
         {/* Chart icon placeholder */}
         <div className="mb-3">
            <svg
               className="w-12 h-12 text-gray-400 dark:text-gray-500 animate-pulse"
               fill="none"
               stroke="currentColor"
               viewBox="0 0 24 24"
               xmlns="http://www.w3.org/2000/svg"
            >
               <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={1.5}
                  d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"
               />
            </svg>
         </div>
         
         {/* Loading text */}
         <p className="text-sm text-gray-500 dark:text-gray-400 font-medium">
            {text}
         </p>
         
         {/* Loading spinner */}
         <div className="mt-2">
            <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-600"></div>
         </div>
         
         {/* Skeleton bars for visual effect */}
         <div className="mt-4 flex items-end space-x-1">
            {[1, 2, 3, 4, 5].map((i) => (
               <div
                  key={i}
                  className="bg-gray-300 dark:bg-gray-600 animate-pulse rounded-sm"
                  style={{
                     width: '8px',
                     height: `${Math.random() * 30 + 10}px`
                  }}
               />
            ))}
         </div>
      </div>
   );
}