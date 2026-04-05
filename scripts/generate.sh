#!/bin/bash

###############################################################################
# AI/SRE Portfolio - Daily Project Generator
# Runs daily to generate and publish a new project
###############################################################################

set -e

# Configuration
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PROJECTS_DIR="$REPO_ROOT/projects"
LOGS_DIR="$REPO_ROOT/logs"
DATE=$(date +"%Y-%m-%d")
LOG_FILE="$LOGS_DIR/generate_${DATE}.log"
PROJECT_FILE="$PROJECTS_DIR/project_${DATE}.md"

# Source .env if it exists
if [[ -f "$REPO_ROOT/.env" ]]; then
  set -a
  source "$REPO_ROOT/.env"
  set +a
fi

# Ensure directories exist
mkdir -p "$PROJECTS_DIR" "$LOGS_DIR"

# Logging function
log() {
  echo "[$(date +'%Y-%m-%d %H:%M:%S')] $*" | tee -a "$LOG_FILE"
}

log "=========================================="
log "Generating AI/SRE Project for $DATE"
log "=========================================="

# Check if project for today already exists
if [[ -f "$PROJECT_FILE" ]]; then
  log "Project already generated for $DATE. Skipping."
  exit 0
fi

# Perplexity API Integration
log "Reading meta-prompt..."
PROMPT=$(cat "$REPO_ROOT/prompts/meta-prompt.md")

# Check for API key
if [[ -z "$PERPLEXITY_API_KEY" ]]; then
  log "❌ PERPLEXITY_API_KEY not set. Exiting."
  exit 1
fi

log "Calling Perplexity API..."

# Call Perplexity API with streaming disabled for easier JSON parsing
RESPONSE=$(curl -s -X POST "https://api.perplexity.ai/chat/completions" \
  -H "Authorization: Bearer $PERPLEXITY_API_KEY" \
  -H "Content-Type: application/json" \
  -d @- << CURL_EOF
{
  "model": "sonar",
  "messages": [
    {
      "role": "system",
      "content": "You are an expert SRE and AI infrastructure engineer. Generate a production-ready project idea in markdown format with all sections requested."
    },
    {
      "role": "user",
      "content": "$PROMPT\n\nGenerate a new AI/SRE project for $(date +%Y-%m-%d). Output ONLY the markdown content, starting with '# AI/SRE Project'. Include all sections: Problem Statement, Architecture, Implementation Steps, Code Skeleton, Metrics, Observability, Failure Analysis, and Next Steps."
    }
  ],
  "max_tokens": 2000,
  "temperature": 0.7,
  "stream": false
}
CURL_EOF
)

# Extract content from response
CONTENT=$(echo "$RESPONSE" | jq -r '.choices[0].message.content' 2>/dev/null)

if [[ -z "$CONTENT" ]] || [[ "$CONTENT" == "null" ]]; then
  log "❌ Failed to get response from Perplexity API"
  log "Response: $RESPONSE"
  exit 1
fi

log "✅ Generated content from Perplexity API"

# Write the generated content to project file
cat > "$PROJECT_FILE" << EOF
$CONTENT

---

**Generated**: $(date)
**Tags**: #SRE #AI #Observability #Scaling #LLMInfra
EOF
log "✅ Project template created at: $PROJECT_FILE"

# Run git operations
cd "$REPO_ROOT"

log "Adding to git..."
git add "$PROJECT_FILE"

log "Committing..."
git commit -m "add: project for $DATE" || log "⚠️  Nothing new to commit"

log "Attempting push (requires origin remote)..."
git push origin main 2>/dev/null || log "⚠️  No remote configured or push failed"

log "=========================================="
log "✅ Generation complete!"
log "Project: $PROJECT_FILE"
log "=========================================="
