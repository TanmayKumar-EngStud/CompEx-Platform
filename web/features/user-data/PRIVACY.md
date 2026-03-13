# 🔐 User Data Ownership & Privacy

## Our Commitment to Users

At Compex, we believe **users own their data**. We're building an ethical platform where transparency and trust are the foundation.

---

## What This Means

### 1. Data Portability
Users can:
- **Download** all their data at any time
- **Import** data to restore progress
- **Transfer** data between devices

### 2. No Lock-In
- No proprietary formats (we use standard JSON)
- No hidden data extraction
- No surprise data collection

### 3. Transparency
- Clear about what data we collect
- Explain why we collect it
- Never sell user data

---

## Data Users Own

| Data Type | Description |
|-----------|-------------|
| **Progress** | Questions answered, accuracy scores |
| **Analytics** | Topic performance, learning streaks |
| **Achievements** | Badges, milestones, collectibles |
| **Preferences** | Settings, themes, goals |

## Data We Need (Minimal)

| Data Type | Why We Need It |
|-----------|---------------|
| **Email** | Account verification, password reset |
| **Username** | Display in app |
| **Auth Token** | Secure login |

---

## Privacy Principles

1. **Minimal Collection** - Only collect what's necessary
2. **Secure Storage** - Encrypted at rest
3. **No Third-Party Sales** - User data never sold
4. **GDPR Compliant** - EU data protection standards
5. **Right to Delete** - Users can request account deletion

---

## API Endpoints

### Export Data
```
GET /api/user/export-data
```
Returns user's complete data as JSON file.

### Import Data
```
POST /api/user/import-data
Accepts JSON backup file to restore progress.

Body:
{
  "_format": "compex-user-data-v1",
  ...user data...
}
```

---

## Security Measures

- HTTPS encryption in transit
- Password hashing (bcrypt)
- Session tokens (JWT)
- Rate limiting on data endpoints
- Audit logging for data access

---

## User Rights

Users have the right to:
- ✅ Access their data
- ✅ Correct their data
- ✅ Export their data
- ✅ Delete their data
- ✅ Object to processing
- ✅ Port their data

---

## Contact

For privacy concerns:
- Email: privacy@compex.live
- Subject: Privacy Concern

---

*"Trust is earned through transparency, not assumed through silence."*
