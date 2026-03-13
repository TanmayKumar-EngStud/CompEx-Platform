# Pagination Module

This module handles fetching and managing paginated problem data in a Next.js application using TypeScript.

## Files Overview

### `fetchProblems.tsx`

-  **Purpose**: Fetches paginated problems from an API and manages the state using a custom hook.
-  **Main Functions**:
   -  `fetchProblems`: Asynchronously fetches problems based on exam name, section name, tags, page number, and limit.
   -  `usePaginatedProblems`: Custom hook that uses `react-query` to manage fetching and state of paginated problems.
-  **Dependencies**: `@tanstack/react-query`, `useState`, `useEffect`.

### `problemDefinition.ts`

-  **Purpose**: Defines TypeScript types for problem data.
-  **Main Types**:
   -  `ProblemsResponse`: Interface for the response object containing problem data.
   -  `Problem`: Interface for an individual problem.

---
