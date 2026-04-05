# Quick Reference - AI/SRE Portfolio System

## What You Have

✅ **Autonomous portfolio system** that:
- Discovers real SRE problems (HN + Perplexity analysis)
- Generates tool ideas (2 per week)  
- Builds daily projects (auto-committed & pushed)
- Runs 100% hands-off (systemd timers, no cron)

## What's Running

### Daily (9 AM UTC)
```bash
generate.sh → Perplexity project → Auto-commit → Auto-push to GitHub
```

### Weekly (Sunday 2 AM UTC)
```bash
extract_problems.py → AI-analyze → problems/problems_YYYY-MM-DD.json
generate_tools.py → Create 2 tools → tools/{tool_name}/
generate.sh → Create project (as above)
```

## What's Generated

```
ai-sre-portfolio/
├── projects/              # Daily projects (Markdown)
├── problems/              # Weekly extracted problems (JSON)
├── tools/                 # Weekly generated tool ideas (with specs + code)
├── builds/                # Fully built, working tools
│   └── ai-sre-readiness-checker/  ← COMPLETE & WORKING
│       ├── src/           (Python modules)
│       ├── tests/         (Unit tests)
│       ├── checklists/    (YAML configs)
│       └── README.md      (Full docs)
└── systemd/               # Service definitions
    ├── ai-sre-daily.service
    ├── ai-sre-daily.timer
    ├── ai-sre-portfolio.service
    └── ai-sre-portfolio.timer
```

## Commands

### View What's Running
```bash
systemctl --user list-timers | grep ai-sre
journalctl --user -u ai-sre-daily.service -f
./scripts/systemd-status.sh
```

### Run Manually (Any Time)
```bash
source .env && python3 scripts/extract_problems.py  # Extract problems
source .env && python3 scripts/generate_tools.py    # Generate tools
source .env && ./scripts/generate.sh                # Generate project
```

### Test the AI-SRE-Readiness-Checker Tool
```bash
cd builds/ai-sre-readiness-checker
bash demo.sh
```

## Key Files

| File | Purpose |
|------|---------|
| `scripts/generate.sh` | Daily project generator |
| `scripts/extract_problems.py` | Weekly problem extraction |
| `scripts/generate_tools.py` | Weekly tool idea generator |
| `systemd/ai-sre-daily.timer` | Daily 9 AM trigger |
| `systemd/ai-sre-portfolio.timer` | Weekly Sunday 2 AM trigger |
| `.env` | Perplexity API key storage |
| `prompts/meta-prompt.md` | Customizable generation prompt |
| `STATUS.md` | Full system status |

## Schedule

| When | What |
|------|------|
| Every day 9 AM UTC | New project generated & pushed |
| Every Sunday 2 AM UTC | Problems extracted + 2 tools generated + project |

## Status Today

- ✅ Perplexity API: Connected & tested
- ✅ GitHub sync: Working (auto-push enabled)
- ✅ Systemd timers: Running
- ✅ First tool: AI-SRE-Readiness-Checker (complete, tested, ready)

## Next Week

- ~ 7 new projects
- ~ 5 new problems discovered
- ~ 2 new tool ideas
- 1-2 new tools fully built (if extended)

## Customize

**Change generation cadence** (2 tools/week):
```python
# In scripts/generate_tools.py, line 215:
for problem in problems[:2]:  # Change 2 to desired number
```

**Change daily run time**:
```bash
# Edit systemd/ai-sre-daily.timer
OnCalendar=*-*-* HH:MM:SS UTC  # Change HH:MM
```

**Change generation focus**:
```bash
# Edit prompts/meta-prompt.md
# Customize the meta-prompt to focus on specific SRE areas
```

## Resources

- GitHub repo: https://github.com/agentbantu-wq/ai-sre-portfolio
- First built tool: `builds/ai-sre-readiness-checker/README.md`
- Full status: `STATUS.md`
- Docs: See project READMEs
