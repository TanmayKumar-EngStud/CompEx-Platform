// Bot Protection Module Exports
export { BotDetectionService, botProtectionConfig, scoreWeights } from './bot-detection';
export { 
  checkRateLimit, 
  checkQuestionRateLimit, 
  checkFeedbackRateLimit,
  checkApiRateLimit,
  getRateLimitHeaders,
  getUserRateLimitStatus,
  type RateLimitResult,
  type RateLimitType,
} from './rate-limiter';
export { HoneypotField, honeypotStyles } from './honeypot';
export { 
  runBotProtectionMigrations,
  createSuspiciousActivityLogTable,
  createUserSessionTrackingTable,
  createBlockedIPsTable,
  insertDefaultRewardConfigs,
} from './schema-migrations';
