# Service Directory

This directory contains backend service functions that interact with the database using Prisma.

## Structure

* **problems/**: Question-related services
  * **queries.ts**: Functions to fetch questions
  * **mutations.ts**: Functions to create/update questions
* **users/**: User-related services
* **analytics/**: Analytics-related services
* **exams/**: Exam and section services

## Key Services

### Problem Services

Functions to interact with questions:
- `getProblems`: Fetch problems with filtering
- `getProblemById`: Get a single problem
- `createProblem`: Create a new problem
- `updateProblem`: Update an existing problem
- `submitAttempt`: Record a user's attempt

### User Services

Functions for user management:
- `getUserById`: Get user details
- `getUserAttempts`: Get user's question attempts
- `updateUserProfile`: Update user profile

### Analytics Services

Functions for performance analytics:
- `getUserPerformance`: Get performance metrics
- `getAccuracyByTag`: Get accuracy by question tag
- `getTimeSpentMetrics`: Get time spent metrics

## Integration with API Routes

These services are used by API routes in `/app/api` to handle database operations:

```typescript
// Example API route using a service
import { getProblems } from '@/service/problems/queries';

export async function GET(request: NextRequest) {
  const searchParams = request.nextUrl.searchParams;
  const examName = searchParams.get("examName") || "GRE";
  const sectionName = searchParams.get("sectionName") || "quants";
  const tags = searchParams.get("tags") ? JSON.parse(searchParams.get("tags")!) : null;
  
  const problems = await getProblems(examName, sectionName, tags);
  
  return NextResponse.json({ problems });
}
```

## Database Interaction

Services use Prisma client to interact with the database:
- Handle complex queries with proper relations
- Implement business logic for data operations
- Provide a clean API for frontend consumption
- Handle error cases and validation