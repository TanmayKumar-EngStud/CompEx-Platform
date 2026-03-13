"use client";

import React from "react";
import { Check, Zap, Crown, Users } from "lucide-react";
import { motion } from "framer-motion";
import { ButtonP, ButtonS } from "@/shared/components/ui/button";
import { useRouter } from "next/navigation";

const PricingCard = ({ 
  title, 
  price, 
  period, 
  features, 
  highlighted, 
  icon: Icon,
  buttonText = "Get Started",
  buttonAction,
  originalPrice
}: {
  title: string;
  price: string;
  period?: string;
  features: string[];
  highlighted?: boolean;
  icon: any;
  buttonText?: string;
  buttonAction: () => void;
  originalPrice?: string;
}) => {
  return (
    <motion.div
      whileHover={{ y: -8, scale: 1.02 }}
      transition={{ duration: 0.3 }}
      className={`relative flex flex-col rounded-2xl p-8 ${
        highlighted
          ? "bg-gradient-to-br from-purple-600 via-purple-700 to-indigo-800 text-white shadow-2xl border-4 border-purple-400"
          : "bg-white dark:bg-gray-800 border-2 border-gray-200 dark:border-gray-700"
      }`}
    >
      {highlighted && (
        <div className="absolute -top-5 left-1/2 transform -translate-x-1/2 bg-gradient-to-r from-yellow-400 to-orange-500 text-black px-4 py-1 rounded-full text-sm font-bold">
          MOST POPULAR
        </div>
      )}
      
      <div className="flex items-center gap-3 mb-4">
        <div className={`p-3 rounded-xl ${highlighted ? "bg-white/20" : "bg-purple-100 dark:bg-purple-900"}`}>
          <Icon className={`w-6 h-6 ${highlighted ? "text-white" : "text-purple-600 dark:text-purple-400"}`} />
        </div>
        <h3 className="text-2xl font-bold">{title}</h3>
      </div>

      <div className="mb-6">
        {originalPrice && (
          <div className="flex items-center gap-2 mb-1">
            <span className={`text-xl line-through opacity-60 ${highlighted ? "text-white" : "text-gray-500"}`}>
              ${originalPrice}
            </span>
            <span className="bg-red-500 text-white text-xs px-2 py-1 rounded-full font-bold">
              LAUNCH OFFER
            </span>
          </div>
        )}
        <div className="flex items-baseline gap-1">
          <span className="text-5xl font-bold">${price}</span>
          {period && <span className={`text-lg ${highlighted ? "text-white/80" : "text-gray-500"}`}>/{period}</span>}
        </div>
      </div>

      <ul className="space-y-3 mb-8 flex-grow">
        {features.map((feature, idx) => (
          <li key={idx} className="flex items-start gap-2">
            <Check className={`w-5 h-5 mt-0.5 flex-shrink-0 ${highlighted ? "text-green-300" : "text-green-600"}`} />
            <span className={highlighted ? "text-white" : "text-gray-700 dark:text-gray-300"}>{feature}</span>
          </li>
        ))}
      </ul>

      {highlighted ? (
        <ButtonP onClick={buttonAction} className="w-full py-6 text-lg font-bold bg-white text-purple-700 hover:bg-gray-100">
          {buttonText}
        </ButtonP>
      ) : (
        <ButtonS onClick={buttonAction} className="w-full py-6 text-lg font-bold">
          {buttonText}
        </ButtonS>
      )}
    </motion.div>
  );
};

