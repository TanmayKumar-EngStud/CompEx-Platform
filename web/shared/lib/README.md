# Shared Library

This directory contains utility functions, constants, and types that are used across the application.

## Structure

* **utils/**: Utility functions
  * **date-utils.ts**: Date formatting and manipulation
  * **string-utils.ts**: String manipulation utilities
  * **math-utils.ts**: Mathematical calculations
  * **validation.ts**: Common validation functions
* **constants/**: Application constants
  * **routes.ts**: Application route definitions
  * **api-endpoints.ts**: API endpoint paths
  * **theme-constants.ts**: Theme-related constants
* **types/**: Shared TypeScript types
  * **api.types.ts**: API response and request types
  * **common.types.ts**: Common utility types
  * **models.types.ts**: Shared model interfaces

## Utility Functions

### Date Utilities

Functions for working with dates:
- `formatDate`: Formats dates in consistent ways
- `calculateDateDifference`: Calculates difference between dates
- `isDateInRange`: Checks if a date is within a range

### String Utilities

Functions for string manipulation:
- `truncate`: Truncates strings with ellipsis
- `slugify`: Converts strings to URL-friendly slugs
- `capitalize`: Capitalizes first letter of strings

### Math Utilities

Functions for mathematical operations:
- `calculatePercentage`: Calculates percentages
- `roundToDecimal`: Rounds numbers to specified decimal places
- `generateRandomNumber`: Generates random numbers within ranges

## Constants

### Routes

Application route definitions:
- `DASHBOARD_ROUTE`: Path to dashboard
- `PROBLEMS_ROUTE`: Path to problems page
- `ANALYTICS_ROUTE`: Path to analytics page

### API Endpoints

API endpoint paths:
- `PROBLEMS_API`: Problems API endpoint
- `USERS_API`: Users API endpoint
- `ANALYTICS_API`: Analytics API endpoint

## Types

### API Types

Types for API interactions:
- `ApiResponse<T>`: Generic API response type
- `PaginatedResponse<T>`: Paginated response type
- `ApiError`: Error response type

### Common Types

Utility types used throughout the application:
- `Nullable<T>`: Type that can be null
- `Optional<T>`: Type with all properties optional
- `DeepPartial<T>`: Deeply optional type

## Usage Example

```tsx
import { formatDate } from '@/shared/lib/utils/date-utils';
import { PROBLEMS_ROUTE } from '@/shared/lib/constants/routes';
import type { ApiResponse } from '@/shared/lib/types/api.types';

// Using date utility
const formattedDate = formatDate(new Date(), 'YYYY-MM-DD');

// Using route constant
router.push(PROBLEMS_ROUTE);

// Using API type
async function fetchData(): Promise<ApiResponse<User>> {
  const response = await fetch('/api/users');
  return response.json();
}
```