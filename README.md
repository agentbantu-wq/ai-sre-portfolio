# AI/SRE Portfolio

> Production-grade AI infrastructure & SRE projects, auto-generated and published daily.

## About

This portfolio showcases **reliability, scalability, observability, and AI systems** expertise through structured, implementable projects focused on real-world SRE challenges.

Every project:
- ✅ Solves a production problem
- ✅ Ships in 1–7 days (MVP)
- ✅ Includes failure mode handling
- ✅ Defines observability & metrics
- ✅ Is GitHub-ready from day 1

## 📂 Structure

```
ai-sre-portfolio/
├── projects/          # Generated project repos & docs
├── prompts/           # Meta-prompts & prompt templates
├── scripts/           # Automation scripts
├── logs/              # Cron & generation logs
└── README.md          # This file
```

## 🚀 Daily Generation

This repo auto-generates a new project daily at **9 AM UTC** using:
- **Meta-Prompter template** for idea generation
- **LLM-powered content** generation (integrated)
- **Git automation** for publishing

### Manual Run

```bash
./scripts/generate.sh
```

## 📋 Project Categories

Projects rotate across:
- 🔍 **Observability Systems** — Metrics, tracing, logging infra
- 🚨 **Incident Automation** — Auto-remediation, auto-escalation
- 🤖 **LLM Infrastructure** — Reliability, scaling, cost control
- 💰 **Cost Optimization** — Resource efficiency, waste reduction
- ☸️ **Kubernetes Intelligence** — Smart scaling, workload optimization

## 📊 Metrics of Success

- **GitHub Activity**: Daily commits
- **Project Completion**: 1–3 day MVPs
- **Code Quality**: Production standards
- **Portfolio Growth**: Measurable expertise narrative

## 🔧 Setup (Automated with Perplexity)

```bash
# Run the interactive setup script
chmod +x setup.sh
./setup.sh
```

This will:
1. ✅ Prompt for your Perplexity API key
2. ✅ Test the API connection
3. ✅ Optionally set up daily cron job (9 AM UTC)
4. ✅ Generate your first project
5. ✅ Make everything executable

### Manual Alternative

```bash
# 1. Set your Perplexity API key
export PERPLEXITY_API_KEY="your-api-key-here"

# 2. Run once manually
./scripts/generate.sh

# 3. Add to crontab (optional)
crontab -e
# Add: 0 9 * * * source /path/to/.env && /path/to/scripts/generate.sh >> /path/to/logs/cron.log 2>&1
```

## 📝 Next Steps

1. [x] Configure Perplexity API
2. [ ] Update meta-prompt with your SRE focus areas (see `prompts/meta-prompt.md`)
3. [ ] Connect to GitHub: `git remote add origin <your-repo>`
4. [ ] Push to GitHub: `git push -u origin main`
5. [ ] Optional: Add GitHub Actions for auto-push
6. [ ] Optional: Add LinkedIn auto-post (social distribution)

---

**Portfolio Growth Starts Here** 🚀
