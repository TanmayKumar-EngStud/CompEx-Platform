# CompEx Platform — Monorepo

> AI-powered standardized test prep platform (GRE & GMAT) — question generation engine, web app, and mobile app (coming soon).

---

## Repository Structure

```
CompEx-Platform/
├── web/            — Next.js + Prisma web application (hosted on Vercel, Neon DB)
├── qgen/           — Python AI question generation engine (Deepseek LLM, Docker)
├── mobile/         — React Native / Expo mobile app [coming soon, same Neon DB]
├── planning/       — Architecture docs, import specs, product roadmap
└── README.md
```

---

## Projects

### `web/` — CompEx Web App
The student-facing platform built with **Next.js**, **TypeScript**, and **Prisma ORM**.
- **Live:** Hosted on [Vercel](https://vercel.com)
- **Database:** [Neon DB](https://neon.tech) (PostgreSQL — shared with mobile)
- Serves GRE & GMAT practice questions, tracks student performance, and powers the AI tutoring experience

### `qgen/` — QGen Question Generation Engine
An AI-powered Python pipeline that auto-generates complete standardized test papers.
- **LLM:** Deepseek (primary), Gemini (fallback)
- **Parallelism:** Up to 105 concurrent API threads (21 sections × 5 threads)
- **Output:** ~1,849 questions across GRE Quants, GRE Verbal, GMAT Quants, GMAT Verbal, GMAT Data Insights
- **Containerized:** Full Docker + docker-compose setup
- Questions are imported into the Neon DB via Prisma for the web and mobile apps to consume

### `mobile/` — CompEx Mobile App *(coming soon)*
A React Native / Expo mobile experience connected to the **same Neon DB** as the web app.
- Shared database schema, shared question bank, shared student data
- Planned feature parity with the web platform

---

## Data Pipeline

```
qgen/ (Deepseek AI generates questions)
    ↓  JSON output (1,849+ questions)
    ↓  Prisma import script
Neon DB (PostgreSQL — single source of truth)
    ↓                    ↓
web/ (Vercel)       mobile/ (coming soon)
```

---

## Planning & Roadmap

See [`planning/`](./planning/) for:
- `QGen-FRESH-Import-Plan.md` — Technical spec for migrating generated questions into the DB
- `future-concepts/compex-bot-evolution-concept.md` — Elo-style AI tutor bot evolution roadmap (v1→v2→v3)

---

## Archived Repositories

The original standalone repositories are preserved as read-only archives on GitHub:
- [`TanmayKumar-EngStud/CompEx`](https://github.com/TanmayKumar-EngStud/CompEx) — original web app repo
- [`TanmayKumar-EngStud/QGen-py-compex`](https://github.com/TanmayKumar-EngStud/QGen-py-compex) — original question engine repo
