
import React from 'react';
import { notFound } from 'next/navigation';
import { getUserAnalytics } from '@/features/user-analytics/services/analytics.service';
import { ActivityHeatmap } from '@/features/user-analytics/components/d3/ActivityHeatmap';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/shared/components/ui/card";
import { ProfileAnalytics } from './ProfileAnalytics';
import { CalendarIcon, Medal, Trophy } from 'lucide-react';
import { format } from 'date-fns';
import Navbar from '@/shared/components/layouts/navbar';
import { UserAvatar } from '@/shared/components/feedback/UserAvatar';

import { getCurrentUser } from '@/shared/lib/utils/auth';
import { EditProfileButton } from './EditProfileButton';
import { GlobalScoreCard } from './GlobalScoreCard';
import { Leaderboard } from './Leaderboard';

interface PageProps {
    params: Promise<{
        username: string;
    }>;
}

export default async function UserProfilePage(props: PageProps) {
    const params = await props.params;
    const { username } = params;

    const decodedUsername = decodeURIComponent(username);

    let data = null;
    try {
        data = await getUserAnalytics(decodedUsername, "GRE") as any;
    } catch (error) {
        console.error("Failed to load user profile:", error);
        // Fallback or specific error component could be triggered here
        // For now, let's treat it as notFound if critical data fails
        notFound();
    }

    const currentUserId = await getCurrentUser();

    if (!data) {
        notFound();
    }

    const { user, analytics } = data;
    const isOwnProfile = currentUserId === user.userid;

    // Calculate total solved from the new array structure
    const totalSolved = analytics.difficulty.reduce((acc: number, curr: any) => acc + curr.correctAttempts, 0);

    return (
        <div className="min-h-screen bg-background">
            <Navbar />
            <div className="container mx-auto py-8 px-4">
                <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">

                    {/* Left Sidebar - User Info */}
                    <div className="lg:col-span-1 space-y-6">
                        <Card data-tour="profile-header">
                            <CardHeader className="flex flex-col items-center">
                                <UserAvatar
                                    username={user.username}
                                    image_url={user.image_url}
                                    size="xl"
                                    className="mb-4"
                                />
                                <CardTitle className="text-2xl">{user.username}</CardTitle>
                                <CardDescription className="flex items-center mt-1 flex-col gap-1">
                                    {user.isVerified && (
                                        <span className="inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-semibold transition-colors focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2 border-transparent bg-secondary text-secondary-foreground hover:bg-secondary/80">
                                            Verified
                                        </span>
                                    )}
                                    <span className="text-xs text-muted-foreground flex items-center mt-1">
                                        <CalendarIcon className="w-3 h-3 mr-1" />
                                        Joined {user.joinDate ? format(new Date(user.joinDate), "MMM yyyy") : "N/A"}
                                    </span>
                                </CardDescription>
                            </CardHeader>
                            <CardContent className="space-y-4">
                                <div className="flex justify-between items-center">
                                    <span className="text-sm font-medium text-muted-foreground">Rank</span>
                                    <span className="text-lg font-bold flex items-center">
                                        <Trophy className="w-4 h-4 mr-1 text-yellow-500" />
                                        {user.rank ? `#${user.rank}` : "Unranked"}
                                    </span>
                                </div>
                                <div className="flex justify-between items-center">
                                    <span className="text-sm font-medium text-muted-foreground">Percentile</span>
                                    <span className="text-lg font-bold">
                                        {user.percentile ? `${Number(user.percentile).toFixed(1)}%` : "-"}
                                    </span>
                                </div>
                                <div className="shrink-0 bg-border h-[1px] w-full my-4" />
                                <div className="space-y-2" data-tour="profile-stats">
                                    <h4 className="text-sm font-semibold">Community Stats</h4>
                                    <div className="flex items-center text-sm text-muted-foreground">
                                        <Medal className="w-4 h-4 mr-2 text-blue-500" />
                                        <span>{totalSolved} Problems Solved</span>
                                    </div>
                                </div>

                                {isOwnProfile && (
                                    <EditProfileButton user={{
                                        userid: user.userid,
                                        username: user.username,
                                        email: user.email,
                                        image_url: user.image_url
                                    }} />
                                )}
                            </CardContent>
                        </Card>

                        {/* Global Performance Scores */}
                        <GlobalScoreCard scores={user.scores} />

                        {/* Pagination Leaderboard */}
                        <Leaderboard currentUsername={decodedUsername} />
                    </div>

                    {/* Right Content - Analytics */}
                    <div className="lg:col-span-3 space-y-6">
                        <ProfileAnalytics username={decodedUsername} initialData={data} />
                    </div>
                </div>
            </div>
        </div>
    );
}
