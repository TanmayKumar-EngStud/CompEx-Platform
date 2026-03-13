import { create } from "zustand";

export interface QuestionTimer {
  questionId: number;
  startTime: number;
  elapsedTime: number; // in milliseconds
  isRunning: boolean;
  lastRecordedTime: number; // the time when user selected an option
  hasRecordedTime: boolean; // whether user has selected an option
}

interface TimerState {
  questionTimers: { [questionId: number]: QuestionTimer };
  currentQuestionId: number | null;
  showTimer: boolean; // global setting to show/hide timer in UI
  
  // Timer management
  startTimer: (questionId: number) => void;
  stopTimer: (questionId: number) => void;
  pauseTimer: (questionId: number) => void;
  resumeTimer: (questionId: number) => void;
  recordOptionSelectedTime: (questionId: number) => void;
  clearRecordedTime: (questionId: number) => void;
  getElapsedTime: (questionId: number) => number;
  getFormattedTime: (questionId: number) => string;
  
  // Settings
  setShowTimer: (show: boolean) => void;
  
  // Utility
  switchQuestion: (fromQuestionId: number | null, toQuestionId: number) => void;
  clearTimer: (questionId: number) => void;
  clearAllTimers: () => void;
}

// Helper function to format time as MM:SS
const formatTime = (milliseconds: number): string => {
  const totalSeconds = Math.floor(milliseconds / 1000);
  const minutes = Math.floor(totalSeconds / 60);
  const seconds = totalSeconds % 60;
  return `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
};

export const useTimerStore = create<TimerState>((set, get) => ({
  questionTimers: {},
  currentQuestionId: null,
  showTimer: true, // Default to show timer
  
  startTimer: (questionId: number) => {
    const state = get();
    const now = Date.now();
    
    set({
      questionTimers: {
        ...state.questionTimers,
        [questionId]: {
          questionId,
          startTime: now,
          elapsedTime: state.questionTimers[questionId]?.elapsedTime || 0,
          isRunning: true,
          lastRecordedTime: 0,
          hasRecordedTime: false,
        }
      },
      currentQuestionId: questionId
    });
  },
  
  stopTimer: (questionId: number) => {
    const state = get();
    const timer = state.questionTimers[questionId];
    
    if (timer && timer.isRunning) {
      const now = Date.now();
      const additionalTime = now - timer.startTime;
      
      set({
        questionTimers: {
          ...state.questionTimers,
          [questionId]: {
            ...timer,
            elapsedTime: timer.elapsedTime + additionalTime,
            isRunning: false,
          }
        }
      });
    }
  },
  
  pauseTimer: (questionId: number) => {
    const state = get();
    const timer = state.questionTimers[questionId];
    
    if (timer && timer.isRunning) {
      const now = Date.now();
      const additionalTime = now - timer.startTime;
      
      set({
        questionTimers: {
          ...state.questionTimers,
          [questionId]: {
            ...timer,
            elapsedTime: timer.elapsedTime + additionalTime,
            isRunning: false,
          }
        }
      });
    }
  },
  
  resumeTimer: (questionId: number) => {
    const state = get();
    const timer = state.questionTimers[questionId];
    
    if (timer && !timer.isRunning) {
      const now = Date.now();
      
      set({
        questionTimers: {
          ...state.questionTimers,
          [questionId]: {
            ...timer,
            startTime: now,
            isRunning: true,
          }
        },
        currentQuestionId: questionId
      });
    }
  },
  
  recordOptionSelectedTime: (questionId: number) => {
    const state = get();
    const timer = state.questionTimers[questionId];
    
    if (timer) {
      const currentElapsed = get().getElapsedTime(questionId);
      
      set({
        questionTimers: {
          ...state.questionTimers,
          [questionId]: {
            ...timer,
            lastRecordedTime: currentElapsed,
            hasRecordedTime: true,
          }
        }
      });
    }
  },
  
  clearRecordedTime: (questionId: number) => {
    const state = get();
    const timer = state.questionTimers[questionId];
    
    if (timer) {
      set({
        questionTimers: {
          ...state.questionTimers,
          [questionId]: {
            ...timer,
            lastRecordedTime: 0,
            hasRecordedTime: false,
          }
        }
      });
    }
  },
  
  getElapsedTime: (questionId: number): number => {
    const state = get();
    const timer = state.questionTimers[questionId];
    
    if (!timer) return 0;
    
    if (timer.isRunning) {
      const now = Date.now();
      return timer.elapsedTime + (now - timer.startTime);
    }
    
    return timer.elapsedTime;
  },
  
  getFormattedTime: (questionId: number): string => {
    const elapsed = get().getElapsedTime(questionId);
    return formatTime(elapsed);
  },
  
  setShowTimer: (show: boolean) => {
    set({ showTimer: show });
  },
  
  switchQuestion: (fromQuestionId: number | null, toQuestionId: number) => {
    const state = get();
    
    // Stop the current timer if running
    if (fromQuestionId && state.questionTimers[fromQuestionId]?.isRunning) {
      get().pauseTimer(fromQuestionId);
    }
    
    // Start or resume the new question timer
    const targetTimer = state.questionTimers[toQuestionId];
    if (targetTimer) {
      // Resume existing timer
      get().resumeTimer(toQuestionId);
    } else {
      // Start new timer
      get().startTimer(toQuestionId);
    }
  },
  
  clearTimer: (questionId: number) => {
    const state = get();
    const { [questionId]: removed, ...remainingTimers } = state.questionTimers;
    
    set({
      questionTimers: remainingTimers,
      currentQuestionId: state.currentQuestionId === questionId ? null : state.currentQuestionId
    });
  },
  
  clearAllTimers: () => {
    set({
      questionTimers: {},
      currentQuestionId: null
    });
  }
}));