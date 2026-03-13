/**
 * Shuffle Loading State Component
 * 
 * Displays an animated loading state specifically for question shuffling operations.
 * This component provides visual feedback to users during shuffle operations.
 */

import React from "react";

interface ShuffleLoadingStateProps {
  message?: string;
  className?: string;
}

export const ShuffleLoadingState: React.FC<ShuffleLoadingStateProps> = ({
  message = "Shuffling questions...",
  className = ""
}) => {
  return (
    <div className={`flex flex-col items-center justify-center py-8 px-4 ${className}`}>
      {/* Animated shuffle icon */}
      <div className="relative mb-4">
        <div className="flex space-x-1">
          {[0, 1, 2].map((index) => (
            <div
              key={index}
              className="w-3 h-8 bg-primary/60 rounded animate-pulse"
              style={{
                animationDelay: `${index * 0.2}s`,
                animationDuration: '1.2s'
              }}
            />
          ))}
        </div>
        
        {/* Shuffle arrows animation */}
        <div className="absolute -top-2 -right-6 text-primary animate-bounce">
          <svg 
            className="w-5 h-5" 
            fill="none" 
            stroke="currentColor" 
            viewBox="0 0 24 24"
          >
            <path 
              strokeLinecap="round" 
              strokeLinejoin="round" 
              strokeWidth={2} 
              d="M7 16V4m0 0L3 8m4-4l4 4m6 0v12m0 0l4-4m-4 4l-4-4" 
            />
          </svg>
        </div>
      </div>

      {/* Loading message */}
      <p className="text-muted-foreground text-sm font-medium animate-pulse">
        {message}
      </p>
      
      {/* Progress dots */}
      <div className="flex space-x-1 mt-3">
        {[0, 1, 2].map((index) => (
          <div
            key={index}
            className="w-2 h-2 bg-primary/40 rounded-full animate-pulse"
            style={{
              animationDelay: `${index * 0.3}s`,
              animationDuration: '1s'
            }}
          />
        ))}
      </div>
    </div>
  );
};