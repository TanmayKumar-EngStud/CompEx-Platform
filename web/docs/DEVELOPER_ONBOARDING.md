# Compex — Developer Onboarding Guide

> Everything a new developer needs to clone, run, and deploy Compex on a Mac.

---

## 1. Prerequisites (Install These First)

| Tool | Install Command | Why |
|---|---|---|
| **Node.js** (v20+) | `brew install node` | Runtime |
| **pnpm** | `npm install -g pnpm` | Package manager (project uses `pnpm`) |
| **Git** | `brew install git` | Version control |
| **PostgreSQL client** | `brew install libpq` | For `psql` CLI (optional, useful for debugging) |

---

## 2. Repository Access

- Get **collaborator access** to the GitHub repo (private repo — owner must invite via GitHub Settings → Collaborators).
- Clone:
  ```bash
  git clone <repo-url>
  cd compex
  pnpm install
  ```

---

## 3. Environment Variables

The project uses **three** env files — none are committed to Git. You must create them manually:

### `.env` (local development database)
```env
DATABASE_URL="postgresql://<user>:<password>@localhost:5433/<dbname>"
SMTP_HOST=smtp.resend.com
SMTP_PORT=587
SMTP_USER=resend
SMTP_PASS=<resend-api-key>
SMTP_SECURE=false
```

### `.env.local` (local overrides & API keys for dev)
```env
JWT_SECRET=<generate-a-random-64-char-hex>
AUTH_SECRET=<generate-a-random-64-char-hex>
OPENAI_API_KEY=<your-openai-key>
DEEPSEEK_API_KEY=<your-deepseek-key>
GOOGLE_AI_STUDIO_KEY=<your-gemini-key>
```

### `.env.production` (production secrets — used for deployment)
```env
DATABASE_URL=<neon-postgres-connection-string>
REDIS_URL=<upstash-redis-url>          # if enabled
JWT_SECRET=<production-jwt-secret>
AUTH_SECRET=<production-auth-secret>
OPENAI_API_KEY=<production-openai-key>
DEEPSEEK_API_KEY=<production-deepseek-key>
GOOGLE_AI_STUDIO_KEY=<production-gemini-key>
SMTP_HOST=smtp.resend.com
SMTP_PORT=587
SMTP_USER=resend
SMTP_PASS=<resend-api-key>
```

> **⚠️ IMPORTANT:** Never commit env files. They are all in `.gitignore`. Share secrets securely (e.g., 1Password, Signal, in-person).

---

## 4. Third-Party Accounts & API Keys to Share/Create

| Service | Purpose | What to share |
|---|---|---|
| **Neon** (neon.tech) | Production PostgreSQL | Connection string, or invite to project |
| **Vercel** | Hosting & deployment | Add as team member on Vercel dashboard |
| **OpenAI** | AI question generation | API key (or create a separate key for her) |
| **DeepSeek** | AI reasoning & chat | API key |
| **Google AI Studio** | Gemini free-tier AI | API key |
| **Resend** (resend.com) | Transactional emails (SMTP) | API key |
| **Upstash** | Redis (if enabled) | Connection URL |
| **Stripe** | Payments (in `package.json`) | API keys (test mode keys for dev) |

> **Tip:** For API keys, it's best to create **separate keys per developer** so you can revoke individually.

---

## 5. Database Setup

### Option A: Use the shared Neon cloud database (easiest)
- Just set `DATABASE_URL` in `.env` to the Neon connection string.
- Run `pnpm prisma generate` to generate the Prisma client.

### Option B: Local PostgreSQL
1. Install: `brew install postgresql@16 && brew services start postgresql@16`
2. Create the database:
   ```bash
   createdb compex_dev
   ```
3. Set `DATABASE_URL` in `.env` to `postgresql://localhost:5432/compex_dev`
4. Push schema & seed:
   ```bash
   pnpm prisma db push
   pnpm prisma db seed
   ```

---

## 6. Running the Project

```bash
# Development
pnpm dev          # Starts Next.js dev server on http://localhost:3000

# Build (production check)
pnpm build

# Lint
pnpm lint

# Prisma Studio (visual DB browser)
pnpm prisma studio
```

---

## 7. Deployment (Vercel)

- The project deploys via **Vercel** (configured in `vercel.json`).
- Build command: `pnpm run build`
- Install command: `pnpm install --frozen-lockfile`
- All production env vars must be set in Vercel Dashboard → Settings → Environment Variables.
- To give deployment access: **Add her as a team member** in Vercel.

---

## 8. Key Project Structure

```
compex/
├── app/              # Next.js App Router (pages, API routes)
├── features/         # Feature modules
├── shared/           # Shared utilities, types, components
├── prisma/           # Database schema & migrations
├── scripts/          # Automation, analysis, diagnostics
├── public/           # Static assets
├── middleware.ts     # Auth middleware
└── docs/             # Documentation
```

---

## 9. Quick Checklist for the New Developer

- [ ] macOS with Homebrew installed
- [ ] Node.js v20+, pnpm, Git installed
- [ ] GitHub repo access (collaborator invite)
- [ ] `.env`, `.env.local` files created with correct values
- [ ] `pnpm install` runs without errors
- [ ] `pnpm prisma generate` completes
- [ ] `pnpm dev` starts successfully on `localhost:3000`
- [ ] Vercel team member access (for deployment)
- [ ] Neon database access (for production DB)
