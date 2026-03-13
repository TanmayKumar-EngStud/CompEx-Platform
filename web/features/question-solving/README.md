# Question Solving Feature

This feature handles the display, interaction, and submission of questions and answers.

## Components

* **question-display.tsx**: Renders a question with options and solution
* **answer-options.tsx**: Displays answer choices for multiple-choice questions
* **solution-viewer.tsx**: Shows the solution after submission
* **progress-tracker.tsx**: Displays progress through a set of questions

### Templates

The `components/templates` folder contains specialized renderers for different question types:
- `data-sufficiency.tsx`: For data sufficiency questions
- `reading-comprehension.tsx`: For reading comprehension questions
- `numeric-entry.tsx`: For numeric entry questions

## Services

* **question-queries.ts**: Functions to fetch questions from the API
* **answer-mutations.ts**: Functions to submit answers
* **solution-formatter.ts**: Formats solution text with LaTeX support
* **progress-calculator.ts**: Calculates progress metrics

## Hooks

* **use-question-navigation.ts**: Manages navigation between questions
* **use-answer-submission.ts**: Handles answer submission logic
* **use-solution-display.ts**: Controls when to show solutions
* **fetchProblems.tsx**: Fetches problems with filtering

## Integration Flow

1. User selects exam type and section in the UI
2. `fetchProblems.tsx` hook fetches filtered questions
3. `question-display.tsx` renders the question
4. User selects an answer in `answer-options.tsx`
5. `use-answer-submission.ts` submits the answer
6. `solution-viewer.tsx` displays the solution if enabled

## API Interactions

- Fetches questions from `/api/problems/getProblems`
- Submits answers to `/api/problems/[id]/attempts`
- Gets solutions from `/api/problems/[id]/solution`

## State Management

Uses Zustand stores to manage:
- Current question state
- Answer selections
- Navigation state
- Progress tracking