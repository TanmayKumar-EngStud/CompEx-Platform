import { create } from "zustand";

/**
 * Pagination and filtering state for problems
 * 
 * Handles:
 * - Page navigation and page size
 * - Tag filtering and search
 * - Exam type and section selection
 * - Sort order configuration
 */

export interface PaginationState {
  page: number;
  pageSize: number;
  totalProblems: number;
  selectedTopics: string[];
  selectedThemes: string[];
  selectedTypes: string[];
  searchedText: string;
  examName: string;
  sectionName: string;
  sectionIndex: number;
  categoryIndex: number;
  sortOrder: 1 | 0 | -1; // 1 = asc, 0 = no sorting, -1 = desc
}

export interface PaginationActions {
  setPage: (page: number) => void;
  setPageSize: (limit: number) => void;
  setTotalProblems: (total: number) => void;
  setSelectedTopics: (topics: string[]) => void;
  setSelectedThemes: (themes: string[]) => void;
  setSelectedTypes: (types: string[]) => void;
  setSearchedText: (text: string) => void;
  setExamName: (name: string) => void;
  setSectionName: (name: string) => void;
  setSectionIndex: (index: number) => void;
  setCategoryIndex: (index: number) => void;
  setSortOrder: (order: 1 | 0 | -1) => void;
  resetPagination: () => void;
}

export type PaginationStore = PaginationState & PaginationActions;

/**
 * Zustand store for pagination and filtering state
 * 
 * @example
 * ```ts
 * const { page, setPage, examName, setExamName } = usePaginationStore();
 * ```
 */
export const usePaginationStore = create<PaginationStore>((set) => ({
  // State
  page: 1,
  pageSize: 10,
  totalProblems: 0,
  selectedTopics: [],
  selectedThemes: [],
  selectedTypes: [],
  searchedText: "",
  examName: "GRE",
  sectionName: "quants",
  sectionIndex: 0,
  categoryIndex: 0,
  sortOrder: 0,

  // Actions
  setPage: (page) => set({ page }),
  setPageSize: (limit) => set({ pageSize: limit }),
  setTotalProblems: (total) => set({ totalProblems: total }),
  setSelectedTopics: (topics) => set({ selectedTopics: topics }),
  setSelectedThemes: (themes) => set({ selectedThemes: themes }),
  setSelectedTypes: (types) => set({ selectedTypes: types }),
  setSearchedText: (text) => set({ searchedText: text }),
  setExamName: (name) => set({
    examName: name,
    selectedTopics: [],
    selectedThemes: [],
    selectedTypes: [],
    page: 1
  }),
  setSectionName: (name) => set({
    sectionName: name,
    selectedTopics: [],
    selectedThemes: [],
    selectedTypes: [],
    page: 1
  }),
  setSectionIndex: (index) => set({
    sectionIndex: index,
    selectedTopics: [],
    selectedThemes: [],
    selectedTypes: [],
    page: 1
  }),
  setCategoryIndex: (index) => set({ categoryIndex: index }),
  setSortOrder: (order) => set({ sortOrder: order }),
  resetPagination: () => set({
    page: 1,
    selectedTopics: [],
    selectedThemes: [],
    selectedTypes: [],
    searchedText: "",
    sortOrder: 0
  }),
}));