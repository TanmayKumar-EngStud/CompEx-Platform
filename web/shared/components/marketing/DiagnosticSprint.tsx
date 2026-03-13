"use client";

import React, { useState } from "react";
import { Card, CardContent } from "@/shared/components/ui/card";
import { ButtonP } from "@/shared/components/ui/button";
import { motion, AnimatePresence } from "framer-motion";
import { CheckCircle2, XCircle, Timer, ArrowRight, Sparkles } from "lucide-react";

const MOCK_QUESTIONS = [
  {
    id: 1,
    question: "If x + y = 10 and x - y = 4, what is the value of xy?",
    options: ["21", "24", "28", "32"],
    correct: "21",
    explanation: "Step-by-step logic:\n1. Solve for x: (x+y) + (x-y) = 14 => 2x = 14 => x = 7.\n2. Solve for y: 7 + y = 10 => y = 3.\n3. Calculation: xy = 7 * 3 = 21.\n\nNote: x=7 is a prime number, ensuring logical consistency with the problem constraints."
  },
  {
    id: 2,
    question: "Which of the following is most nearly opposite in meaning to 'Ephemeral'?",
    options: ["Fleeting", "Eternal", "Brief", "Transparent"],
    correct: "Eternal",
    explanation: "Ephemeral means short-lived; Eternal means lasting forever."
  }
];

