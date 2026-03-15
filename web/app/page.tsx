"use client";

import React from "react";
import Link from "next/link";
import { ButtonP, ButtonS } from "@/shared/components/ui/button";
import Navbar from "@/shared/components/layouts/navbar";
import Footer from "@/shared/components/layouts/footer";
import { Sfont } from "@/shared/lib/configs/fonts";
import { Vflow } from "@/shared/components/layouts/flows";
import { useAttemptsStore } from "@/shared/stores/problems/attempts";
import { BarChart3, Target, Clock, Layers, CheckCircle2, Bot, Users, Trophy, RefreshCw } from "lucide-react";
import { Card, CardContent } from "@/shared/components/ui/card";
import dynamic from "next/dynamic";

const DiagnosticSprint = dynamic(
   () => import("@/shared/components/marketing/DiagnosticSprint").then(mod => ({ default: mod.DiagnosticSprint })),
   {
      ssr: false,
      loading: () => (
         <Card className="w-full max-w-2xl mx-auto border-border bg-card shadow-sm">
            <CardContent className="p-8 text-center py-16">
               <div className="inline-flex p-3 rounded-full bg-muted mb-6">
                  <div className="w-8 h-8 rounded-full bg-muted-foreground/20 animate-pulse" />
               </div>
               <div className="h-7 w-56 bg-muted rounded mx-auto mb-4 animate-pulse" />
               <div className="h-4 w-80 bg-muted rounded mx-auto mb-8 animate-pulse" />
               <div className="h-12 w-full bg-muted rounded-lg animate-pulse" />
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
   <div className="flex flex-col gap-4 p-6 border border-border rounded-xl bg-card hover:border-primary/30 transition-colors duration-200">
      <div className="p-2.5 rounded-lg bg-primary/10 text-primary w-fit">
         <Icon className="w-5 h-5" />
      </div>
      <div className="space-y-1.5">
         <h3 className="font-semibold text-base text-foreground">{title}</h3>
         <p className="text-muted-foreground text-sm leading-relaxed">{description}</p>
      </div>
   </div>
);

const Home: React.FC = () => {
   const footerItems = Object.entries(content).map(
      ([direction, obj], index) => {
         return (
            <Vflow gap={4} key={index}>
               <h4 className="text-sm font-semibold uppercase tracking-widest text-muted-foreground mb-4">{obj.heading}</h4>
               <ul className="space-y-3">
                  {Object.entries(obj.children).map(([name, href], index) => {
                     return (
                        <li key={index}>
                           <a href={href as string} className="text-sm text-muted-foreground hover:text-foreground transition-colors">
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

   return (
      <div className="flex flex-col min-h-screen font-sans selection:bg-primary/20">
         <Navbar />
         <main className="flex-1">
            {/* Hero Section */}
            <section className="py-24 md:py-36 border-b border-border">
               <div className="container px-6 mx-auto max-w-3xl text-center">
                  <p className="text-sm font-semibold uppercase tracking-widest text-primary mb-6">
                     GRE &amp; GMAT Practice Platform
                  </p>
                  <h1 className="font-serif text-4xl md:text-6xl lg:text-[4.5rem] font-bold tracking-tight mb-7 text-foreground leading-[1.1]">
                     The Data-Driven Way<br className="hidden md:block" /> to Master GRE &amp; GMAT.
                  </h1>
                  <p className="text-lg text-muted-foreground mb-10 leading-relaxed max-w-xl mx-auto">
                     Stop guessing where you need to improve. Compex pinpoints your exact weaknesses with granular analytics and unlimited AI-generated practice.
                  </p>
                  <div className="flex flex-col sm:flex-row items-center gap-3 justify-center">
                     <Link href={userId !== 0 ? "/dashboard/explore" : "/signup?force=true"} passHref>
                        <ButtonP className="h-12 px-8 text-base font-semibold">
                           Start Practicing Free
                        </ButtonP>
                     </Link>
                     <Link href="/learn">
                        <ButtonS className="h-12 px-8 text-base">
                           View Methodology
                        </ButtonS>
                     </Link>
                  </div>

                  {/* Product Hunt Badge */}
                  <div className="mt-10 flex justify-center opacity-80 hover:opacity-100 transition-opacity">
                     <a href="https://www.producthunt.com/products/compex?embed=true&utm_source=badge-featured&utm_medium=badge&utm_campaign=badge-compex" target="_blank" rel="noopener noreferrer">
                        <img
                           src="https://api.producthunt.com/widgets/embed-image/v1/featured.svg?post_id=1070685&theme=light&t=1770272581532"
                           alt="CompEx - The data-driven way to master GRE & GMAT | Product Hunt"
                           style={{ width: '200px', height: '43px' }}
                           width="200"
                           height="43"
                           className="rounded-md"
                        />
                     </a>
                  </div>

                  <div className="mt-20">
                     <DiagnosticSprint />
                  </div>
               </div>
            </section>

            {/* Methodology Section */}
            <section id="methodology" className="py-24">
               <div className="container px-6 mx-auto">
                  <div className="max-w-2xl mb-16">
                     <p className="text-sm font-semibold uppercase tracking-widest text-primary mb-4">How It Works</p>
                     <h2 className="font-serif text-3xl md:text-4xl font-bold mb-4 tracking-tight text-foreground">Built like a modern tech stack. For your brain.</h2>
                     <p className="text-muted-foreground text-base leading-relaxed">
                        The LeetCode approach to exam prep: daily challenges, streak tracking, and relentless focus on targeted problem-solving.
                     </p>
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 max-w-7xl mx-auto">
                     <FeatureItem
                        icon={Bot}
                        title="AI-Powered Question Engine"
                        description="We use the Deepseek-Reasoning model with multi-stage instructions to generate fresh, complex problems daily — never running dry."
                     />
                     <FeatureItem
                        icon={Trophy}
                        title="Gamified Progression"
                        description="Earn XP, maintain daily streaks, and unlock badges. Turns preparation into a habit you actually want to keep."
                     />
                     <FeatureItem
                        icon={Users}
                        title="Global Peer Benchmarking"
                        description="Compare your speed and accuracy against the global cohort. Know not just your score, but your standing."
                     />
                     <FeatureItem
                        icon={Layers}
                        title="Granular Tagging System"
                        description="Questions tagged by Exam, Section, Topic, and Sub-topic. You don't study 'Math' — you practice 'Quadratic Equations with Inequalities'."
                     />
                     <FeatureItem
                        icon={BarChart3}
                        title="Real-Time Analytics"
                        description="Track accuracy trends, difficulty distribution, and skill breakdowns the moment you submit an answer."
                     />
                     <FeatureItem
                        icon={Target}
                        title="Efficiency vs. Mastery"
                        description="Understand your speed-accuracy tradeoff. Find where you're 'Fast but Careless' or 'Accurate but Slow'."
                     />
                     <FeatureItem
                        icon={Clock}
                        title="Time Management Analysis"
                        description="Visualize time spent on correct vs. incorrect answers. Eliminate sunk-cost time sinks before exam day."
                     />
                     <FeatureItem
                        icon={CheckCircle2}
                        title="Activity Heatmaps"
                        description="A GitHub-style heatmap holds you accountable to your study schedule. Consistency compounds."
                     />
                     <FeatureItem
                        icon={RefreshCw}
                        title="Daily Fresh Content"
                        description="New problem sets injected every 24 hours. Your preparation never hits a ceiling."
                     />
                  </div>
               </div>
            </section>

            {/* Supported Exams */}
            <section id="exams" className="py-20 border-t border-border bg-muted/40">
               <div className="container px-6 mx-auto">
                  <div className="flex flex-col md:flex-row justify-between items-end mb-12 gap-6">
                     <div>
                        <p className="text-sm font-semibold uppercase tracking-widest text-primary mb-3">Question Banks</p>
                        <h2 className="font-serif text-3xl font-bold text-foreground">Supported Exams</h2>
                        <p className="text-muted-foreground mt-2 text-sm">Current practice banks available today.</p>
                     </div>
                     <Link href="/dashboard/mock">
                        <ButtonS className="shrink-0">View All Problem Sets</ButtonS>
                     </Link>
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                     <Card className="hover:border-primary/40 transition-colors duration-200 cursor-pointer group">
                        <CardContent className="p-8 flex flex-col gap-5">
                           <div className="flex justify-between items-start">
                              <Sfont style={1} className="font-serif text-5xl font-bold text-foreground group-hover:text-primary transition-colors duration-200">GRE</Sfont>
                              <span className="text-xs font-semibold uppercase tracking-wider text-primary border border-primary/30 bg-primary/5 px-2.5 py-1 rounded-md">Live</span>
                           </div>
                           <div>
                              <h3 className="text-lg font-semibold mb-2">Graduate Record Examination</h3>
                              <p className="text-muted-foreground text-sm leading-relaxed">
                                 Full coverage of Quantitative Reasoning and Verbal Reasoning. Includes Data Interpretation and Reading Comprehension blocks.
                              </p>
                           </div>
                           <div className="flex gap-6 text-sm text-muted-foreground pt-2 border-t border-border">
                              <span className="flex items-center gap-1.5"><CheckCircle2 className="w-4 h-4 text-primary" /> 1,500+ Questions</span>
                              <span className="flex items-center gap-1.5"><CheckCircle2 className="w-4 h-4 text-primary" /> Adaptive Mocks</span>
                           </div>
                        </CardContent>
                     </Card>

                     <Card className="hover:border-primary/40 transition-colors duration-200 cursor-pointer group">
                        <CardContent className="p-8 flex flex-col gap-5">
                           <div className="flex justify-between items-start">
                              <Sfont style={1} className="font-serif text-5xl font-bold text-foreground group-hover:text-primary transition-colors duration-200">GMAT</Sfont>
                              <span className="text-xs font-semibold uppercase tracking-wider text-primary border border-primary/30 bg-primary/5 px-2.5 py-1 rounded-md">Live</span>
                           </div>
                           <div>
                              <h3 className="text-lg font-semibold mb-2">Focus Edition Included</h3>
                              <p className="text-muted-foreground text-sm leading-relaxed">
                                 Dedicated practice for Data Insights, Quantitative, and Verbal Reasoning. Master the adaptive algorithm logic.
                              </p>
                           </div>
                           <div className="flex gap-6 text-sm text-muted-foreground pt-2 border-t border-border">
                              <span className="flex items-center gap-1.5"><CheckCircle2 className="w-4 h-4 text-primary" /> Data Insights Ready</span>
                              <span className="flex items-center gap-1.5"><CheckCircle2 className="w-4 h-4 text-primary" /> 800-Level Problems</span>
                           </div>
                        </CardContent>
                     </Card>
                  </div>
               </div>
            </section>

            {/* Final CTA */}
            <section className="py-24 bg-foreground">
               <div className="container px-6 mx-auto text-center max-w-2xl">
                  <h2 className="font-serif text-3xl md:text-5xl font-bold mb-5 tracking-tight text-background">Start your improvement arc today.</h2>
                  <p className="text-base mb-10 text-background/70 max-w-lg mx-auto leading-relaxed">
                     No credit card required. Instant access to better practice.
                  </p>
                  <Link href="/signup?force=true" passHref>
                     <ButtonP className="h-12 px-10 text-base font-semibold bg-background text-foreground hover:bg-background/90 transition-colors">
                        Create Free Account
                     </ButtonP>
                  </Link>
               </div>
            </section>
         </main>
         <Footer
            className="bg-muted/50 text-muted-foreground py-14 border-t border-border"
            centerItems={footerItems}
         />
      </div>
   );
};

export default Home;
