/**
 * Question ID Manager
 * 
 * Handles efficient question ID array management for pagination, filtering,
 * and shuffling operations. This class maintains the question order state
 * and provides utilities for pagination calculations.
 * 
 * Updated to support QuestionIdItem format for better parent-child question handling.
 */

import { QuestionIdEntry, QuestionIdItem, QuestionIdGroup } from "../types/pagination-cache.types";

export interface QuestionIdState {
  /** Original unfiltered question ID entries */
  originalIds: QuestionIdEntry[];

  /** Currently active question ID entries (may be filtered or shuffled) */
  activeIds: QuestionIdEntry[];

  /** Filtered question ID entries (subset of original) */
  filteredIds: QuestionIdEntry[];

  /** Whether the active list is currently shuffled */
  isShuffled: boolean;

  /** Whether the active list is currently filtered */
  isFiltered: boolean;

  /** Applied filter tags */
  activeFilters: string[];

  /** Questions per page for pagination calculations */
  questionsPerPage: number;
}

export class QuestionIdManager {
  private state: QuestionIdState;

  constructor(
    originalIds: QuestionIdEntry[] = [],
    questionsPerPage: number = 10
  ) {
    this.state = {
      originalIds: [...originalIds],
      activeIds: [...originalIds],
      filteredIds: [],
      isShuffled: false,
      isFiltered: false,
      activeFilters: [],
      questionsPerPage
    };
  }

  /**
   * Initialize with original question ID entries
   */
  setOriginalIds(ids: QuestionIdEntry[]): void {
    this.state.originalIds = [...ids];

    // If no filters are active, update active IDs
    if (!this.state.isFiltered) {
      this.state.activeIds = [...ids];
    }
  }

  /**
   * Get the original unfiltered question ID entries
   */
  getOriginalIds(): QuestionIdEntry[] {
    return [...this.state.originalIds];
  }

  /**
   * Get currently active question ID entries
   */
  getActiveIds(): QuestionIdEntry[] {
    return [...this.state.activeIds];
  }

  /**
   * Apply filter and update active IDs
   */
  applyFilter(filteredIds: QuestionIdEntry[], filterTags: string[]): void {
    this.state.filteredIds = [...filteredIds];
    this.state.activeIds = [...filteredIds];
    this.state.isFiltered = true;
    this.state.isShuffled = false; // Reset shuffle when applying new filter
    this.state.activeFilters = [...filterTags];

    console.log(`🏷️  Applied filter: ${filteredIds.length} questions remaining`);
  }

  /**
   * Remove all filters and restore original IDs
   */
  removeFilter(): void {
    this.state.activeIds = [...this.state.originalIds];
    this.state.filteredIds = [];
    this.state.isFiltered = false;
    this.state.isShuffled = false; // Reset shuffle when removing filter
    this.state.activeFilters = [];

    console.log(`🔄 Filter removed: restored to ${this.state.originalIds.length} questions`);
  }

  /**
   * Shuffle the currently active question ID entries using Fisher-Yates algorithm
   */
  shuffleActiveIds(): QuestionIdEntry[] {
    if (this.state.activeIds.length === 0) {
      console.warn('⚠️  No active IDs to shuffle');
      return [];
    }

    const shuffled = this.fisherYatesShuffle([...this.state.activeIds]);
    this.state.activeIds = shuffled;
    this.state.isShuffled = true;

    console.log(`🔀 Shuffled ${shuffled.length} question ID entries`);
    return [...shuffled];
  }

  /**
   * Set active IDs to a pre-shuffled order (preserves advanced shuffle algorithms)
   */
  setShuffledActiveIds(shuffledIds: QuestionIdEntry[]): void {
    if (shuffledIds.length === 0) {
      console.warn('⚠️  Cannot set empty shuffled IDs');
      return;
    }

    // Validate that shuffledIds contains the same questions as current activeIds
    const currentIds = this.extractAllProblemIds(this.state.activeIds);
    const shuffledProblemIds = this.extractAllProblemIds(shuffledIds);
    const currentSet = new Set(currentIds);
    const shuffledSet = new Set(shuffledProblemIds);

    if (currentSet.size !== shuffledSet.size ||
      !Array.from(currentSet).every(id => shuffledSet.has(id))) {
      console.warn('⚠️  Shuffled IDs do not match current active IDs');
      return;
    }

    this.state.activeIds = [...shuffledIds];
    this.state.isShuffled = true;

    console.log(`✅ Applied pre-shuffled order to ${shuffledIds.length} question ID entries`);
  }

