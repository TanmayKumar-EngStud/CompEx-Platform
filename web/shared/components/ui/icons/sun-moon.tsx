import React from "react";

export function SunIcon() {
   return (
      <svg
         className="w-4 h-4"
         fill="none"
         stroke="currentColor"
         viewBox="0 0 24 24"
         xmlns="http://www.w3.org/2000/svg"
      >
         <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={1}
            d="M12 3v2m0 14v2m9-9h-2M5 12H3m15.364-6.364l-1.414 1.414M6.343 17.657l-1.415 1.415m12.02 0l-1.414-1.414M6.343 6.343L4.929 4.929m7.071 14.142a7 7 0 110-14 7 7 0 010 14z"
         />
      </svg>
   );
}

export function MoonIcon() {
   return (
      <svg
         className="w-4 h-4"
         fill="none"
         stroke="currentColor"
         viewBox="0 0 24 24"
         xmlns="http://www.w3.org/2000/svg"
      >
         <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={1}
            d="M21 12.79A9 9 0 1111.21 3a7 7 0 109.79 9.79z"
         />
      </svg>
   );
}
