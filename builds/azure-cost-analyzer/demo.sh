#!/bin/bash
# Azure Cost Analyzer Demo

echo "💰 Azure Cost Analyzer Demo"
echo "============================="

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
azure-cost-analyzer --help

echo ""
echo "✅ Demo complete! Try:"
echo "  azure-cost-analyzer analyze --days 30"
echo "  azure-cost-analyzer anomalies --severity critical"
echo "  azure-cost-analyzer trends --days 30"
echo "  azure-cost-analyzer dashboard --output dashboard.json"