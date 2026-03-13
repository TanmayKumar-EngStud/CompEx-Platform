import React from "react";
import { Alert, AlertDescription } from "@/shared/components/feedback/alert";

/**
 * Default template for unknown question types
 * 
 * Provides a fallback when a specific template is not available
 * for a question type. Shows basic question structure.
 */

interface DefaultTemplateProps {
   type?: string;
   title?: string;
   text?: string;
   options?: { [key: string]: { optiontext: string } };
   selectedOption?: string[];
   handleOptionClick?: (option: string | string[]) => void;
   metadata?: any;
   [key: string]: any;
}

function DefaultTemplate({
   type = "Unknown",
   title = "Question",
   text = "",
   options = {},
   selectedOption = [],
   handleOptionClick,
   metadata,
   ...props
}: DefaultTemplateProps) {
   return (
      <div className="space-y-4 p-4">
         {/* Warning about unknown template */}
         <Alert className="border-amber-200 bg-amber-50 dark:border-amber-800 dark:bg-amber-950">
            <AlertDescription className="text-amber-800 dark:text-amber-200">
               <strong>Template Not Found:</strong> Using default template for question type "{type}".
               This question may not display correctly.
            </AlertDescription>
         </Alert>

         {/* Question title */}
         {title && (
            <div className="border-b pb-2">
               <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100">
                  {title}
               </h3>
               <p className="text-sm text-gray-500 dark:text-gray-400">
                  Question Type: {type}
               </p>
            </div>
         )}

         {/* Question text */}
         {text && (
            <div className="prose prose-sm max-w-none dark:prose-invert">
               <div dangerouslySetInnerHTML={{ __html: text }} />
            </div>
         )}

         {/* Metadata display (if any) */}
         {metadata && (
            <div className="bg-gray-50 dark:bg-gray-800 p-3 rounded-lg">
               <h4 className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Additional Information:
               </h4>
               <pre className="text-xs text-gray-600 dark:text-gray-400 whitespace-pre-wrap">
                  {JSON.stringify(metadata, null, 2)}
               </pre>
            </div>
         )}

         {/* Basic options display */}
         {Object.keys(options).length > 0 && (
            <div className="space-y-2">
               <h4 className="text-sm font-medium text-gray-700 dark:text-gray-300">
                  Options:
               </h4>
               <div className="space-y-2">
                  {Object.entries(options).map(([key, option]) => (
                     <div
                        key={key}
                        className={`p-3 border rounded-lg cursor-pointer transition-colors ${
                           selectedOption.includes(option.optiontext)
                              ? "border-blue-500 bg-blue-50 dark:bg-blue-950"
                              : "border-gray-200 dark:border-gray-700 hover:border-gray-300 dark:hover:border-gray-600"
                        }`}
                        onClick={() => handleOptionClick?.(option.optiontext)}
                     >
                        <div className="flex items-center space-x-2">
                           <div
                              className={`w-4 h-4 rounded-full border-2 ${
                                 selectedOption.includes(option.optiontext)
                                    ? "border-blue-500 bg-blue-500"
                                    : "border-gray-300 dark:border-gray-600"
                              }`}
                           />
                           <span className="text-sm text-gray-700 dark:text-gray-300">
                              {key}: {option.optiontext}
                           </span>
                        </div>
                     </div>
                  ))}
               </div>
            </div>
         )}

         {/* Debug information in development */}
         {process.env.NODE_ENV === "development" && (
            <details className="mt-4">
               <summary className="text-xs text-gray-500 cursor-pointer">
                  Debug Information
               </summary>
               <pre className="mt-2 text-xs text-gray-400 bg-gray-100 dark:bg-gray-800 p-2 rounded">
                  {JSON.stringify(props, null, 2)}
               </pre>
            </details>
         )}
      </div>
   );
}

export default DefaultTemplate;