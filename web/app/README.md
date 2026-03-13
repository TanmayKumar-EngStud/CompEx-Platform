# App Directory

This directory contains the Next.js App Router implementation, which handles routing, layouts, and API endpoints.

## Structure

* **app/(dashboard)**: Main application routes with dashboard layout
  * **problems**: Question browsing and solving interface
  * **analytics**: User performance analytics
* **app/api**: Backend API routes
  * **problems**: Question-related endpoints
  * **analytics**: Analytics data endpoints
  * **auth**: Authentication endpoints

## Key Components

### Page Components

Page components define the content for each route. They:
- Fetch data from API endpoints
- Render the appropriate UI components
- Handle client-side navigation

### API Routes

API routes provide backend functionality:
- `GET/POST /api/problems`: Fetch and filter questions
- `GET/POST /api/problems/[id]`: Individual question operations
- `POST /api/problems/[id]/attempts`: Submit question attempts

## Integration with Other Folders

- Uses components from `/features` for business functionality
- Uses components from `/shared` for UI elements
- Connects to database via Prisma client
- Implements business logic defined in `/service`

## Example Flow

1. User navigates to `/problems`
2. `app/problems/page.tsx` renders
3. Page fetches data from `/api/problems`
4. API route uses Prisma to query database
5. Data is passed to components from `/features/question-solving`
6. UI is rendered with components from `/shared/components`