export const DiagnosticSprint = () => {
  const [step, setStep] = useState(0); // 0: Start, 1: Q1, 2: Q2, 3: Result
  const [answers, setAnswers] = useState<Record<number, string>>({});
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [showExplanation, setShowExplanation] = useState(false);

  const handleAnswer = (ans: string) => {
    setAnswers({ ...answers, [step]: ans });
    setShowExplanation(true);
  };

  const nextStep = () => {
    setShowExplanation(false);
    if (step === MOCK_QUESTIONS.length) {
      setIsAnalyzing(true);
      setTimeout(() => setIsAnalyzing(false), 1500); // Simulate AI processing
    }
    setStep(step + 1);
  };

  return (
    <Card className="w-full max-w-2xl mx-auto overflow-hidden border-primary/20 bg-background/50 backdrop-blur-xl shadow-2xl">
      <CardContent className="p-8">
        <AnimatePresence mode="wait">
          {step === 0 && (
            <motion.div
              key="start"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              className="text-center py-8"
            >
              <div className="inline-flex p-3 rounded-full bg-primary/10 text-primary mb-6">
                <Timer className="w-8 h-8" />
              </div>
              <h3 className="text-2xl font-bold mb-4">60-Second Diagnostic</h3>
              <p className="text-muted-foreground mb-8">
                Solve 2 real GRE-style questions to see your predicted score range.
                Our AI will analyze your speed and accuracy.
              </p>
              <ButtonP onClick={() => setStep(1)} className="w-full h-12 text-lg">
                Start Sprint
              </ButtonP>
            </motion.div>
          )}

          {step > 0 && step <= MOCK_QUESTIONS.length && (
            <motion.div
              key={`q-${step}`}
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -20 }}
              className="space-y-6"
            >
              <div className="flex justify-between items-center mb-4">
                <span className="text-xs font-bold uppercase tracking-wider text-primary">Question {step} of {MOCK_QUESTIONS.length}</span>
                <div className="flex gap-1">
                  {[1, 2].map(i => (
                    <div key={i} className={`h-1.5 w-8 rounded-full ${i <= step ? 'bg-primary' : 'bg-muted'}`} />
                  ))}
                </div>
              </div>

              <h4 className="text-xl font-medium leading-relaxed">
                {MOCK_QUESTIONS[step - 1].question}
              </h4>

              <div className="grid grid-cols-1 gap-3">
                {MOCK_QUESTIONS[step - 1].options.map((opt) => {
                  const isSelected = answers[step] === opt;
                  const isCorrect = opt === MOCK_QUESTIONS[step - 1].correct;

                  return (
                    <button
                      key={opt}
                      disabled={showExplanation}
                      onClick={() => handleAnswer(opt)}
                      className={`p-4 text-left rounded-xl border-2 transition-all duration-200 ${showExplanation
                        ? (isCorrect ? 'border-green-500 bg-green-500/10' : (isSelected ? 'border-red-500 bg-red-500/10' : 'border-border opacity-50'))
                        : 'border-border hover:border-primary hover:bg-primary/5'
                        }`}
                    >
                      <div className="flex justify-between items-center">
                        <span>{opt}</span>
                        {showExplanation && isCorrect && <CheckCircle2 className="w-5 h-5 text-green-500" />}
                        {showExplanation && isSelected && !isCorrect && <XCircle className="w-5 h-5 text-red-500" />}
                      </div>
                    </button>
                  );
                })}
              </div>

              {showExplanation && (
                <motion.div
                  initial={{ opacity: 0, height: 0 }}
                  animate={{ opacity: 1, height: 'auto' }}
                  className="p-6 rounded-xl bg-muted/50 border border-border"
                >
                  <div className="flex justify-between items-center mb-4">
                    <p className="text-sm font-bold flex items-center gap-2 text-primary">
                      <Sparkles className="w-4 h-4" /> AI COACH INSIGHT
                    </p>
                    <div className="flex gap-2">
                      <button className="text-[10px] md:text-xs px-3 md:px-4 py-2 bg-background rounded-md border border-border hover:bg-muted transition-colors">View Details</button>
                      <button className="text-[10px] md:text-xs px-5 md:px-6 py-2.5 md:py-3 bg-primary text-primary-foreground rounded-md hover:bg-primary/90 transition-all font-bold shadow-sm">Ask AI</button>
                    </div>
                  </div>
                  <p className="text-sm text-muted-foreground whitespace-pre-line leading-relaxed">{MOCK_QUESTIONS[step - 1].explanation}</p>
                  <ButtonP onClick={nextStep} className="mt-6 w-full h-12">
                    {step === MOCK_QUESTIONS.length ? "Analyze Performance" : "Next Question"} <ArrowRight className="ml-2 w-4 h-4" />
                  </ButtonP>
                </motion.div>
              )}
            </motion.div>
          )}

          {isAnalyzing && (
            <motion.div
              key="analyzing"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="py-12 text-center space-y-6"
            >
              <div className="relative w-24 h-24 mx-auto">
                <div className="absolute inset-0 border-4 border-primary/20 rounded-full" />
                <motion.div
                  animate={{ rotate: 360 }}
                  transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
                  className="absolute inset-0 border-4 border-primary border-t-transparent rounded-full"
                />
              </div>
              <div>
                <h3 className="text-xl font-bold mb-2">AI is analyzing your performance...</h3>
                <div className="flex flex-col gap-3 max-w-xs mx-auto">
                  <div className="h-3 bg-muted rounded-full overflow-hidden">
                    <motion.div
                      initial={{ width: 0 }}
                      animate={{ width: "100%" }}
                      transition={{ duration: 1.5 }}
                      className="h-full bg-primary"
                    />
                  </div>
                  <div className="flex justify-between text-[10px] font-bold text-muted-foreground uppercase tracking-widest">
                    <motion.span animate={{ opacity: [0.5, 1, 0.5] }} transition={{ duration: 1, repeat: Infinity }}>Calculating Accuracy</motion.span>
                    <motion.span animate={{ opacity: [0.5, 1, 0.5] }} transition={{ duration: 1, repeat: Infinity, delay: 0.5 }}>Benchmarking Speed</motion.span>
                  </div>
                  {/* Performance Skeleton Pulses */}
                  <div className="space-y-2 pt-4">
                    <div className="h-4 w-3/4 bg-muted rounded animate-pulse" />
                    <div className="h-4 w-1/2 bg-muted rounded animate-pulse" />
                  </div>
                </div>
              </div>
            </motion.div>
          )}

          {step > MOCK_QUESTIONS.length && !isAnalyzing && (
            <motion.div
              key="result"
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              className="text-center py-8"
            >
              <div className="inline-flex p-4 rounded-full bg-green-500/10 text-green-500 mb-6">
                <Sparkles className="w-10 h-10" />
              </div>
              <h3 className="text-3xl font-bold mb-2">Predicted: 162-167</h3>
              <p className="text-muted-foreground mb-8">
                Based on your {Object.values(answers).filter((a, i) => a === MOCK_QUESTIONS[i].correct).length}/2 accuracy
                and rapid response time.
              </p>
              <div className="space-y-3">
                <a href="/signup?force=true" className="w-full">
                  <ButtonP className="w-full h-12 text-lg">
                    Get Full Personalized Report
                  </ButtonP>
                </a>

                <button
                  onClick={() => {
                    const text = `I just completed the Compex Diagnostic Sprint! 🚀\n\nPredicted score: 162-167 range.\nAccuracy: ${Object.values(answers).filter((a, i) => a === MOCK_QUESTIONS[i].correct).length}/2\n\nTry it yourself at compex.live! @CompexPrep`;
                    window.open(`https://twitter.com/intent/tweet?text=${encodeURIComponent(text)}`, '_blank');
                  }}
                  className="flex items-center justify-center gap-2 w-full py-3 rounded-xl border-2 border-primary/20 bg-primary/5 text-sm font-bold text-primary hover:bg-primary/10 transition-all duration-300"
                >
                  <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 24 24"><path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z" /></svg>
                  SHARE SCORE ON X
                </button>
                <p className="text-xs text-muted-foreground pt-2">Join 1,000+ students using Compex to peak.</p>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </CardContent>
    </Card>
  );
};
