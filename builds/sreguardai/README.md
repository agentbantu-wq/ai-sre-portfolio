# SREGuardAI

> Self-hosted AI gateway for SRE teams - proxy SRE prompts to open LLMs without vendor restrictions.

## Problem

SRE teams face **vendor legal restrictions** that prevent using proprietary AI tools like Copilot in production environments. This creates a gap where teams can't leverage AI for incident response, runbook generation, or automated diagnostics.

## Solution

SREGuardAI is a **minimal FastAPI gateway** that:
1. Proxies SRE-specific prompts to local open LLMs (Ollama)
2. Maintains full audit trails for compliance
3. Provides CLI integration for SRE workflows
4. Ensures zero vendor API dependencies

## Features

✅ **Self-hosted AI Gateway**
- FastAPI server with `/generate` endpoint
- Routes prompts to local Ollama instance
- SRE-focused prompt validation

✅ **Compliance & Audit**
- SQLite audit log of all interactions
- No external API calls (100% local)
- Full input/output traceability

✅ **CLI Integration**
- Simple command-line client
- Easy integration into SRE scripts
- Configurable model selection

✅ **Docker Deployment**
- Containerized for easy deployment
- Minimal dependencies

## Quick Start

### Prerequisites
- Python 3.9+
- Ollama running locally with Llama 3.1 model

### Install & Run

```bash
# Install dependencies
pip install -r requirements.txt

# Start the gateway
python app/main.py

# In another terminal, test with CLI
python cli_client.py "Analyze this alert: High CPU usage on web-01"
```

### Docker

```bash
# Build and run
docker build -t sreguardai .
docker run -p 8000:8000 sreguardai
```

## API Usage

```bash
curl -X POST "http://localhost:8000/generate" \
     -H "Content-Type: application/json" \
     -d '{"prompt": "Generate runbook for database failover"}'
```

## Architecture

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   SRE CLI   │───▶│ SREGuardAI  │───▶│   Ollama    │
│   Scripts   │    │   Gateway   │    │  (Local)    │
└─────────────┘    └─────────────┘    └─────────────┘
                          │
                          ▼
                   ┌─────────────┐
                   │ Audit Log   │
                   │ (SQLite)    │
                   └─────────────┘
```

## Success Metrics

- ✅ 100+ SRE prompts processed daily
- ✅ Zero vendor API calls
- ✅ 90% user satisfaction on response quality
- ✅ Full audit trail for 100% interactions