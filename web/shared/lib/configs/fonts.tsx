// components/FontComponents.tsx

import { Pfonts, Sfonts, Bfonts, Afonts } from "@/shared/lib/configs/fontDefinitions";
import React from "react";
import clsx from "clsx";

interface FontProps {
   children: React.ReactNode;
   style: number;
   className?: string;
}

const getFontClass = (fonts: any[], style: number): string => {
   if (style < 1 || style > fonts.length) {
      throw new Error(
         `Invalid style number. Please use a value between 1 and ${fonts.length}.`
      );
   }
   return fonts[style - 1].variable;
};

export const Pfont: React.FC<FontProps> = ({ children, style, className }) => {
   return (
      <span className={clsx(getFontClass(Pfonts, style), className)}>
         {children}
      </span>
   );
};

export const Sfont: React.FC<FontProps> = ({ children, style, className }) => {
   return (
      <span className={clsx(getFontClass(Sfonts, style), className)}>
         {children}
      </span>
   );
};

export const Bfont: React.FC<FontProps> = ({ children, style, className }) => {
   return (
      <span className={clsx(getFontClass(Bfonts, style), className)}>
         {children}
      </span>
   );
};

export const Afont: React.FC<FontProps> = ({ children, style, className }) => {
   return (
      <span className={clsx(getFontClass(Afonts, style), className)}>
         {children}
      </span>
   );
};
