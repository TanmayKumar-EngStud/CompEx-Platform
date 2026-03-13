import React from "react";
import DynamicChartRenderer from "./graphs/DynamicChartRenderer";
import DataTable from "./tables/DataTable";
import PivotTable from "./tables/PivotTable";

// Layout helper to add consistent spacing and optional sub-titles
export const LayoutWrapper = ({ children, title, description }: { children: React.ReactNode, title?: string, description?: string }) => (
    <div className="flex flex-col gap-3">
        {title && <h3 className="text-sm font-semibold text-muted-foreground uppercase tracking-wider">{title}</h3>}
        {description && <p className="text-sm text-muted-foreground leading-relaxed italic border-l-2 border-primary/20 pl-3">{description}</p>}
        {children}
    </div>
);

export const reDirectGraph = (type: string, metadata: any): React.ReactNode => {
    // Skip internal metadata fields as requested
    if (type === "generatedBy" || type === "questionType") return null;

    // Handle nested arrays recursively
    if (Array.isArray(metadata)) {
        return (
            <div className="flex flex-col gap-8 w-full">
                {metadata.map((item, idx) => (
                    <React.Fragment key={idx}>
                        {reDirectGraph(item?.type || type, item)}
                    </React.Fragment>
                ))}
            </div>
        );
    }

    const normalizedType = type?.toLowerCase().replace(/_/g, " ");

    // Check for chart types
    if (
        normalizedType?.includes("chart") ||
        normalizedType?.includes("graph") ||
        normalizedType?.includes("plot") ||
        normalizedType === "area" ||
        metadata?.graph ||
        metadata?.type?.toLowerCase().includes("chart")
    ) {
        const chartType = (metadata?.type || normalizedType || type).toLowerCase().replace(/_/g, " ");
        const chartTitle = metadata.title || metadata.graph?.title || metadata.structure?.title || metadata?.graph?.structure?.title;

        // Special check for grouped bar charts
        const isGroupedBarChart =
            chartType === "bar chart" &&
            metadata?.graph?.data?.length > 0 &&
            Object.keys(metadata.graph.data[0]).some((key) => !isNaN(parseInt(key)));

        return (
            <LayoutWrapper title={chartTitle} description={metadata.description}>
                <DynamicChartRenderer type={isGroupedBarChart ? "grouped bar chart" : chartType} metadata={metadata} />
            </LayoutWrapper>
        );
    }

    // Check for table types
    if (normalizedType?.includes("table") || metadata?.table) {
        const tableTitle = metadata.title || metadata.table?.title || metadata.structure?.title || metadata?.table?.structure?.title;
        if (normalizedType === "pivot table" || metadata?.table === "pivot table") {
            return (
                <LayoutWrapper title={tableTitle} description={metadata.description}>
                    <PivotTable metadata={metadata} />
                </LayoutWrapper>
            );
        }
        return (
            <LayoutWrapper title={tableTitle} description={metadata.description}>
                <DataTable metadata={metadata} />
            </LayoutWrapper>
        );
    }

    if (normalizedType?.includes("passage") || normalizedType === "paragraph" || type === "Passage" || normalizedType?.includes("source")) {
        const getPassages = () => {
            // If it's a SourceX object, find the passage inside it
            const potentialPassage = metadata?.passage || metadata?.para || metadata?.text;
            if (potentialPassage) {
                return Array.isArray(potentialPassage) ? potentialPassage : [potentialPassage];
            }

            if (typeof metadata === "string") return [metadata];
            if (Array.isArray(metadata)) return metadata;
            if (metadata?.passage) return Array.isArray(metadata.passage) ? metadata.passage : [metadata.passage];
            if (metadata?.para) return Array.isArray(metadata.para) ? metadata.para : [metadata.para];
            return [];
        };

        const passages = getPassages();
        return (
            <div className="flex flex-col gap-4">
                {passages.map((item: any, index: number) => {
                    const text = typeof item === "string" ? item : (item?.para || item?.text || "");
                    return <p key={index} className="font-serif text-[15px] leading-[1.7] text-foreground/90 antialiased">{text}</p>;
                })}
            </div>
        );
    }

    // Fallback for SourceX or other container types: try to render their children
    if (normalizedType?.includes("source") && typeof metadata === "object" && metadata !== null) {
        const children = Object.entries(metadata).filter(([k]) => k !== "type" && k !== "title");
        if (children.length > 0) {
            return (
                <div className="flex flex-col gap-4">
                    {children.map(([k, v], idx) => (
                        <div key={idx}>{reDirectGraph(k, v)}</div>
                    ))}
                </div>
            );
        }
    }

    return (
        <div className="p-6 border border-dashed border-border/60 rounded-xl bg-muted/5 flex flex-col items-center justify-center text-center">
            <div className="text-xs font-bold text-muted-foreground/60 uppercase tracking-widest mb-1">Renderer Missing</div>
            <div className="text-sm text-muted-foreground">Component for "{type}" not prepared yet</div>
        </div>
    );
};
