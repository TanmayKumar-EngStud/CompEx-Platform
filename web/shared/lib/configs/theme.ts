// Theme utility functions

// Function to get the current theme
export function getTheme(): 'light' | 'dark' | 'system' {
  if (typeof window === 'undefined') return 'system';
  
  const storedTheme = localStorage.getItem('compex-theme-preference');
  if (storedTheme) {
    return storedTheme as 'light' | 'dark' | 'system';
  }
  
  return 'system';
}

// Function to determine if the current theme is dark
export function isDarkTheme(): boolean {
  if (typeof window === 'undefined') return false;
  
  const theme = getTheme();
  if (theme === 'dark') return true;
  if (theme === 'light') return false;
  
  // If system, check media query
  return window.matchMedia('(prefers-color-scheme: dark)').matches;
}

// Function to get appropriate color for charts based on theme
export function getChartColors(isDark: boolean) {
  return {
    primary: isDark ? 'hsl(217.2, 91.2%, 59.8%)' : 'hsl(221.2, 83.2%, 53.3%)',
    secondary: isDark ? 'hsl(142.1, 70.6%, 45.3%)' : 'hsl(142.1, 76.2%, 36.3%)',
    tertiary: isDark ? 'hsl(47.9, 95.8%, 53.1%)' : 'hsl(47.9, 95.8%, 53.1%)',
    quaternary: isDark ? 'hsl(346.8, 77.2%, 49.8%)' : 'hsl(346.8, 77.2%, 49.8%)',
    quinary: isDark ? 'hsl(262.1, 83.3%, 67.8%)' : 'hsl(262.1, 83.3%, 57.8%)',
  };
}