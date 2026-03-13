import React, { memo } from "react";
import { QuestionProps } from "./questionDisplay";

/**
 * Memoized question display component
 * 
 * Implements strategic memoization to prevent unnecessary re-renders
 * of the question display component, which can be expensive due to
 * math rendering and complex template components.
 */

/**
 * Custom comparison function for React.memo
 * 
 * Implements shallow comparison for props that affect rendering.
 * This prevents unnecessary re-renders when irrelevant props change.
 * 
 * @param prevProps - Previous props
 * @param nextProps - Next props  
 * @returns True if props are equal (skip re-render), false otherwise
 */
function arePropsEqual(prevProps: QuestionProps, nextProps: QuestionProps): boolean {
   // Critical props that always trigger re-render if changed
   if (
      prevProps.questionId !== nextProps.questionId ||
      prevProps.type !== nextProps.type ||
      prevProps.title !== nextProps.title ||
      prevProps.text !== nextProps.text ||
      prevProps.showSolution !== nextProps.showSolution ||
      prevProps.isLongOptions !== nextProps.isLongOptions
   ) {
      return false;
   }

   // Compare selected options array
   if (
      prevProps.selectedOption.length !== nextProps.selectedOption.length ||
      !prevProps.selectedOption.every((option, index) => option === nextProps.selectedOption[index])
   ) {
      return false;
   }

   // Compare correct options array (if provided)
   if (prevProps.correctOption && nextProps.correctOption) {
      if (
         prevProps.correctOption.length !== nextProps.correctOption.length ||
         !prevProps.correctOption.every((option, index) => option === nextProps.correctOption?.[index])
      ) {
         return false;
      }
   } else if (prevProps.correctOption !== nextProps.correctOption) {
      return false;
   }

   // Deep comparison for options object
   const prevOptionsKeys = Object.keys(prevProps.options);
   const nextOptionsKeys = Object.keys(nextProps.options);
   
   if (prevOptionsKeys.length !== nextOptionsKeys.length) {
      return false;
   }

   for (const key of prevOptionsKeys) {
      if (
         !nextProps.options[key] ||
         prevProps.options[key].optiontext !== nextProps.options[key].optiontext
      ) {
         return false;
      }
   }

   // Compare metadata and solution (shallow comparison)
   if (prevProps.metadata !== nextProps.metadata) {
      return false;
   }

   if (prevProps.solution !== nextProps.solution) {
      return false;
   }

   // Compare pagination-related props
   if (
      prevProps.showPagination !== nextProps.showPagination ||
      prevProps.size !== nextProps.size
   ) {
      return false;
   }

   // Compare question IDs array
   if (prevProps.questionIds && nextProps.questionIds) {
      if (
         prevProps.questionIds.length !== nextProps.questionIds.length ||
         !prevProps.questionIds.every((id, index) => {
            const prevId = id;
            const nextId = nextProps.questionIds?.[index];
            
            // Handle both number and object types
            if (typeof prevId === 'number' && typeof nextId === 'number') {
               return prevId === nextId;
            }
            
            if (typeof prevId === 'object' && typeof nextId === 'object') {
               return JSON.stringify(prevId) === JSON.stringify(nextId);
            }
            
            return false;
         })
      ) {
         return false;
      }
   } else if (prevProps.questionIds !== nextProps.questionIds) {
      return false;
   }

   // All checks passed - props are considered equal
   return true;
}

/**
 * Memoized version of QuestionDisplay component
 * 
 * This wrapper provides intelligent memoization for the QuestionDisplay component
 * to prevent expensive re-renders when props haven't meaningfully changed.
 * 
 * Key optimizations:
 * - Custom comparison function focuses on props that affect rendering
 * - Prevents re-renders from function reference changes
 * - Optimizes for common prop change patterns
 * 
 * @param props - Question display props
 * @returns Memoized question display component
 */
export const MemoizedQuestionDisplay = memo<QuestionProps>((props) => {
   // Import the actual QuestionDisplay component dynamically
   // This allows us to wrap it without circular dependencies
   const QuestionDisplay = require("./questionDisplay").default;
   
   return <QuestionDisplay {...props} />;
}, arePropsEqual);

// Set display name for React DevTools
MemoizedQuestionDisplay.displayName = "MemoizedQuestionDisplay";

export default MemoizedQuestionDisplay;