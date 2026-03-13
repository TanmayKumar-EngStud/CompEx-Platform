import * as React from "react"
import { Slot } from "@radix-ui/react-slot"
import { cva, type VariantProps } from "class-variance-authority"
import Link from "next/link";
import { cn } from "@/shared/lib/utils"
import { classNames } from "@/shared/lib/utils/formatting";

const buttonVariants = cva(
   "inline-flex items-center justify-center whitespace-nowrap rounded-md text-sm font-medium transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring disabled:pointer-events-none disabled:opacity-50",
   {
      variants: {
         variant: {
            default:
               "bg-primary text-primary-foreground shadow hover:bg-primary/90",
            destructive:
               "bg-destructive text-destructive-foreground shadow-sm hover:bg-destructive/90",
            outline:
               "border border-input bg-background shadow-sm hover:bg-accent hover:text-accent-foreground",
            secondary:
               "bg-secondary text-secondary-foreground shadow-sm hover:bg-secondary/80",
            ghost: "hover:bg-accent hover:text-accent-foreground",
            link: "text-primary underline-offset-4 hover:underline",
         },
         size: {
            default: "h-9 px-4 py-2",
            sm: "h-8 rounded-md px-3 text-xs",
            lg: "h-10 rounded-md px-8",
            icon: "h-9 w-9",
         },
      },
      defaultVariants: {
         variant: "default",
         size: "default",
      },
   }
)

export interface ButtonProps
   extends React.ButtonHTMLAttributes<HTMLButtonElement>,
   VariantProps<typeof buttonVariants> {
   asChild?: boolean
}

const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
   ({ className, variant, size, asChild = false, ...props }, ref) => {
      const Comp = asChild ? Slot : "button"
      return (
         <Comp
            className={cn(buttonVariants({ variant, size, className }))}
            ref={ref}
            {...props}
         />
      )
   }
)
Button.displayName = "Button"

// Legacy button components for backward compatibility
export interface ButtonProps_Legacy extends React.ButtonHTMLAttributes<HTMLButtonElement> {
   children: React.ReactNode;
}

interface LinkProps {
   name: string;
   count: number;
   href: string;
   isActive: boolean;
   color1: string | null;
   color2: string | null;
   className?: string;
   key?: any;
}

interface ButtonLinkProps {
   name: string;
   isActive: boolean;
   href: string;
   color1: string;
   color2: string;
   textColor?: string;
   textColorInactive?: string;
   className?: string;
   key?: any;
   onMouseEnter?: () => void;
}

export function ButtonP({ children, className, onClick, disabled }: ButtonProps_Legacy) {
   return (
      <button
         className={`px-4 py-2 rounded-lg font-medium text-primary-foreground bg-primary hover:bg-primary/90 transition-colors disabled:opacity-50 disabled:cursor-not-allowed ${className}`}
         onClick={onClick}
         disabled={disabled}
      >
         {children}
      </button>
   );
}

export function ButtonS({ children, className, onClick, disabled }: ButtonProps_Legacy) {
   return (
      <button
         className={`px-3 py-1.5 rounded-md text-sm font-medium text-secondary-foreground bg-secondary hover:bg-secondary/80 transition-colors disabled:opacity-50 disabled:cursor-not-allowed ${className}`}
         onClick={onClick}
         disabled={disabled}
      >
         {children}
      </button>
   );
}

export function TagLinks({
   name,
   count,
   href,
   isActive,
   color1,
   color2,
   className = "",
}: LinkProps) {
   // Use consistent theme colors instead of gradients
   const useConsistentColors = color1 === null && color2 === null;

   return (
      <Link
         href={href}
         className={classNames(
            "inline-flex items-center px-3 py-1.5 rounded-full text-sm font-medium transition-all duration-300 hover:scale-105 active:scale-95",
            useConsistentColors
               ? isActive
                  ? "bg-primary text-primary-foreground shadow-lg border border-primary"
                  : "bg-muted text-muted-foreground hover:bg-muted/80 border border-border"
               : isActive ? "shadow-lg ring-2 ring-white/20" : "shadow-sm hover:shadow-md",
            className
         )}
         style={useConsistentColors ? {
            transform: isActive ? "translateY(-1px)" : "translateY(0)",
         } : {
            background: isActive
               ? `linear-gradient(135deg, ${color1}, ${color2})`
               : `linear-gradient(135deg, ${color2}, ${color1})`,
            color: "#ffffff",
            transform: isActive ? "translateY(-1px)" : "translateY(0)",
         }}
      >
         <span className="font-semibold">{name}</span>
         {count !== undefined && count > 0 && (
            <span className={classNames(
               "ml-1.5 px-1.5 py-0.5 text-xs rounded-full",
               useConsistentColors
                  ? isActive
                     ? "bg-primary-foreground/20 text-primary-foreground"
                     : "bg-foreground/20 text-foreground"
                  : "bg-white/20"
            )}>
               {count}
            </span>
         )}
      </Link>
   );
}

export function ButtonLinks({
   name,
   isActive,
   href,
   color1,
   color2,
   textColor = "white",
   textColorInactive = "white",
   className = "",
   onMouseEnter,
}: ButtonLinkProps) {
   return (
      <Link
         href={href}
         onMouseEnter={onMouseEnter}
         prefetch={true}
         className={`px-4 py-2 rounded-full text-sm font-medium transition-colors duration-200 ${className}`}
         style={{
            background: isActive ? color1 : color2,
            color: isActive ? textColor : textColorInactive,
            boxShadow: "0 2px 3px rgba(0, 0, 0, 0.1)",
            border: "1px solid rgba(255, 255, 255, 0.1)",
         }}
      >
         {`${name}`}
      </Link>
   );
}

export { Button, buttonVariants }