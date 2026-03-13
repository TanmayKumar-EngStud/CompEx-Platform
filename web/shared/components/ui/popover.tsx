"use client"

import * as React from "react"
import { cn } from "@/shared/lib/utils"

interface PopoverProps extends React.HTMLAttributes<HTMLDivElement> {
  children: React.ReactNode;
  open?: boolean;
  onOpenChange?: (open: boolean) => void;
}

const Popover = React.forwardRef<HTMLDivElement, PopoverProps>(
  ({ className, children, open, onOpenChange, ...props }, ref) => (
    <div
      ref={ref}
      className={cn("relative inline-block", className)}
      {...props}
    >
      {children}
    </div>
  )
)
Popover.displayName = "Popover"

interface PopoverTriggerProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  asChild?: boolean;
}

const PopoverTrigger = React.forwardRef<HTMLButtonElement, PopoverTriggerProps>(
  ({ className, children, asChild, ...props }, ref) => {
    if (asChild) {
      return <>{children}</>
    }
    
    return (
      <button
        ref={ref}
        className={cn("cursor-pointer", className)}
        {...props}
      >
        {children}
      </button>
    )
  }
)
PopoverTrigger.displayName = "PopoverTrigger"

interface PopoverContentProps extends React.HTMLAttributes<HTMLDivElement> {
  align?: "start" | "center" | "end";
}

const PopoverContent = React.forwardRef<HTMLDivElement, PopoverContentProps>(
  ({ className, children, align = "start", ...props }, ref) => (
    <div
      ref={ref}
      className={cn(
        "absolute z-50 min-w-[200px] rounded-md border bg-popover p-4 text-popover-foreground shadow-md",
        "top-full mt-2",
        align === "start" && "left-0",
        align === "center" && "left-1/2 -translate-x-1/2",
        align === "end" && "right-0",
        className
      )}
      {...props}
    >
      {children}
    </div>
  )
)
PopoverContent.displayName = "PopoverContent"

export { Popover, PopoverTrigger, PopoverContent }