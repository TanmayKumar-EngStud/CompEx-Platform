import { createPreset } from "fumadocs-ui/tailwind-plugin";
import type { Config } from "tailwindcss";

const config: Config = {
   darkMode: ["class"],
   presets: [
      createPreset({
         cssPrefix: "fd-",
      }),
   ],
   content: [
      "./pages/**/*.{js,ts,jsx,tsx,mdx}",
      "./components/**/*.{js,ts,jsx,tsx,mdx}",
      "./app/**/*.{js,ts,jsx,tsx,mdx}",
      "./features/**/*.{js,ts,jsx,tsx,mdx}",
      "./shared/**/*.{js,ts,jsx,tsx,mdx}",
      "./content/**/*.{md,mdx}",
      "./mdx-components.tsx",
      "./node_modules/fumadocs-ui/dist/**/*.js",
   ],
   theme: {
      container: {
         center: true,
         padding: "2rem",
         screens: {
            "2xl": "1400px",
         },
      },
      extend: {
         colors: {
            border: "hsl(var(--border))",
            input: "hsl(var(--input))",
            ring: "hsl(var(--ring))",
            background: "hsl(var(--background))",
            foreground: "hsl(var(--foreground))",
            primary: {
               DEFAULT: "hsl(var(--primary))",
               foreground: "hsl(var(--primary-foreground))",
            },
            secondary: {
               DEFAULT: "hsl(var(--secondary))",
               foreground: "hsl(var(--secondary-foreground))",
            },
            destructive: {
               DEFAULT: "hsl(var(--destructive))",
               foreground: "hsl(var(--destructive-foreground))",
            },
            muted: {
               DEFAULT: "hsl(var(--muted))",
               foreground: "hsl(var(--muted-foreground))",
            },
            accent: {
               DEFAULT: "hsl(var(--accent))",
               foreground: "hsl(var(--accent-foreground))",
            },
            popover: {
               DEFAULT: "hsl(var(--popover))",
               foreground: "hsl(var(--popover-foreground))",
            },
            card: {
               DEFAULT: "hsl(var(--card))",
               foreground: "hsl(var(--card-foreground))",
            },
            chart: {
               "1": "hsl(var(--chart-1))",
               "2": "hsl(var(--chart-2))",
               "3": "hsl(var(--chart-3))",
               "4": "hsl(var(--chart-4))",
               "5": "hsl(var(--chart-5))",
            },
         },
         borderRadius: {
            lg: "var(--radius)",
            md: "calc(var(--radius) - 2px)",
            sm: "calc(var(--radius) - 4px)",
         },
         fontFamily: {
            serif: ["var(--font-serif)", "serif"],
            primary1: "var(--font-primary-1)",
            primary2: "var(--font-primary-2)",
            primary3: "var(--font-primary-3)",
            secondary1: "var(--font-secondary-1)",
            secondary2: "var(--font-secondary-2)",
            secondary3: "var(--font-secondary-3)",
            body1: "var(--font-body-1)",
            body2: "var(--font-body-2)",
            body3: "var(--font-body-3)",
            accent1: "var(--font-accent-1)",
            accent2: "var(--font-accent-2)",
            accent3: "var(--font-accent-3)",
         },
         backgroundImage: {
            "gradient-radial": "radial-gradient(var(--tw-gradient-stops))",
            "gradient-conic":
               "conic-gradient(from 180deg at 50% 50%, var(--tw-gradient-stops))",
         },
      },
   },
   plugins: [require("tailwindcss-animate")],
};

export default config;
