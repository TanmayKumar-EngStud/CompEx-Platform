/**
 * Legacy service file - replaced by focused service modules
 * 
 * This file now re-exports functions from the new focused service modules
 * to maintain backward compatibility while implementing better separation of concerns.
 * 
 * @deprecated - Import directly from specific service modules:
 * - question-pagination-service.ts
 * - question-details-service.ts  
 * - question-attempt-service.ts
 */

// Re-export functions from focused service modules
export { 
   getProblemsForPagination,
   type PaginatedProblemData,
   type ProblemWithAttempt,
   type ProblemSetWithAttempts
} from "./question-pagination-service";

export { 
   getQuestionDetails,
   type QuestionDetails
} from "./question-details-service";

export { 
   submitUserAttemptSERVER as submitUserAttempt,
   type AttemptResult
} from "./question-attempt-service";