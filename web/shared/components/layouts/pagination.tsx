"use client";

import React from "react";
import { usePaginationStore } from "@/shared/stores/problems";
import { Button } from "@/shared/components/ui/button";
import {
   Select,
   SelectContent,
   SelectItem,
   SelectTrigger,
   SelectValue,
} from "@/shared/components/ui/select";

const Pagination = ({
   totalProblems,
}: {
   totalProblems: number | undefined;
}) => {
   const { page, pageSize, setPage, setPageSize } = usePaginationStore();
   const totalPages =
      pageSize > 0 ? Math.ceil((totalProblems ?? 0) / pageSize) : 0;

   const pageNumbers = [];
   for (let i = 1; i <= totalPages; i++) {
      pageNumbers.push(i);
   }

   return (
      <div className="flex items-center justify-between p-4">
         <div className="flex items-center space-x-4">
            <span className="text-sm text-muted-foreground">
               {pageSize} / page
            </span>
            <Select
               onValueChange={(value) => {
                  const newPageSize = Number(value);
                  if (newPageSize !== pageSize) {
                     setPageSize(newPageSize);
                  }
               }}
               defaultValue={pageSize.toString()}
            >
               <SelectTrigger className="w-[100px]">
                  <SelectValue />
               </SelectTrigger>
               <SelectContent>
                  <SelectItem value="10">10</SelectItem>
                  <SelectItem value="20">20</SelectItem>
                  <SelectItem value="50">50</SelectItem>
               </SelectContent>
            </Select>
         </div>
         <div className="flex items-center space-x-2">
            <Button
               variant="outline"
               size="sm"
               onClick={() => setPage(page - 1)}
               disabled={page === 1}
            >
               &lt;
            </Button>
            {pageNumbers.map((number) => (
               <Button
                  key={number}
                  variant={page === number ? "default" : "outline"}
                  size="sm"
                  onClick={() => setPage(number)}
               >
                  {number}
               </Button>
            ))}
            <Button
               variant="outline"
               size="sm"
               onClick={() => setPage(page + 1)}
               disabled={page === totalPages}
            >
               &gt;
            </Button>
         </div>
      </div>
   );
};

export default Pagination;
