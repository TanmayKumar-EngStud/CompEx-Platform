# Exam Management Hooks

This directory contains React hooks specific to the exam management feature.

## Available Hooks

-  **use-exam-section-logic.ts**: Manages exam section logic and state

## Hook Details

### use-exam-section-logic.ts

Provides a clean interface for components to manage exam section state and operations without directly accessing the service layer.

```typescript
interface ExamSectionLogic {
   /** Array of section names for current exam */
   tabProperties: string[];
   /** Current exam name */
   examName: string;
   /** Current section name */
   sectionName: string;
   /** Switch to a different section */
   switchSection: (section: string) => void;
   /** Validate if a section is valid for current exam */
   isValidSection: (section: string) => boolean;
   /** Get default section for current exam */
   getDefaultSection: () => string;
}

function useExamSectionLogic(): ExamSectionLogic {
   // Uses usePaginationStore for state management
   // Integrates with examSectionService for business logic
   // Provides memoized functions for performance

   return {
      tabProperties,
      examName,
      sectionName,
      switchSection,
      isValidSection,
      getDefaultSection,
   };
}
```

**Features:**

-  Manages exam section state through centralized store
-  Validates section changes before applying them
-  Provides memoized functions to prevent unnecessary re-renders
-  Integrates with exam section service for business logic
-  Handles default section selection for different exam types

**Usage Example:**

```tsx
import { useExamSectionLogic } from "@/features/exam-management/hooks/use-exam-section-logic";

function ExamSectionPanel() {
   const {
      tabProperties,
      examName,
      sectionName,
      switchSection,
      isValidSection,
      getDefaultSection,
   } = useExamSectionLogic();

   return (
      <div>
         <h2>Current Exam: {examName}</h2>
         <h3>Current Section: {sectionName}</h3>

         <div className="section-tabs">
            {tabProperties.map((section) => (
               <button
                  key={section}
                  onClick={() => switchSection(section)}
                  className={section === sectionName ? "active" : ""}
               >
                  {section}
               </button>
            ))}
         </div>
      </div>
   );
}
```

## Integration Points

### With Services

-  **examSectionService**: Uses service functions for section validation and configuration
-  **Problem Store**: Integrates with pagination store for state management

### With Components

-  **ExamSectionPanel**: Primary consumer for section navigation
-  **Tab Components**: Uses section properties for rendering tabs
-  **Panel Components**: Uses section state for content filtering

## State Management

The hook uses the `usePaginationStore` for state management:

-  Reads current exam and section names
-  Updates section name through store actions
-  Maintains consistency with other parts of the application

## Performance Optimizations

-  **Memoized Functions**: All callback functions are memoized to prevent unnecessary re-renders
-  **Memoized Properties**: Tab properties are memoized based on exam name
-  **Validation Caching**: Section validation results are computed efficiently

## Error Handling

-  Validates section changes before applying them
-  Logs warnings for invalid section attempts
-  Provides fallback to default sections when needed
-  Handles edge cases for unknown exam types
