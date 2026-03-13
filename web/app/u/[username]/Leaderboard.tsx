"use client";
import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from "@/shared/components/ui/card";
import { ChevronLeft, ChevronRight, Trophy, Medal } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { usePaginationStore } from '@/shared/stores/problems/pagination';
import Link from 'next/link';

interface LeaderboardUser {
    rank: number;
    username: string;
    xp: number;
    rating: number;
}

interface LeaderboardProps {
    currentUsername: string;
}

export function Leaderboard({ currentUsername }: LeaderboardProps) {
    const { examName } = usePaginationStore();
    const [users, setUsers] = useState<LeaderboardUser[]>([]);
    const [page, setPage] = useState(1);
    const [totalPages, setTotalPages] = useState(1);
    const [loading, setLoading] = useState(true);

    const fetchLeaderboard = React.useCallback(async (requestedPage?: number) => {
        setLoading(true);
        try {
            const url = new URL('/api/analytics/leaderboard', window.location.origin);
            url.searchParams.append('exam', examName);
            url.searchParams.append('username', currentUsername);
            if (requestedPage) url.searchParams.append('page', requestedPage.toString());

            const res = await fetch(url);
            const data = await res.json();

            setUsers(data.users);
            setPage(data.currentPage);
            setTotalPages(Math.ceil(data.totalUsers / data.pageSize));
        } catch (error) {
            console.error("Leaderboard fetch error:", error);
        } finally {
            setLoading(false);
        }
    }, [examName, currentUsername]);

    useEffect(() => {
        fetchLeaderboard();
    }, [fetchLeaderboard]); // Auto-center on exam switch

    const handlePrev = () => {
        if (page > 1) fetchLeaderboard(page - 1);
    }

    const handleNext = () => {
        if (page < totalPages) fetchLeaderboard(page + 1);
    }

    const getRankIcon = (rank: number) => {
        if (rank === 1) return <Trophy className="w-4 h-4 text-amber-500" />;
        if (rank === 2) return <Medal className="w-4 h-4 text-slate-400" />;
        if (rank === 3) return <Medal className="w-4 h-4 text-amber-700" />;
        return <span className="text-[10px] font-bold opacity-30">{rank}</span>;
    }

    return (
        <Card className="border-primary/10 bg-card/50 backdrop-blur-sm">
            <CardHeader className="p-4 pb-2">
                <CardTitle className="text-sm font-bold flex items-center gap-2">
                    <Trophy className="w-4 h-4 text-primary" />
                    Global Rankings
                </CardTitle>
            </CardHeader>
            <CardContent className="p-2 space-y-1">
                <div className="min-h-[450px]">
                    <AnimatePresence mode="wait">
                        {loading ? (
                            <div className="h-[400px] flex items-center justify-center opacity-30">
                                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary" />
                            </div>
                        ) : (
                            <motion.div
                                initial={{ opacity: 0 }}
                                animate={{ opacity: 1 }}
                                exit={{ opacity: 0 }}
                                className="space-y-1"
                            >
                                {users.map((user) => (
                                    <div
                                        key={user.username}
                                        className={`flex items-center justify-between p-2 px-3 rounded-lg transition-colors ${user.username === currentUsername
                                            ? 'bg-primary/20 border border-primary/20'
                                            : 'hover:bg-primary/5'
                                            }`}
                                    >
                                        <div className="flex items-center gap-3">
                                            <div className="w-6 flex justify-center">
                                                {getRankIcon(user.rank)}
                                            </div>
                                            <Link
                                                href={`/u/${user.username}`}
                                                className={`text-xs font-medium hover:underline transition-all ${user.username === currentUsername ? 'text-primary' : 'hover:text-primary/80'}`}
                                            >
                                                {user.username}
                                            </Link>
                                        </div>
                                        <div className="text-right">
                                            <span className="text-[11px] font-black opacity-70">
                                                {user.rating}
                                            </span>
                                            <span className="text-[9px] uppercase font-bold opacity-30 ml-1">/ 100</span>
                                        </div>
                                    </div>
                                ))}
                            </motion.div>
                        )}
                    </AnimatePresence>
                </div>

                <div className="flex items-center justify-between p-2 pt-4 border-t border-border/50">
                    <button
                        onClick={handlePrev}
                        disabled={page === 1 || loading}
                        className="p-1 hover:bg-primary/10 rounded-md disabled:opacity-20 transition-colors"
                    >
                        <ChevronLeft className="w-4 h-4" />
                    </button>
                    <span className="text-[10px] font-bold opacity-50 uppercase tracking-tighter">
                        Page {page} of {totalPages}
                    </span>
                    <button
                        onClick={handleNext}
                        disabled={page === totalPages || loading}
                        className="p-1 hover:bg-primary/10 rounded-md disabled:opacity-20 transition-colors"
                    >
                        <ChevronRight className="w-4 h-4" />
                    </button>
                </div>
            </CardContent>
        </Card>
    );
}
