#!/bin/bash
# Azure Alert Analyzer Demo

echo "📊 Azure Monitor Alert Analyzer Demo"
echo "====================================="

# Install dependencies
echo "📦 Installing dependencies..."
pip install -e .

# Run basic analysis (will require Azure credentials)
echo ""
echo "🔍 Running demo analysis..."
echo "Note: Requires Azure subscription access"

# Show help
echo ""
echo "Available commands:"
azure-alert-analyzer --help

echo ""
echo "✅ Demo complete! Try:"
echo "  azure-alert-analyzer analyze --days 7"
echo "  azure-alert-analyzer dashboard --output dashboard.json"