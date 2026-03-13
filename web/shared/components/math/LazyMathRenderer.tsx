import { lazy, Suspense } from "react";

/**
 * Lazy-loaded KaTeX math renderer
 * 
 * KaTeX is a heavy library (~200KB) used for rendering mathematical expressions.
 * This component loads KaTeX on-demand to improve initial bundle size.
 */

// Lazy load the actual math renderer component
const MathRenderer = lazy(() => import("./MathRenderer"));

/**
 * Props for the math renderer component
 */
interface LazyMathRendererProps {
   /**
    * Mathematical expression to render
    */
   expression: string;
   /**
    * Whether to render in display mode (block) or inline mode
    */
   displayMode?: boolean;
   /**
    * Additional CSS classes
    */
   className?: string;
   /**
    * Fallback text while loading
    */
   fallbackText?: string;
}

/**
 * Math rendering skeleton component
 */
function MathSkeleton({ 
   expression, 
   fallbackText = "Loading math..." 
}: { 
   expression: string; 
   fallbackText?: string; 
}) {
   return (
      <div 
         className="inline-flex items-center space-x-2 text-gray-500 dark:text-gray-400 font-mono text-sm bg-gray-100 dark:bg-gray-800 px-2 py-1 rounded"
         role="status"
         aria-label={fallbackText}
      >
         {/* Math icon */}
         <svg
            className="w-4 h-4 animate-pulse"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
            xmlns="http://www.w3.org/2000/svg"
         >
            <path
               strokeLinecap="round"
               strokeLinejoin="round"
               strokeWidth={2}
               d="M9 7h6m0 10v-3m-3 3h.01M9 17h.01M9 14h.01M12 14h.01M15 11h.01M12 11h.01M9 11h.01M7 21h10a2 2 0 002-2V5a2 2 0 00-2-2H7a2 2 0 00-2 2v14a2 2 0 002 2z"
            />
         </svg>
         
         {/* Truncated expression preview */}
         <span className="truncate max-w-32">
            {expression.length > 20 ? `${expression.substring(0, 20)}...` : expression}
         </span>
         
         {/* Loading spinner */}
         <div className="animate-spin rounded-full h-3 w-3 border-b border-gray-400"></div>
      </div>
   );
}

/**
 * Lazy math renderer with suspense boundary
 * 
 * Provides a loading state while KaTeX library is being loaded.
 * Falls back to raw expression text if rendering fails.
 * 
 * @param expression - LaTeX mathematical expression to render
 * @param displayMode - Whether to render in block or inline mode
 * @param className - Additional CSS classes
 * @param fallbackText - Text to show while loading
 * @returns JSX element with rendered math or loading state
 */
export function LazyMathRenderer({ 
   expression, 
   displayMode = false, 
   className = "",
   fallbackText = "Loading math..."
}: LazyMathRendererProps) {
   // Don't load KaTeX for simple expressions without math symbols
   const hasMathSymbols = /[\\${}^_]/.test(expression);
   
   if (!hasMathSymbols) {
      return <span className={className}>{expression}</span>;
   }

   return (
      <Suspense 
         fallback={<MathSkeleton expression={expression} fallbackText={fallbackText} />}
      >
         <MathRenderer 
            expression={expression}
            displayMode={displayMode}
            className={className}
         />
      </Suspense>
   );
}