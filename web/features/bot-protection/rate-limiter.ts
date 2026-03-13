// Rate Limiting Middleware for Compex
// Prevents bot attacks and abuse

import { prisma } from '@/lib/prisma';

// In-memory rate limiting (use Redis in production)
const rateLimitStore = new Map<string, { count: number; resetTime: number }>();

const CONFIG = {
  // Window in milliseconds
  WINDOW_1_MINUTE: 60 * 1000,
  WINDOW_1_HOUR: 60 * 60 * 1000,
  WINDOW_1_DAY: 24 * 60 * 60 * 1000,
  
  // Max requests per window
  MAX_REQUESTS_PER_MINUTE: 30,
  MAX_REQUESTS_PER_HOUR: 200,
  MAX_REQUESTS_PER_DAY: 1000,
  
  // Question answering limits
  MAX_ANSWERS_PER_MINUTE: 10,
  MAX_ANSWERS_PER_HOUR: 50,
  MAX_ANSWERS_PER_DAY: 200,
};

export type RateLimitType = 'general' | 'question' | 'feedback';

export interface RateLimitResult {
  allowed: boolean;
  remaining: number;
  resetTime: number;
  limit: number;
  window: string;
}

/**
 * Check rate limit for a given key
 */
export function checkRateLimit(
  key: string,
  type: RateLimitType = 'general',
  windowMs: number = CONFIG.WINDOW_1_MINUTE,
  maxRequests: number = CONFIG.MAX_REQUESTS_PER_MINUTE
): RateLimitResult {
  const now = Date.now();
  const record = rateLimitStore.get(key);
  
  if (!record || now > record.resetTime) {
    // New or expired window
    rateLimitStore.set(key, {
      count: 1,
      resetTime: now + windowMs,
    });
    return {
      allowed: true,
      remaining: maxRequests - 1,
      resetTime: now + windowMs,
      limit: maxRequests,
      window: `${windowMs / 1000}s`,
    };
  }
  
  if (record.count >= maxRequests) {
    return {
      allowed: false,
      remaining: 0,
      resetTime: record.resetTime,
      limit: maxRequests,
      window: `${windowMs / 1000}s`,
    };
  }
  
  record.count++;
  return {
    allowed: true,
    remaining: maxRequests - record.count,
    resetTime: record.resetTime,
    limit: maxRequests,
    window: `${windowMs / 1000}s`,
  };
}

/**
 * Check question answering rate limit
 */
export function checkQuestionRateLimit(userId: string): RateLimitResult {
  return checkRateLimit(
    `question:${userId}`,
    'question',
    CONFIG.WINDOW_1_HOUR,
    CONFIG.MAX_ANSWERS_PER_HOUR
  );
}

/**
 * Check feedback submission rate limit
 */
export function checkFeedbackRateLimit(userId: string): RateLimitResult {
  return checkRateLimit(
    `feedback:${userId}`,
    'feedback',
    CONFIG.WINDOW_1_DAY,
    CONFIG.MAX_ANSWERS_PER_DAY
  );
}

/**
 * Check general API rate limit
 */
export function checkApiRateLimit(ip: string): RateLimitResult {
  return checkRateLimit(
    `api:${ip}`,
    'general',
    CONFIG.WINDOW_1_MINUTE,
    CONFIG.MAX_REQUESTS_PER_MINUTE
  );
}

/**
 * Get rate limit headers for response
 */
export function getRateLimitHeaders(result: RateLimitResult): Record<string, string> {
  return {
    'X-RateLimit-Limit': result.limit.toString(),
    'X-RateLimit-Remaining': result.remaining.toString(),
    'X-RateLimit-Reset': result.resetTime.toString(),
    'X-RateLimit-Window': result.window,
  };
}

/**
 * Clean up expired rate limit records (call periodically)
 */
export function cleanupRateLimitStore() {
  const now = Date.now();
  for (const [key, record] of rateLimitStore.entries()) {
    if (now > record.resetTime) {
      rateLimitStore.delete(key);
    }
  }
}

/**
 * Get rate limit info for a user (for display)
 */
export async function getUserRateLimitStatus(userId: number) {
  const user = await prisma.users.findUnique({
    where: { userid: userId },
    select: { userid: true },
  });
  
  if (!user) return null;
  
  const hourLimit = checkQuestionRateLimit(userId.toString());
  const dailyLimit = checkRateLimit(
    `question:${userId}`,
    'question',
    CONFIG.WINDOW_1_DAY,
    CONFIG.MAX_ANSWERS_PER_DAY
  );
  
  return {
    hourly: {
      remaining: hourLimit.remaining,
      limit: hourLimit.limit,
      resetAt: new Date(hourLimit.resetTime).toISOString(),
    },
    daily: {
      remaining: dailyLimit.remaining,
      limit: dailyLimit.limit,
      resetAt: new Date(dailyLimit.resetTime).toISOString(),
    },
  };
}
