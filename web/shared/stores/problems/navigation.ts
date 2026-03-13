import { create } from "zustand";

/**
 * Navigation state for question window and question browsing
 * 
 * Handles:
 * - Question IDs management
 * - Window navigation state
 * - Question data list for question window
 */

export interface QuestionState {
  type: string;
  problemid: number;
  title: string;
  text: string;
  options_type: string | null;
  problemoptions: { optionid: number; optiontext: string; group?: string }[];
  metadata: any;
}

type QuestionIds = number | { [key: string]: number[] };

export interface NavigationState {
  questionIds: QuestionIds[];
  questionDataList: QuestionState[];
  windowSize: number;
  start: number;
  currentQuestionDetails: QuestionState;
}

export interface NavigationActions {
  setQuestionIds: (ids: QuestionIds[]) => void;
  setStart: (id: number) => void;
  pasteQuestionDataList: (questionData: QuestionState[]) => void;
  setQuestionDataList: (questionData: QuestionState) => void;
  setCurrentQuestionDetails: (question: QuestionState) => void;
  resetNavigation: () => void;
}

export type NavigationStore = NavigationState & NavigationActions;

/**
 * Helper function to add question data with window size limit
 */
function addQuestionData(
  questionDataList: QuestionState[],
  size: number,
  questionData: QuestionState
): { updatedList: QuestionState[]; incrementStart: boolean } {
  let incrementStart = false;
  if (questionDataList.length < size) {
    questionDataList.push(questionData);
  } else {
    questionDataList.shift(); // Remove the first element
    questionDataList.push(questionData); // Add the new element at the end
    incrementStart = true;
  }
  return { updatedList: questionDataList, incrementStart };
}

/**
 * Default question state
 */
const defaultQuestionState: QuestionState = {
  type: "",
  problemid: 0,
  title: "questionTitle",
  text: "question",
  options_type: null,
  problemoptions: [{ optionid: 0, optiontext: "" }],
  metadata: {},
};

/**
 * Zustand store for question navigation
 * 
 * @example
 * ```ts
 * const { questionIds, setQuestionIds, start, setStart } = useNavigationStore();
 * ```
 */
export const useNavigationStore = create<NavigationStore>((set, get) => ({
  // State
  questionIds: [],
  questionDataList: [],
  windowSize: 5,
  start: -1,
  currentQuestionDetails: defaultQuestionState,

  // Actions
  setQuestionIds: (ids) => set({ questionIds: ids }),
  setStart: (id) => set({ start: id }),

  /**
   * Replace entire question data list (used when fetching multiple questions)
   */
  pasteQuestionDataList: (questionData) => {
    const currentList = get().questionDataList;
    if (JSON.stringify(currentList) !== JSON.stringify(questionData)) {
      set({ questionDataList: questionData });
    }
  },

  /**
   * Add single question to data list with window size management
   */
  setQuestionDataList: (questionData) => {
    const { updatedList } = addQuestionData(
      [...get().questionDataList],
      get().windowSize,
      questionData
    );
    set({ questionDataList: updatedList });
  },

  setCurrentQuestionDetails: (question) => set({ currentQuestionDetails: question }),

  resetNavigation: () => set({
    questionIds: [],
    questionDataList: [],
    start: -1,
    currentQuestionDetails: defaultQuestionState,
  }),
}));