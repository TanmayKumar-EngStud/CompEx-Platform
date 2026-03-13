import React from "react";
import {
    Table,
    TableBody,
    TableCell,
    TableHead,
    TableHeader,
    TableRow,
} from "@/shared/components/ui/table";
import { Maximize2, X } from "lucide-react";
import ReactDOM from "react-dom";

interface DataTableProps {
    metadata: any;
}

const DataTable: React.FC<DataTableProps> = ({ metadata }) => {
    // Standardize metadata access to support both flat and nested structures (from GI/MSR)
    const structure =
        metadata?.table?.structure ||
        metadata?.table ||
        metadata?.structure ||
        metadata ||
        {};

    const title = structure.title || metadata.title || "";
    const description = structure.description || metadata.description || "";

    // Handle different table structures
    const getTableData = () => {
        // Structure A: headers, rows (Standard/Sortable)
        if (structure.headers && structure.rows) {
            return {
                headers: structure.headers,
                rows: structure.rows
            };
        }

        // Structure B: entities, attributes, comparison_data (Comparison)
        if (structure.entities && structure.attributes) {
            // Transform comparison table to standard rows
            // Headers: Attributes, Rows: Entities
            return {
                headers: ["", ...structure.attributes],
                rows: structure.entities.map((entity: string, idx: number) => [
                    entity,
                    ...(structure.comparison_data ? structure.comparison_data.map((col: any[]) => col[idx]) : [])
                ])
            };
        }

        // Structure C: columns, data, rows (Legacy/MSR type)
        if (structure.columns && structure.data && structure.rows) {
            return {
                headers: ["", ...structure.columns],
                rows: structure.rows.map((row: string, idx: number) => [
                    row,
                    ...(structure.data[idx] || [])
                ])
            };
        }

        return null;
    };

    const data = getTableData();

    if (!data) {
        return (
            <div className="p-4 border border-dashed rounded text-muted-foreground text-sm">
                Table data format not recognized.
            </div>
        );
    }

    const [isExpanded, setIsExpanded] = React.useState(false);
    const [mounted, setMounted] = React.useState(false);

    React.useEffect(() => {
        setMounted(true);
    }, []);

    // Helper to render the table content
    const renderTableContent = (isModal: boolean) => (
        <div className={`overflow-x-auto rounded-xl border border-slate-300 dark:border-slate-500/50 bg-muted/5 ${!isModal ? "scrollbar-thin scrollbar-thumb-muted-foreground/20 scrollbar-track-transparent" : ""}`}>
            <Table>
                <TableHeader>
                    <TableRow className="bg-muted/30 border-b border-slate-300 dark:border-slate-500/50 hover:bg-muted/30">
                        {data.headers.map((header: string, index: number) => (
                            <TableHead
                                key={index}
                                className={`font-semibold ${isModal ? "text-xs py-5" : "text-[10px] py-4"} uppercase tracking-widest text-muted-foreground ${index === 0 ? "text-left pl-6" : "text-center"} ${index < data.headers.length - 1 ? "border-r border-slate-300 dark:border-slate-500/50" : ""}`}
                            >
                                {header}
                            </TableHead>
                        ))}
                    </TableRow>
                </TableHeader>
                <TableBody>
                    {data.rows.map((row: any[], rowIndex: number) => (
                        <TableRow
                            key={rowIndex}
                            className={`hover:bg-muted/20 transition-all group ${rowIndex < data.rows.length - 1 ? "border-b border-slate-300 dark:border-slate-500/50" : ""}`}
                        >
                            {row.map((cell: any, cellIndex: number) => {
                                const isFirstColumn = cellIndex === 0;
                                const isNumeric = typeof cell === "number";

                                return (
                                    <TableCell
                                        key={cellIndex}
                                        className={`${isModal ? "py-5 text-sm" : "py-4 text-[13px]"} ${isFirstColumn
                                            ? "font-semibold text-foreground/80 pl-6"
                                            : "text-center text-muted-foreground group-hover:text-foreground/70"
                                            } ${cellIndex < row.length - 1 ? "border-r border-slate-300 dark:border-slate-500/50" : ""}`}
                                    >
                                        {isNumeric ? (
                                            cell > 1000 ? cell.toLocaleString() : cell
                                        ) : cell}
                                    </TableCell>
                                );
                            })}
                        </TableRow>
                    ))}
                </TableBody>
            </Table>
        </div>
    );

    // Modal Portal for Expanded View
    const ExpandedModal = () => {
        if (!mounted || !isExpanded) return null;

        return ReactDOM.createPortal(
            <div className="fixed inset-0 z-[100] flex items-center justify-center p-4 sm:p-8 bg-black/60 backdrop-blur-sm animate-in fade-in duration-200">
                <div
                    className="bg-card w-full max-w-6xl max-h-[90vh] rounded-2xl shadow-2xl overflow-hidden flex flex-col animate-in zoom-in-95 duration-200 border border-border"
                    onClick={(e) => e.stopPropagation()}
                >
                    <div className="flex items-center justify-between p-6 border-b bg-muted/30">
                        <div>
                            {title && <h3 className="font-semibold text-lg">{title}</h3>}
                            {description && <p className="text-sm text-muted-foreground mt-1">{description}</p>}
                        </div>
                        <button
                            onClick={() => setIsExpanded(false)}
                            className="p-2 hover:bg-muted rounded-full transition-colors text-muted-foreground hover:text-foreground"
                        >
                            <X className="w-5 h-5" />
                        </button>
                    </div>
                    <div className="flex-1 overflow-auto p-6 bg-card/50">
                        {renderTableContent(true)}
                    </div>
                </div>
                {/* Click outside to close */}
                <div className="absolute inset-0 -z-10" onClick={() => setIsExpanded(false)} />
            </div>,
            document.body
        );
    };

    return (
        <div className="flex flex-col gap-4 w-full relative group/table">
            <div className="relative">
                {/* Maximize Button - shows on hover or if scrollable (simplification: always show but subtle) */}
                <button
                    onClick={() => setIsExpanded(true)}
                    className="absolute top-2 right-2 z-10 p-1.5 bg-background/80 hover:bg-background backdrop-blur text-muted-foreground hover:text-primary rounded-md shadow-sm border border-border/50 opacity-0 group-hover/table:opacity-100 transition-opacity"
                    title="Expand Table"
                >
                    <Maximize2 className="w-4 h-4" />
                </button>

                {renderTableContent(false)}
            </div>

            <ExpandedModal />
        </div>
    );
};

export default DataTable;
