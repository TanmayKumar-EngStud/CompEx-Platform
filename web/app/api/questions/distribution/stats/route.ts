// API Route: Get Question Distribution Analytics
// GET /api/questions/distribution/stats

import { NextRequest, NextResponse } from 'next/server';
import { prisma } from '@/lib/prisma';
import { QuestionDistributionService } from '@/features/question-distribution/question-distribution';

export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url);
    const sectionId = searchParams.get('sectionId');
    const examTypeId = searchParams.get('examTypeId');
    
    // Get basic analytics from distribution service
    const analytics = await QuestionDistributionService.getDistributionAnalytics();
    
    // Get section breakdown
    const sections = await prisma.sections.findMany({
      select: {
        sectionid: true,
        name: true,
        _count: {
          select: { problems: { where: { isMockQuestion: true } } },
        },
      },
    });
    
    // Get quality distribution
    const qualityRanges = await prisma.problems.groupBy({
      by: ['difficulty'],
      where: {
        isMockQuestion: true,
        ...(sectionId ? { sectionid: parseInt(sectionId) } : {}),
        ...(examTypeId ? { examtypeid: parseInt(examTypeId) } : {}),
      },
      _count: true,
      _avg: {
        popularityIndex: true,
        totalattemptscount: true,
      },
    });
    
    // Get recent additions (last 7 days)
    const weekAgo = new Date(Date.now() - 7 * 24 * 60 * 60 * 1000);
    const recentAdditions = await prisma.problems.count({
      where: {
        isMockQuestion: true,
        addedDate: { gte: weekAgo },
      },
    });
    
    // Get questions needing regeneration
    const needsRegeneration = await prisma.problems.count({
      where: {
        isMockQuestion: true,
        metadata: { path: ['needsRegeneration'], equals: true },
      },
    });
    
    // Calculate recommendations
    const recommendations = this.generateRecommendations(analytics, {
      recentAdditions,
      needsRegeneration,
      totalSections: sections.length,
    });
    
    return NextResponse.json({
      success: true,
      overview: {
        totalQuestions: analytics.total,
        independent: analytics.byType.independent,
        contextual: analytics.byType.contextual,
        ratio: {
          independent: analytics.total > 0 
            ? (analytics.byType.independent / analytics.total * 100).toFixed(1) + '%'
            : '0%',
          contextual: analytics.total > 0 
            ? (analytics.byType.contextual / analytics.total * 100).toFixed(1) + '%'
            : '0%',
        },
      },
      byDifficulty: analytics.byDifficulty,
      bySection: sections.map(s => ({
        id: s.sectionid,
        name: s.name,
        count: s._count.problems,
      })),
      recentActivity: {
        last7Days: recentAdditions,
        needsRegeneration,
      },
      qualityMetrics: qualityRanges.map(q => ({
        difficulty: q.difficulty,
        count: q._count,
        avgPopularity: q._avg.popularityIndex?.toFixed(2) || '0',
        avgAttempts: q._avg.totalattemptscount?.toFixed(0) || '0',
      })),
      recommendations,
      generatedAt: new Date().toISOString(),
    });
    
  } catch (error) {
    console.error('Error getting distribution stats:', error);
    return NextResponse.json(
      { error: 'Failed to get distribution statistics' },
      { status: 500 }
    );
  }
}

// Generate recommendations based on analytics
function generateRecommendations(analytics: any, context: { recentAdditions: number; needsRegeneration: number; totalSections: number }): string[] {
  const recommendations: string[] = [];
  
  // Check balance
  const total = analytics.total;
  if (total === 0) {
    return ['⚠️ No questions in database. Add questions to get started.'];
  }
  
  const independentPct = analytics.byType.independent / total;
  const contextualPct = analytics.byType.contextual / total;
  
  if (independentPct > 0.8) {
    recommendations.push('🟡 Too many independent questions. Consider adding more contextual questions for variety.');
  } else if (independentPct < 0.3) {
    recommendations.push('🟡 Too many contextual questions. Consider adding more independent questions.');
  } else {
    recommendations.push('✅ Good balance between independent and contextual questions.');
  }
  
  // Check difficulty distribution
  const easy = analytics.byDifficulty.find((d: any) => d.level <= 0)?._count || 0;
  const medium = analytics.byDifficulty.find((d: any) => d.level >= 1 && d.level <= 2)?._count || 0;
  const hard = analytics.byDifficulty.find((d: any) => d.level >= 3)?._count || 0;
  
  if (easy / total < 0.1) {
    recommendations.push('🟡 Low on easy questions. New users may struggle.');
  }
  if (hard / total > 0.4) {
    recommendations.push('🟡 High proportion of hard questions. May discourage users.');
  }
  
  // Check recent activity
  if (context.recentAdditions < 10) {
    recommendations.push('📝 Only ' + context.recentAdditions + ' new questions this week. Consider adding more.');
  } else if (context.recentAdditions > 100) {
    recommendations.push('📈 Great progress! ' + context.recentAdditions + ' new questions this week.');
  }
  
  // Check regeneration needs
  if (context.needsRegeneration > 20) {
    recommendations.push('🔄 ' + context.needsRegeneration + ' questions need regeneration. Run Antigravity AI batch.');
  }
  
  // Check section coverage
  if (context.totalSections < 5) {
    recommendations.push('📚 Limited topic coverage. Add questions across more sections.');
  }
  
  return recommendations;
}
