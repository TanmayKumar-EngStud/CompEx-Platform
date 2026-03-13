
"use client";

import React from 'react';
import { Card, CardContent } from "@/shared/components/ui/card";
import { Zap, Target, Crown, Info, Twitter } from 'lucide-react';
import { motion } from 'framer-motion';

interface GlobalScoreCardProps {
    scores: {
        practice: number;
        mock: number;
        global: number;
    };
}

export function GlobalScoreCard({ scores }: GlobalScoreCardProps) {
    const handleShare = () => {
        const text = `My Compex stats are in! 🚀\n\n🎯 Global Rating: ${scores.global}/100\n⚡ Practice XP: ${scores.practice.toLocaleString()}\n👑 Mock Power: ${scores.mock}\n\nPreparing for the GRE with @CompexPrep! Join the elite cohort.`;
        const url = `https://twitter.com/intent/tweet?text=${encodeURIComponent(text)}`;
        window.open(url, '_blank');
    };

    const scoreItems = [
        {
            label: "Practice XP",
            value: scores.practice.toLocaleString(),
            icon: <Zap className="w-4 h-4" />,
            color: "text-amber-500",
            bg: "bg-amber-500/10",
            description: "Weighted by problem difficulty (L1-L5)",
            percent: Math.min((scores.practice / 50000) * 100, 100)
        },
        {
            label: "Mock Power",
            value: scores.mock,
            icon: <Crown className="w-4 h-4" />,
            color: "text-purple-500",
            bg: "bg-purple-500/10",
            description: "Percentile + Best Score balance",
            percent: scores.mock
        }
    ];

    return (
        <Card className="overflow-hidden border-primary/10 bg-gradient-to-br from-card to-primary/5">
            <CardContent className="p-6 space-y-6">
                {/* Global Elite Score */}
                <div className="relative">
                    <div className="flex items-center justify-between mb-2">
                        <div className="flex items-center gap-2">
                            <div className="p-2 rounded-lg bg-primary/10 text-primary">
                                <Target className="w-5 h-5" />
                            </div>
                            <div>
                                <h3 className="text-sm font-bold uppercase tracking-wider opacity-70">Global Rating</h3>
                                <p className="text-[10px] text-muted-foreground">Composite performance index</p>
                            </div>
                        </div>
                        <div className="text-right">
                            <span className="text-3xl font-black text-primary">{scores.global}</span>
                            <span className="text-xs font-bold opacity-50 ml-1">/ 100</span>
                        </div>
                    </div>

                    <div className="h-3 w-full bg-primary/10 rounded-full overflow-hidden">
                        <motion.div
                            initial={{ width: 0 }}
                            animate={{ width: `${scores.global}%` }}
                            transition={{ duration: 1, ease: "easeOut" }}
                            className="h-full bg-primary shadow-[0_0_15px_rgba(var(--primary),0.5)]"
                        />
                    </div>
                </div>

                <div className="grid grid-cols-2 gap-4">
                    {scoreItems.map((item, idx) => (
                        <div key={idx} className="space-y-3 p-4 rounded-xl bg-background/50 border border-border/50">
                            <div className="flex items-center justify-between">
                                <div className={`p-1.5 rounded-md ${item.bg} ${item.color}`}>
                                    {item.icon}
                                </div>
                                <div className="group relative">
                                    <Info className="w-3 h-3 text-muted-foreground opacity-30 cursor-help group-hover:opacity-100 transition-opacity" />
                                    <div className="absolute bottom-full right-0 mb-2 w-32 p-2 bg-popover text-[10px] rounded-lg border border-border opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none z-50 shadow-xl">
                                        {item.description}
                                    </div>
                                </div>
                            </div>
                            <div>
                                <h4 className="text-[10px] font-bold uppercase opacity-50">{item.label}</h4>
                                <p className="text-xl font-black">{item.value}</p>
                            </div>
                            <div className="h-1 w-full bg-muted rounded-full overflow-hidden">
                                <motion.div
                                    initial={{ width: 0 }}
                                    animate={{ width: `${item.percent}%` }}
                                    transition={{ duration: 1, delay: 0.2, ease: "easeOut" }}
                                    className={`h-full ${item.bg.replace('/10', '')}`}
                                />
                            </div>
                        </div>
                    ))}
                </div>

                {/* Twitter Share Button */}
                <div className="pt-2 border-t border-primary/10">
                    <button 
                        onClick={handleShare}
                        className="w-full flex items-center justify-center gap-2 px-4 py-2.5 rounded-xl bg-[#1DA1F2] text-white text-xs font-bold hover:bg-[#1a8cd8] transition-all hover:scale-[1.02] active:scale-[0.98] shadow-lg shadow-[#1DA1F2]/10"
                    >
                        <Twitter className="w-3.5 h-3.5" />
                        SHARE STATS TO TWITTER / X
                    </button>
                </div>
            </CardContent>
        </Card>
    );
}
