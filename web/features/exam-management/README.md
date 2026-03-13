# Exam Management Feature

This feature handles the organization and selection of exam types, sections, and tags.

## Components

-  **exam-selector.tsx**: Dropdown for selecting exam type
-  **section-filter.tsx**: Tabs or buttons for filtering by section
-  **tag-selector.tsx**: Multi-select for filtering by tags
-  **difficulty-badge.tsx**: Visual indicator of question difficulty

## Services

-  **exam-queries.ts**: Functions to fetch exam types and sections
-  **tag-queries.ts**: Functions to fetch and manage tags
-  **exam-mutations.ts**: Functions to update exam configuration

## Hooks

-  **use-exam-selection.ts**: Manages exam type selection state
-  **use-section-filtering.ts**: Manages section filtering state
-  **use-tag-filtering.ts**: Manages tag selection and filtering

## Stores

-  **exam-store.ts**: Zustand store for exam selection state
-  **tag-store.ts**: Zustand store for tag selection state

## Integration Flow

1. User opens the problems page
2. `exam-selector.tsx` displays available exam types
3. User selects an exam type
4. `section-filter.tsx` updates to show sections for that exam
5. User selects a section
6. `tag-selector.tsx` displays tags relevant to the selected exam and section
7. User selects tags to filter questions
8. Selected filters are passed to the question-solving feature to fetch filtered questions

## API Interactions

-  Fetches exam types from `/api/exams/types`
-  Fetches sections from `/api/exams/sections?examType={examType}`
-  Fetches tags from `/api/tags?examType={examType}&section={section}`
-  Updates user preferences via `/api/users/preferences/exams`

## Data Models

This feature interacts with the following database models:

-  `ExamType`: Different exam types (GRE, GMAT, CAT)
-  `Section`: Exam sections (Quants, Verbal, etc.)
-  `Tag`: Question categorization tags
-  `UserPreference`: User's saved exam preferences

## State Management

The exam selection state is managed through Zustand stores:

```typescript
// Example of exam-store.ts structure
interface ExamState {
   currentExam: string;
   currentSection: string;
   selectedTags: string[];
   setExam: (exam: string) => void;
   setSection: (section: string) => void;
   setTags: (tags: string[]) => void;
}
```

## Integration with Other Features

-  **Question Solving**: Provides filtering parameters for question fetching
-  **User Analytics**: Provides context for performance metrics
-  **User Preferences**: Saves and loads user's preferred exam settings
