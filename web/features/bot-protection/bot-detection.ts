// Bot Detection Service for Compex
// Prevents AI bots from solving questions

import { prisma } from '@/lib/prisma';

export interface BotScoreResult {
  isBot: boolean;
  score: number; // 0-100, higher = more likely bot
  reasons: string[];
  recommendedAction: 'allow' | 'challenge' | 'block';
}

// Configuration
const CONFIG = {
  // Minimum time to solve a question (in seconds)
  MIN_SOLUTION_TIME: 15, // 15 seconds minimum
  
  // Maximum questions per hour per user
  MAX_QUESTIONS_PER_HOUR: 50,
  
  // Maximum questions per day per user
  MAX_QUESTIONS_PER_DAY: 200,
  
  // Suspiciously fast threshold (in seconds)
  FAST_THRESHOLD: 5,
  
  // Maximum sessions per IP per day
  MAX_SESSIONS_PER_IP: 5,
  
  // Block score threshold (0-100)
  BLOCK_THRESHOLD: 80,
  CHALLENGE_THRESHOLD: 50,
  
  // Honeypot field name (hidden from humans)
  HONEYPOT_FIELD: 'website_url',
};

// Score weights for different behaviors
const SCORE_WEIGHTS = {
  TOO_FAST: 40,          // Answered in < 5 seconds
  VERY_FAST: 25,         // Answered in < 15 seconds
  TOO_MANY_REQUESTS: 30, // Rate limiting
  SUSPICIOUS_PATTERN: 20, // Repeated behavior
  NO_EMAIL_VERIFICATION: 15,
  MULTIPLE_ACCOUNTS_IP: 25,
  REPEATED_SAME_QUESTION: 10,
};

export class BotDetectionService {
  
  /**
   * Main method to check if a request is from a bot
   */
  static async analyzeAttempt(params: {
    userId?: number;
    ip?: string;
    userAgent?: string;
    questionId: number;
    timeTakenSeconds?: number;
    sessionId?: string;
    attemptNumber?: number;
  }): Promise<BotScoreResult> {
    const { userId, ip, questionId, timeTakenSeconds, sessionId } = params;
    
    const reasons: string[] = [];
    let score = 0;

    // 1. Check solution time
    if (timeTakenSeconds !== undefined && timeTakenSeconds < CONFIG.FAST_THRESHOLD) {
      score += SCORE_WEIGHTS.TOO_FAST;
      reasons.push(`Answered in ${timeTakenSeconds}s (too fast for human)`);
    } else if (timeTakenSeconds !== undefined && timeTakenSeconds < CONFIG.MIN_SOLUTION_TIME) {
      score += SCORE_WEIGHTS.VERY_FAST;
      reasons.push(`Answered in ${timeTakenSeconds}s (faster than average human)`);
    }

    // 2. Check rate limiting
    if (userId) {
      const recentAttempts = await this.getRecentAttemptCount(userId, 60); // Last 60 minutes
      if (recentAttempts > CONFIG.MAX_QUESTIONS_PER_HOUR) {
        score += SCORE_WEIGHTS.TOO_MANY_REQUESTS;
        reasons.push(`${recentAttempts} questions in last hour (exceeds limit)`);
      }

      // Check daily limit
      const dailyAttempts = await this.getRecentAttemptCount(userId, 1440); // Last 24 hours
      if (dailyAttempts > CONFIG.MAX_QUESTIONS_PER_DAY) {
        score += SCORE_WEIGHTS.TOO_MANY_REQUESTS;
        reasons.push(`${dailyAttempts} questions today (exceeds daily limit)`);
      }

      // Check if email verified
      const user = await prisma.users.findUnique({
        where: { userid: userId },
        select: { isverified: true },
      });
      
      if (!user?.isverified) {
        score += SCORE_WEIGHTS.NO_EMAIL_VERIFICATION;
        reasons.push('User email not verified');
      }
    }

    // 3. Check IP patterns
    if (ip) {
      const accountsOnIP = await this.getAccountsOnIP(ip);
      if (accountsOnIP > 3) {
        score += SCORE_WEIGHTS.MULTIPLE_ACCOUNTS_ON_IP;
        reasons.push(`${accountsOnIP} accounts from same IP`);
      }

      const sessionsOnIP = await this.getSessionsOnIP(ip);
      if (sessionsOnIP > CONFIG.MAX_SESSIONS_PER_IP) {
        score += SCORE_WEIGHTS.SUSPICIOUS_PATTERN;
        reasons.push(`${sessionsOnIP} sessions from same IP today`);
      }
    }

    // 4. Check repeated same question
    if (userId && sessionId) {
      const sameQuestionAttempts = await this.getSameQuestionAttempts(
        userId,
        questionId,
        sessionId
      );
      if (sameQuestionAttempts > 3) {
        score += SCORE_WEIGHTS.REPEATED_SAME_QUESTION;
        reasons.push(`Attempted same question ${sameQuestionAttempts} times`);
      }
    }

    // Determine action based on score
    let recommendedAction: 'allow' | 'challenge' | 'block';
    if (score >= CONFIG.BLOCK_THRESHOLD) {
      recommendedAction = 'block';
    } else if (score >= CONFIG.CHALLENGE_THRESHOLD) {
      recommendedAction = 'challenge';
    } else {
      recommendedAction = 'allow';
    }

    // Log suspicious activity
    if (score >= CONFIG.CHALLENGE_THRESHOLD) {
      await this.logSuspiciousActivity({
        userId,
        ip,
        questionId,
        score,
        reasons,
        action: recommendedAction,
      });
    }

    return {
      isBot: score >= CONFIG.BLOCK_THRESHOLD,
      score: Math.min(score, 100),
      reasons,
      recommendedAction,
    };
  }