export default function PricingPage() {
  const router = useRouter();

  const plans = [
    {
      title: "Free",
      price: "0",
      icon: Zap,
      features: [
        "10 questions per day",
        "Basic analytics",
        "Streak tracking & XP",
        "Global leaderboard",
        "Topic tags & filters",
        "AI explanations"
      ],
      buttonText: "Start Free",
      buttonAction: () => router.push("/dashboard")
    },
    {
      title: "Pro",
      price: "4.99",
      originalPrice: "9.99",
      period: "month",
      icon: Crown,
      highlighted: true,
      features: [
        "Unlimited questions",
        "All difficulty levels",
        "Full mock exams (1/month)",
        "Detailed analytics & reports",
        "Adaptive learning mode",
        "Performance comparison",
        "Priority support",
        "Ad-free experience"
      ],
      buttonText: "Upgrade to Pro",
      buttonAction: () => {
        // TODO: Implement Stripe checkout
        alert("Stripe checkout coming soon!");
      }
    },
    {
      title: "Team",
      price: "14.99",
      originalPrice: "29.99",
      period: "month",
      icon: Users,
      features: [
        "All Pro features",
        "5 team members",
        "Team dashboard",
        "Student progress tracking",
        "Custom study plans",
        "Bulk assignments",
        "Team analytics",
        "Priority support"
      ],
      buttonText: "Get Team Plan",
      buttonAction: () => {
        // TODO: Implement Stripe checkout
        alert("Stripe checkout coming soon!");
      }
    }
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 via-purple-50 to-indigo-100 dark:from-gray-900 dark:via-purple-900/20 dark:to-indigo-900/20 py-20 px-4">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          className="text-center mb-16"
        >
          <h1 className="text-5xl md:text-6xl font-bold mb-4 bg-gradient-to-r from-purple-600 to-indigo-600 bg-clip-text text-transparent">
            Simple, Transparent Pricing
          </h1>
          <p className="text-xl text-gray-600 dark:text-gray-400 max-w-2xl mx-auto">
            Start free, upgrade when you're ready. No hidden fees, cancel anytime.
          </p>
        </motion.div>

        {/* Launch Offer Banner */}
        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: 0.2 }}
          className="bg-gradient-to-r from-red-500 to-pink-500 text-white rounded-xl p-6 mb-12 text-center shadow-lg"
        >
          <h2 className="text-2xl font-bold mb-2">🎉 Launch Offer - First 30 Days Only!</h2>
          <p className="text-lg">Get <strong>50% OFF</strong> all paid plans. Use code: <code className="bg-white/20 px-3 py-1 rounded">LAUNCH50</code></p>
        </motion.div>

        {/* Pricing Cards */}
        <div className="grid md:grid-cols-3 gap-8 mb-16">
          {plans.map((plan, idx) => (
            <motion.div
              key={plan.title}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.1 * idx }}
            >
              <PricingCard {...plan} />
            </motion.div>
          ))}
        </div>

        {/* FAQ Section */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.4 }}
          className="bg-white dark:bg-gray-800 rounded-2xl p-8 shadow-lg"
        >
          <h2 className="text-3xl font-bold mb-6 text-center">Common Questions</h2>
          <div className="grid md:grid-cols-2 gap-6">
            {[
              {
                q: "Can I cancel anytime?",
                a: "Yes! No hidden fees. Cancel from your account settings anytime."
              },
              {
                q: "What payment methods do you accept?",
                a: "We accept all major credit cards, debit cards, Apple Pay, and Google Pay via Stripe."
              },
              {
                q: "Is my payment information secure?",
                a: "Absolutely. We use Stripe for payments and never store your card details."
              },
              {
                q: "Can I switch plans later?",
                a: "Yes! Upgrade or downgrade your plan anytime from your account settings."
              }
            ].map((faq, idx) => (
              <div key={idx} className="space-y-2">
                <h3 className="font-bold text-lg text-gray-900 dark:text-white">{faq.q}</h3>
                <p className="text-gray-600 dark:text-gray-400">{faq.a}</p>
              </div>
            ))}
          </div>
        </motion.div>

        {/* Footer CTA */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.6 }}
          className="text-center mt-12"
        >
          <p className="text-gray-600 dark:text-gray-400 mb-4">
            Start with our free plan and upgrade when you're ready
          </p>
          <ButtonP onClick={() => router.push("/dashboard")} className="px-8 py-4 text-lg">
            Get Started Free →
          </ButtonP>
        </motion.div>
      </div>
    </div>
  );
}
