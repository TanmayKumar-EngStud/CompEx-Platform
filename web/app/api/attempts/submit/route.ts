// API Route: Submit Question Attempt with Bot Protection
// POST /api/attempts/submit

import { NextRequest, NextResponse } from 'next/server';
import { jose } from '@/lib/jwt';
import { prisma } from '@/lib/prisma';
import { BotDetectionService } from '@/features/bot-protection/bot-detection';
import { checkQuestionRateLimit, getRateLimitHeaders } from '@/features/bot-protection/rate-limiter';

export async function POST(request: NextRequest) {
  try {
    // 1. Get user from JWT
    const token = request.cookies.get('token')?.value;
    if (!token) {
      return NextResponse.json(
        { error: 'Authentication required' },
        { status: 401 }
      );
    }

    const payload = await jose.jwtVerify(token);
    const userId = payload.userId as number;

    // 2. Check rate limiting
    const rateLimit = checkQuestionRateLimit(userId.toString());
    if (!rateLimit.allowed) {
      return NextResponse.json(
        { 
          error: 'Too many questions. Please wait before answering more.',
          retryAfter: Math.ceil((rateLimit.resetTime - Date.now()) / 1000),
        },
        { 
          status: 429,
          headers: getRateLimitHeaders(rateLimit),
        }
      );
    }

    // 3. Parse request body
    const body = await request.json();
    const { 
      questionId, 
      selectedOptions, 
      timeTakenSeconds,
      sessionId,
      // Honeypot field - if filled, it's a bot
      website_url,
    } = body;

    // 4. Check honeypot (bot detection)
    if (website_url && website_url.length > 0) {
      // Bot detected! Log and reject
      await BotDetectionService.analyzeAttempt({
        userId,
        questionId,
        timeTakenSeconds,
        ip: request.headers.get('x-forwarded-for') || 'unknown',
      });

      return NextResponse.json(
        { error: 'Submission rejected. Please try again.' },
        { status: 403 }
      );
    }

    // 5. Validate minimum time (prevent instant answers)
    const MIN_TIME = 10; // 10 seconds minimum
    if (timeTakenSeconds && timeTakenSeconds < MIN_TIME) {
      return NextResponse.json(
        { 
          error: `You answered too fast! Please spend at least ${MIN_TIME} seconds on each question.`,
          requiresChallenge: true,
        },
        { status: 429 }
      );
    }

    // 6. Run bot detection analysis
    const botAnalysis = await BotDetectionService.analyzeAttempt({
      userId,
      questionId,
      timeTakenSeconds,
      sessionId,
      ip: request.headers.get('x-forwarded-for') || undefined,
    });

    if (botAnalysis.recommendedAction === 'block') {
      return NextResponse.json(
        { 
          error: 'Suspicious activity detected. Please verify you are human.',
          requiresHumanVerification: true,
          challenge: BotDetectionService.generateChallenge(),
        },
        { status: 403 }
      );
    }

    // 7. Save the attempt
    const attempt = await prisma.userattempts.create({
      data: {
        userid: userId,
        problemid: questionId,
        timetaken: `${timeTakenSeconds || 0} seconds`,
        attemptdate: new Date(),
        iscorrect: selectedOptions?.some((opt: number) => opt === 1) || false,
      },
    });

    // 8. Return success with analysis
    return NextResponse.json({
      success: true,
      attemptId: attempt.attemptid,
      isBot: botAnalysis.isBot,
      botScore: botAnalysis.score,
      rateLimit: {
        remaining: rateLimit.remaining,
        resetAt: new Date(rateLimit.resetTime).toISOString(),
      },
    }, {
      headers: getRateLimitHeaders(rateLimit),
    });

  } catch (error) {
    console.error('Error submitting attempt:', error);
    return NextResponse.json(
      { error: 'Failed to submit attempt' },
      { status: 500 }
    );
  }
}
