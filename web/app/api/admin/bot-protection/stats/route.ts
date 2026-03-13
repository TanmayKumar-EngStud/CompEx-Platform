// Admin API: Get Bot Detection Analytics
// GET /api/admin/bot-protection/stats

import { NextRequest, NextResponse } from 'next/server';
import { prisma } from '@/lib/prisma';

export async function GET(request: NextRequest) {
  try {
    // Get time range from query params
    const { searchParams } = new URL(request.url);
    const hours = parseInt(searchParams.get('hours') || '24');

    const cutoff = new Date(Date.now() - hours * 60 * 60 * 1000);

    // Get suspicious activity stats
    const suspiciousActivity = await prisma.$queryRaw`
      SELECT 
        COUNT(*) FILTER (WHERE action = 'block') as blocked_count,
        COUNT(*) FILTER (WHERE action = 'challenge') as challenge_count,
        COUNT(*) FILTER (WHERE action = 'allow') as allowed_count,
        AVG(score) FILTER (WHERE createdAt > ${cutoff}) as avg_score,
        COUNT(DISTINCT "userId") FILTER (WHERE createdAt > ${cutoff}) as unique_suspicious_users
      FROM "SuspiciousActivityLog"
      WHERE createdAt > ${cutoff} OR "SuspiciousActivityLog" IS NULL
    `.catch(() => ({ blocked_count: 0, challenge_count: 0, allowed_count: 0, avg_score: 0, unique_suspicious_users: 0 }));

    // Get user verification stats
    const userStats = await prisma.users.aggregate({
      _count: true,
    });

    const verifiedUsers = await prisma.users.count({
      where: { isverified: true },
    });

    // Get attempt stats
    const recentAttempts = await prisma.userattempts.count({
      where: {
        attemptdate: { gte: cutoff },
      },
    });

    // Get very fast attempts (possible bots)
    const fastAttempts = await prisma.$queryRaw`
      SELECT COUNT(*) as count
      FROM "userattempts"
      WHERE "attemptdate" > ${cutoff}
      AND ("timetaken" LIKE '0%' OR "timetaken" LIKE '1%' OR "timetaken" LIKE '2%' OR "timetaken" LIKE '3%' OR "timetaken" LIKE '4%')
    `.catch(() => ({ count: 0 }));

    return NextResponse.json({
      success: true,
      period: `${hours} hours`,
      userStats: {
        total: userStats._count,
        verified: verifiedUsers,
        unverified: userStats._count - verifiedUsers,
        verificationRate: userStats._count > 0 
          ? ((verifiedUsers / userStats._count) * 100).toFixed(1) 
          : '0',
      },
      attemptStats: {
        total: Number(recentAttempts) || 0,
        veryFast: Number(fastAttempts?.count) || 0,
        veryFastPercentage: Number(recentAttempts) > 0
          ? (((Number(fastAttempts?.count) || 0) / Number(recentAttempts)) * 100).toFixed(2)
          : '0',
      },
      botDetection: {
        blocked: Number(suspiciousActivity.blocked_count) || 0,
        challenged: Number(suspiciousActivity.challenge_count) || 0,
        allowed: Number(suspiciousActivity.allowed_count) || 0,
        avgScore: Number(suspiciousActivity.avg_score)?.toFixed(1) || '0',
        uniqueSuspiciousUsers: Number(suspiciousActivity.unique_suspicious_users) || 0,
      },
      recommendations: generateRecommendations({
        verificationRate: userStats._count > 0 ? (verifiedUsers / userStats._count) : 0,
        veryFastPercentage: Number(recentAttempts) > 0 
          ? ((Number(fastAttempts?.count) || 0) / Number(recentAttempts))
          : 0,
        blockedCount: Number(suspiciousActivity.blocked_count) || 0,
      }),
      generatedAt: new Date().toISOString(),
    });

  } catch (error) {
    console.error('Error getting bot protection stats:', error);
    return NextResponse.json(
      { error: 'Failed to get stats' },
      { status: 500 }
    );
  }
}

function generateRecommendations(stats: {
  verificationRate: number;
  veryFastPercentage: number;
  blockedCount: number;
}): string[] {
  const recommendations: string[] = [];

  if (stats.verificationRate < 0.5) {
    recommendations.push('🔴 CRITICAL: Only ' + (stats.verificationRate * 100).toFixed(0) + '% of users are verified. Consider requiring email verification before attempting questions.');
  }

  if (stats.veryFastPercentage > 0.05) {
    recommendations.push('🟡 WARNING: ' + (stats.veryFastPercentage * 100).toFixed(1) + '% of attempts are suspiciously fast. Consider increasing minimum time requirement.');
  }

  if (stats.blockedCount > 10) {
    recommendations.push('🟡 INFO: ' + stats.blockedCount + ' bot attempts blocked recently. System is working correctly.');
  }

  if (stats.verificationRate > 0.8 && stats.veryFastPercentage < 0.02) {
    recommendations.push('🟢 GOOD: User verification rate is high and suspicious attempts are low. Bot protection is effective!');
  }

  return recommendations;
}
