# API Directory

This directory contains the backend API routes implemented using Next.js API Routes.

## Structure

* **problems/**: Question-related endpoints
  * **getProblems/**: Fetch problems with filtering
  * **getProblemById/**: Get a single problem
  * **attempts/**: Submit and retrieve question attempts
* **exams/**: Exam-related endpoints
  * **types/**: Fetch exam types
  * **sections/**: Fetch sections for exam types
* **tags/**: Tag-related endpoints
* **users/**: User-related endpoints
  * **profile/**: User profile operations
  * **preferences/**: User preferences operations
* **analytics/**: Analytics-related endpoints
  * **performance/**: User performance metrics
  * **sessions/**: Study session data

## API Design Patterns

### RESTful Endpoints

The API follows RESTful conventions:
- `GET`: Retrieve resources
- `POST`: Create resources
- `PUT`: Update resources
- `DELETE`: Remove resources

### Request Handling

Each API route follows a consistent pattern:
1. Extract parameters from request
2. Validate input data
3. Call appropriate service function
4. Handle errors
5. Return formatted response

## Example API Route

```typescript
// /api/problems/route.ts
import { NextRequest, NextResponse } from 'next/server';
import { getProblems } from '@/service/problems/queries';

export async function GET(request: NextRequest) {
  try {
    const searchParams = request.nextUrl.searchParams;
    const examName = searchParams.get("examName") || "GRE";
    const sectionName = searchParams.get("sectionName") || "quants";
    const tags = searchParams.get("tags") ? JSON.parse(searchParams.get("tags")!) : null;
    
    const problems = await getProblems(examName, sectionName, tags);
    
    return NextResponse.json({ problems });
  } catch (error) {
    console.error("Error fetching problems:", error);
    return NextResponse.json(
      { error: "Failed to fetch problems" },
      { status: 500 }
    );
  }
}
```

## Error Handling

API routes use consistent error handling:
- HTTP status codes for different error types
- Structured error responses with error messages
- Logging of errors for debugging

## Authentication

Protected routes use authentication middleware:
- Verify user session
- Check permissions
- Return appropriate error for unauthorized access

## Integration with Services

API routes use functions from the `/service` directory to:
- Query the database
- Process business logic
- Format responses

This separation keeps API routes focused on request handling while service functions handle business logic.