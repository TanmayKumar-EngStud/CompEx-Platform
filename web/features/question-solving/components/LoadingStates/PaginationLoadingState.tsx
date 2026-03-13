/**
 * Pagination Loading State Component
 * 
 * Displays loading states for pagination operations including page navigation,
 * section switching, and filter application.
 */

import React from "react";
import { Loader2 } from "lucide-react";

interface PaginationLoadingStateProps {
  type?: 'navigation' | 'filter' | 'section' | 'general';
  message?: string;
  className?: string;
  showProgress?: boolean;
  progress?: number; // 0-100
}

export const PaginationLoadingState: React.FC<PaginationLoadingStateProps> = ({
  type = 'general',
  message,
  className = "",
  showProgress = false,
  progress = 0
}) => {
  const getDefaultMessage = (type: string) => {
    switch (type) {
      case 'navigation':
        return 'Loading questions...';
      case 'filter':
        return 'Loading filtered questions...';
      case 'section':
        return 'Switching section...';
      default:
        return 'Loading...';
    }
  };

  const displayMessage = message || getDefaultMessage(type);

  // consistent loading spinner for all types
  const getLoadingIcon = (type: string) => {
    return <Loader2 className="w-8 h-8 animate-spin text-primary/80" />;
  };

  return (
    <div className={`flex flex-col items-center justify-center py-6 px-4 ${className}`}>
      {/* Loading icon */}
      <div className="text-primary mb-3">
        {getLoadingIcon(type)}
      </div>

      {/* Loading message */}
      <p className="text-muted-foreground text-sm font-medium mb-3">
        {displayMessage}
      </p>

      {/* Optional progress bar */}
      {showProgress && (
        <div className="w-48 bg-muted rounded-full h-2">
          <div
            className="bg-primary h-2 rounded-full transition-all duration-300 ease-out"
            style={{ width: `${Math.min(100, Math.max(0, progress))}%` }}
          />
        </div>
      )}

      {/* Animated dots */}
      <div className="flex space-x-1 mt-2">
        {[0, 1, 2].map((index) => (
          <div
            key={index}
            className="w-1.5 h-1.5 bg-primary/60 rounded-full animate-pulse"
            style={{
              animationDelay: `${index * 0.2}s`,
              animationDuration: '1.5s'
            }}
          />
        ))}
      </div>
    </div>
  );
};