"use client";

import React from "react";
import { Check, Zap, Crown, Users } from "lucide-react";
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
    <div
      className={`relative flex flex-col rounded-xl p-8 border transition-colors duration-200 ${
        highlighted
          ? "bg-foreground text-background border-foreground shadow-xl"
          : "bg-card text-card-foreground border-border hover:border-primary/30"
      }`}
    >
      {highlighted && (
        <div className="absolute -top-3.5 left-1/2 -translate-x-1/2 bg-primary text-primary-foreground px-3 py-0.5 rounded-full text-xs font-semibold uppercase tracking-wider whitespace-nowrap">
          Most Popular
        </div>
      )}

      <div className="flex items-center gap-3 mb-6">
        <div className={`p-2 rounded-lg ${highlighted ? "bg-white/15" : "bg-muted"}`}>
          <Icon className={`w-5 h-5 ${highlighted ? "text-background" : "text-primary"}`} />
        </div>
        <h3 className="text-xl font-semibold">{title}</h3>
      </div>

      <div className="mb-8">
        {originalPrice && (
          <div className="flex items-center gap-2 mb-1">
            <span className={`text-base line-through ${highlighted ? "text-background/50" : "text-muted-foreground"}`}>
              ${originalPrice}
            </span>
            <span className={`text-xs font-semibold px-2 py-0.5 rounded ${highlighted ? "bg-background/20 text-background" : "bg-primary/10 text-primary"}`}>
              Launch offer
            </span>
          </div>
        )}
        <div className="flex items-baseline gap-1">
          <span className="text-4xl font-bold">${price}</span>
          {period && <span className={`text-sm ${highlighted ? "text-background/60" : "text-muted-foreground"}`}>/{period}</span>}
        </div>
      </div>

      <ul className="space-y-2.5 mb-8 flex-grow">
        {features.map((feature, idx) => (
          <li key={idx} className="flex items-start gap-2.5 text-sm">
            <Check className={`w-4 h-4 mt-0.5 flex-shrink-0 ${highlighted ? "text-background/80" : "text-primary"}`} />
            <span className={highlighted ? "text-background/90" : "text-foreground/80"}>{feature}</span>
          </li>
        ))}
      </ul>

      {highlighted ? (
        <ButtonP onClick={buttonAction} className="w-full py-2.5 font-semibold bg-background text-foreground hover:bg-background/90 transition-colors">
          {buttonText}
        </ButtonP>
      ) : (
        <ButtonS onClick={buttonAction} className="w-full py-2.5 font-semibold">
          {buttonText}
        </ButtonS>
      )}
    </div>
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
        alert("Stripe checkout coming soon!");
      }
    }
  ];

  return (
    <div className="min-h-screen bg-background py-20 px-4">
      <div className="max-w-5xl mx-auto">

        {/* Header */}
        <div className="text-center mb-14">
          <p className="text-sm font-semibold uppercase tracking-widest text-primary mb-4">Pricing</p>
          <h1 className="font-serif text-4xl md:text-5xl font-bold mb-4 text-foreground tracking-tight">
            Simple, transparent pricing.
          </h1>
          <p className="text-base text-muted-foreground max-w-md mx-auto">
            Start free, upgrade when you&apos;re ready. No hidden fees, cancel anytime.
          </p>
        </div>

        {/* Launch Offer Banner */}
        <div className="border border-primary/30 bg-primary/5 rounded-lg p-4 mb-10 text-center">
          <p className="text-sm font-medium text-foreground">
            <span className="font-semibold text-primary">Launch offer — first 30 days only:</span>{" "}
            50% off all paid plans with code{" "}
            <code className="font-mono bg-muted px-1.5 py-0.5 rounded text-foreground text-xs">LAUNCH50</code>
          </p>
        </div>

        {/* Pricing Cards */}
        <div className="grid md:grid-cols-3 gap-6 mb-16">
          {plans.map((plan) => (
            <PricingCard key={plan.title} {...plan} />
          ))}
        </div>

        {/* FAQ */}
        <div className="border border-border rounded-xl p-8 bg-card">
          <h2 className="font-serif text-2xl font-bold mb-8 text-foreground">Common questions</h2>
          <div className="grid md:grid-cols-2 gap-8">
            {[
              {
                q: "Can I cancel anytime?",
                a: "Yes. No hidden fees — cancel directly from your account settings, no questions asked."
              },
              {
                q: "What payment methods do you accept?",
                a: "All major credit and debit cards, plus Apple Pay and Google Pay via Stripe."
              },
              {
                q: "Is my payment information secure?",
                a: "We use Stripe for all payments and never store your card details on our servers."
              },
              {
                q: "Can I switch plans later?",
                a: "Yes. Upgrade or downgrade at any time from your account settings."
              }
            ].map((faq, idx) => (
              <div key={idx}>
                <h3 className="font-semibold text-sm text-foreground mb-1.5">{faq.q}</h3>
                <p className="text-sm text-muted-foreground leading-relaxed">{faq.a}</p>
              </div>
            ))}
          </div>
        </div>

        {/* Footer CTA */}
        <div className="text-center mt-12">
          <p className="text-sm text-muted-foreground mb-4">
            Start with our free plan and upgrade when you&apos;re ready.
          </p>
          <ButtonP onClick={() => router.push("/dashboard")} className="px-8 py-2.5 text-sm font-semibold">
            Get started free →
          </ButtonP>
        </div>
      </div>
    </div>
  );
}
