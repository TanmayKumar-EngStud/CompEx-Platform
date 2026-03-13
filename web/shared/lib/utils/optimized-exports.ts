/**
 * Optimized component exports for better tree-shaking
 * 
 * This file provides specific exports instead of barrel exports
 * to improve bundle size optimization and tree-shaking effectiveness.
 * 
 * Instead of using `export * from "./components"`, we explicitly export
 * only the components that are actually used, reducing bundle size.
 */

// Core UI components (most frequently used)
export { Button } from "@/shared/components/ui/button";
export { Label } from "@/shared/components/ui/label";
export { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/shared/components/ui/select";
export { Switch } from "@/shared/components/ui/switch";
export { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/shared/components/ui/table";

// Layout and structure components
export { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/shared/components/ui/card";
export { Skeleton } from "@/shared/components/ui/skeleton";

// Feedback and loading components
export { Alert, AlertDescription, AlertTitle } from "@/shared/components/feedback/alert";
export { Badge } from "@/shared/components/feedback/badge";

// Overlay and popup components
export { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "@/shared/components/feedback/tooltip";

/**
 * Component categories for conditional imports
 * 
 * These allow importing only specific categories of components
 * when working with particular features.
 */

// Note: Component category objects have been removed to avoid
// import/export complexity during the migration to focused stores.
// Use direct imports from specific component files instead.