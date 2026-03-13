/**
 * Priority Cache Progress Component
 * 
 * Shows loading progress for prioritized cache operations with
 * visual indicators for different priority levels.
 */

"use client";
import React from 'react';
import { Badge } from "@/shared/components/feedback/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/shared/components/ui/card";
import { CheckCircle, Clock, Download, Zap } from "lucide-react";

// Simple progress bar component
const Progress: React.FC<{ value: number; className?: string }> = ({ value, className = "" }) => {
  return (
    <div className={`w-full bg-gray-200 rounded-full h-2 ${className}`}>
      <div 
        className="bg-blue-600 h-2 rounded-full transition-all duration-300 ease-in-out"
        style={{ width: `${Math.min(100, Math.max(0, value))}%` }}
      />
    </div>
  );
};

interface PriorityCacheProgressProps {
  loadingState: {
    immediate: boolean;
    high: boolean;
    background: boolean;
    progress: {
      completed: number;
      total: number;
      currentTask: string;
    };
  };
  className?: string;
  showDetails?: boolean;
}

const PriorityIcon: React.FC<{ priority: 'immediate' | 'high' | 'background' | 'completed' }> = ({ priority }) => {
  switch (priority) {
    case 'immediate':
      return <Zap className="h-4 w-4 text-yellow-500" />;
    case 'high':
      return <Clock className="h-4 w-4 text-orange-500" />;
    case 'background':
      return <Download className="h-4 w-4 text-blue-500" />;
    case 'completed':
      return <CheckCircle className="h-4 w-4 text-green-500" />;
    default:
      return null;
  }
};

const PriorityBadge: React.FC<{ 
  type: 'immediate' | 'high' | 'background';
  isActive: boolean;
  isCompleted: boolean;
}> = ({ type, isActive, isCompleted }) => {
  const getVariant = () => {
    if (isCompleted) return 'default';
    if (isActive) return 'destructive';
    return 'secondary';
  };

  const getLabel = () => {
    switch (type) {
      case 'immediate':
        return 'Critical';
      case 'high':
        return 'Important';
      case 'background':
        return 'Background';
      default:
        return type;
    }
  };

  return (
    <Badge variant={getVariant()} className="flex items-center gap-1">
      <PriorityIcon priority={isCompleted ? 'completed' : type} />
      {getLabel()}
      {isActive && <span className="animate-pulse">•</span>}
    </Badge>
  );
};

export const PriorityCacheProgress: React.FC<PriorityCacheProgressProps> = ({
  loadingState,
  className = "",
  showDetails = true
}) => {
  const { immediate, high, background, progress } = loadingState;
  const { completed, total, currentTask } = progress;
  
  // Don't show if nothing is loading
  if (!immediate && !high && !background && completed === 0) {
    return null;
  }

  const progressPercentage = total > 0 ? (completed / total) * 100 : 0;
  const isAnyLoading = immediate || high || background;

  return (
    <Card className={`w-full ${className}`}>
      <CardHeader className="pb-3">
        <CardTitle className="text-sm font-medium flex items-center gap-2">
          <Download className="h-4 w-4" />
          Intelligent Cache Loading
        </CardTitle>
      </CardHeader>
      
      <CardContent className="space-y-3">
        {/* Overall Progress */}
        <div className="space-y-2">
          <div className="flex justify-between text-sm">
            <span>Overall Progress</span>
            <span className="text-muted-foreground">
              {completed}/{total} tasks
            </span>
          </div>
          <Progress 
            value={progressPercentage} 
            className="h-2"
          />
        </div>

        {/* Priority Status Badges */}
        <div className="flex gap-2 flex-wrap">
          <PriorityBadge 
            type="immediate" 
            isActive={immediate} 
            isCompleted={!immediate && completed > 0}
          />
          <PriorityBadge 
            type="high" 
            isActive={high} 
            isCompleted={!high && completed > 2}
          />
          <PriorityBadge 
            type="background" 
            isActive={background} 
            isCompleted={!background && completed === total}
          />
        </div>

        {/* Current Task */}
        {currentTask && isAnyLoading && (
          <div className="text-xs text-muted-foreground bg-muted p-2 rounded">
            <span className="font-medium">Current:</span> {currentTask}
          </div>
        )}

        {/* Details */}
        {showDetails && (
          <div className="text-xs text-muted-foreground space-y-1">
            <div className="flex items-center gap-2">
              <PriorityIcon priority="immediate" />
              <span>Critical data loads first for immediate use</span>
            </div>
            <div className="flex items-center gap-2">
              <PriorityIcon priority="high" />
              <span>Related sections load next for quick access</span>
            </div>
            <div className="flex items-center gap-2">
              <PriorityIcon priority="background" />
              <span>Other exams load in background when idle</span>
            </div>
          </div>
        )}

        {/* Success State */}
        {!isAnyLoading && completed === total && total > 0 && (
          <div className="flex items-center gap-2 text-sm text-green-600 bg-green-50 p-2 rounded">
            <CheckCircle className="h-4 w-4" />
            <span>All data cached successfully!</span>
          </div>
        )}
      </CardContent>
    </Card>
  );
};

/**
 * Compact version for smaller spaces
 */
export const PriorityCacheProgressCompact: React.FC<PriorityCacheProgressProps> = ({
  loadingState,
  className = ""
}) => {
  const { immediate, high, background, progress } = loadingState;
  const { completed, total, currentTask } = progress;
  
  if (!immediate && !high && !background && completed === 0) {
    return null;
  }

  const progressPercentage = total > 0 ? (completed / total) * 100 : 0;
  const isAnyLoading = immediate || high || background;

  return (
    <div className={`flex items-center gap-2 p-2 bg-muted/50 rounded-lg ${className}`}>
      <div className="flex gap-1">
        <PriorityIcon priority={immediate ? 'immediate' : high ? 'high' : background ? 'background' : 'completed'} />
      </div>
      
      <div className="flex-1">
        <Progress value={progressPercentage} className="h-1" />
      </div>
      
      <div className="text-xs text-muted-foreground">
        {completed}/{total}
      </div>
      
      {isAnyLoading && (
        <div className="text-xs text-muted-foreground animate-pulse">
          Loading...
        </div>
      )}
    </div>
  );
};

export default PriorityCacheProgress;