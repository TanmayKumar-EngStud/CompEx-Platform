// components/Header.tsx

import clsx from "clsx";
import React from "react";

interface HeaderProps {
   leftItems?: React.ReactNode[];
   centerItems?: React.ReactNode[];
   rightItems?: React.ReactNode[];
   gap?: number;
   className?: string;
}

const Header: React.FC<HeaderProps> = ({
   leftItems = [],
   centerItems = [],
   rightItems = [],
   gap = 5,
   className = "",
}) => {
   return (
      <header
         className={clsx(
            "sticky top-0 z-50 w-full border-b bg-background/80 backdrop-blur-md supports-[backdrop-filter]:bg-background/60",
            className
         )}
      >
         <div className="w-full flex h-16 items-center px-6 sm:px-12">
            <div className="flex flex-1 items-center justify-start gap-6 sm:gap-8">
               {leftItems.map((item, index) => (
                  <div key={index}>{item}</div>
               ))}
            </div>
            <div className="flex items-center justify-center">
               {centerItems.map((item, index) => (
                  <div key={index}>{item}</div>
               ))}
            </div>
            <div className="flex flex-1 items-center justify-end gap-2 sm:gap-4">
               {rightItems.map((item, index) => (
                  <div key={index}>{item}</div>
               ))}
            </div>
         </div>
      </header>
   );
};

export default Header;
