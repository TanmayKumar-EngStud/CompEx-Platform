
"use client";
import React from "react";
import MinimalDropdown from "@/shared/components/interactive/dropdown";
import { usePaginationStore } from "@/shared/stores/problems/pagination";

export function ProblemPageControls() {
    const { examName, setExamName, setSectionName, setSectionIndex, pageSize, setPageSize, setPage } = usePaginationStore();
    return (
        <div className="flex gap-5 items-center p-4 border-b border-border">
            <div className="flex items-center gap-3">
                <h3 className="text-lg font-semibold">Exam</h3>
                <MinimalDropdown
                    items={["GRE", "GMAT"]}
                    getStoreName={() => examName}
                    setStoreName={(name: string) => {
                        setExamName(name);
                        // Reset section to default for the new exam
                        const defaultSection = name === "GMAT" ? "quants" : "quants";
                        setSectionName(defaultSection);
                        setSectionIndex(0);
                    }}
                    defaultVal="Select an Exam"
                />
            </div>

            <div className="flex items-center gap-3 ml-auto">
                <h3 className="text-lg font-semibold">Items per page</h3>
                <MinimalDropdown
                    items={["5", "10", "20", "50"]}
                    getStoreName={() => pageSize.toString()}
                    setStoreName={(size: string) => {
                        setPageSize(parseInt(size));
                        setPage(1);
                    }}
                    defaultVal="10"
                />
            </div>
        </div>
    );
}
