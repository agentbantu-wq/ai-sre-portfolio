#!/bin/bash
# SREGuardAI Demo Script

echo "🚀 SREGuardAI Demo"
echo "=================="

# Check if Ollama is running (optional)
if curl -s http://localhost:11434/api/tags > /dev/null; then
    echo "✅ Ollama is running"
else
    echo "⚠️  Ollama not detected. Install and run: ollama serve"
    echo "   Then pull model: ollama pull llama3.1"
fi

# Install dependencies
echo "📦 Installing dependencies..."
pip install -e .

# Start server in background
echo "🌐 Starting SREGuardAI server..."
python app/main.py &
SERVER_PID=$!

# Wait for server to start
sleep 3

# Test CLI
echo "🧪 Testing CLI client..."
echo "Prompt: 'Generate runbook for handling pod crashes'"
python cli_client.py "Generate runbook for handling pod crashes"

echo ""
echo "Prompt: 'Analyze this alert log: ERROR connection timeout'"
python cli_client.py "Analyze this alert log: ERROR connection timeout"

# Test API directly
echo ""
echo "🔗 Testing API endpoint..."
curl -X POST "http://localhost:8000/generate" \
     -H "Content-Type: application/json" \
     -d '{"prompt": "What are common causes of database connection pool exhaustion?"}'

# Cleanup
echo ""
echo "🧹 Cleaning up..."
kill $SERVER_PID

echo "✅ Demo complete!"