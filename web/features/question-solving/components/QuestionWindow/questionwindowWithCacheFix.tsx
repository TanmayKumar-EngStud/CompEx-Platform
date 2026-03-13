/**
 * Question Window with Cache Fix Integration
 * 
 * This is an example of how to integrate the cache fix solution
 * with your existing question window component.
 */

import React from "react";
import { QuestionFloatingWindowProps } from "@/features/question-solving/hooks/(definitions)/questionDefinition";
import PrismaErrorHandler from "@/shared/components/error-handling/PrismaErrorHandler";

// Import your existing question window component
import QuestionAttempt from "./questionwindow";

const QuestionAttemptWithCacheFix: React.FC<QuestionFloatingWindowProps> = (props) => {
  return (
    <PrismaErrorHandler
      autoRefresh={true}
      showErrorUI={true}
      onError={(error) => {
        console.log('🚨 Cache-related error detected:', error.message);
        // Optional: Add additional error handling logic here
      }}
    >
      <QuestionAttempt
        {...props}
      />
    </PrismaErrorHandler>
  );
};

export default QuestionAttemptWithCacheFix;