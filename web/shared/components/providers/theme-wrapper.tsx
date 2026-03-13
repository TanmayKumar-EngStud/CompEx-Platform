"use client";

import { useEffect, useState } from "react";
import { useTheme } from "next-themes";

export function ThemeWrapper({ children }: { children: React.ReactNode }) {
   const [mounted, setMounted] = useState(false);
   const { resolvedTheme } = useTheme();

   useEffect(() => {
      setMounted(true);
   }, []);

   // During SSR and before mounting, don't apply any theme-specific classes
   if (!mounted) {
      return <>{children}</>;
   }

   // After mounting, the theme is resolved and we can safely apply theme classes
   return <>{children}</>;
}