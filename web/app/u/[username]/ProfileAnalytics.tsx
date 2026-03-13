"use client";

import React, { useEffect, useState } from 'react';
import { usePaginationStore } from '@/shared/stores/problems/pagination';
import { useTutorialStore } from "@/shared/stores/tutorial-store";
import { ActionableStats } from '@/user-analytics/components/d3/ActionableStats';
import { TopicQuadrantChart } from '@/features/user-analytics/components/d3/TopicQuadrantChart';
import { TestTubeDonut } from '@/features/user-analytics/components/d3/TestTubeDonut';
import { OutcomeTimeDistribution } from '@/features/user-analytics/components/d3/OutcomeTimeDistribution';
import { SectionDistributionDonut } from '@/features/user-analytics/components/d3/SectionDistributionDonut';
import { MockDashboard } from '@/features/user-analytics/components/d3/MockDashboard/MockDashboard';
import { SkillBarChart } from '@/features/user-analytics/components/d3/SkillBarChart';
import { ActivityHeatmap } from '@/features/user-analytics/components/d3/ActivityHeatmap';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/shared/components/ui/card";
import { Loader2, ChevronDown } from 'lucide-react';
import { Checkbox } from "@/shared/components/ui/checkbox";
import { Label } from "@/shared/components/ui/label";
import { examSectionService } from '@/features/exam-management/services/exam-section-service';
import {
    Select,
    SelectContent,
    SelectItem,
    SelectTrigger,
    SelectValue,
} from "@/shared/components/ui/select";
import { Button } from "@/shared/components/ui/button";

interface ProfileAnalyticsProps {
    username: string;
    initialData: any;
}

