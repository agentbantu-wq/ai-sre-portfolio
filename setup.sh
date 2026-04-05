#!/bin/bash

###############################################################################
# AI/SRE Portfolio - Setup Script
# Configures Perplexity API integration and cron automation
###############################################################################

set -e

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "=========================================="
echo "AI/SRE Portfolio - Setup"
echo "=========================================="
echo ""

# 1. Check for .env file
if [[ ! -f "$REPO_ROOT/.env" ]]; then
  echo "⚠️  .env file not found. Creating from template..."
  cp "$REPO_ROOT/.env.example" "$REPO_ROOT/.env"
  echo "✅ Created .env (update with your Perplexity API key)"
fi

# 2. Prompt for Perplexity API key
echo ""
echo "1️⃣  Perplexity API Configuration"
echo "   Get your free API key: https://www.perplexity.ai/api"
echo ""
read -sp "Enter your Perplexity API key (hidden): " API_KEY
echo ""

if [[ -n "$API_KEY" ]]; then
  sed -i "s/^PERPLEXITY_API_KEY=.*/PERPLEXITY_API_KEY=$API_KEY/" "$REPO_ROOT/.env"
  echo "✅ API key saved to .env"
else
  echo "⚠️  No API key provided. You'll need to edit .env manually."
fi

# 3. Test Perplexity API
echo ""
echo "2️⃣  Testing Perplexity API..."
source "$REPO_ROOT/.env"

TEST_RESPONSE=$(curl -s -X POST "https://api.perplexity.ai/chat/completions" \
  -H "Authorization: Bearer $PERPLEXITY_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"model":"sonar","messages":[{"role":"user","content":"Say hello"}],"max_tokens":10}' | jq -r '.choices[0].message.content' 2>/dev/null)

if [[ -n "$TEST_RESPONSE" ]] && [[ "$TEST_RESPONSE" != "null" ]]; then
  echo "✅ Perplexity API is working!"
else
  echo "❌ Perplexity API test failed. Check your API key."
  exit 1
fi

# 4. Make scripts executable
echo ""
echo "3️⃣  Making scripts executable..."
chmod +x "$REPO_ROOT/scripts/generate.sh"
chmod +x "$REPO_ROOT/scripts/extract_problems.py"
chmod +x "$REPO_ROOT/scripts/generate_tools.py"
chmod +x "$REPO_ROOT/setup.sh"
echo "✅ Scripts are executable"

# 5. Install systemd services (primary automation)
echo ""
echo "4️⃣  Installing systemd services..."
mkdir -p "$HOME/.config/systemd/user"

# Copy service files
cp "$REPO_ROOT/systemd/ai-sre-portfolio.service" "$HOME/.config/systemd/user/"
cp "$REPO_ROOT/systemd/ai-sre-portfolio.timer" "$HOME/.config/systemd/user/"
cp "$REPO_ROOT/systemd/ai-sre-daily.service" "$HOME/.config/systemd/user/"
cp "$REPO_ROOT/systemd/ai-sre-daily.timer" "$HOME/.config/systemd/user/"

# Reload systemd
systemctl --user daemon-reload

echo "✅ Systemd services installed:"
echo "   • Daily project generation: ai-sre-daily.timer (9 AM UTC)"
echo "   • Weekly problem extraction: ai-sre-portfolio.timer (Sunday 2 AM UTC)"

# 6. Enable systemd timers (primary)
echo ""
echo "5️⃣  Automation Setup"
read -p "Enable systemd timers for automation? (y/n) " ENABLE_SYSTEMD

if [[ "$ENABLE_SYSTEMD" == "y" ]]; then
  systemctl --user enable ai-sre-daily.timer
  systemctl --user enable ai-sre-portfolio.timer
  systemctl --user start ai-sre-daily.timer
  systemctl --user start ai-sre-portfolio.timer
  echo "✅ Systemd timers enabled and started"
  
  # Optional: remove old cron job
  if crontab -l 2>/dev/null | grep -q "scripts/generate.sh"; then
    read -p "Remove old cron job? (y/n) " REMOVE_CRON
    if [[ "$REMOVE_CRON" == "y" ]]; then
      (crontab -l | grep -v "scripts/generate.sh") | crontab -
      echo "✅ Removed old cron job"
    fi
  fi
else
  # Fallback to cron
  echo "⚠️  Using legacy cron automation"
  CRON_JOB="0 9 * * * source $REPO_ROOT/.env && $REPO_ROOT/scripts/generate.sh >> $REPO_ROOT/logs/cron.log 2>&1"
  
  if crontab -l 2>/dev/null | grep -q "scripts/generate.sh"; then
    echo "⚠️  Cron job already exists. Skipping..."
  else
    (crontab -l 2>/dev/null; echo "$CRON_JOB") | crontab -
    echo "✅ Cron job installed (daily at 9 AM UTC)"
  fi
fi

# 7. Manual test
echo ""
echo "6️⃣  Manual Test (optional)"
read -p "Run first generation now? (y/n) " RUN_NOW

if [[ "$RUN_NOW" == "y" ]]; then
  source "$REPO_ROOT/.env"
  "$REPO_ROOT/scripts/generate.sh"
fi

echo ""
echo "=========================================="
echo "✅ Setup Complete!"
echo "=========================================="
echo ""
echo "📋 Git Configuration:"
echo "  1. git remote add origin <your-github-repo>"
echo "  2. git push -u origin main"
echo ""
echo "📋 Systemd Commands (if enabled):"
echo "  • Check status: systemctl --user status ai-sre-daily.timer"
echo "  • View logs: journalctl --user -u ai-sre-daily.service -f"
echo "  • Disable timer: systemctl --user stop ai-sre-daily.timer"
echo ""
echo "📋 Manual Run:"
echo "  • Generate project: ./scripts/generate.sh"
echo "  • Extract problems: python3 scripts/extract_problems.py"
echo "  • Generate tools: python3 scripts/generate_tools.py"
echo ""
echo "🎯 Automation Schedule:"
echo "  • Daily: Project generation at 9 AM UTC"
echo "  • Weekly: Problem extraction + tool generation at 2 AM UTC Sunday"
echo ""
