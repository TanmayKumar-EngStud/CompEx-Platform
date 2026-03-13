
"use client";

import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from "@/shared/components/ui/card";
import { AlertTriangle, Zap, Target } from 'lucide-react';

interface SkillStat {
    tag: string;
    section: string;
    accuracy: number;
    avgTime: number;
    attemptCount: number;
}

interface Props {
    skills: SkillStat[];
}

export function ActionableStats({ skills }: Props) {
    if (!skills || skills.length === 0) return null;

    // 1. Weakest Links
    const weakestLinks = [...skills]
        .filter(s => s.accuracy < 65 && s.attemptCount > 0)
        .sort((a, b) => b.attemptCount - a.attemptCount)
        .slice(0, 3);

    // 2. Efficiency Gains
    const efficiencyGains = [...skills]
        .filter(s => s.accuracy >= 80 && s.avgTime > 120)
        .sort((a, b) => b.avgTime - a.avgTime)
        .slice(0, 2);

    // 3. Best Performers
    const bestPerformers = [...skills]
        .filter(s => s.accuracy >= 90 && s.attemptCount > 5)
        .sort((a, b) => b.accuracy - a.accuracy)
        .slice(0, 2);

    return (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
            <Card className="bg-red-50/50 border-red-100 dark:bg-red-950/10 dark:border-red-900/20">
                <CardHeader className="pb-2 text-red-700 dark:text-red-400">
                    <CardTitle className="text-sm font-bold flex items-center gap-2">
                        <AlertTriangle className="w-4 h-4" /> Priority Areas
                    </CardTitle>
                </CardHeader>
                <CardContent className="space-y-2">
                    {weakestLinks.map(s => (
                        <div key={s.tag} className="flex justify-between items-center text-xs">
                            <span className="font-medium truncate max-w-[120px]">{s.tag}</span>
                            <span className="font-bold">{s.accuracy}%</span>
                        </div>
                    ))}
                    {weakestLinks.length === 0 && <p className="text-[10px] opacity-50 italic">Solve more problems to identify areas needing focus.</p>}
                </CardContent>
            </Card>

            <Card className="bg-amber-50/50 border-amber-100 dark:bg-amber-950/10 dark:border-amber-900/20">
                <CardHeader className="pb-2 text-amber-700 dark:text-amber-400">
                    <CardTitle className="text-sm font-bold flex items-center gap-2">
                        <Zap className="w-4 h-4" /> Speed Gains
                    </CardTitle>
                </CardHeader>
                <CardContent className="space-y-2">
                    {efficiencyGains.map(s => (
                        <div key={s.tag} className="flex justify-between items-center text-xs">
                            <span className="font-medium truncate max-w-[120px]">{s.tag}</span>
                            <span className="font-bold">{s.avgTime}s</span>
                        </div>
                    ))}
                    {efficiencyGains.length === 0 && <p className="text-[10px] opacity-50 italic">Practice more to analyze your speed across topics.</p>}
                </CardContent>
            </Card>

            <Card className="bg-green-50/50 border-green-100 dark:bg-green-950/10 dark:border-green-900/20">
                <CardHeader className="pb-2 text-green-700 dark:text-green-400">
                    <CardTitle className="text-sm font-bold flex items-center gap-2">
                        <Target className="w-4 h-4" /> Strength Zones
                    </CardTitle>
                </CardHeader>
                <CardContent className="space-y-2">
                    {bestPerformers.map(s => (
                        <div key={s.tag} className="flex justify-between items-center text-xs">
                            <span className="font-medium truncate max-w-[120px]">{s.tag}</span>
                            <span className="font-bold">{s.accuracy}%</span>
                        </div>
                    ))}
                    {bestPerformers.length === 0 && <p className="text-[10px] opacity-50 italic">Maintain consistent high accuracy to build strength zones.</p>}
                </CardContent>
            </Card>
        </div>
    );
}
