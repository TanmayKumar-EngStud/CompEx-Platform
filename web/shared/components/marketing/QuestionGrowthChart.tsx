"use client";

import React, { useEffect, useState } from 'react';
import {
    AreaChart,
    Area,
    XAxis,
    YAxis,
    CartesianGrid,
    Tooltip,
    ResponsiveContainer,
    LineChart,
    Line,
    Legend
} from 'recharts';
import { motion } from 'framer-motion';
import { TrendingUp, BarChart3, Award } from 'lucide-react';

interface StatsData {
    date: string;
    count: number;
    quality: number;
}

export default function QuestionGrowthChart() {
    const [data, setData] = useState<StatsData[]>([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        fetch('/api/questions/growth-stats')
            .then(res => res.json())
            .then(d => {
                setData(d);
                setLoading(false);
            })
            .catch(err => {
                console.error("Failed to fetch stats:", err);
                setLoading(false);
            });
    }, []);

    if (loading) {
        return (
            <div className="w-full h-64 flex items-center justify-center bg-slate-900/30 rounded-xl border border-slate-800 animate-pulse">
                <div className="flex flex-col items-center gap-2">
                    <BarChart3 className="w-8 h-8 text-slate-700" />
                    <span className="text-xs text-slate-500 uppercase tracking-widest font-bold">Initializing Intelligence Feed...</span>
                </div>
            </div>
        );
    }

    return (
        <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="w-full space-y-4 p-6 bg-slate-900/40 backdrop-blur-md rounded-2xl border border-slate-800"
        >
            <div className="flex items-center justify-between mb-6">
                <div>
                    <h3 className="text-lg font-bold text-white flex items-center gap-2">
                        <TrendingUp className="w-5 h-5 text-indigo-400" />
                        Intelligence Evolution
                    </h3>
                    <p className="text-xs text-slate-500">Autonomous question synthesis & quality audit metrics</p>
                </div>
                <div className="flex gap-4">
                    <div className="text-right">
                        <span className="block text-[10px] text-slate-500 uppercase font-bold tracking-tighter">Pool Size</span>
                        <span className="text-xl font-mono text-indigo-400">{data[data.length - 1]?.count || 0}</span>
                    </div>
                    <div className="text-right">
                        <span className="block text-[10px] text-slate-500 uppercase font-bold tracking-tighter">Avg Quality</span>
                        <span className="text-xl font-mono text-emerald-400">{data[data.length - 1]?.quality || 0}/10</span>
                    </div>
                </div>
            </div>

            <div className="h-64 w-full">
                <ResponsiveContainer width="100%" height="100%">
                    <AreaChart data={data} margin={{ top: 10, right: 10, left: 0, bottom: 0 }}>
                        <defs>
                            <linearGradient id="colorCount" x1="0" y1="0" x2="0" y2="1">
                                <stop offset="5%" stopColor="#4f46e5" stopOpacity={0.3} />
                                <stop offset="95%" stopColor="#4f46e5" stopOpacity={0} />
                            </linearGradient>
                        </defs>
                        <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" vertical={false} />
                        <XAxis
                            dataKey="date"
                            stroke="#64748b"
                            fontSize={10}
                            tickLine={false}
                            axisLine={false}
                            tickFormatter={(str) => {
                                const date = new Date(str);
                                return date.toLocaleDateString([], { month: 'short', day: 'numeric' });
                            }}
                        />
                        <YAxis hide domain={['auto', 'auto']} />
                        <Tooltip
                            contentStyle={{ backgroundColor: '#0f172a', border: '1px solid #334155', borderRadius: '8px', fontSize: '12px' }}
                            itemStyle={{ color: '#e2e8f0' }}
                        />
                        <Area
                            type="monotone"
                            dataKey="count"
                            stroke="#6366f1"
                            fillOpacity={1}
                            fill="url(#colorCount)"
                            strokeWidth={2}
                            name="Question Pool"
                        />
                        <Area
                            type="monotone"
                            dataKey="quality"
                            stroke="#10b981"
                            fill="transparent"
                            strokeWidth={2}
                            strokeDasharray="5 5"
                            name="Quality Index"
                        />
                    </AreaChart>
                </ResponsiveContainer>
            </div>

            <div className="pt-4 border-t border-slate-800 flex items-center justify-between">
                <p className="text-[10px] text-slate-500 italic max-w-xs">
                    * Quality index is computed using community feedback variance and hallucination detection heuristics.
                </p>
                <div className="flex items-center gap-1 text-[10px] font-bold text-indigo-400 uppercase tracking-widest">
                    <Award className="w-3 h-3" />
                    High Fidelity
                </div>
            </div>
        </motion.div>
    );
}
