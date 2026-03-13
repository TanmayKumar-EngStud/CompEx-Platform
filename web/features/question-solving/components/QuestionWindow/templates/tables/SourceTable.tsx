import React from "react";
import {
   Table,
   TableBody,
   TableCell,
   TableHead,
   TableHeader,
   TableRow,
} from "@/shared/components/ui/table";

interface SourceTableProps {
   tableData: {
      columns: string[];
      rows: string[];
      data: any[][];
      table_name?: string;
      type: string;
   };
   description?: string;
}

const SourceTable: React.FC<SourceTableProps> = ({
   tableData,
   description,
}) => {
   return (
      <div className="flex flex-col gap-4">
         {tableData.table_name && (
            <h3 className="text-md font-semibold">{tableData.table_name}</h3>
         )}
         {description && <p className="text-sm text-gray-600">{description}</p>}

         <div className="overflow-x-auto rounded-lg border border-slate-300 dark:border-slate-500/50">
            <Table>
               <TableHeader>
                  <TableRow className="border-b border-slate-300 dark:border-slate-500/50 bg-muted/50">
                     {/* Empty cell for row headers */}
                     <TableHead className="font-bold border-r border-slate-300 dark:border-slate-500/50"></TableHead>
                     {tableData.columns.map((column, index) => (
                        <TableHead
                           key={index}
                           className={`font-bold text-center border-r border-slate-300 dark:border-slate-500/50 ${index === tableData.columns.length - 1 ? "border-r-0" : ""}`}
                        >
                           {column}
                        </TableHead>
                     ))}
                  </TableRow>
               </TableHeader>
               <TableBody>
                  {tableData.rows.map((row, rowIndex) => (
                     <TableRow key={rowIndex} className="border-b border-slate-200 dark:border-slate-700/50 last:border-b-0">
                        {/* Row header */}
                        <TableCell className="font-medium border-r border-slate-200 dark:border-slate-700/50">{row}</TableCell>
                        {/* Row data */}
                        {tableData.data[rowIndex].map((cell, cellIndex) => (
                           <TableCell key={cellIndex} className={`text-center border-r border-slate-200 dark:border-slate-700/50 ${cellIndex === tableData.data[rowIndex].length - 1 ? "border-r-0" : ""}`}>
                              {formatCellValue(cell)}
                           </TableCell>
                        ))}
                     </TableRow>
                  ))}
               </TableBody>
            </Table>
         </div>
      </div>
   );
};

// Helper function to format cell values
const formatCellValue = (value: any) => {
   if (typeof value === "number") {
      // Check if it's a percentage
      if (value <= 1 && value > 0) {
         return `${(value * 100).toFixed(1)}%`;
      }
      return value.toLocaleString();
   }
   return value;
};

export default SourceTable;
