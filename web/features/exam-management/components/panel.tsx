"use client";
import clsx from "clsx";
import React from "react";

interface PanelProps {
   children: React.ReactNode;
   active: boolean;
}
const Panel: React.FC<PanelProps> = ({ children, active = false }) => {
   // Using theme variables for better dark mode support
   const properties = `bg-card left-0 w-full rounded-lg border border-border shadow-sm overflow-auto p-3`;
   return (
      <div className={clsx(properties, !active && "hidden")}>{children}</div>
   );
};

export default Panel;
