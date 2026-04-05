# AI/SRE Portfolio

> **Real-world problem discovery → Tool generation → Daily projects**
>
> An autonomous system that discovers SRE pain points via Reddit/HN, generates tool ideas with Perplexity, and publishes production-grade projects daily.

## About

This portfolio automates **problem-driven development** in the AI/SRE space:

1. **Weekly**: Scrapes Reddit/HN for real SRE pain points
2. **Weekly**: Generates 3 tool ideas from the top problems
3. **Daily**: Creates a new, production-ready project

Every project:
- ✅ Solves a validated production problem
- ✅ Ships in 1–7 days (MVP)
- ✅ Includes failure mode handling
- ✅ Defines observability & metrics
- ✅ Is GitHub-ready from day 1

## 📂 Structure

```
ai-sre-portfolio/
├── projects/          # Generated projects (daily)
├── problems/          # Extracted pain points (weekly)
├── tools/             # Tool ideas & code skeletons (weekly)
├── prompts/           # Meta-prompts for idea generation
├── scripts/           # Automation pipeline
│   ├── generate.sh           # Project generator
│   ├── extract_problems.py   # Reddit/HN scraper
│   └── generate_tools.py     # Tool idea generator
├── systemd/           # Linux service definitions
├── logs/              # Execution logs
└── README.md          # This file
```

## 🚀 Automation Pipeline

### Three-Part Weekly Cycle

| Stage | When | What | Tool |
|-------|------|------|------|
| **Discovery** | Sunday 2 AM UTC | Extract SRE problems from Reddit/HN | `extract_problems.py` |
| **Design** | Sunday 2 AM UTC | Generate 3 tool ideas from problems | `generate_tools.py` |
| **Build** | Daily 9 AM UTC | Create production-grade project | `generate.sh` |

### Automation Method (Systemd)

Uses **systemd user services** for reliable, no-dependency automation:

```bash
# Check daily timer
systemctl --user status ai-sre-daily.timer

# View latest execution
journalctl --user -u ai-sre-daily.service -n 50

# Disable/enable
systemctl --user stop ai-sre-daily.timer
systemctl --user start ai-sre-daily.timer
```

### Manual Execution

```bash
# Generate new project
./scripts/generate.sh

# Extract problems from Reddit/HN
python3 scripts/extract_problems.py

# Generate tool ideas
python3 scripts/generate_tools.py
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

### One-Command Setup

```bash
chmod +x setup.sh
./setup.sh
```

This interactive script will:
1. ✅ Prompt for your Perplexity API key
2. ✅ Test API connection
3. ✅ Install systemd services & timers
4. ✅ Enable weekly problem/tool generation
5. ✅ Enable daily project generation
6. ✅ Optionally run first generation

### What Gets Installed

- **systemd services**: `ai-sre-daily.service`, `ai-sre-portfolio.service`
- **systemd timers**: `ai-sre-daily.timer` (daily 9 AM UTC), `ai-sre-portfolio.timer` (Sunday 2 AM UTC)
- **Dependencies**: Python 3, Perplexity API key (free tier available)

### Verify Installation

```bash
# List installed services
systemctl --user list-unit-files | grep ai-sre

# Check next execution time
systemctl --user list-timers | grep ai-sre

# View recent logs
journalctl --user -u ai-sre-daily.service -f
```

## 🔍 Problem Discovery Workflow

Every **Sunday 2 AM UTC**, the system:

1. **Scrapes Reddit & Hacker News** for SRE/AI discussions
   - Monitors: r/sre, r/devops, r/observability, Hacker News
   - Keywords: incident, scaling, reliability, observability, kubernetes, AI

2. **Extracts top problems** using Perplexity
   - Ranks by relevance and community interest
   - Captures: title, description, severity, impact

3. **Generates tool ideas** from extracted problems
   - Creates: repo structure, tech stack, MVP scope
   - Outputs: `tools/{tool_name}/` with specifications

### Example: Weekly Output

```
problems/
└── problems_2026-04-06.json    # Top 5 extracted problems

tools/
├── unified_incident_correlator/
│   ├── tool_spec.json
│   ├── main.py
│   ├── config.py
│   └── requirements.txt
├── failure_pattern_detector/
│   └── ...
└── slack_incident_manager/
    └── ...

projects/
└── project_2026-04-06.md       # Daily project (9 AM UTC)
```

## 🛠 Building from Problems

The tool generation creates:
- **Validated problems** (from real community discussion)
- **Minimal tool specs** (buildable in 3-7 days)
- **Code skeletons** (Python/Go starting points)
- **Success metrics** (measurable outcomes)

You can then take any tool and:
1. Expand the code skeleton
2. Add tests & CI/CD
3. Publish as open-source
4. Reference real problem it solves

## 📝 Next Steps & Advanced Setup

### Essential
1. [x] Configure Perplexity API via `./setup.sh`
2. [ ] Customize meta-prompt: `prompts/meta-prompt.md`
3. [ ] Connect to GitHub: `git remote add origin <your-repo>`
4. [ ] Push to GitHub: `git push -u origin main`

### Recommended
1. [ ] Set up GitHub Actions to auto-push from systemd
2. [ ] Monitor cron logs daily: `tail -f logs/*.log`
3. [ ] Review weekly problem extracts: `cat problems/problems_*.json`
4. [ ] Test systemd timers manually before first run

### Optional Enhancements
1. [ ] Add LinkedIn auto-post script (publish projects)
2. [ ] Create GitHub Pages for portfolio showcase
3. [ ] Add email notifications on new projects
4. [ ] Integrate with Slack for daily summaries

## 🐛 Troubleshooting

**Systemd timer not running?**
```bash
# Check if user services are enabled
systemctl --user is-enabled ai-sre-daily.timer

# Enable and start
systemctl --user enable --now ai-sre-daily.timer

# Check status
systemctl --user status ai-sre-daily.timer
```

**API errors?**
```bash
# Test Perplexity API manually
curl -X POST "https://api.perplexity.ai/chat/completions" \
  -H "Authorization: Bearer $PERPLEXITY_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"model":"sonar","messages":[{"role":"user","content":"test"}],"max_tokens":10}'
```

**Python dependencies missing?**
```bash
# Required: Python 3.8+
python3 --version

# Optional: Reddit scraping (for full problem discovery)
pip install praw requests
```

## 📊 What to Expect

### After Sunday (Weekly Run)
- New file: `problems/problems_YYYY-MM-DD.json` (top 5 problems)
- New folder: `tools/{tool_name}/` (3 tool ideas with code skeletons)

### Daily (9 AM UTC)
- New file: `projects/project_YYYY-MM-DD.md` (production-ready project)
- Auto-committed and pushed to GitHub

### Monthly
- 30+ projects in portfolio
- 12+ tool ideas extracted
- Clear narrative: "Building tools from real SRE pain points"

---

**Portfolio Growth Starts Here** 🚀

## 📚 Learn More

- [Perplexity API Docs](https://docs.perplexity.ai/)
- [Systemd User Services](https://wiki.archlinux.org/title/Systemd/user)
- [Top Reddit SRE Communities](https://www.reddit.com/r/sre/)
- [Hacker News Latest](https://news.ycombinator.com/newest)
