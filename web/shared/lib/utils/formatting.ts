export function classNames(...classes: string[]) {
   return classes.filter(Boolean).join(" ");
}

export function truncateBrackets(text: string | null | undefined): string {
   if (!text) return "";
   return text.replace(/\s*\([^)]*\)/g, "").trim();
}

/**
 * Parses time strings into numeric seconds
 * Handles formats: "11 min 37 sec", "35 sec", "MM:SS", "SS"
 */
export const parseTimeToSeconds = (timeStr: string | null | undefined): number => {
   if (!timeStr || typeof timeStr !== "string") return 0;

   // Handle "11 min 37 sec" or "35 sec" format
   if (timeStr.includes("min") || timeStr.includes("sec")) {
      let totalSeconds = 0;
      const minMatch = timeStr.match(/(\d+)\s*min/);
      const secMatch = timeStr.match(/(\d+)\s*sec/);

      if (minMatch) totalSeconds += parseInt(minMatch[1]) * 60;
      if (secMatch) totalSeconds += parseInt(secMatch[1]);

      return totalSeconds;
   }

   // Fallback to original MM:SS format or plain number
   try {
      const parts = timeStr.split(":").map(Number);
      if (parts.length === 2) {
         return (
            (isNaN(parts[0]) ? 0 : parts[0] * 60) +
            (isNaN(parts[1]) ? 0 : parts[1])
         );
      } else if (parts.length === 1) {
         return isNaN(parts[0]) ? 0 : parts[0];
      }
      return 0;
   } catch {
      return 0;
   }
};