# Exam Management Types

This directory contains TypeScript type definitions for the exam management feature.

## Overview

Currently, type definitions are distributed across various files in the exam-management feature. This directory serves as a central location for shared type definitions and interfaces.

## Current Type Locations

### Service Types

**exam-section-service.ts**
```typescript
interface ExamSectionConfig {
  examSections: Record<string, string[]>;
  defaultSections: Record<string, string>;
}
```

### Hook Types

**use-exam-section-logic.ts**
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
```

### External Dependencies

**Tag Definition** (from question-solving feature)
```typescript
interface Tag {
  name: string;
  examtypeid: number;
  sectionid: number;
  count: number; // number of questions with that tag
  isActive: boolean; // if that tag is selected by the user
}
```

## Recommended Type Definitions

The following types should be centralized in this directory:

### Core Exam Types

```typescript
// Exam type identifier
type ExamType = 'GRE' | 'GMAT' | 'CAT' | 'SAT' | 'LSAT';

// Section identifiers for different exams
type GRESection = 'quants' | 'verbal';
type GMATSection = 'quants' | 'verbal' | 'integrated reasoning';
type CATSection = 'VA' | 'RC' | 'DI' | 'LR';

// Union type for all sections
type ExamSection = GRESection | GMATSection | CATSection;

// Exam configuration
interface ExamConfig {
  examType: ExamType;
  sections: ExamSection[];
  defaultSection: ExamSection;
  timeLimit?: number;
  questionCount?: number;
}
```

### User Preference Types

```typescript
interface ExamPreferences {
  userId: string;
  preferredExam: ExamType;
  preferredSection: ExamSection;
  selectedTags: string[];
  lastUpdated: Date;
}

interface UserExamHistory {
  userId: string;
  examType: ExamType;
  section: ExamSection;
  completedAt: Date;
  score?: number;
  accuracy?: number;
}
```

### API Response Types

```typescript
interface ExamTypesResponse {
  examTypes: {
    id: string;
    name: ExamType;
    displayName: string;
    sections: ExamSection[];
  }[];
}

interface SectionsResponse {
  examType: ExamType;
  sections: {
    id: string;
    name: ExamSection;
    displayName: string;
    questionCount: number;
  }[];
}

interface TagsResponse {
  examType: ExamType;
  section: ExamSection;
  tags: Tag[];
}
```

## Migration Plan

To improve type safety and maintainability, consider:

1. **Centralize Types**: Move all exam-related types to this directory
2. **Create Index File**: Export all types from a single `index.ts` file
3. **Update Imports**: Update all feature files to import from centralized types
4. **Add Validation**: Create runtime type validation utilities

## Usage Guidelines

### Importing Types

```typescript
// Recommended approach (once centralized)
import type { 
  ExamType, 
  ExamSection, 
  ExamConfig,
  ExamPreferences 
} from '@/features/exam-management/types';

// Current approach (distributed)
import type { ExamSectionLogic } from '../hooks/use-exam-section-logic';
import type { ExamSectionConfig } from '../services/exam-section-service';
```

### Type Guards

```typescript
// Example type guards for runtime validation
function isValidExamType(value: string): value is ExamType {
  return ['GRE', 'GMAT', 'CAT', 'SAT', 'LSAT'].includes(value);
}

function isValidSection(examType: ExamType, section: string): boolean {
  const validSections = getValidSectionsForExam(examType);
  return validSections.includes(section as ExamSection);
}
```

## Integration Points

### With Other Features

- **Question Solving**: Shares Tag interface and exam filtering types
- **User Analytics**: Uses exam context types for performance metrics
- **User Management**: Uses preference types for user settings

### With External Libraries

- **Prisma**: Database model types should align with these definitions
- **API Routes**: Request/response types should use these interfaces
- **Zustand Stores**: Store state types should extend these base types

## Future Enhancements

- Add strict typing for exam-specific business rules
- Create discriminated unions for exam-specific configurations
- Add validation schemas using libraries like Zod
- Generate API client types from these definitions
