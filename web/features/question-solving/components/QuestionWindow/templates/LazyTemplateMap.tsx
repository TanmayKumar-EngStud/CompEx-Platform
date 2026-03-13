import { lazy, ComponentType, Suspense } from "react";
import { Skeleton } from "@/shared/components/ui/skeleton";

/**
 * Lazy-loaded question templates for optimal bundle size
 * 
 * Templates are loaded on-demand based on question type to reduce
 * initial bundle size. Each template is only loaded when needed.
 */

// Lazy load all template components
const DSTemplate = lazy(() => import("./DS"));
const RCTemplate = lazy(() => import("./RC"));
const CRTemplate = lazy(() => import("./CR"));
const NETemplate = lazy(() => import("./NE"));
const SETemplate = lazy(() => import("./SE"));
const TC23Template = lazy(() => import("./TC-23"));
const ParentChildTemplate = lazy(() => import("./ParentChild"));
const GITemplate = lazy(() => import("./GI"));
const TATemplate = lazy(() => import("./TA"));
const MSRTemplate = lazy(() => import("./msr"));
const DichotomousTemplate = lazy(() => import("./Dichotomous"));

/**
 * Template component map with lazy loading
 */
const TEMPLATE_MAP = {
   DS: DSTemplate,
   RC: RCTemplate,
   CR: CRTemplate,
   NE: NETemplate,
   SE: SETemplate,
   "TC-23": TC23Template,
   ParentChild: ParentChildTemplate,
   GI: GITemplate,
   TA: TATemplate,
   MSR: MSRTemplate,
   DICHOTOMOUS: DichotomousTemplate,
} as const;

/**
 * Template loader functions for preloading
 */
const TEMPLATE_LOADERS = {
   DS: () => import("./DS"),
   RC: () => import("./RC"),
   CR: () => import("./CR"),
   NE: () => import("./NE"),
   SE: () => import("./SE"),
   "TC-23": () => import("./TC-23"),
   ParentChild: () => import("./ParentChild"),
   GI: () => import("./GI"),
   TA: () => import("./TA"),
   MSR: () => import("./msr"),
   DICHOTOMOUS: () => import("./Dichotomous"),
} as const;

/**
 * Default template for unknown question types
 */
const DefaultTemplate = lazy(() => import("./Default"));

/**
 * Template loading skeleton
 */
function TemplateSkeleton({ type }: { type: string }) {
   return (
      <div className="space-y-4 p-4" role="status" aria-label={`Loading ${type} template...`}>
         {/* Title skeleton */}
         <Skeleton className="h-6 w-3/4" />

         {/* Content skeleton */}
         <div className="space-y-2">
            <Skeleton className="h-4 w-full" />
            <Skeleton className="h-4 w-5/6" />
            <Skeleton className="h-4 w-4/6" />
         </div>

         {/* Options skeleton */}
         <div className="space-y-2 mt-6">
            {[1, 2, 3, 4].map((i) => (
               <div key={i} className="flex items-center space-x-2">
                  <Skeleton className="h-4 w-4 rounded-full" />
                  <Skeleton className="h-4 w-32" />
               </div>
            ))}
         </div>
      </div>
   );
}

/**
 * Props that are common to all template components
 */
interface TemplateProps {
   [key: string]: any;
}

/**
 * Wrapper component for lazy-loaded templates with suspense boundary
 */
interface LazyTemplateWrapperProps extends TemplateProps {
   TemplateComponent: ComponentType<any>;
   type: string;
}

function LazyTemplateWrapper({
   TemplateComponent,
   type,
   ...props
}: LazyTemplateWrapperProps) {
   return (
      <Suspense fallback={<TemplateSkeleton type={type} />}>
         <TemplateComponent {...props} />
      </Suspense>
   );
}

/**
 * Gets the appropriate template component for a question type
 * 
 * Returns a lazy-loaded template component wrapped with Suspense
 * for the specified question type. Falls back to default template
 * for unknown types.
 * 
 * @param type - Question type (DS, RC, CR, etc.)
 * @param props - Props to pass to the template component
 * @returns JSX element with lazy-loaded template
 */
export function getTemplateComponent(type: string, props: TemplateProps = {}) {
   const normalizedType = type as keyof typeof TEMPLATE_MAP;
   const TemplateComponent = TEMPLATE_MAP[normalizedType] || DefaultTemplate;

   return (
      <LazyTemplateWrapper
         TemplateComponent={TemplateComponent}
         type={type}
         {...props}
      />
   );
}

/**
 * Pre-loads a template component for better UX
 * 
 * Can be called to pre-load templates that are likely to be used soon.
 * This is useful for improving perceived performance.
 * 
 * @param type - Question type to preload
 */
export async function preloadTemplate(type: string): Promise<void> {
   const normalizedType = type as keyof typeof TEMPLATE_LOADERS;
   const templateLoader = TEMPLATE_LOADERS[normalizedType];

   if (templateLoader) {
      try {
         await templateLoader();
      } catch (error) {
         console.warn(`Failed to preload template ${type}:`, error);
      }
   }
}

/**
 * Pre-loads multiple templates
 * 
 * @param types - Array of question types to preload
 */
export async function preloadTemplates(types: string[]): Promise<void> {
   const preloadPromises = types.map(type => preloadTemplate(type));
   await Promise.allSettled(preloadPromises);
}

/**
 * Available template types
 */
export const TEMPLATE_TYPES = Object.keys(TEMPLATE_MAP) as Array<keyof typeof TEMPLATE_MAP>;

/**
 * Checks if a template type is supported
 * 
 * @param type - Question type to check
 * @returns True if template exists, false otherwise
 */
export function isTemplateTypeSupported(type: string): boolean {
   return type in TEMPLATE_MAP;
}