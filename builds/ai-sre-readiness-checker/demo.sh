#!/bin/bash

# Demo script for AI-SRE-Readiness-Checker
# Shows how to run the tool

set -e

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "=========================================="
echo "AI-SRE-Readiness-Checker Demo"
echo "=========================================="
echo ""

# Ensure venv exists
if [[ ! -d "$REPO_ROOT/.venv" ]]; then
    echo "🔧 Creating virtual environment..."
    python3 -m venv "$REPO_ROOT/.venv"
    source "$REPO_ROOT/.venv/bin/activate"
    pip install -q click pyyaml
else
    source "$REPO_ROOT/.venv/bin/activate"
fi

echo "📋 This tool evaluates AI SRE tools for production readiness"
echo ""
echo "Pillars evaluated:"
echo "  1. Context - Can access metrics, logs, traces, runbooks"
echo "  2. Investigation - Correlates signals, finds root cause"
echo "  3. Actionability - Can execute fixes, dry-run, remediate"
echo "  4. Safety - Audit logs, guardrails, approval workflows"
echo "  5. Efficiency - Fast response, low overhead, scales"
echo ""
echo "Example usage:"
echo "  python3 -c 'from src.config import get_default_checklist; import json; print(json.dumps(get_default_checklist(), indent=2))' | head -30"
echo ""

# Show checklist
echo "📊 Default Checklist (Context pillar):"
python3 << 'PYEOF'
from src.config import get_default_checklist
import json

checklist = get_default_checklist()
context = checklist.get('context', [])
for i, criterion in enumerate(context[:3], 1):
    print(f"  {i}. {criterion.get('name', 'N/A')}")
    print(f"     {criterion.get('description', '')}")
PYEOF

echo ""
echo "✅ Tool is ready for evaluation!"
echo "=========================================="
