"use client";

import React from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";

import { ButtonP, ButtonS } from "@/shared/components/ui/button";
import Navbar from "@/shared/components/layouts/navbar";
import Footer from "@/shared/components/layouts/footer";
import { Pfont, Sfont } from "@/shared/lib/configs/fonts";
import { Vflow } from "@/shared/components/layouts/flows";
import { useAttemptsStore } from "@/shared/stores/problems/attempts";
import { BarChart3, Target, Clock, Layers, CheckCircle2, ArrowRight, Bot, Users, Trophy, Sparkles } from "lucide-react";
import { Card, CardContent } from "@/shared/components/ui/card";
import dynamic from "next/dynamic";

const DiagnosticSprint = dynamic(
   () => import("@/shared/components/marketing/DiagnosticSprint").then(mod => ({ default: mod.DiagnosticSprint })),
   {
      ssr: false,
      loading: () => (
         <Card className="w-full max-w-2xl mx-auto border-primary/20 bg-background/50 backdrop-blur-xl shadow-2xl">
            <CardContent className="p-8 text-center py-16">
               <div className="inline-flex p-3 rounded-full bg-primary/10 mb-6">
                  <div className="w-8 h-8 rounded-full bg-primary/20 animate-pulse" />
               </div>
               <div className="h-7 w-56 bg-muted rounded mx-auto mb-4 animate-pulse" />
               <div className="h-4 w-80 bg-muted rounded mx-auto mb-8 animate-pulse" />
               <div className="h-12 w-full bg-primary/20 rounded-lg animate-pulse" />
            </CardContent>
         </Card>
      ),
   }
);

const content = {
   left: {
      heading: "Platform",
      children: {
         "Methodology": "#methodology",
         "Exams": "#exams",
         "Login": "/login",
         "Sign Up": "/signup",
      },
   },
   right: {
      heading: "Connect",
      children: {
         "Instagram": "https://instagram.com/compex_live",
         "Feedback": "/feedback",
      },
   },
};

const FeatureItem = ({ icon: Icon, title, description }: { icon: any, title: string, description: string }) => (
   <Card className="h-full border-border/50 bg-background/50 hover:bg-muted/50 transition-all duration-300 hover:shadow-lg hover:border-primary/20 group">
      <CardContent className="p-6 flex flex-col items-start gap-4">
         <div className="p-3 rounded-xl bg-primary/10 text-primary group-hover:scale-110 transition-transform duration-300">
            <Icon className="w-6 h-6" />
         </div>
         <div className="space-y-2">
            <h3 className="font-bold text-xl">{title}</h3>
            <p className="text-muted-foreground text-sm leading-relaxed">{description}</p>
         </div>
      </CardContent>
   </Card>
);

