"use client";

import React from "react";
import { Crown, Sparkles, Zap } from "lucide-react";
import { motion } from "framer-motion";
import { ButtonP } from "@/shared/components/ui/button";
import { useRouter } from "next/navigation";

interface ProUpgradePromptProps {
  feature?: string;
  description?: string;
  compact?: boolean;
}

export const ProUpgradePrompt: React.FC<ProUpgradePromptProps> = ({
  feature = "AI Coach Solutions",
  description = "Get detailed step-by-step explanations for every question",
  compact = false
}) => {
  const router = useRouter();

  if (compact) {
    return (
      <div className="flex items-center justify-between p-4 bg-gradient-to-r from-purple-50 to-indigo-50 dark:from-purple-900/20 dark:to-indigo-900/20 border-2 border-purple-200 dark:border-purple-700 rounded-xl">
        <div className="flex items-center gap-3">
          <Crown className="w-5 h-5 text-purple-600 dark:text-purple-400" />
          <div>
            <p className="font-semibold text-sm text-gray-900 dark:text-white">
              Unlock {feature}
            </p>
            <p className="text-xs text-gray-600 dark:text-gray-400">
              Upgrade to Pro for unlimited access
            </p>
          </div>
        </div>
        <ButtonP 
          onClick={() => router.push("/pricing")}
          className="px-4 py-2 text-sm"
        >
          Upgrade
        </ButtonP>
      </div>
    );
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
      className="w-full p-8 bg-gradient-to-br from-purple-100 via-indigo-100 to-purple-50 dark:from-purple-900/30 dark:via-indigo-900/30 dark:to-purple-900/20 border-2 border-purple-300 dark:border-purple-600 rounded-2xl shadow-lg relative overflow-hidden"
    >
      {/* Decorative elements */}
      <div className="absolute top-0 right-0 w-40 h-40 bg-purple-300/20 dark:bg-purple-500/10 rounded-full -mr-20 -mt-20 blur-3xl" />
      <div className="absolute bottom-0 left-0 w-32 h-32 bg-indigo-300/20 dark:bg-indigo-500/10 rounded-full -ml-16 -mb-16 blur-3xl" />

      <div className="relative">
        {/* Icon header */}
        <div className="flex items-center justify-center mb-6">
          <motion.div
            animate={{ 
              rotate: [0, 5, -5, 0],
              scale: [1, 1.05, 1]
            }}
            transition={{ 
              duration: 2,
              repeat: Infinity,
              repeatDelay: 1
            }}
            className="p-4 bg-gradient-to-br from-purple-600 to-indigo-600 rounded-2xl shadow-xl"
          >
            <Crown className="w-10 h-10 text-white" />
          </motion.div>
        </div>

        {/* Content */}
        <div className="text-center mb-6">
          <h3 className="text-2xl font-bold text-gray-900 dark:text-white mb-2 flex items-center justify-center gap-2">
            <Sparkles className="w-5 h-5 text-yellow-500" />
            Unlock {feature}
            <Sparkles className="w-5 h-5 text-yellow-500" />
          </h3>
          <p className="text-gray-700 dark:text-gray-300 text-base max-w-md mx-auto">
            {description}
          </p>
        </div>

        {/* Benefits */}
        <div className="mb-6 space-y-2">
          {[
            "Detailed step-by-step explanations",
            "AI-powered insights & strategies",
            "Unlimited questions per day",
            "Full mock exams & analytics"
          ].map((benefit, idx) => (
            <motion.div
              key={idx}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.1 * idx }}
              className="flex items-center gap-2 text-sm text-gray-700 dark:text-gray-300"
            >
              <Zap className="w-4 h-4 text-purple-600 dark:text-purple-400" />
              <span>{benefit}</span>
            </motion.div>
          ))}
        </div>

        {/* CTA */}
        <div className="flex flex-col sm:flex-row gap-3 items-center justify-center">
          <ButtonP 
            onClick={() => router.push("/pricing")}
            className="px-8 py-3 text-lg font-bold bg-gradient-to-r from-purple-600 to-indigo-600 hover:from-purple-700 hover:to-indigo-700 shadow-lg"
          >
            <Crown className="w-5 h-5 mr-2" />
            Upgrade to Pro
          </ButtonP>
          <button
            onClick={() => router.push("/pricing")}
            className="text-sm text-purple-700 dark:text-purple-300 hover:underline"
          >
            See all features →
          </button>
        </div>

        {/* Pricing hint */}
        <div className="mt-4 text-center">
          <p className="text-xs text-gray-600 dark:text-gray-400">
            Starting at <span className="font-bold text-purple-700 dark:text-purple-300">$4.99/month</span>
            {" "}• 50% OFF Launch Offer
          </p>
        </div>
      </div>
    </motion.div>
  );
};

export default ProUpgradePrompt;
