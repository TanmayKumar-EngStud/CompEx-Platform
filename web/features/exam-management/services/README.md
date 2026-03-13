# Exam Management Services

This directory contains service functions that handle business logic for the exam management feature.

## Available Services

* **exam-queries.ts**: Functions to fetch exam types and sections
* **tag-queries.ts**: Functions to fetch and manage tags
* **exam-mutations.ts**: Functions to update exam configuration

## Service Details

### exam-queries.ts

Functions for fetching exam types and sections:

```typescript
// Fetch all exam types
async function fetchExamTypes() {
  // Fetches available exam types (GRE, GMAT, CAT, etc.)
  // Returns formatted exam type data
}

// Fetch sections for an exam type
async function fetchSections(examTypeId: string) {
  // Fetches sections for a specific exam type
  // E.g., Quants, Verbal for GRE
}

// Fetch exam configuration
async function fetchExamConfig(examTypeId: string) {
  // Fetches complete exam configuration
  // Includes sections, time limits, question counts
}
```

### tag-queries.ts

Functions for fetching and managing tags:

```typescript
// Fetch tags for exam and section
async function fetchTags(examTypeId: string, sectionId?: string) {
  // Fetches tags filtered by exam type and optionally section
  // Returns formatted tag data with counts
}

// Fetch popular tags
async function fetchPopularTags(limit: number = 10) {
  // Fetches most frequently used tags
  // Used for tag suggestions
}

// Search tags
async function searchTags(query: string) {
  // Searches tags by name
  // Used for tag selection autocomplete
}
```

### exam-mutations.ts

Functions for updating exam configuration:

```typescript
// Save user exam preferences
async function saveExamPreferences(userId: string, preferences: ExamPreferences) {
  // Saves user's preferred exam type, sections, and tags
  // Used for personalization
}

// Create new tag
async function createTag(tagData: TagData) {
  // Creates a new tag in the system
  // Admin functionality
}

// Update exam configuration
async function updateExamConfig(examTypeId: string, configData: ExamConfigData) {
  // Updates exam configuration
  // Admin functionality
}
```

## Integration with API

These services interact with the following API endpoints:
- `/api/exams/types` - Fetch exam types
- `/api/exams/sections` - Fetch sections for exam types
- `/api/tags` - Fetch and manage tags
- `/api/users/preferences/exams` - Save user exam preferences

## Integration with Components

These services are used by:
- Exam selector components to display available exams
- Section filter components to show relevant sections
- Tag selector components to display and filter tags
- Admin components to manage exam configuration

## Error Handling

All services include proper error handling:
- API request failures
- Validation errors
- Data formatting issues
- Authentication and authorization checks