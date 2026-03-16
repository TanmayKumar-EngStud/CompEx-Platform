#!/bin/bash
# ============================================================
# CompEx-Platform Monorepo Setup Script
# Run this ONCE from your Mac Terminal inside the CompEx-Platform folder:
#   cd ~/Desktop/CompEx-Platform && bash setup-monorepo.sh
# ============================================================

set -e
echo "🚀 Setting up CompEx-Platform monorepo..."

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

# ── Step 1: Clean up broken .git from VM attempt ─────────────
echo ""
echo "Step 1/5: Cleaning up old .git..."
rm -rf .git
echo "✅ Done"

# ── Step 2: Initialize fresh git repo ────────────────────────
echo ""
echo "Step 2/5: Initializing git..."
git init
git branch -m main
git config user.name "Tanmay Kumar"
git config user.email "tanmay44a@gmail.com"
echo "✅ Done"

# ── Step 3: Initial commit (README + planning + mobile) ──────
echo ""
echo "Step 3/5: Committing structure, planning docs, and mobile stub..."
git add README.md planning/ mobile/
git commit -m "chore: initialize CompEx-Platform monorepo

- Root README with platform overview and data pipeline
- planning/ docs: import spec + bot evolution roadmap
- mobile/ stub: ready for React Native app (shared Neon DB)"
echo "✅ Done"

# ── Step 4: Merge QGen-FRESH history into qgen/ ──────────────
echo ""
echo "Step 4/5: Merging QGen-FRESH history into qgen/ (this preserves all commits)..."
git remote add qgen-origin "$HOME/Desktop/QGen-FRESH"
git fetch qgen-origin
git merge -s ours --no-commit --allow-unrelated-histories qgen-origin/master
git read-tree --prefix=qgen/ -u qgen-origin/master
git commit -m "feat(qgen): merge QGen-FRESH question engine (full history preserved)

Integrated from github.com/TanmayKumar-EngStud/QGen-py-compex
- Python AI question generator using Deepseek LLM + Gemini fallback
- Docker containerized, multi-threaded (105 concurrent API connections)
- Generates GRE and GMAT questions (1849+ across 5 sections)
- 5-step per-question pipeline: metadata, title, text, solution, options"
git remote remove qgen-origin
echo "✅ Done — QGen-FRESH history merged!"

# ── Step 5: Merge CompEx history into web/ ───────────────────
echo ""
echo "Step 5/5: Merging CompEx web app history into web/ (this preserves all commits)..."
git remote add web-origin "$HOME/Desktop/compex"
git fetch web-origin
git merge -s ours --no-commit --allow-unrelated-histories web-origin/main
git read-tree --prefix=web/ -u web-origin/main
git commit -m "feat(web): merge CompEx web app (full history preserved)

Integrated from github.com/TanmayKumar-EngStud/CompEx
- Next.js + TypeScript + Prisma platform
- Hosted on Vercel, database on Neon DB (PostgreSQL)
- Auth, dashboard, AI coach, GRE/GMAT question practice
- Google OAuth, Fumadocs /learn section"
git remote remove web-origin
echo "✅ Done — CompEx history merged!"

# ── Final: Set GitHub remote and push ────────────────────────
echo ""
echo "══════════════════════════════════════════════════════════"
echo "✅ Monorepo built successfully!"
echo ""
echo "Git log summary:"
git log --oneline | head -10
echo ""
echo "Next steps — run these commands to push to GitHub:"
echo ""
echo "  git remote add origin https://github.com/TanmayKumar-EngStud/CompEx-Platform.git"
echo "  git push -u origin main"
echo ""
echo "Then archive old repos at:"
echo "  https://github.com/TanmayKumar-EngStud/CompEx/settings"
echo "  https://github.com/TanmayKumar-EngStud/QGen-py-compex/settings"
echo "══════════════════════════════════════════════════════════"
