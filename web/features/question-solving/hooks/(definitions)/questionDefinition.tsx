export interface Option {
   optionid: number;
   optiontext: string;
}

export interface Metadata {
   diagram: string | undefined;
   hints: string[];
   tags: string[];
}

export interface QuestionData {
   problemid: number;
   text: string;
   title: string;
   problemoptions: Option;
   metadata: Metadata;
}

export interface QuestionFloatingWindowProps {
   onClose: () => void;
   onFinish: (localAttempts?: Map<number, string[]>) => void;
   showTimer?: boolean;
   hideLabels?: boolean;
}

export interface ResultWindowProps {
   onClose: () => void;
   localAttempts?: Map<number, string[]>;
   hideLabels?: boolean;
   isFullPage?: boolean;
   closeButtonText?: string;
}

export interface PaginationProps {
   questionIds: (number | { [key: string]: number[] })[];
   currentQuestionId: number;
   size: number;
   onPageChange: (id: number) => void;
}
