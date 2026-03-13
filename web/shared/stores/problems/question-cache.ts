import { create } from "zustand";
import { QuestionState } from "./navigation";

/**
 * Question cache management for performance optimization
 * 
 * Handles:
 * - LRU cache for question content
 * - Prefetching logic for smooth navigation
 * - Cache eviction and management
 */

interface CachedQuestion extends QuestionState {
  cachedAt: number;
  accessCount: number;
  lastAccessed: number;
}

interface QuestionCache {
  [questionId: number]: CachedQuestion;
}

type QuestionIds = number | { [key: string]: number[] };

export interface QuestionCacheState {
  questionCache: QuestionCache;
  cacheSize: number;
  prefetchSize: number;
  lastPrefetchIndex: number;
}

export interface QuestionCacheActions {
  addToCache: (questions: QuestionState[]) => void;
  getFromCache: (questionId: number) => QuestionState | null;
  markQuestionAccessed: (questionId: number) => void;
  evictLRUFromCache: () => void;
  prefetchQuestions: (currentIndex: number, questionIds: QuestionIds[]) => Promise<void>;
  invalidateQuestions: (questionIds: number[]) => void;
  clearCache: () => void;
  setCacheSize: (size: number) => void;
  setPrefetchSize: (size: number) => void;
}

export type QuestionCacheStore = QuestionCacheState & QuestionCacheActions;

/**
 * Helper function to flatten question IDs for prefetching
 */
function flattenQuestionIds(questionIds: QuestionIds[]): number[] {
  let ids: number[] = [];
  questionIds.forEach((id) => {
    if (typeof id === "number") {
      ids.push(id);
    } else {
      Object.values(id)[0].forEach((i) => {
        ids.push(i);
      });
    }
  });
  return ids;
}

/**
 * Zustand store for question cache management
 * 
 * @example
 * ```ts
 * const { getFromCache, addToCache, prefetchQuestions } = useQuestionCacheStore();
 * ```
 */
export const useQuestionCacheStore = create<QuestionCacheStore>((set, get) => ({
  // State
  questionCache: {},
  cacheSize: 25, // Cache up to 25 questions
  prefetchSize: 8, // Prefetch 8 questions ahead
  lastPrefetchIndex: -1,

  // Actions
  /**
   * Add questions to cache with LRU eviction
   */
  addToCache: (questions) => {
    const state = get();
    const now = Date.now();
    const newCache = { ...state.questionCache };

    questions.forEach(question => {
      const existing = newCache[question.problemid];
      newCache[question.problemid] = {
        ...question,
        cachedAt: existing?.cachedAt || now,
        accessCount: (existing?.accessCount || 0) + 1,
        lastAccessed: now,
      };
    });

    // Evict LRU items if cache is full
    const cacheKeys = Object.keys(newCache);
    if (cacheKeys.length > state.cacheSize) {
      const sortedByLRU = cacheKeys
        .map(key => ({ id: parseInt(key), ...newCache[parseInt(key)] }))
        .sort((a, b) => a.lastAccessed - b.lastAccessed);

      const itemsToRemove = sortedByLRU.slice(0, cacheKeys.length - state.cacheSize);
      itemsToRemove.forEach(item => {
        delete newCache[item.id];
      });
    }

    set({ questionCache: newCache });
  },

  /**
   * Get question from cache without updating access time
   */
  getFromCache: (questionId) => {
    const state = get();
    const cached = state.questionCache[questionId];
    if (cached) {
      // Return question without cache metadata
      const { cachedAt, accessCount, lastAccessed, ...question } = cached;
      return question;
    }
    return null;
  },

  /**
   * Mark question as accessed (updates LRU data)
   */
  markQuestionAccessed: (questionId) => {
    const state = get();
    const cached = state.questionCache[questionId];
    if (cached) {
      const newCache = { ...state.questionCache };
      newCache[questionId] = {
        ...cached,
        lastAccessed: Date.now(),
        accessCount: cached.accessCount + 1,
      };
      set({ questionCache: newCache });
    }
  },

  /**
   * Manually evict least recently used item from cache
   */
  evictLRUFromCache: () => {
    const state = get();
    const cacheKeys = Object.keys(state.questionCache);
    if (cacheKeys.length === 0) return;

    const lruItem = cacheKeys
      .map(key => ({ id: parseInt(key), ...state.questionCache[parseInt(key)] }))
      .sort((a, b) => a.lastAccessed - b.lastAccessed)[0];

    const newCache = { ...state.questionCache };
    delete newCache[lruItem.id];
    set({ questionCache: newCache });
  },

  /**
   * Prefetch questions for smooth navigation
   * 
   * @param currentIndex - Current question index for prefetch calculation
   * @param questionIds - Array of question IDs to prefetch from
   */
  prefetchQuestions: async (currentIndex, questionIds) => {
    const state = get();

    // Prevent excessive prefetching - only prefetch if we've moved significantly
    if (Math.abs(currentIndex - state.lastPrefetchIndex) < 3) {
      console.log(`⏭️ Skipping prefetch - too close to last prefetch (current: ${currentIndex}, last: ${state.lastPrefetchIndex})`);
      return;
    }

    const flattenedIds = flattenQuestionIds(questionIds);
    const prefetchStart = currentIndex + 5; // windowSize
    const prefetchEnd = Math.min(prefetchStart + state.prefetchSize, flattenedIds.length);

    const questionsToFetch: number[] = [];
    for (let i = prefetchStart; i < prefetchEnd; i++) {
      const questionId = flattenedIds[i];
      if (!state.questionCache[questionId]) {
        questionsToFetch.push(questionId);
      }
    }

    if (questionsToFetch.length > 0) {
      // Update last prefetch index IMMEDIATELY to prevent race conditions
      set({ lastPrefetchIndex: currentIndex });

      try {
        console.log(`🚀 Prefetching ${questionsToFetch.length} questions: [${questionsToFetch.join(', ')}]`);
        const response = await fetch("/api/problems/getQuestions", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ questionId: questionsToFetch }),
        });
        const questions: QuestionState[] = await response.json();

        // Add to cache
        get().addToCache(questions);
        console.log(`✅ Prefetched and cached ${questions.length} questions`);
      } catch (error) {
        console.warn("Failed to prefetch questions:", error);
      }
    } else {
      console.log(`📋 All upcoming questions already cached (cache size: ${Object.keys(state.questionCache).length})`);
      set({ lastPrefetchIndex: currentIndex });
    }
  },

  /**
   * Invalidate specific questions from cache so they get re-fetched with fresh data
   * Used after submitting answers to ensure solved state is reflected on re-navigation
   */
  invalidateQuestions: (questionIds) => {
    const state = get();
    const newCache = { ...state.questionCache };
    questionIds.forEach(id => { delete newCache[id]; });
    set({ questionCache: newCache });
  },

  clearCache: () => set({ questionCache: {} }),
  setCacheSize: (size) => set({ cacheSize: size }),
  setPrefetchSize: (size) => set({ prefetchSize: size }),
}));