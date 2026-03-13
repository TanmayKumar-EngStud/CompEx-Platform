import { useMemo } from "react";
import katex from "katex";
import "katex/dist/katex.min.css";

/**
 * KaTeX math renderer component
 * 
 * This component handles the actual rendering of mathematical expressions
 * using KaTeX. It's loaded lazily to improve initial bundle size.
 */

interface MathRendererProps {
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
}

/**
 * Renders mathematical expressions using KaTeX
 * 
 * Uses useMemo to optimize re-rendering of complex mathematical expressions.
 * Handles rendering errors gracefully by falling back to raw text.
 * 
 * @param expression - LaTeX mathematical expression to render
 * @param displayMode - Whether to render in block or inline mode
 * @param className - Additional CSS classes
 * @returns JSX element with rendered math
 */
function MathRenderer({ 
   expression, 
   displayMode = false, 
   className = "" 
}: MathRendererProps) {
   const renderedMath = useMemo(() => {
      try {
         // Configure KaTeX options for optimal rendering
         const options = {
            displayMode,
            throwOnError: false, // Don't throw on rendering errors
            errorColor: "#cc0000", // Red color for error text
            strict: "warn" as const, // Warn on deprecated commands
            trust: false, // Don't trust user input
            macros: {
               // Define common macros for better performance
               "\\RR": "\\mathbb{R}",
               "\\NN": "\\mathbb{N}",
               "\\ZZ": "\\mathbb{Z}",
               "\\QQ": "\\mathbb{Q}",
               "\\CC": "\\mathbb{C}",
            },
         };

         return katex.renderToString(expression, options);
      } catch (error) {
         // Log error for debugging but don't crash the component
         console.warn("KaTeX rendering error:", error);
         return null;
      }
   }, [expression, displayMode]);

   // If rendering failed, fall back to raw expression
   if (!renderedMath) {
      return <span className={`font-mono text-red-600 ${className}`}>{expression}</span>;
   }

   return (
      <span
         className={className}
         dangerouslySetInnerHTML={{ __html: renderedMath }}
      />
   );
}

export default MathRenderer;