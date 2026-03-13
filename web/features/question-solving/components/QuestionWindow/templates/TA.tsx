import React from "react";
import TS_TAQuestion from "./TS-TA";
import SortableTable from "./tables/SortableTable";

interface TAQuestionProps {
   text: string;
   metadata: any;
}

export const TAQuestion: React.FC<TAQuestionProps> = ({ text, metadata }) => {
   console.log("TA QUESTION DEBUG:", {
      textSnippet: text.slice(0, 50),
      metadataKeys: metadata ? Object.keys(metadata) : 'null',
      fullMetadata: metadata
   });
   // Safety check: metadata might be undefined or structure might vary
   if (!metadata) return <div>{text}</div>;

   // Flexible extraction: check for 'tables' array, 'table' object, 'Table' key, 
   // or the very specific metadata[0].Table structure shown in logs.
   let tableData: any = null;

   if (Array.isArray(metadata.metadata) && metadata.metadata.length > 0 && metadata.metadata[0].Table) {
      // Structure: metadata: [ { Table: { ... } } ]
      tableData = metadata.metadata[0].Table;
   } else if (Array.isArray(metadata.tables) && metadata.tables.length > 0) {
      tableData = metadata.tables[0];
   } else if (metadata.table) {
      tableData = metadata.table;
   } else if (metadata.Table) {
      tableData = metadata.Table;
   } else if (metadata.structure && (metadata.structure.columns || metadata.structure.headers)) {
      // Metadata itself is the table
      tableData = metadata;
   }

   if (!tableData) {
      // Graceful fallback if no table found - but log for debug
      console.error("TA UI: Could not find table data in metadata", metadata);
      return <div className="p-4 text-red-500">Error: Table data not found. Check console for logs.</div>;
   }

   const type = tableData.type;
   if (type === "time-series table") {
      return (
         <>
            <p className="mb-4">{text}</p>
            <TS_TAQuestion text={text} metadata={metadata} />
         </>
      );
   }

   // Normalize headers and rows for SortableTable
   let headers: string[] = [];
   let rows: (string | number)[][] = [];

   // Case 1: Standard 'headers' and 'rows' (from Table object)
   if (tableData.headers && tableData.rows) {
      headers = tableData.headers;
      rows = tableData.rows;
   }
   // Case 2: Standard 'columns' and 'data' (legacy/other)
   else if (tableData.columns && tableData.data) {
      headers = tableData.columns.map((c: any) => typeof c === 'string' ? c : Object.keys(c)[0]);
      rows = tableData.data;
   }
   // Case 3: 'structure' object
   else if (tableData.structure) {
      const s = tableData.structure;
      headers = s.headers || s.columns || [];
      rows = s.rows || s.data || [];
   }
   // Case 4: Legacy 'data_columns'
   else if (tableData.data_columns && tableData.data) {
      headers = tableData.data_columns.map((c: any) => typeof c === 'string' ? c : Object.keys(c)[0]);
      rows = tableData.data;
   }

   return (
      <div className="flex flex-col gap-6">
         <div className="text-sm font-medium leading-relaxed">{text}</div>
         <SortableTable
            headers={headers}
            rows={rows}
            title={tableData.title || (tableData.structure && tableData.structure.title)}
         />
      </div>
   );
};

export default TAQuestion;
