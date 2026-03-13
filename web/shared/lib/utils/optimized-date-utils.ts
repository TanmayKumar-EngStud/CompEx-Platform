/**
 * Optimized date utilities for better tree-shaking
 * 
 * This file provides specific date-fns imports to improve bundle size
 * by only including the functions we actually use.
 */

// Specific imports for better tree-shaking
import {
  startOfMonth,
  endOfMonth,
  startOfWeek,
  endOfWeek,
  addDays,
  format,
  addMonths,
  subMonths,
  isSameMonth,
  isSameDay,
  isToday,
  isAfter,
  isBefore,
  parseISO,
} from "date-fns";

/**
 * Re-export specific date functions for use throughout the app
 * 
 * This approach reduces bundle size compared to importing from
 * the main date-fns package which includes all functions.
 */
export {
   startOfMonth,
   endOfMonth,
   startOfWeek,
   endOfWeek,
   addDays,
   format,
   addMonths,
   subMonths,
   isSameMonth,
   isSameDay,
   isToday,
   isAfter,
   isBefore,
   parseISO,
};

/**
 * Common date utilities for the application
 */
export const dateUtils = {
   startOfMonth,
   endOfMonth,
   startOfWeek,
   endOfWeek,
   addDays,
   format,
   addMonths,
   subMonths,
   isSameMonth,
   isSameDay,
   isToday,
   isAfter,
   isBefore,
   parseISO,
} as const;

/**
 * Commonly used date formats
 */
export const DATE_FORMATS = {
   DISPLAY: "MMM d, yyyy",
   INPUT: "yyyy-MM-dd",
   FULL: "EEEE, MMMM d, yyyy",
   SHORT: "MM/dd/yy",
   ISO: "yyyy-MM-dd'T'HH:mm:ssxxx",
} as const;

/**
 * Utility function to format dates consistently
 * 
 * @param date - Date to format
 * @param formatString - Format string or predefined format
 * @returns Formatted date string
 */
export function formatDate(
   date: Date | string | number,
   formatString: string = DATE_FORMATS.DISPLAY
): string {
   const dateObj = typeof date === "string" ? parseISO(date) : new Date(date);
   return format(dateObj, formatString);
}