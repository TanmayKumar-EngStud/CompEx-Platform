import React, { useEffect, useState } from "react";
import { useTimerStore } from "@/features/user-analytics/hooks/timerDefinition";

interface TimerProps {
  questionId: number;
  className?: string;
}

const Timer: React.FC<TimerProps> = ({ questionId, className = "" }) => {
  const { 
    getFormattedTime, 
    showTimer, 
    questionTimers,
    getElapsedTime 
  } = useTimerStore();
  
  const [displayTime, setDisplayTime] = useState("00:00");
  const [showBlinkAnimation, setShowBlinkAnimation] = useState(false);
  
  const timer = questionTimers[questionId];
  
  // Update display time every second for running timers
  useEffect(() => {
    if (!timer?.isRunning) return;
    
    const interval = setInterval(() => {
      setDisplayTime(getFormattedTime(questionId));
    }, 1000);
    
    return () => clearInterval(interval);
  }, [timer?.isRunning, questionId, getFormattedTime]);
  
  // Update display time when timer changes
  useEffect(() => {
    setDisplayTime(getFormattedTime(questionId));
  }, [questionId, getFormattedTime, timer?.elapsedTime]);
  
  // Trigger blink animation when user records time (selects option)
  useEffect(() => {
    if (timer?.hasRecordedTime && timer.lastRecordedTime > 0) {
      setShowBlinkAnimation(true);
      const timeout = setTimeout(() => {
        setShowBlinkAnimation(false);
      }, 1000); // Blink for 1 second
      
      return () => clearTimeout(timeout);
    }
  }, [timer?.lastRecordedTime, timer?.hasRecordedTime]);
  
  // Don't render if timer is disabled in settings
  if (!showTimer) {
    return null;
  }
  
  return (
    <div className={`flex items-center gap-2 ${className}`}>
      <div className="flex items-center gap-1">
        <svg 
          className="w-4 h-4 text-muted-foreground" 
          fill="none" 
          strokeWidth="2" 
          stroke="currentColor" 
          viewBox="0 0 24 24"
        >
          <circle cx="12" cy="12" r="10"/>
          <polyline points="12,6 12,12 16,14"/>
        </svg>
        <span 
          className={`font-mono text-sm font-medium transition-all duration-300 ${
            showBlinkAnimation 
              ? "text-green-500 animate-pulse scale-110" 
              : timer?.isRunning 
                ? "text-foreground" 
                : "text-muted-foreground"
          }`}
        >
          {displayTime}
        </span>
      </div>
      
      {/* Status indicator */}
      <div className="flex items-center">
        {timer?.isRunning && (
          <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"/>
        )}
        {timer && !timer.isRunning && timer.elapsedTime > 0 && (
          <div className="w-2 h-2 bg-yellow-500 rounded-full"/>
        )}
        {timer?.hasRecordedTime && (
          <div className={`ml-1 text-xs transition-all duration-300 ${
            showBlinkAnimation ? "text-green-500 font-bold" : "text-green-600"
          }`}>
            ✓
          </div>
        )}
      </div>
      
      {/* Last recorded time tooltip */}
      {timer?.hasRecordedTime && timer.lastRecordedTime > 0 && (
        <div className="text-xs text-muted-foreground" title="Time when option was selected">
          ({Math.floor(timer.lastRecordedTime / 1000)}s)
        </div>
      )}
    </div>
  );
};

export default Timer;