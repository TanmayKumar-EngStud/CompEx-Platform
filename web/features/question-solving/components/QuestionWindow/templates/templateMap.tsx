import { TAQuestion } from "./TA";
import { GIQuestion } from "./GI";
import DSTemplate from "./DS";
import RCTemplate from "./RC";
import CRTemplate from "./CR";
import DichotomousTemplate from "./Dichotomous";


import { FC } from "react";

type TemplateProps = {
   text: string;
   metadata?: any;
   options?: Record<string, { optiontext: string }>;
   selectedOption?: string[];
   correctOption?: string[];
   handleOptionClick?: (option: string | string[]) => void;
   handleClear?: () => void;
   isLongOptions?: boolean;
   questionDisplayfn: (text: string) => React.JSX.Element[];
   isAttempting?: boolean;
   [key: string]: any;
};

const templateMap = {
   DS: DSTemplate,
   GI: GIQuestion,
   TA: TAQuestion,
   RC: RCTemplate,
   CR: CRTemplate,
   default: ({ text, questionDisplayfn }: TemplateProps) => (
      <div className="text-base">{questionDisplayfn(text)}</div>
   ),
} as const;

type TemplateKey = keyof typeof templateMap;
export type TemplateComponent = FC<TemplateProps>;

export const getTemplateComponent = (type: string): FC<TemplateProps> => {
   const templateType = type as TemplateKey;
   return (templateMap[templateType] ||
      templateMap.default) as FC<TemplateProps>;
};

export default templateMap;
