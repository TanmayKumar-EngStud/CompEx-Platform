# Question Solving Services

This directory contains service functions that handle business logic for the question-solving feature.

## Available Services

-  **question-queries.ts**: Functions to fetch questions from the API
-  **answer-mutations.ts**: Functions to submit answers
-  **solution-formatter.ts**: Formats solution text with LaTeX support
-  **progress-calculator.ts**: Calculates progress metrics
-  **question-validator.ts**: Validates question data and answers

## Service Details

### question-queries.ts

Functions for fetching questions:

```typescript
// Fetch questions with filtering
async function fetchQuestions(
   examType: string,
   section: string,
   tags?: string[]
) {
   // Fetches questions from API with filters
   // Returns formatted question data
}

// Fetch a single question by ID
async function fetchQuestionById(id: string) {
   // Fetches specific question
   // Includes options, solution, and metadata
}

// Fetch related questions
async function fetchRelatedQuestions(questionId: string, count: number = 3) {
   // Fetches questions similar to the current one
   // Based on tags and difficulty
}
```

### answer-mutations.ts

Functions for submitting and processing answers:

```typescript
// Submit an answer attempt
async function submitAnswer(
   questionId: string,
   answer: string,
   timeSpent: number
) {
   // Validates answer format
   // Submits to API
   // Returns correctness and solution
}

// Update answer after review
async function updateAnswerAttempt(attemptId: string, notes: string) {
   // Updates an existing attempt with notes
   // Used for review and learning
}
```

### solution-formatter.ts

Functions for formatting solution text:

```typescript
// Format solution with LaTeX support
function formatSolution(solutionText: string) {
   // Processes LaTeX expressions
   // Formats step-by-step solutions
   // Handles special characters and formatting
}

// Generate simplified solution
function generateSimplifiedSolution(fullSolution: string) {
   // Creates a simplified version for hints
}
```

### progress-calculator.ts

Functions for calculating progress metrics:

```typescript
// Calculate completion percentage
function calculateCompletion(
   totalQuestions: number,
   attemptedQuestions: number
) {
   // Returns percentage of questions completed
}

// Calculate accuracy metrics
function calculateAccuracy(attempts: Attempt[]) {
   // Calculates overall and per-category accuracy
}

// Calculate improvement over time
function calculateImprovement(historicalAttempts: Attempt[]) {
   // Analyzes improvement trends
}
```

### question-validator.ts

Functions for validating questions and answers:

```typescript
// Validate question data
function validateQuestion(questionData: QuestionData) {
   // Ensures question has required fields
   // Validates options and solution
}

// Validate answer format
function validateAnswer(answer: string, questionType: string) {
   // Checks if answer matches expected format
   // Different validation for multiple choice, numeric, etc.
}
```

## Integration with API

These services interact with the following API endpoints:

-  `/api/problems/getProblems` - Fetch filtered problems
-  `/api/problems/getProblemById` - Fetch a specific problem
-  `/api/problems/attempts` - Submit and retrieve attempts

## Integration with Components

These services are used by:

-  Question display components to show questions
-  Answer submission components to process answers
-  Solution viewers to format and display solutions
-  Progress trackers to show completion metrics

## Error Handling

All services include proper error handling:

-  API request failures
-  Validation errors
-  Data formatting issues
-  Timeout handling