export function ProfileAnalytics({ username, initialData }: ProfileAnalyticsProps) {
    const { examName } = usePaginationStore();
    const [data, setData] = useState(initialData);
    const [isLoading, setIsLoading] = useState(false);
    const [isFirstLoad, setIsFirstLoad] = useState(true);
    const [selectedSection, setSelectedSection] = useState<string>("quants");
    const [includeMock, setIncludeMock] = useState<boolean>(false);

    const availableSections = React.useMemo(() => {
        return examSectionService.getTabPropertiesForExam(examName);
    }, [examName]);

    useEffect(() => {
        if (isFirstLoad) {
            setIsFirstLoad(false);
            return;
        }

        const fetchAnalytics = async () => {
            setIsLoading(true);
            try {
                const sectionParam = selectedSection !== "All" ? `&section=${selectedSection}` : "";
                const mockParam = `&includeMock=${includeMock}`;
                const res = await fetch(`/api/analytics/profile/${username}?exam=${examName}${sectionParam}${mockParam}`);
                if (res.ok) {
                    const newData = await res.json();
                    setData(newData);
                }
            } catch (error) {
                console.error("Failed to fetch analytics:", error);
            } finally {
                setIsLoading(false);
            }
        };


        fetchAnalytics();
    }, [examName, username, isFirstLoad, selectedSection, includeMock]);

    const { pageTours, startTour, isTourRunning } = useTutorialStore();

    useEffect(() => {
        if (!pageTours.profile && !isTourRunning && !isLoading && !isFirstLoad) {
            const timer = setTimeout(() => startTour("profile"), 1000);
            return () => clearTimeout(timer);
        }
    }, [pageTours.profile, isTourRunning, isLoading, isFirstLoad, startTour]);

    const analytics = data.analytics;

    return (
        <div className="space-y-6 relative">
            {isLoading && (
                <div className="absolute inset-0 bg-background/50 backdrop-blur-[1px] z-10 flex items-center justify-center rounded-xl transition-all">
                    <Loader2 className="w-8 h-8 animate-spin text-primary opacity-50" />
                </div>
            )}

            {/* Top Row: Distribution & Activity */}
            <div className="grid grid-cols-1 lg:grid-cols-[350px_1fr] gap-6">
                <Card className="border-primary/5 flex flex-col">
                    <CardHeader className="pb-2">
                        <CardTitle className="text-base">Focus Distribution</CardTitle>
                        <CardDescription className="text-xs">Attempts by Exam Section</CardDescription>
                    </CardHeader>
                    <CardContent className="flex-1 flex items-center justify-center p-0 pb-4">
                        <SectionDistributionDonut data={analytics.sectionDistribution || []} />
                    </CardContent>
                </Card>

                <div data-tour="profile-heatmap">
                    <ActivityHeatmap data={analytics.heatmap} joinDate={data.user?.joinDate} />
                </div>
            </div>

            {/* Filters & Controls Row */}
            <Card className="bg-primary/[0.02] border-primary/10">
                <CardContent className="py-4 flex flex-wrap items-center justify-between gap-4">
                    <div className="flex flex-col gap-1">
                        <h2 className="text-xl font-bold tracking-tight">Analytics Dashboard</h2>
                        <p className="text-xs text-muted-foreground italic">Filter your performance data by exam section and source.</p>
                    </div>

                    <div className="flex items-center gap-6">
                        <div className="flex flex-col gap-1.5">
                            <Label className="text-[10px] font-bold uppercase tracking-wider opacity-60">Exam Section</Label>
                            <Select value={selectedSection} onValueChange={setSelectedSection}>
                                <SelectTrigger className="w-[160px] h-9 text-sm capitalize bg-background">
                                    <SelectValue placeholder="Select Section" />
                                </SelectTrigger>
                                <SelectContent>
                                    {availableSections.filter(s => s.toLowerCase() !== "all").map((section) => (
                                        <SelectItem
                                            key={section}
                                            value={section}
                                            className="capitalize text-sm"
                                        >
                                            {section}
                                        </SelectItem>
                                    ))}
                                </SelectContent>
                            </Select>
                        </div>

                        <div className="flex flex-col gap-2 items-start mt-4">
                            <div className="flex items-center space-x-2">
                                <Checkbox
                                    id="include-mock"
                                    checked={includeMock}
                                    onCheckedChange={(checked) => setIncludeMock(!!checked)}
                                    className="data-[state=checked]:bg-primary data-[state=checked]:border-primary"
                                />
                                <Label
                                    htmlFor="include-mock"
                                    className="text-xs font-semibold cursor-pointer select-none"
                                >
                                    Include Mock Data
                                </Label>
                            </div>
                        </div>
                    </div>
                </CardContent>
            </Card>

            {/* Top Row: Problems & Skills */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                <div className="lg:col-span-1">
                    <Card className="h-full flex flex-col">
                        <CardHeader>
                            <CardTitle className="text-lg">Problems</CardTitle>
                            <CardDescription>Difficulty Breakdown</CardDescription>
                        </CardHeader>
                        <CardContent className="flex-1 flex flex-col justify-start items-center pt-10 pb-6">
                            <TestTubeDonut data={analytics.difficulty} />
                        </CardContent>
                    </Card>
                </div>
                <div className="lg:col-span-2">
                    <Card className="h-full flex flex-col">
                        <CardHeader className="pb-2">
                            <CardTitle className="text-lg">Skill Breakdown</CardTitle>
                            <CardDescription>Topic Specific Performance</CardDescription>
                        </CardHeader>
                        <CardContent className="flex-1 min-h-[400px]">
                            <SkillBarChart data={analytics.skills} />
                        </CardContent>
                    </Card>
                </div>
            </div>

            {/* Actionable Insights Row */}
            <ActionableStats skills={analytics.skills} />

            {/* Deep Analysis Section: Efficiency & Time */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <Card className="border-primary/5">
                    <CardContent className="pt-8">
                        <TopicQuadrantChart data={analytics.skills} />
                    </CardContent>
                </Card>

                <Card className="border-primary/5">
                    <CardContent className="pt-8 h-full">
                        <OutcomeTimeDistribution data={analytics.timeAnalysis} />
                    </CardContent>
                </Card>
            </div>

            {/* Mock Performance Section */}
            <MockDashboard username={username} examName={examName} />
        </div>
    );
}
