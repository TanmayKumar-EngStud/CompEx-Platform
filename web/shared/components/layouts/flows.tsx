import React from "react";
import clsx from "clsx";
export function Hflow({
   className,
   children,
   gap = 0,
}: {
   className?: string;
   children: React.ReactNode;
   gap?: number;
}) {
   return (
      <div
         className={clsx("flex flex-row", className)}
         style={{ gap: `${gap}px` }}
      >
         {children}
      </div>
   );
}

export function Vflow({
   className,
   children,
   gap = 0,
}: {
   className?: string;
   children: React.ReactNode;
   gap?: number;
}) {
   return (
      <div
         className={clsx("flex flex-col", className)}
         style={{ gap: `${gap}px` }}
      >
         {children}
      </div>
   );
}
