"use client";
import React, { useEffect, useState } from "react";
import { SunIcon, MoonIcon } from "@/shared/components/ui/icons/sun-moon";
import { useTheme } from "next-themes";

const ThemeToggle: React.FC = () => {
   const { resolvedTheme, setTheme } = useTheme();
   const [mounted, setMounted] = useState(false);

   // Only mount component after hydration to prevent hydration mismatch
   useEffect(() => {
      setMounted(true);
   }, []);

   // Don't render anything until component is mounted
   if (!mounted) {
      // Return a placeholder with the same dimensions to prevent layout shift
      return <div className="w-10 h-10 rounded-full bg-transparent"></div>;
   }

   return (
      <button
         onClick={() => setTheme(resolvedTheme === "dark" ? "light" : "dark")}
         className="w-10 h-10 rounded-full bg-primary/20 dark:bg-primary/30 flex items-center justify-center text-primary"
         aria-label="Toggle theme"
         type="button"
      >
         {resolvedTheme === "dark" ? <SunIcon /> : <MoonIcon />}
      </button>
   );
};

export default ThemeToggle;
