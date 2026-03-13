import type { Metadata } from "next";
import { Inter, Lora } from "next/font/google";
import { Analytics } from '@vercel/analytics/react';
import { SpeedInsights } from '@vercel/speed-insights/next';
import ReactQueryProvider from "@/shared/components/providers/react-query-provider";
import { WebVitalsTracker } from "@/shared/components/performance/WebVitalsTracker";
import { PerformanceMonitor, PerformanceBudgetChecker } from "@/shared/components/performance/PerformanceMonitor";
import { CacheValidator } from "@/shared/components/dev/cache-validator";
import { FeedbackButton } from "@/shared/components/feedback/FeedbackButton";
import "./globals.css"; // Global styles
import Providers from "./providers";
const inter = Inter({ subsets: ["latin"], variable: "--font-inter" });
const lora = Lora({ subsets: ["latin"], variable: "--font-serif" });
export const metadata: Metadata = {
   title: "CompEx",
   description: "Platform to prepare for prepare for competitive exams",
   icons: {
      icon: [
         { url: "/favicon.ico" },
         { url: "/icon-v2.png", type: "image/png" },
      ],
      apple: "/icon-v2.png",
   },
};

export default function RootLayout({
   children,
}: Readonly<{
   children: React.ReactNode;
}>) {
   return (
      <html lang="en" suppressHydrationWarning>
         <head>
         </head>
         <body className={`${inter.variable} ${lora.variable} ${inter.className} overflow-x-auto`}>
            <ReactQueryProvider>
               <Providers>
                  <WebVitalsTracker
                     enableAnalytics={process.env.NODE_ENV === 'production'}
                     enableConsoleLog={process.env.NODE_ENV === 'development'}
                     endpoint="/api/metrics"
                     sampleRate={0.1}
                  />
                  {children}
                  <FeedbackButton />
                  {/* Heavy dev monitoring components - disabled to hit sub-2s startup target */}
                  {/* {process.env.NODE_ENV === 'development' && (
                     <>
                        <PerformanceMonitor />
                        <PerformanceBudgetChecker />
                        <CacheValidator 
                           interval={30000}
                           autoReload={false}
                           devOnly={true}
                        />
                     </>
                  )} */}
               </Providers>
            </ReactQueryProvider>
            <Analytics />
            <SpeedInsights />
         </body>
      </html>
   );
}
