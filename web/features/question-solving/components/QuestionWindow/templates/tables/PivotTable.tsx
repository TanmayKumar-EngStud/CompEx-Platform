import {
   Table,
   TableBody,
   TableCell,
   TableHead,
   TableHeader,
   TableRow,
} from "@/shared/components/ui/table";

interface PivotTableProps {
   metadata: any;
}

const PivotTable: React.FC<PivotTableProps> = ({ metadata }) => {
   // Helper function to format numbers
   const formatValue = (value: number) => {
      if (typeof value === "number") {
         return value > 1000 ? value.toLocaleString() : value.toString();
      }
      return value;
   };

   // Extract the properly structured data from metadata
   const structure = (metadata as any)?.table || (metadata as any)?.structure || metadata || {};

   let columns: string[] = [],
      data: Record<string, Record<string, any>> = {},
      index: string[] = [],
      description = metadata?.description || structure?.description || "";

   if (structure.data_matrix) {
      // Dummy data structure: row_headers, column_headers, data_matrix
      columns = structure.column_headers || [];
      index = structure.row_headers || [];

      // Transform matrix to Record structure
      data = {};
      index.forEach((rowKey, rowIdx) => {
         data[rowKey] = {};
         columns.forEach((colKey, colIdx) => {
            data[rowKey][colKey] = structure.data_matrix[rowIdx]?.[colIdx];
         });
      });
   } else if ("graph" in metadata) {
      columns = metadata.graph.columns || [];
      data = metadata.graph.data || {};
      index = metadata.graph.index || [];
   } else {
      columns = metadata.columns || [];
      data = metadata.data || {};
      index = metadata.index || [];
   }

   return (
      <div className="flex flex-col gap-4 w-full">
         <div className="overflow-x-auto rounded-xl border border-slate-300 dark:border-slate-500/50 bg-muted/5">
            <Table>
               <TableHeader>
                  <TableRow className="bg-muted/30 border-b border-slate-300 dark:border-slate-500/50 hover:bg-muted/30">
                     <TableHead className="font-semibold text-[10px] uppercase tracking-widest text-muted-foreground py-4 pl-6 text-left border-r border-slate-300 dark:border-slate-500/50">
                        {/* Empty corner cell */}
                     </TableHead>
                     {columns.map((column: string, colIdx: number) => (
                        <TableHead
                           key={column}
                           className={`font-semibold text-[10px] uppercase tracking-widest text-muted-foreground py-4 text-center ${colIdx < columns.length - 1 ? "border-r border-slate-300 dark:border-slate-500/50" : ""}`}
                        >
                           {column}
                        </TableHead>
                     ))}
                  </TableRow>
               </TableHeader>
               <TableBody>
                  {index?.map((rowKey: string, rowIdx: number) => (
                     <TableRow
                        key={rowKey}
                        className={`hover:bg-muted/20 transition-all group ${rowIdx < index.length - 1 ? "border-b border-slate-300 dark:border-slate-500/50" : ""}`}
                     >
                        <TableCell className="py-4 text-[13px] font-semibold text-foreground/80 pl-6 text-left border-r border-slate-300 dark:border-slate-500/50">
                           {rowKey}
                        </TableCell>
                        {columns.map((column: string, colIdx: number) => {
                           const value = data[rowKey]?.[column];
                           return (
                              <TableCell
                                 key={`${rowKey}-${column}`}
                                 className={`py-4 text-[13px] text-center text-muted-foreground group-hover:text-foreground/70 ${colIdx < columns.length - 1 ? "border-r border-slate-300 dark:border-slate-500/50" : ""}`}
                              >
                                 {value !== undefined ? formatValue(value) : "—"}
                              </TableCell>
                           );
                        })}
                     </TableRow>
                  ))}
               </TableBody>
            </Table>
         </div>
      </div>
   );
};

export default PivotTable;
