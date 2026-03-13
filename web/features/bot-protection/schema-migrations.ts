// Suspicious Activity Log - Database Schema
// Run this to create the tracking table

import { prisma } from '@/lib/prisma';

export async function createSuspiciousActivityLogTable() {
  await prisma.$queryRaw`
    CREATE TABLE IF NOT EXISTS "SuspiciousActivityLog" (
      "id" SERIAL PRIMARY KEY,
      "userId" INTEGER,
      "ip" TEXT,
      "questionId" INTEGER NOT NULL,
      "score" INTEGER NOT NULL,
      "reasons" TEXT NOT NULL,
      "action" TEXT NOT NULL CHECK ("action" IN ('allow', 'challenge', 'block')),
      "createdAt" TIMESTAMP(6) NOT NULL DEFAULT NOW()
    );
    
    CREATE INDEX IF NOT EXISTS "SuspiciousActivityLog_userId_idx" ON "SuspiciousActivityLog"("userId");
    CREATE INDEX IF NOT EXISTS "SuspiciousActivityLog_ip_idx" ON "SuspiciousActivityLog"("ip");
    CREATE INDEX IF NOT EXISTS "SuspiciousActivityLog_createdAt_idx" ON "SuspiciousActivityLog"("createdAt");
  `;
}

// Track user session and IP for rate limiting
export async function createUserSessionTrackingTable() {
  await prisma.$queryRaw`
    CREATE TABLE IF NOT EXISTS "UserSessionLog" (
      "id" SERIAL PRIMARY KEY,
      "userId" INTEGER,
      "sessionId" TEXT NOT NULL,
      "ip" TEXT,
      "userAgent" TEXT,
      "questionCount" INTEGER DEFAULT 0,
      "startedAt" TIMESTAMP(6) NOT NULL DEFAULT NOW(),
      "lastActivityAt" TIMESTAMP(6) NOT NULL DEFAULT NOW()
    );
    
    CREATE INDEX IF NOT EXISTS "UserSessionLog_userId_idx" ON "UserSessionLog"("userId");
    CREATE INDEX IF NOT EXISTS "UserSessionLog_ip_idx" ON "UserSessionLog"("ip");
    CREATE INDEX IF NOT EXISTS "UserSessionLog_sessionId_idx" ON "UserSessionLog"("sessionId");
  `;
}

// Blocked IPs table
export async function createBlockedIPsTable() {
  await prisma.$queryRaw`
    CREATE TABLE IF NOT EXISTS "BlockedIPs" (
      "id" SERIAL PRIMARY KEY,
      "ip" TEXT UNIQUE NOT NULL,
      "reason" TEXT,
      "blockedAt" TIMESTAMP(6) NOT NULL DEFAULT NOW(),
      "expiresAt" TIMESTAMP(6),
      "isPermanent" BOOLEAN DEFAULT FALSE
    );
    
    CREATE INDEX IF NOT EXISTS "BlockedIPs_ip_idx" ON "BlockedIPs"("ip");
    CREATE INDEX IF NOT EXISTS "BlockedIPs_expiresAt_idx" ON "BlockedIPs"("expiresAt");
  `;
}

// Run all migrations
export async function runBotProtectionMigrations() {
  try {
    await createSuspiciousActivityLogTable();
    await createUserSessionTrackingTable();
    await createBlockedIPsTable();
    console.log('✅ Bot protection tables created successfully');
  } catch (error) {
    console.error('❌ Error creating bot protection tables:', error);
    throw error;
  }
}

// Sample data for testing
export async function insertDefaultRewardConfigs() {
  await prisma.$queryRaw`
    INSERT INTO "FeedbackRewardConfig" 
    ("name", "description", "ratingThreshold", "collectibleType", "isActive", "createdAt")
    VALUES 
    ('Quality Hunter', 'Award when user rates 5+ questions as 8+', 8.0, 'quality_hunter', TRUE, NOW()),
    ('Feedback Hero', 'Award when user provides 10+ feedbacks', 0, 'feedback_hero', TRUE, NOW()),
    ('Honest Critic', 'Award when user rates 5+ questions as 4 or below', 4.0, 'honest_critic', TRUE, NOW())
    ON CONFLICT DO NOTHING;
  `;
}
