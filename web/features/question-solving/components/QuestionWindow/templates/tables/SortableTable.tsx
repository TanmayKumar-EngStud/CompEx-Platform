import React, { useState, useMemo } from 'react';
import { ArrowUp, ArrowDown, ChevronsUpDown } from 'lucide-react';

interface SortableTableProps {
    headers: string[];
    rows: (string | number)[][];
    title?: string;
}

type SortDirection = 'asc' | 'desc' | null;

interface SortConfig {
    key: number; // Column index
    direction: SortDirection;
}

export const SortableTable: React.FC<SortableTableProps> = ({ headers, rows, title }) => {
    const [sortConfig, setSortConfig] = useState<SortConfig>({ key: 0, direction: null });

    const sortedRows = useMemo(() => {
        if (sortConfig.direction === null) return rows;

        const sorted = [...rows].sort((a, b) => {
            const aValue = a[sortConfig.key];
            const bValue = b[sortConfig.key];

            if (aValue === bValue) return 0;

            // Handle mixed types generally by converting to string if needed, 
            // but ideally standard tables have consistent column types.
            // If generic check:
            const isNumber = typeof aValue === 'number' && typeof bValue === 'number';

            if (isNumber) {
                return sortConfig.direction === 'asc'
                    ? (aValue as number) - (bValue as number)
                    : (bValue as number) - (aValue as number);
            }

            // String comparison
            const aStr = String(aValue).toLowerCase();
            const bStr = String(bValue).toLowerCase();

            if (sortConfig.direction === 'asc') {
                return aStr.localeCompare(bStr);
            } else {
                return bStr.localeCompare(aStr);
            }
        });
        return sorted;
    }, [rows, sortConfig]);

    const handleSort = (index: number) => {
        let direction: SortDirection = 'asc';
        if (sortConfig.key === index && sortConfig.direction === 'asc') {
            direction = 'desc';
        } else if (sortConfig.key === index && sortConfig.direction === 'desc') {
            // Optional: Toggle back to default (null) or stick to desc?
            // Standard exam usually toggles asc <-> desc.
            direction = 'asc';
        }
        setSortConfig({ key: index, direction });
    };

    return (
        <div className="w-full flex flex-col gap-2">
            {title && <h3 className="font-semibold text-sm text-center text-gray-800 mb-1">{title}</h3>}
            <div className="overflow-x-auto border border-slate-300 dark:border-slate-500/50 rounded shadow-sm">
                <table className="w-full border-collapse bg-background text-sm">
                    <thead>
                        <tr className="bg-muted border-b border-slate-300 dark:border-slate-500/50">
                            {headers.map((header, index) => (
                                <th
                                    key={index}
                                    onClick={() => handleSort(index)}
                                    className="px-4 py-2 text-left font-semibold text-foreground/80 cursor-pointer hover:bg-muted/80 select-none border-r border-slate-300 dark:border-slate-500/50 last:border-r-0 transition-colors"
                                >
                                    <div className="flex items-center justify-between gap-2 group">
                                        <span>{header}</span>
                                        <span className="text-muted-foreground/60 group-hover:text-foreground/80">
                                            {sortConfig.key === index ? (
                                                sortConfig.direction === 'asc' ? <ArrowUp size={14} /> : <ArrowDown size={14} />
                                            ) : (
                                                <ChevronsUpDown size={14} className="opacity-0 group-hover:opacity-50" />
                                            )}
                                        </span>
                                    </div>
                                </th>
                            ))}
                        </tr>
                    </thead>
                    <tbody>
                        {sortedRows.map((row, rowIndex) => (
                            <tr
                                key={rowIndex}
                                className={`
                           border-b border-slate-300 dark:border-slate-500/50 last:border-b-0 
                           ${rowIndex % 2 === 0 ? 'bg-background' : 'bg-muted/30'}
                           hover:bg-primary/5 transition-colors
                        `}
                            >
                                {row.map((cell, cellIndex) => (
                                    <td
                                        key={cellIndex}
                                        className={`px-4 py-2 border-r border-slate-200 dark:border-slate-700/50 last:border-r-0 ${typeof cell === 'number' ? 'text-right font-mono' : 'text-left'
                                            }`}
                                    >
                                        {typeof cell === 'number' ? cell.toLocaleString() : cell}
                                    </td>
                                ))}
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>
        </div>
    );
};

export default SortableTable;
