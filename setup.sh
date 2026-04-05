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

# 4. Cron setup
echo ""
echo "3️⃣  Cron Automation Setup"
echo "   Run daily project generation at 9 AM UTC"
echo ""
read -p "Do you want to set up daily cron job? (y/n) " SETUP_CRON

if [[ "$SETUP_CRON" == "y" ]]; then
  CRON_JOB="0 9 * * * source $REPO_ROOT/.env && $REPO_ROOT/scripts/generate.sh >> $REPO_ROOT/logs/cron.log 2>&1"
  
  # Check if cron job already exists
  if crontab -l 2>/dev/null | grep -q "scripts/generate.sh"; then
    echo "⚠️  Cron job already exists. Skipping..."
  else
    (crontab -l 2>/dev/null; echo "$CRON_JOB") | crontab -
    echo "✅ Cron job installed!"
  fi
fi

# 5. Make scripts executable
echo ""
echo "4️⃣  Making scripts executable..."
chmod +x "$REPO_ROOT/scripts/generate.sh"
chmod +x "$REPO_ROOT/setup.sh"
echo "✅ Scripts are executable"

# 6. Manual test
echo ""
echo "5️⃣  Manual Test (generating first project)"
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
echo "📋 Next Steps:"
echo "  1. Add remote: git remote add origin <your-github-repo>"
echo "  2. Push: git push -u origin main"
echo "  3. Check logs: tail -f logs/cron.log"
echo "  4. Manual run: ./scripts/generate.sh"
echo ""
echo "💡 Cron will run daily at 9 AM UTC"
echo ""
