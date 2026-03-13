"use client";
import React from "react";

import {
   Select,
   SelectContent,
   SelectItem,
   SelectTrigger,
   SelectValue,
} from "@/shared/components/ui/select";

interface MinimalDropdownProps {
   items: string[];
   getStoreName: () => string;
   setStoreName: (name: string) => void;
   defaultVal?: string; // Made defaultVal optional as SelectValue can handle null/undefined
}

const MinimalDropdown: React.FC<MinimalDropdownProps> = ({
   items,
   getStoreName,
   setStoreName,
   defaultVal = "select an option",
}) => {
   const selectedValue = getStoreName();

   const handleValueChange = (value: string) => {
      setStoreName(value);
   };

   return (
      <Select onValueChange={handleValueChange} value={selectedValue || ""}>
         <SelectTrigger className="w-[180px] focus:outline-none focus-visible:ring-0 focus-visible:ring-offset-0">
            <SelectValue placeholder={defaultVal} />
         </SelectTrigger>
         <SelectContent>
            {items.map((item) => (
               <SelectItem key={item} value={item}>
                  {item}
               </SelectItem>
            ))}
         </SelectContent>
      </Select>
   );
};

export default MinimalDropdown;
