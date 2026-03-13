/**
 * Enhanced Pagination Controls Component
 *
 * Provides pagination controls with smooth loading states, section awareness,
 * and integration with the intelligent caching system.
 */

import React from "react";
import { Button } from "@/shared/components/ui/button";
import {
   Select,
   SelectContent,
   SelectItem,
   SelectTrigger,
   SelectValue,
} from "@/shared/components/ui/select";
import { PaginationLoadingState } from "../LoadingStates";

interface PaginationControlsProps {
   currentPage: number;
   totalPages: number;
   totalQuestions: number;
   questionsPerPage: number;
   onPageChange: (page: number) => void;
   onPageSizeChange?: (pageSize: number) => void;
   isLoading?: boolean;
   loadingType?: "navigation" | "filter" | "section" | "general";
   className?: string;
   showPageSizeSelector?: boolean;
   showQuickJump?: boolean;
   disabled?: boolean;
}

export const PaginationControls: React.FC<PaginationControlsProps> = ({
   currentPage,
   totalPages,
   totalQuestions,
   questionsPerPage,
   onPageChange,
   onPageSizeChange,
   isLoading = false,
   loadingType = "navigation",
   className = "",
   showPageSizeSelector = true,
   showQuickJump = true,
   disabled = false,
}) => {
   const [jumpToPage, setJumpToPage] = React.useState("");

   const startQuestion = (currentPage - 1) * questionsPerPage + 1;
   const endQuestion = Math.min(currentPage * questionsPerPage, totalQuestions);

   const handlePrevious = () => {
      if (currentPage > 1 && !isLoading && !disabled) {
         onPageChange(currentPage - 1);
      }
   };

   const handleNext = () => {
      if (currentPage < totalPages && !isLoading && !disabled) {
         onPageChange(currentPage + 1);
      }
   };

   const handleJumpToPage = () => {
      const pageNum = parseInt(jumpToPage);
      if (pageNum >= 1 && pageNum <= totalPages && pageNum !== currentPage) {
         onPageChange(pageNum);
         setJumpToPage("");
      }
   };

   const handlePageSizeChange = (newPageSize: string) => {
      if (onPageSizeChange) {
         onPageSizeChange(parseInt(newPageSize));
      }
   };

   // Generate page buttons for quick access
   const getPageButtons = () => {
      const buttons = [];
      const maxButtons = 5;
      let startPage = Math.max(1, currentPage - Math.floor(maxButtons / 2));
      let endPage = Math.min(totalPages, startPage + maxButtons - 1);

      // Adjust start if we're near the end
      if (endPage - startPage < maxButtons - 1) {
         startPage = Math.max(1, endPage - maxButtons + 1);
      }

      // Add first page and ellipsis if needed
      if (startPage > 1) {
         buttons.push(
            <Button
               key="1"
               variant={1 === currentPage ? "default" : "outline"}
               size="sm"
               onClick={() => onPageChange(1)}
               disabled={isLoading || disabled}
               className="min-w-[40px]"
            >
               1
            </Button>
         );
         if (startPage > 2) {
            buttons.push(
               <span key="ellipsis1" className="px-2 text-muted-foreground">
                  ...
               </span>
            );
         }
      }

      // Add page buttons
      for (let i = startPage; i <= endPage; i++) {
         buttons.push(
            <Button
               key={i}
               variant={i === currentPage ? "default" : "outline"}
               size="sm"
               onClick={() => onPageChange(i)}
               disabled={isLoading || disabled}
               className="min-w-[40px]"
            >
               {i}
            </Button>
         );
      }

      // Add last page and ellipsis if needed
      if (endPage < totalPages) {
         if (endPage < totalPages - 1) {
            buttons.push(
               <span key="ellipsis2" className="px-2 text-muted-foreground">
                  ...
               </span>
            );
         }
         buttons.push(
            <Button
               key={totalPages}
               variant={totalPages === currentPage ? "default" : "outline"}
               size="sm"
               onClick={() => onPageChange(totalPages)}
               disabled={isLoading || disabled}
               className="min-w-[40px]"
            >
               {totalPages}
            </Button>
         );
      }

      return buttons;
   };

   if (isLoading) {
      return (
         <div
            className={`bg-background/50 backdrop-blur-sm border rounded-lg p-4 ${className}`}
         >
            <PaginationLoadingState type={loadingType} />
         </div>
      );
   }

   return (
      <div className={`flex items-center justify-between p-4 ${className}`}>
         {/* Left: Page size selector in "X / page" format */}
         {showPageSizeSelector && (
            <div className="flex items-center gap-2">
               <Select
                  value={questionsPerPage.toString()}
                  onValueChange={handlePageSizeChange}
                  disabled={disabled}
               >
                  <SelectTrigger className="w-16 h-10">
                     <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                     <SelectItem value="5">5</SelectItem>
                     <SelectItem value="10">10</SelectItem>
                     <SelectItem value="20">20</SelectItem>
                     <SelectItem value="50">50</SelectItem>
                  </SelectContent>
               </Select>
               <span className="text-sm text-muted-foreground">/ page</span>
            </div>
         )}

         {/* Center: Showing X-Y of Z questions */}
         <div className="text-sm text-muted-foreground">
            Showing {startQuestion}-{endQuestion} of {totalQuestions} questions
         </div>

         {/* Right: Page navigation */}
         <div className="flex items-center gap-1">
            {/* Previous button */}
            <Button
               variant="outline"
               size="sm"
               onClick={handlePrevious}
               disabled={currentPage <= 1 || disabled}
               className="px-3"
            >
               &lt;
            </Button>

            {/* Page buttons */}
            {getPageButtons()}

            {/* Next button */}
            <Button
               variant="outline"
               size="sm"
               onClick={handleNext}
               disabled={currentPage >= totalPages || disabled}
               className="px-3"
            >
               &gt;
            </Button>
         </div>
      </div>
   );
};
