import { NextRequest, NextResponse } from 'next/server';
import { prisma } from "@/shared/lib/configs/prisma";
import { getUserIdFromRequest } from "@/shared/lib/utils/auth";

// POST /api/feedback/question - Submit feedback for a question
export async function POST(req: NextRequest) {
    try {
        const body = await req.json();
        const { questionId, rating, comment, isHelpful } = body;
        // Use server-side auth — don't trust client-sent userId
        const userId = await getUserIdFromRequest(req);

        // Validate rating
        if (!rating || rating < 1 || rating > 10) {
            return NextResponse.json({ error: 'Rating must be between 1 and 10' }, { status: 400 });
        }

        // Create feedback
        const feedback = await prisma.questionFeedback.create({
            data: {
                questionId: parseInt(questionId),
                userId: userId ? parseInt(userId) : null,
                rating,
                comment,
                isHelpful
            }
        });

        // Calculate quality metrics for this question
        await updateQuestionQualityMetrics(parseInt(questionId));

        // Check if user earns a collectible
        const collectibleReward = await checkAndAwardCollectible(userId ? parseInt(userId) : null);

        return NextResponse.json({
            success: true,
            feedback,
            reward: collectibleReward
        });

    } catch (error) {
        console.error('Error submitting feedback:', error);
        return NextResponse.json({ error: 'Failed to submit feedback' }, { status: 500 });
    }
}

// GET /api/feedback/question - Get feedback stats for a question
export async function GET(req: NextRequest) {
    try {
        const { searchParams } = new URL(req.url);
        const questionId = searchParams.get('questionId');

        if (!questionId) {
            return NextResponse.json({ error: 'Question ID required' }, { status: 400 });
        }

        const metrics = await prisma.questionQualityMetrics.findUnique({
            where: { questionId: parseInt(questionId) }
        });

        const recentFeedback = await prisma.questionFeedback.findMany({
            where: { questionId: parseInt(questionId) },
            orderBy: { createdAt: 'desc' },
            take: 10
        });

        return NextResponse.json({
            metrics,
            recentFeedback
        });

    } catch (error) {
        console.error('Error fetching feedback:', error);
        return NextResponse.json({ error: 'Failed to fetch feedback' }, { status: 500 });
    }
}

// Helper: Update quality metrics for a question
async function updateQuestionQualityMetrics(questionId: number) {
    const feedbacks = await prisma.questionFeedback.findMany({
        where: { questionId }
    });

    if (feedbacks.length === 0) return;

    const ratings = feedbacks.map(f => f.rating);
    const avgRating = ratings.reduce((a, b) => a + b, 0) / ratings.length;
    
    // Calculate variance
    const squaredDiffs = ratings.map(r => Math.pow(r - avgRating, 2));
    const variance = squaredDiffs.reduce((a, b) => a + b, 0) / ratings.length;

    // Calculate quality score (higher = better, penalize low variance)
    const qualityScore = avgRating * (1 - (variance / 100)); // Penalize high variance

    await prisma.questionQualityMetrics.upsert({
        where: { questionId },
        update: {
            avgRating,
            ratingCount: ratings.length,
            variance,
            qualityScore,
            lastCalculatedAt: new Date()
        },
        create: {
            questionId,
            avgRating,
            ratingCount: ratings.length,
            variance,
            qualityScore
        }
    });
}

// Helper: Check and award collectibles
async function checkAndAwardCollectible(userId: number | null) {
    if (!userId) return null;

    // Check different collectible triggers
    const userFeedbacks = await prisma.questionFeedback.findMany({
        where: { userId }
    });

    if (userFeedbacks.length === 0) return null;

    // Check for "Quality Hunter" - provided high ratings consistently
    const highRatingCount = userFeedbacks.filter(f => f.rating >= 8).length;
    if (highRatingCount >= 5) {
        const existing = await prisma.userCollectible.findFirst({
            where: { userId, collectibleType: 'quality_hunter' }
        });
        if (!existing) {
            const collectible = await prisma.userCollectible.create({
                data: {
                    userId,
                    collectibleType: 'quality_hunter',
                    collectibleName: 'Quality Hunter',
                    collectibleIcon: '🎯',
                    description: 'Rated 5+ questions as high quality'
                }
            });
            return collectible;
        }
    }

    // Check for "Feedback Hero" - provided 10+ feedbacks
    if (userFeedbacks.length >= 10) {
        const existing = await prisma.userCollectible.findFirst({
            where: { userId, collectibleType: 'feedback_hero' }
        });
        if (!existing) {
            const collectible = await prisma.userCollectible.create({
                data: {
                    userId,
                    collectibleType: 'feedback_hero',
                    collectibleName: 'Feedback Hero',
                    collectibleIcon: '⭐',
                    description: 'Provided 10+ question feedbacks'
                }
            });
            return collectible;
        }
    }

    // Check for "Honest Critic" - provided 5+ low ratings (helpful for improvement)
    const lowRatingCount = userFeedbacks.filter(f => f.rating <= 4).length;
    if (lowRatingCount >= 5) {
        const existing = await prisma.userCollectible.findFirst({
            where: { userId, collectibleType: 'honest_critic' }
        });
        if (!existing) {
            const collectible = await prisma.userCollectible.create({
                data: {
                    userId,
                    collectibleType: 'honest_critic',
                    collectibleName: 'Honest Critic',
                    collectibleIcon: '🔍',
                    description: 'Helped identify 5+ low-quality questions'
                }
            });
            return collectible;
        }
    }

    return null;
}
