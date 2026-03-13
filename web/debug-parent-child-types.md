# Debug Analysis: Parent-Child Questions Type Mismatch

## Problem Summary
Parent-child questions (Problem Sets) are not displaying properly in the question table. This analysis examines the data flow and type mismatches.

## Data Flow Analysis

### 1. API Response Structure (`question-pagination-service.ts`)
Returns `PaginatedProblemData`:
```typescript
interface PaginatedProblemData {
   problemData: (ProblemWithAttempt | ProblemSetWithAttempts)[];
   totalProblems: number;
}

interface ProblemWithAttempt {
   problemid: number;        // ❌ number (not string)
   title: string;
   difficulty: number | null;
   addedDate: Date | null;   // ❌ Date (not string)
   type: string | null;
   problemsSetId: number | null;
   iscorrect: boolean | null;
}

interface ProblemSetWithAttempts {
   problemsSetId: number;
   title: string;
   isExpanded: boolean;      // ✅ correct
   problems: ProblemWithAttempt[];
}
```

### 2. Expected UI Structure (`cache.ts`)
QuestionTable expects `HybridProblem`:
```typescript
interface Problem {
  problemid: string;         // ❌ expects string (gets number)
  title: string;
  difficulty: number;
  addedDate: string;         // ❌ expects string (gets Date)
  problemtags: { tags: { name: string | null } }[];  // ❌ missing
  iscorrect: boolean | null | undefined;
  absoluteIndex?: number;    // ❌ missing
}

interface ProblemsSet {
  problemsSetId: number;
  title: string;
  difficulty?: number;       // ❌ missing in API response
  addedDate?: string;        // ❌ missing in API response
  isExpanded: boolean;       // ✅ correct
  problems: Problem[];
  absoluteIndex?: number;    // ❌ missing
}

type HybridProblem = ProblemsSet | Problem;
```

## Key Type Mismatches Identified

### 1. Problem ID Type Mismatch
- **API returns**: `problemid: number`
- **UI expects**: `problemid: string`

### 2. Date Format Mismatch
- **API returns**: `addedDate: Date | null`
- **UI expects**: `addedDate: string`

### 3. Missing Properties in API Response
- **Missing in API**: `problemtags`, `absoluteIndex`
- **Required by UI**: For sorting, navigation, and tag display

### 4. ProblemSet Missing Properties
- **Missing in API**: `difficulty`, `addedDate` on parent ProblemSet
- **UI expects**: These properties for display consistency

### 5. Child Problems Missing Properties
- **Missing in API**: `problemtags`, `absoluteIndex`
- **Required by UI**: For proper child problem handling

## Impact on Problem Sets Display

1. **Type Casting Issues**: The data doesn't match expected types, causing potential runtime errors
2. **Missing Navigation Indices**: `absoluteIndex` is missing, breaking question navigation
3. **Incomplete Child Data**: Child problems lack necessary metadata
4. **Date Formatting**: API returns Date objects but UI expects strings

## Recommended Solutions

### Option 1: Transform API Data (Recommended)
Add transformation layer in `problems-table-section.tsx` to convert API data to UI format:
- Convert `problemid` from number to string
- Convert `addedDate` from Date to string
- Add missing `absoluteIndex` based on position
- Populate default values for missing properties

### Option 2: Update API Response
Modify `question-pagination-service.ts` to return data in UI-expected format:
- Include `problemtags` in the query
- Add `absoluteIndex` calculation
- Format dates as strings
- Include parent-level metadata for ProblemSets

### Option 3: Update UI Types
Modify `HybridProblem` types to match API reality, but this would break other components.

## Files Requiring Changes

1. **Primary Fix**: `problems-table-section.tsx` - Add data transformation
2. **Alternative**: `question-pagination-service.ts` - Modify API response
3. **Types**: Update type definitions for consistency

## Testing Requirements

1. Test individual problems display
2. Test problem sets expansion/collapse
3. Test navigation between parent and child questions
4. Test date formatting
5. Test solved/unsolved status display