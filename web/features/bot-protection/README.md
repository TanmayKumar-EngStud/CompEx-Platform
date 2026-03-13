# 🤖 Compex Bot Protection System

Comprehensive protection against AI bots solving questions on your platform.

## Overview

This system prevents bots from:
- Solving questions faster than humans can
- Submitting feedback at scale
- Creating multiple accounts from same IP
- Abusing your API endpoints

## Features

### 1. Time-Based Detection
- Real humans need 2-10 minutes per question
- Bots answer in < 5 seconds
- **Action**: Block or challenge suspicious attempts

### 2. Rate Limiting
| Endpoint | Limit |
|----------|-------|
| Question attempts | 50/hour, 200/day |
| Feedback submission | Unlimited but tracked |
| General API | 30/minute |

### 3. Email Verification Required
- Users must verify email before submitting quality feedback
- Unverified users get flagged for review
- Reduces fake/spam accounts

### 4. Honeypot Traps
- Invisible form fields that humans never see
- Bots automatically fill them
- Instant detection and blocking

### 5. IP & Session Tracking
- Track multiple accounts per IP
- Detect suspicious patterns
- Block repeat offenders

## Files

```
features/bot-protection/
├── bot-detection.ts      # Main bot detection service
├── rate-limiter.ts       # Rate limiting middleware
├── honeypot.tsx          # Invisible trap component
├── schema-migrations.ts  # Database tables
└── README.md             # This file
```

## Usage

### Basic Bot Check

```typescript
import { BotDetectionService } from '@/features/bot-protection/bot-detection';

const result = await BotDetectionService.analyzeAttempt({
  userId: 123,
  questionId: 456,
  timeTakenSeconds: 45,
  ip: '192.168.1.1',
  sessionId: 'abc123',
});

if (result.recommendedAction === 'block') {
  return { error: 'Bot detected!' };
}
```

### Rate Limiting

```typescript
import { checkQuestionRateLimit, getRateLimitHeaders } from '@/features/bot-protection/rate-limiter';

const rateLimit = checkQuestionRateLimit(userId.toString());
if (!rateLimit.allowed) {
  return NextResponse.json(
    { error: 'Too many questions' },
    { status: 429, headers: getRateLimitHeaders(rateLimit) }
  );
}
```

### Honeypot in Forms

```tsx
import { HoneypotField } from '@/features/bot-protection/honeypot';

<form>
  <HoneypotField 
    name="website_url" 
    onBotDetected={() => formRef.current?.reset()} 
  />
  {/* Other form fields... */}
</form>
```

### API Route Integration

```typescript
// app/api/attempts/submit/route.ts
import { BotDetectionService } from '@/features/bot-protection/bot-detection';

// All the protection is built into the route!
```

## Admin Dashboard

Access bot protection analytics:

```
GET /api/admin/bot-protection/stats?hours=24
```

Returns:
```json
{
  "userStats": {
    "total": 1000,
    "verified": 750,
    "verificationRate": "75.0"
  },
  "attemptStats": {
    "total": 5000,
    "veryFast": 50,
    "veryFastPercentage": "1.00"
  },
  "botDetection": {
    "blocked": 25,
    "challenged": 100,
    "avgScore": "45.5"
  },
  "recommendations": [
    "🔴 CRITICAL: Only 75% of users are verified..."
  ]
}
```

## Database Tables

Run migrations to create:

| Table | Purpose |
|-------|---------|
| `SuspiciousActivityLog` | Track all flagged activities |
| `UserSessionLog` | Track sessions and IPs |
| `BlockedIPs` | Block repeat offender IPs |

### Run Migrations

```typescript
// Run once
import { runBotProtectionMigrations } from '@/features/bot-protection/schema-migrations';

await runBotProtectionMigrations();
```

## Configuration

Edit `bot-detection.ts` to customize:

```typescript
const CONFIG = {
  MIN_SOLUTION_TIME: 15,        // Minimum seconds per question
  MAX_QUESTIONS_PER_HOUR: 50,   // Hourly limit
  MAX_QUESTIONS_PER_DAY: 200,   // Daily limit
  FAST_THRESHOLD: 5,            // Suspiciously fast threshold
  BLOCK_THRESHOLD: 80,          // Score to block (0-100)
  CHALLENGE_THRESHOLD: 50,      // Score to challenge
};
```

## Scoring System

| Behavior | Score |
|----------|-------|
| Answered in < 5 seconds | +40 |
| Answered in < 15 seconds | +25 |
| Too many requests | +30 |
| Multiple accounts per IP | +25 |
| Email not verified | +15 |
| Repeated same question | +10 |

**Actions:**
- **Block**: Score ≥ 80
- **Challenge**: Score ≥ 50
- **Allow**: Score < 50

## CAPTCHA Challenge

When challenged, users see a simple math question:

```
What is 3 + 7? = [____]
```

## Monitoring

### Check Recent Suspicious Activity

```sql
SELECT * FROM "SuspiciousActivityLog" 
ORDER BY "createdAt" DESC 
LIMIT 100;
```

### Blocked IPs

```sql
SELECT * FROM "BlockedIPs" 
WHERE expiresAt > NOW() OR isPermanent = TRUE;
```

## Best Practices

1. **Start strict, relax later** — Better to block real users than let bots in
2. **Monitor daily** — Check `/api/admin/bot-protection/stats` regularly
3. **Require email verification** — Single biggest deterrent
4. **Use honeypot fields** — Zero friction for humans
5. **Log everything** — Evidence for future analysis

## Warning Signs

🚨 **Red Flags:**
- < 50% user verification rate
- > 5% "very fast" attempts
- Same IP with 5+ accounts

✅ **Healthy Signs:**
- > 80% verification rate
- < 2% very fast attempts
- < 10 blocked attempts/day

## Future Improvements

- [ ] Redis for rate limiting (distributed)
- [ ] Machine learning for pattern detection
- [ ] Two-factor authentication for unverified users
- [ ] CAPTCHA service integration (hCaptcha/ReCAPTCHA)
- [ ] VPN/Proxy detection
- [ ] Browser fingerprinting
