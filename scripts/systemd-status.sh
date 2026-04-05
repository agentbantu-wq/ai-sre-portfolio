#!/bin/bash

###############################################################################
# AI/SRE Portfolio - Systemd Status & Diagnostic Tool
# Helps debug systemd service issues
###############################################################################

set -e

echo "=========================================="
echo "AI/SRE Portfolio - Systemd Diagnostics"
echo "=========================================="
echo ""

# 1. Check if services are installed
echo "1️⃣  Checking installed services..."
echo ""
echo "Installed unit files:"
systemctl --user list-unit-files | grep ai-sre || echo "  (none found)"
echo ""

# 2. Check service status
echo "2️⃣  Service Status:"
echo ""
systemctl --user status ai-sre-daily.service || echo "  ai-sre-daily.service not active"
echo ""
systemctl --user status ai-sre-portfolio.service || echo "  ai-sre-portfolio.service not active"
echo ""

# 3. Check timers
echo "3️⃣  Timers & Next Run Times:"
echo ""
systemctl --user list-timers --all | grep ai-sre || echo "  (no timers found)"
echo ""

# 4. Recent logs
echo "4️⃣  Recent Execution Logs (last 20 lines):"
echo ""
journalctl --user -u ai-sre-daily.service -u ai-sre-portfolio.service -n 20 --no-pager || echo "  (no logs found)"
echo ""

# 5. .env file check
REPO_ROOT="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
echo "5️⃣  Configuration Check:"
echo ""
if [[ -f "$REPO_ROOT/.env" ]]; then
  echo "  ✅ .env file exists"
  if grep -q "PERPLEXITY_API_KEY=" "$REPO_ROOT/.env"; then
    API_KEY=$(grep "PERPLEXITY_API_KEY=" "$REPO_ROOT/.env" | cut -d= -f2)
    if [[ -n "$API_KEY" ]] && [[ "$API_KEY" != "" ]]; then
      echo "  ✅ PERPLEXITY_API_KEY is set"
    else
      echo "  ❌ PERPLEXITY_API_KEY is empty"
    fi
  fi
else
  echo "  ❌ .env file not found"
fi

echo ""

# 6. Helpful commands
echo "=========================================="
echo "💡 Helpful Commands:"
echo "=========================================="
echo ""
echo "View detailed logs:"
echo "  journalctl --user -u ai-sre-daily.service -f"
echo ""
echo "Start timer manually:"
echo "  systemctl --user start ai-sre-daily.timer"
echo ""
echo "Check next scheduled run:"
echo "  systemctl --user list-timers ai-sre-daily.timer"
echo ""
echo "Run service immediately (for testing):"
echo "  systemctl --user start ai-sre-daily.service"
echo ""
echo "Reload systemd daemon:"
echo "  systemctl --user daemon-reload"
echo ""