const Home: React.FC = () => {
   const footerItems = Object.entries(content).map(
      ([direction, obj], index) => {
         return (
            <Vflow gap={4} key={index}>
               <h4 className="text-lg font-bold mb-4">{obj.heading}</h4>
               <ul className="space-y-2">
                  {Object.entries(obj.children).map(([name, href], index) => {
                     return (
                        <li key={index}>
                           <a href={href as string} className="hover:text-primary transition-colors">
                              {name}
                           </a>
                        </li>
                     );
                  })}
               </ul>
            </Vflow>
         );
      }
   );

   const { userId } = useAttemptsStore();
   const router = useRouter();


   return (
      <div className="flex flex-col min-h-screen font-sans selection:bg-primary/20">
         <Navbar />
         <main className="flex-1">
            {/* Hero Section: Direct & SEO Optimized */}
            <section className="relative py-20 md:py-32 overflow-hidden">
               {/* Background Gradients */}
               <div className="absolute top-0 left-1/2 -translate-x-1/2 w-full h-full max-w-7xl z-[-1] opacity-40 dark:opacity-20 pointer-events-none">
                  <div className="absolute top-10 left-1/4 w-72 h-72 bg-primary/30 rounded-full blur-[128px]" />
                  <div className="absolute bottom-10 right-1/4 w-96 h-96 bg-purple-500/20 rounded-full blur-[128px]" />
               </div>

               <div className="container px-6 mx-auto max-w-4xl text-center relative z-10">
                  <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-primary/10 text-primary text-sm font-medium mb-8 animate-in fade-in slide-in-from-bottom-4 duration-700">
                     <Sparkles className="w-4 h-4" />
                     <span>The Future of Exam Prep is Here</span>
                  </div>
                  <h1 className="text-4xl md:text-6xl lg:text-7xl font-extrabold tracking-tight mb-8 text-foreground leading-tight">
                     The <span className="text-transparent bg-clip-text bg-gradient-to-r from-primary to-purple-600">Data-Driven</span> Way<br className="hidden md:block" /> to Master GRE & GMAT.
                  </h1>
                  <p className="text-lg md:text-xl text-muted-foreground mb-10 leading-relaxed max-w-2xl mx-auto">
                     Stop guessing where you need to improve. Compex provides a targeted practice environment with precise analytics to isolate weaknesses, optimize speed, and guarantee score improvement.
                  </p>
                  <div className="flex flex-col sm:flex-row items-center gap-4 justify-center">
                     <Link href={userId !== 0 ? "/dashboard/explore" : "/signup?force=true"} passHref>
                        <ButtonP className="h-14 px-8 text-lg shadow-xl shadow-primary/20 hover:shadow-2xl hover:shadow-primary/30 transition-all duration-300">
                           Start Practicing Free
                        </ButtonP>
                     </Link>
                     <Link href="/learn">
                        <ButtonS className="h-14 px-8 text-lg border-primary/20 hover:bg-primary/5 backdrop-blur-sm">
                           View Methodology
                        </ButtonS>
                     </Link>
                  </div>

                  {/* Product Hunt Badge Integration */}
                  <div className="mt-12 flex justify-center animate-in fade-in slide-in-from-bottom-8 duration-1000 delay-500">
                     <a href="https://www.producthunt.com/products/compex?embed=true&utm_source=badge-featured&utm_medium=badge&utm_campaign=badge-compex" target="_blank" rel="noopener noreferrer">
                        <img
                           src="https://api.producthunt.com/widgets/embed-image/v1/featured.svg?post_id=1070685&theme=light&t=1770272581532"
                           alt="CompEx - The data-driven way to master GRE & GMAT | Product Hunt"
                           style={{ width: '250px', height: '54px' }}
                           width="250"
                           height="54"
                           className="hover:scale-105 transition-transform duration-300 shadow-lg rounded-lg"
                        />
                     </a>
                  </div>

                  <div className="mt-20">
                     <DiagnosticSprint />
                  </div>
               </div>
            </section>

            {/* Methodology: The "How" */}
            <section id="methodology" className="py-24 bg-muted/30">
               <div className="container px-6 mx-auto">
                  <div className="text-center max-w-4xl mx-auto mb-20">
                     <h2 className="text-3xl md:text-5xl font-bold mb-6 tracking-tight">Built Like a Modern Tech Stack.<br />For Your Brain.</h2>
                     <p className="text-muted-foreground text-lg leading-relaxed max-w-2xl mx-auto">
                        We took the &quot;LeetCode approach&quot; to exam prep: Daily challenges, streak tracking, and a relentless focus on problem-solving.
                     </p>
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 max-w-7xl mx-auto">
                     {/* Row 1: The Core */}
                     <FeatureItem
                        icon={Bot}
                        title="Deepseek-Powered AI Engine"
                        description="Our questions aren't static. We use the Deepseek-Reasoning model with multi-stage system instructions to generate fresh, complex problems daily."
                     />
                     <FeatureItem
                        icon={Trophy}
                        title="Gamified Progression"
                        description="Inspired by platforms like LeetCode, we turn study into a game. Earn XP, maintain daily streaks, and unlock badges. Makes practice addictive."
                     />
                     <FeatureItem
                        icon={Users}
                        title="Global Peer Benchmarking"
                        description="Don't just track your score; track your standing. Compare your speed and accuracy against the global cohort to see exactly where you rank."
                     />

                     {/* Row 2: The Analytics */}
                     <FeatureItem
                        icon={Layers}
                        title="Granular Tagging System"
                        description="Questions are tagged by Exam, Section, Topic, and Sub-topic. You don't just study 'Math'; you practice ' Quadratic Equations with Inequalities'."
                     />
                     <FeatureItem
                        icon={BarChart3}
                        title="Real-Time Analytics"
                        description="Our dashboard updates instantly. Track your accuracy trend, difficulty distribution, and skill breakdown to know exactly where you stand."
                     />
                     <FeatureItem
                        icon={Target}
                        title="Efficiency vs. Mastery"
                        description="Understand your trade-off between speed and accuracy. Identify topics where you are 'Fast but Careless' or 'Accurate but Slow'."
                     />

                     {/* Row 3: The Experience */}
                     <FeatureItem
                        icon={Clock}
                        title="Time Management Analysis"
                        description="Visualize time spent on correct vs. incorrect answers. Eliminate 'Sunk Cost' time sinkholes during your exam with precision."
                     />
                     <FeatureItem
                        icon={CheckCircle2}
                        title="Activity Heatmaps"
                        description="Consistency is key. Our GitHub-style activity heatmap visualizes your daily study habits, holding you accountable to your schedule."
                     />
                     <FeatureItem
                        icon={Sparkles}
                        title="Daily Fresh Content"
                        description="Never run out of practice material. Our AI pipeline injects new problem sets every 24 hours, keeping your preparation challenging."
                     />
                  </div>
               </div>
            </section>

            {/* Supported Exams */}
            <section id="exams" className="py-20 border-t border-border">
               <div className="container px-6 mx-auto">
                  <div className="flex flex-col md:flex-row justify-between items-end mb-12 gap-6">
                     <div>
                        <h2 className="text-3xl font-bold mb-2">Supported Exams</h2>
                        <p className="text-muted-foreground">Current question banks available for practice.</p>
                     </div>
                     <Link href="/dashboard/mock">
                        <ButtonS>View All Problem Sets</ButtonS>
                     </Link>
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                     <Card className="hover:border-primary/50 hover:shadow-xl hover:shadow-primary/5 transition-all duration-300 cursor-pointer group bg-background/50 backdrop-blur-sm">
                        <CardContent className="p-8 flex flex-col gap-5">
                           <div className="flex justify-between items-start">
                              <Sfont style={1} className="text-4xl font-bold group-hover:text-primary transition-colors duration-300">GRE</Sfont>
                              <span className="bg-primary/10 text-primary text-xs font-bold px-3 py-1.5 rounded-full uppercase tracking-wider">Live</span>
                           </div>
                           <h3 className="text-xl font-bold">Graduate Record Examination</h3>
                           <p className="text-muted-foreground text-sm leading-relaxed">
                              Full coverage of Quantitative Reasoning and Verbal Reasoning sections. Includes Data Interpretation and Reading Comprehension specific blocks.
                           </p>
                           <ul className="grid grid-cols-2 gap-3 text-sm text-muted-foreground mt-4">
                              <li className="flex items-center gap-2 group-hover:text-primary transition-colors"><CheckCircle2 className="w-4 h-4 text-primary" /> 1,500+ Questions</li>
                              <li className="flex items-center gap-2 group-hover:text-primary transition-colors"><CheckCircle2 className="w-4 h-4 text-primary" /> Adaptive Mocks</li>
                           </ul>
                        </CardContent>
                     </Card>

                     <Card className="hover:border-primary/50 hover:shadow-xl hover:shadow-primary/5 transition-all duration-300 cursor-pointer group bg-background/50 backdrop-blur-sm">
                        <CardContent className="p-8 flex flex-col gap-5">
                           <div className="flex justify-between items-start">
                              <Sfont style={1} className="text-4xl font-bold group-hover:text-primary transition-colors duration-300">GMAT</Sfont>
                              <span className="bg-primary/10 text-primary text-xs font-bold px-3 py-1.5 rounded-full uppercase tracking-wider">Live</span>
                           </div>
                           <h3 className="text-xl font-bold">Focus Edition Included</h3>
                           <p className="text-muted-foreground text-sm leading-relaxed">
                              Dedicated practice for Data Insights, Quantitative, and Verbal Reasoning. Master the adaptive algorithm logic.
                           </p>
                           <ul className="grid grid-cols-2 gap-3 text-sm text-muted-foreground mt-4">
                              <li className="flex items-center gap-2 group-hover:text-primary transition-colors"><CheckCircle2 className="w-4 h-4 text-primary" /> Data Insights Ready</li>
                              <li className="flex items-center gap-2 group-hover:text-primary transition-colors"><CheckCircle2 className="w-4 h-4 text-primary" /> 800-Level Problems</li>
                           </ul>
                        </CardContent>
                     </Card>
                  </div>
               </div>
            </section>

            {/* Final CTA */}
            <section className="py-24 relative overflow-hidden">
               <div className="absolute inset-0 bg-primary/90 z-0">
                  <div className="absolute inset-0 bg-[radial-gradient(circle_at_center,_var(--tw-gradient-stops))] from-white/10 to-transparent opacity-50"></div>
               </div>
               <div className="container px-6 mx-auto text-center max-w-4xl relative z-10 text-primary-foreground">
                  <h2 className="text-3xl md:text-5xl font-bold mb-6 tracking-tight">Start Your Improvement Arc Today.</h2>
                  <p className="text-xl mb-10 opacity-90 max-w-2xl mx-auto leading-relaxed">
                     Join a community of high-performers. No credit card required, just instant access to better practice.
                  </p>
                  <Link href="/signup?force=true" passHref>
                     <ButtonS className="h-16 px-12 text-lg bg-background text-foreground hover:bg-background/90 hover:scale-105 transition-all duration-300 border-transparent shadow-2xl">
                        Create Free Account
                     </ButtonS>
                  </Link>
               </div>
            </section>
         </main>
         <Footer
            className="bg-muted text-muted-foreground py-12"
            centerItems={footerItems}
         />
      </div>
   );
};

export default Home;