  /**
   * Restore original order of active IDs
   */
  restoreOriginalOrder(): void {
    if (this.state.isFiltered) {
      // If filtered, restore filtered order (not shuffled)
      this.state.activeIds = [...this.state.filteredIds];
    } else {
      // If not filtered, restore original order
      this.state.activeIds = [...this.state.originalIds];
    }

    this.state.isShuffled = false;
    console.log(`📋 Restored original order for ${this.state.activeIds.length} questions`);
  }

  /**
   * Get question ID entries for a specific page
   */
  getPageQuestionIds(pageNumber: number): QuestionIdEntry[] {
    const startIndex = (pageNumber - 1) * this.state.questionsPerPage;
    const endIndex = startIndex + this.state.questionsPerPage;

    const pageIds = this.state.activeIds.slice(startIndex, endIndex);

    console.log(`📄 Page ${pageNumber}: ${pageIds.length} question ID entries (indices ${startIndex}-${endIndex - 1})`);
    return pageIds;
  }

  /**
   * Calculate total number of pages based on active IDs
   */
  getTotalPages(): number {
    return Math.ceil(this.state.activeIds.length / this.state.questionsPerPage);
  }

  /**
   * Get total number of active questions
   */
  getTotalQuestions(): number {
    return this.state.activeIds.length;
  }

  /**
   * Find which page contains a specific question ID (searches within problem sets too)
   */
  findPageForQuestionId(questionId: string | number): number | null {
    const targetId = typeof questionId === 'string' ? parseInt(questionId, 10) : questionId;

    for (let i = 0; i < this.state.activeIds.length; i++) {
      const item = this.state.activeIds[i];

      // Check if it's an individual problem
      if ('problemid' in item && item.problemid === targetId) {
        return Math.floor(i / this.state.questionsPerPage) + 1;
      }

      // Check if it's a problem set with child problems
      if ('problemsSetId' in item && item.problems) {
        const hasChildProblem = item.problems.some(child => child.problemid === targetId);
        if (hasChildProblem) {
          return Math.floor(i / this.state.questionsPerPage) + 1;
        }
      }
    }

    return null;
  }

  /**
   * Get the index of a question within the active list (searches within problem sets too)
   */
  getQuestionIndex(questionId: string | number): number {
    const targetId = typeof questionId === 'string' ? parseInt(questionId, 10) : questionId;

    for (let i = 0; i < this.state.activeIds.length; i++) {
      const item = this.state.activeIds[i];

      // Check if it's an individual problem
      if ('problemid' in item && item.problemid === targetId) {
        return i;
      }

      // Check if it's a problem set with child problems
      if ('problemsSetId' in item && item.problems) {
        const hasChildProblem = item.problems.some(child => child.problemid === targetId);
        if (hasChildProblem) {
          return i;
        }
      }
    }

    return -1;
  }

  /**
   * Check if a specific page number is valid
   */
  isValidPage(pageNumber: number): boolean {
    return pageNumber >= 1 && pageNumber <= this.getTotalPages();
  }

  /**
   * Get question ID entries for a range of pages (useful for prefetching)
   */
  getPageRangeQuestionIds(startPage: number, endPage: number): QuestionIdEntry[] {
    const startIndex = (startPage - 1) * this.state.questionsPerPage;
    const endIndex = endPage * this.state.questionsPerPage;

    return this.state.activeIds.slice(startIndex, endIndex);
  }

  /**
   * Get current state information
   */
  getState(): Readonly<QuestionIdState> {
    return { ...this.state };
  }

  /**
   * Get pagination metadata for current state
   */
  getPaginationInfo(currentPage: number = 1): {
    currentPage: number;
    totalPages: number;
    totalQuestions: number;
    questionsPerPage: number;
    hasNextPage: boolean;
    hasPreviousPage: boolean;
    isFirstPage: boolean;
    isLastPage: boolean;
    startIndex: number;
    endIndex: number;
    pageQuestionIds: QuestionIdEntry[];
  } {
    const totalPages = this.getTotalPages();
    const totalQuestions = this.getTotalQuestions();
    const startIndex = (currentPage - 1) * this.state.questionsPerPage;
    const endIndex = Math.min(startIndex + this.state.questionsPerPage, totalQuestions);

    return {
      currentPage,
      totalPages,
      totalQuestions,
      questionsPerPage: this.state.questionsPerPage,
      hasNextPage: currentPage < totalPages,
      hasPreviousPage: currentPage > 1,
      isFirstPage: currentPage === 1,
      isLastPage: currentPage === totalPages,
      startIndex,
      endIndex,
      pageQuestionIds: this.getPageQuestionIds(currentPage)
    };
  }

