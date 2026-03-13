"use client";
import React, { ReactNode } from "react";
import { cn } from "@/shared/lib/utils"; // ShadCN's utility for className concatenation

interface TabProp {
   children: ReactNode;
   on?: boolean;
   onClick?: () => void;
   className?: string;
}

const Tab: React.FC<TabProp> = ({ children, onClick, on = false, className }) => {
   return (
      <button
         onClick={onClick}
         className={cn(
            "inline-flex items-center justify-center whitespace-nowrap rounded-md px-3 py-1.5 text-sm font-medium ring-offset-background transition-all focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50",
            "w-full",
            on
               ? "bg-background text-foreground shadow-sm"
               : "text-muted-foreground hover:bg-muted/50",
            className,
            "data-[state=active]:shadow data-[state=active]:bg-background data-[state=active]:text-foreground"
         )}
      >
         {children}
      </button>
   );
};

export default Tab;
