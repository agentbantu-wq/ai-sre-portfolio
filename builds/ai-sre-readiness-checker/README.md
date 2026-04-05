# AI-SRE-Readiness-Checker

> Evaluate AI SRE tools for production readiness in under 1 hour.

## Problem

SRE teams want to adopt AI-driven automation but face **long development cycles and unproven reliability**. Most tools fail on:
- Context awareness (missing incident data)
- Investigation capability (shallow diagnostics)
- Actionability (can't auto-remediate or suggest fixes)
- Safety (no guardrails or dry-run modes)
- Efficiency (adds latency/overhead)

**Result**: Teams waste weeks evaluating tools only to find they're not production-ready.

## Solution

AI-SRE-Readiness-Checker is a **lightweight CLI framework** that:
1. Scores any AI SRE tool against 5 production pillars
2. Generates a 0-100 readiness score
3. Simulates incidents to test real-world capability
4. Creates actionable reports with pass/fail criteria

## Features

✅ **5-Pillar Evaluation**
- **Context**: Can the tool access required incident/infra data?
- **Investigation**: Does it correlate logs/metrics properly?
- **Actionability**: Can it suggest or execute fixes?
- **Safety**: Has dry-run mode? Guardrails? Audit logs?
- **Efficiency**: What's the latency/resource overhead?

✅ **Configurable Checklists**
- YAML-based criteria (20+ checks per pillar)
- Customizable for your SRE maturity level

✅ **Scenario Testing**
- Mock incidents (pod crash, high latency, OOM, etc.)
- Tests how tool responds without real infra

✅ **Production Reports**
- Scored breakdown (0-100)
- Pass/fail on each criterion
- Next steps & gap analysis

## Quick Start

```bash
# Install
pip install -e .

# Evaluate a tool (interactive)
ai-sre-readiness --tool "PagerDuty Event Intelligence"

# Or use YAML config
ai-sre-readiness --config my-tool-eval.yaml

# Output: readiness_report_TIMESTAMP.html
```

## Example Report

```
Tool: DataDog Incident AI
Readiness Score: 72/100

✅ Context (18/20)
  - Accesses metrics ✓
  - Accesses logs ✓
  - Accesses traces ✗ (requires Enterprise)
  - Can fetch runbooks ✓

✅ Investigation (14/20)
  - Correlates logs/metrics ✓
  - Identifies patterns ✓
  - Suggests root cause ✓
  - Articulates confidence level ✗

⚠️  Actionability (10/15)
  - Can dry-run fixes ✗
  - Auto-remediate ✗
  - Suggests remediation ✓
  - Respects change windows ✓

✅ Safety (16/20)
  - Audit log of decisions ✓
  - Guardrails configured ✓
  - Requires approval for actions ✓
  - Rate limiting ✗ (server-side only)

⚠️  Efficiency (14/15)
  - Response time < 10s ✓ (avg 2.3s)
  - Resource overhead < 5% ✓
  - Scales with incident volume ✓

Recommendation
- Good for **investigation & alerting suppression**
- Poor for **autonomous remediation**
- Gap: Lacks proactive prediction
```

## MVP Scope (3 Days)

**Day 1**: Core CLI + pillar framework
- Click CLI with interactive prompts
- Pillar definitions + checklist loading
- Basic YAML config parsing

**Day 2**: Scenario testing
- Mock incident generator
- Response testing harness
- Report template

**Day 3**: Reporting & polish
- HTML/JSON report generation
- Gap analysis + recommendations
- Documentation & examples

## Success Metrics

- **Accuracy**: 80%+ match vs. manual expert evaluations
- **Speed**: Evaluate any tool in < 1 hour
- **Adoption**: Used by 5+ SRE teams to validate tools
- **Impact**: Saves teams 4-6 weeks per tool evaluation

## Architecture

```
src/
├── cli.py              # Click entry point
├── evaluator.py        # Core scoring logic
├── pillars/            # Pillar implementations
│   ├── context.py
│   ├── investigation.py
│   ├── actionability.py
│   ├── safety.py
│   └── efficiency.py
├── scenarios.py        # Mock incident generator
├── report.py           # HTML/JSON report generation
└── config.py           # Config loader

tests/
├── test_cli.py
├── test_evaluator.py
└── test_scenarios.py

checklists/
├── production_ready.yaml       # Default checklist
├── startup_sre.yaml            # Simplified for small teams
└── enterprise_sre.yaml         # Comprehensive

docs/
├── USAGE.md
├── CUSTOMIZATION.md
└── examples/
```

## Install & Run

```bash
git clone <this-repo>
cd ai-sre-readiness-checker

pip install -e .

# Interactive evaluation
ai-sre-readiness

# Or config-driven
ai-sre-readiness --config checklists/production_ready.yaml
```

## Next Steps

1. Expand checklist criteria (currently 20, target 50+)
2. Add Slack/Teams integration for team sharing
3. Connect to real integrations (PagerDuty, DataDog APIs)
4. Build comparison tool (score multiple tools side-by-side)
5. Create SRE community checklist database

---

**Tags**: `#SRE` `#AI` `#Tooling` `#Evaluation` `#ProductionReady`
