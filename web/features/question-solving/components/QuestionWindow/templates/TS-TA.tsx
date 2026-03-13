import React, { useEffect } from "react";
interface TS_TAProps {
   text: string;
   metadata: any;
}
import {
   Table,
   TableBody,
   TableCell,
   TableHead,
   TableHeader,
   TableRow,
} from "@/shared/components/ui/table";

export const TS_TAQuestion: React.FC<TS_TAProps> = ({ text, metadata }) => {
   const table = metadata.tables[0];
   const cols = table.data_columns.map((col: any) =>
      typeof col === "string" ? col : Object.keys(col)[0]
   );
   const columns = [table.time_column, ...cols];
   const renderTableHeaders = () => {
      return (
         <TableHeader>
            <TableRow>
               {columns.map((column: string, index: number) => (
                  <TableHead
                     key={index}
                     className="text-center font-bold text-color-black"
                  >
                     {column}
                  </TableHead>
               ))}
            </TableRow>
         </TableHeader>
      );
   };

   const renderTableBody = () => {
      return (
         <TableBody>
            {table.data.map((row: JSON, index: number) => (
               <TableRow key={index}>
                  {columns.map((colName: string, idx: number) => (
                     <TableCell
                        key={`${colName}-${index}-${idx}`}
                        className="text-center"
                     >
                        {table.data[index][colName]}
                     </TableCell>
                  ))}
               </TableRow>
            ))}
         </TableBody>
      );
   };
   return (
      <div>
         <Table>
            {renderTableHeaders()}
            {renderTableBody()}
         </Table>
      </div>
   );
};

export default TS_TAQuestion;
