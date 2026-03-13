"use client";

import React, { useState, useEffect } from 'react';
import { Sparkles, Trophy, Star, Gift, Lock } from 'lucide-react';

interface Collectible {
    id: number;
    collectibleType: string;
    collectibleName: string;
    collectibleIcon: string | null;
    description: string | null;
    earnedAt: string;
}

interface UserCollectiblesProps {
    userId: number;
}

export default function UserCollectibles({ userId }: UserCollectiblesProps) {
    const [collectibles, setCollectibles] = useState<Collectible[]>([]);
    const [loading, setLoading] = useState(true);
    const [showAll, setShowAll] = useState(false);

    useEffect(() => {
        fetchCollectibles();
    }, [userId]);

    const fetchCollectibles = async () => {
        try {
            const res = await fetch(`/api/collectibles?userId=${userId}`);
            const data = await res.json();
            setCollectibles(data.earned || []);
        } catch (error) {
            console.error('Error fetching collectibles:', error);
        } finally {
            setLoading(false);
        }
    };

    const displayCollectibles = showAll ? collectibles : collectibles.slice(0, 5);

    if (loading) {
        return (
            <div className="flex gap-2 animate-pulse">
                {[1, 2, 3].map((i) => (
                    <div key={i} className="w-12 h-12 bg-muted rounded-xl" />
                ))}
            </div>
        );
    }

    if (collectibles.length === 0) {
        return (
            <div className="text-center py-4">
                <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-muted mb-3">
                    <Trophy className="w-8 h-8 text-muted-foreground" />
                </div>
                <p className="text-sm text-muted-foreground">
                    Complete challenges to earn badges!
                </p>
            </div>
        );
    }

    return (
        <div className="space-y-3">
            <div className="flex items-center gap-2 mb-2">
                <Sparkles className="w-4 h-4 text-amber-500" />
                <span className="text-sm font-semibold">Badges Earned</span>
                <span className="text-xs text-muted-foreground">({collectibles.length})</span>
            </div>

            <div className="flex flex-wrap gap-2">
                {displayCollectibles.map((collectible) => (
                    <CollectibleBadge key={collectible.id} collectible={collectible} />
                ))}
                
                {collectibles.length > 5 && !showAll && (
                    <button
                        onClick={() => setShowAll(true)}
                        className="w-12 h-12 rounded-xl bg-muted hover:bg-muted/80 flex items-center justify-center text-sm font-medium text-muted-foreground transition-colors"
                    >
                        +{collectibles.length - 5}
                    </button>
                )}
            </div>

            {showAll && collectibles.length > 5 && (
                <button
                    onClick={() => setShowAll(false)}
                    className="text-xs text-muted-foreground hover:text-foreground transition-colors"
                >
                    Show less
                </button>
            )}
        </div>
    );
}

function CollectibleBadge({ collectible }: { collectible: Collectible }) {
    const [showTooltip, setShowTooltip] = useState(false);

    return (
        <div 
            className="relative group"
            onMouseEnter={() => setShowTooltip(true)}
            onMouseLeave={() => setShowTooltip(false)}
        >
            <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-amber-100 to-amber-200 dark:from-amber-900/30 dark:to-amber-800/20 border border-amber-200 dark:border-amber-800 flex items-center justify-center text-2xl shadow-sm hover:shadow-md hover:scale-105 transition-all cursor-pointer">
                {collectible.collectibleIcon || '🏆'}
            </div>

            {/* Tooltip */}
            {showTooltip && (
                <div className="absolute bottom-full left-1/2 -translate-x-1/2 mb-2 w-48 p-3 bg-card border border-border rounded-xl shadow-lg z-50 animate-in fade-in duration-200">
                    <p className="font-bold text-sm">{collectible.collectibleName}</p>
                    <p className="text-xs text-muted-foreground mt-1">{collectible.description}</p>
                    <p className="text-[10px] text-muted-foreground mt-2">
                        Earned {new Date(collectible.earnedAt).toLocaleDateString()}
                    </p>
                    <div className="absolute bottom-0 left-1/2 -translate-x-1/2 translate-y-1/2 w-3 h-3 bg-card border-r border-b border-border rotate-45" />
                </div>
            )}
        </div>
    );
}

// Compact version for header/profile
export function CollectiblesIndicator({ userId, compact = false }: { userId: number; compact?: boolean }) {
    const [count, setCount] = useState(0);
    const [latestIcon, setLatestIcon] = useState<string | null>(null);

    useEffect(() => {
        const fetchCount = async () => {
            try {
                const res = await fetch(`/api/collectibles?userId=${userId}`);
                const data = await res.json();
                setCount((data.earned || []).length);
                if (data.earned?.length > 0) {
                    setLatestIcon(data.earned[0].collectibleIcon);
                }
            } catch (error) {
                console.error('Error fetching collectible count:', error);
            }
        };
        fetchCount();
    }, [userId]);

    if (count === 0) return null;

    if (compact) {
        return (
            <div className="flex items-center gap-1 px-2 py-1 bg-amber-50 dark:bg-amber-900/20 rounded-lg">
                <Trophy className="w-3 h-3 text-amber-600" />
                <span className="text-xs font-bold text-amber-700 dark:text-amber-400">{count}</span>
            </div>
        );
    }

    return (
        <div className="flex items-center gap-2 px-3 py-2 bg-gradient-to-r from-amber-50 to-orange-50 dark:from-amber-900/20 dark:to-orange-900/10 rounded-xl border border-amber-200 dark:border-amber-800">
            {latestIcon && <span className="text-xl">{latestIcon}</span>}
            <div className="flex flex-col">
                <span className="text-xs font-bold text-amber-700 dark:text-amber-400">
                    {count} Badge{count !== 1 ? 's' : ''}
                </span>
                <span className="text-[10px] text-amber-600/70 dark:text-amber-500/70">Collected</span>
            </div>
        </div>
    );
}
