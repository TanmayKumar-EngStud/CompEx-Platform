
"use client";

import React, { useEffect, useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/shared/components/ui/card";
import { MockBoxPlotChart } from './MockBoxPlotChart';
import { MockScatterPlot } from './MockScatterPlot';
import { PercentileTrendChart } from '../PercentileTrendChart';
import { ScoreDistributionChart } from '../ScoreDistributionChart';
import { Loader2 } from 'lucide-react';

interface Props {
    username: string;
    examName: string;
}

export function MockDashboard({ username, examName }: Props) {
    const [data, setData] = useState<any>(null);
    const [isLoading, setIsLoading] = useState(true);

    useEffect(() => {
        const fetchMockAnalytics = async () => {
            setIsLoading(true);
            try {
                const res = await fetch(`/api/analytics/mock/${username}?exam=${examName}`);
                if (res.ok) {
                    const newData = await res.json();
                    setData(newData);
                }
            } catch (error) {
                console.error("Failed to fetch mock analytics:", error);
            } finally {
                setIsLoading(false);
            }
        };

        fetchMockAnalytics();
    }, [username, examName]);

    if (isLoading) {
        return (
            <div className="h-64 flex items-center justify-center">
                <Loader2 className="w-8 h-8 animate-spin opacity-20" />
            </div>
        );
    }

    if (!data || !data.mocks || data.mocks.length === 0) {
        return (
            <Card className="h-64 flex flex-col items-center justify-center text-center opacity-50 border-dashed">
                <span className="text-4xl mb-4">📉</span>
                <p>No mock data available for {examName} yet.</p>
                <p className="text-xs">Take a mock test to see your performance analysis.</p>
            </Card>
        );
    }

    return (
        <div className="space-y-6">
            <Card>
                <CardHeader className="pb-2">
                    <CardTitle className="text-xl">Mock Scoreboard</CardTitle>
                    <CardDescription>
                        Performance analysis relative to the community and mock difficulty.
                    </CardDescription>
                </CardHeader>
                <CardContent className="space-y-8">
                    <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 items-start">
                        <div className="w-full h-full">
                            <MockBoxPlotChart data={data.mocks} />
                        </div>
                        <div className="w-full h-full border-l lg:pl-8">
                            <MockScatterPlot data={data.mocks} />
                        </div>
                    </div>

                    <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 pt-6 border-t">
                        <div className="lg:col-span-1">
                            <PercentileTrendChart data={data.percentileTrend} />
                        </div>
                        <div className="lg:col-span-1 border-l lg:pl-8">
                            <ScoreDistributionChart
                                data={data.latestMockDistribution}
                                userScore={data.mocks[data.mocks.length - 1]?.userScore || 0}
                            />
                        </div>
                    </div>
                </CardContent>
            </Card>
        </div>
    );
}