  /**
   * Update questions per page setting
   */
  setQuestionsPerPage(questionsPerPage: number): void {
    if (questionsPerPage < 1) {
      console.warn('⚠️  Questions per page must be at least 1');
      return;
    }

    this.state.questionsPerPage = questionsPerPage;
    console.log(`📏 Updated questions per page to: ${questionsPerPage}`);
  }

  /**
   * Check if the manager has any questions
   */
  hasQuestions(): boolean {
    return this.state.activeIds.length > 0;
  }

  /**
   * Get summary statistics
   */
  getStats(): {
    totalOriginal: number;
    totalActive: number;
    totalFiltered: number;
    isShuffled: boolean;
    isFiltered: boolean;
    activeFilters: string[];
    totalPages: number;
    questionsPerPage: number;
  } {
    return {
      totalOriginal: this.state.originalIds.length,
      totalActive: this.state.activeIds.length,
      totalFiltered: this.state.filteredIds.length,
      isShuffled: this.state.isShuffled,
      isFiltered: this.state.isFiltered,
      activeFilters: [...this.state.activeFilters],
      totalPages: this.getTotalPages(),
      questionsPerPage: this.state.questionsPerPage
    };
  }

  /**
   * Export current state for persistence
   */
  exportState(): QuestionIdState {
    return { ...this.state };
  }

  /**
   * Import state from persistence
   */
  importState(state: Partial<QuestionIdState>): void {
    this.state = {
      ...this.state,
      ...state
    };

    console.log(`📥 Imported state: ${this.state.activeIds.length} active questions`);
  }

  /**
   * Reset to initial state with original IDs
   */
  reset(): void {
    this.state = {
      originalIds: [...this.state.originalIds],
      activeIds: [...this.state.originalIds],
      filteredIds: [],
      isShuffled: false,
      isFiltered: false,
      activeFilters: [],
      questionsPerPage: this.state.questionsPerPage
    };

    console.log(`🔄 Reset to original state: ${this.state.originalIds.length} questions`);
  }

  /**
   * Extract all individual problem IDs from question ID entries (for validation)
   */
  private extractAllProblemIds(questionIdEntries: QuestionIdEntry[]): number[] {
    const problemIds: number[] = [];

    questionIdEntries.forEach(item => {
      if ('problemid' in item) {
        // Individual problem
        problemIds.push(item.problemid);
      } else if ('problemsSetId' in item && item.problems) {
        // Problem set - add all child problem IDs
        item.problems.forEach(child => {
          problemIds.push(child.problemid);
        });
      }
    });

    return problemIds;
  }

  /**
   * Private helper: Fisher-Yates shuffle algorithm
   */
  private fisherYatesShuffle<T>(array: T[]): T[] {
    const shuffled = [...array];
    for (let i = shuffled.length - 1; i > 0; i--) {
      const j = Math.floor(Math.random() * (i + 1));
      [shuffled[i], shuffled[j]] = [shuffled[j], shuffled[i]];
    }
    return shuffled;
  }

  /**
   * Debug method to log current state
   */
  debugPrint(): void {
    const stats = this.getStats();
    console.log('\n📊 QuestionIdManager State:');
    console.log(`   Original Questions: ${stats.totalOriginal}`);
    console.log(`   Active Questions: ${stats.totalActive}`);
    console.log(`   Total Pages: ${stats.totalPages}`);
    console.log(`   Questions Per Page: ${stats.questionsPerPage}`);
    console.log(`   Is Shuffled: ${stats.isShuffled}`);
    console.log(`   Is Filtered: ${stats.isFiltered}`);
    if (stats.isFiltered) {
      console.log(`   Active Filters: [${stats.activeFilters.join(', ')}]`);
      console.log(`   Filtered Questions: ${stats.totalFiltered}`);
    }
    console.log('');
  }

  /**
   * Static utility: Extract string IDs from QuestionIdEntry array (for API compatibility)
   */
  static extractStringIdsFromQuestionIdEntries(questionIdEntries: QuestionIdEntry[]): string[] {
    const stringIds: string[] = [];

    questionIdEntries.forEach(item => {
      if ('problemid' in item) {
        // Individual problem
        stringIds.push(String(item.problemid));
      } else if ('problemsSetId' in item && item.problems) {
        // Problem set - add all child problem IDs
        item.problems.forEach(child => {
          stringIds.push(String(child.problemid));
        });
      }
    });

    return stringIds;
  }
}