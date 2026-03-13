import { create } from "zustand";

export interface questionResult {
   type: string;
   problemid: number;
   correctoption: string[];
   title: string;
   selectedoption: string[];
   timetaken: string;

   //to display that question,
   text: string;
   diagram: string | null;
   // charttype: string;
   // chartdata: string; //later I will add this feature.
   options: { optiontext: string; group: string }[];
   solution: string;
   options_type: string | null;
   difficulty: number;
   metadata: any;
   problemtags?: any[];
   parentTags?: string[];
   // partialcorrectnessscore: number;
}

interface resultdatadefinition {
   resultData: null | questionResult[];
   setResultData: (data: questionResult[]) => void;
}

export const useResultData = create<resultdatadefinition>((set) => ({
   resultData: null,
   setResultData: (data: questionResult[]) => set({ resultData: data }),
}));