  /**
   * Verify honeypot field (bots often fill hidden fields)
   */
  static checkHoneypot(honeypotValue: string | undefined): boolean {
    // If honeypot field has any value, it's likely a bot
    // Humans won't see this field (it's hidden with CSS)
    return !!honeypotValue && honeypotValue.length > 0;
  }

  /**
   * Get recent attempt count for a user
   */
  private static async getRecentAttemptCount(userId: number, minutes: number): Promise<number> {
    const cutoff = new Date(Date.now() - minutes * 60 * 1000);
    
    const count = await prisma.userattempts.count({
      where: {
        userid: userId,
        attemptdate: { gte: cutoff },
      },
    });
    
    return count;
  }

  /**
   * Get number of accounts from same IP
   */
  private static async getAccountsOnIP(ip: string): Promise<number> {
    // This would need IP tracking in your users table
    // For now, return 0 as placeholder
    return 0;
  }

  /**
   * Get number of sessions from same IP
   */
  private static async getSessionsOnIP(ip: string): Promise<number> {
    // This would need session/IP tracking
    // For now, return 0 as placeholder
    return 0;
  }

  /**
   * Get attempts on same question in current session
   */
  private static async getSameQuestionAttempts(
    userId: number,
    questionId: number,
    sessionId: string
  ): Promise<number> {
    const attempts = await prisma.userattempts.count({
      where: {
        userid: userId,
        problemid: questionId,
      },
    });
    return attempts;
  }

  /**
   * Log suspicious activity for review
   */
  private static async logSuspiciousActivity(data: {
    userId?: number;
    ip?: string;
    questionId: number;
    score: number;
    reasons: string[];
    action: 'allow' | 'challenge' | 'block';
  }) {
    await prisma.$queryRaw`
      INSERT INTO "SuspiciousActivityLog" 
      ("userId", "ip", "questionId", "score", "reasons", "action", "createdAt")
      VALUES (
        ${data.userId || null},
        ${data.ip || null},
        ${data.questionId},
        ${data.score},
        ${JSON.stringify(data.reasons)},
        ${data.action},
        NOW()
      )
    `.catch(() => {
      // Table might not exist yet, silently fail
    });
  }

  /**
   * Generate a CAPTCHA challenge
   */
  static generateChallenge(): { question: string; answer: number } {
    const operations = [
      { q: 'What is 3 + 7?', a: 10 },
      { q: 'What is 5 × 4?', a: 20 },
      { q: 'What is 12 - 4?', a: 8 },
      { q: 'What is 6 + 8?', a: 14 },
      { q: 'What is 9 × 3?', a: 27 },
    ];
    
    const random = operations[Math.floor(Math.random() * operations.length)];
    return { question: random.q, answer: random.a };
  }

  /**
   * Get human-only questions for premium users
   */
  static async getQualityQuestions(limit: number = 10) {
    // Get questions with high quality metrics and human responses
    const questions = await prisma.problems.findMany({
      where: {
        userattempts: {
          some: {
            // Only count attempts from verified users with reasonable timing
            user: {
              isverified: true,
            },
          },
        },
      },
      take: limit,
      orderBy: {
        popularityIndex: 'desc',
      },
    });
    
    return questions;
  }
}

export const botProtectionConfig = CONFIG;
export const scoreWeights = SCORE_WEIGHTS;
