#!/bin/bash
# SSL Expiry Checker Demo

echo "🔒 SSL Certificate Expiry Checker Demo"
echo "======================================"

# Install dependencies
echo "📦 Installing dependencies..."
pip install -e .

# Basic check
echo ""
echo "🔍 Basic domain check:"
python -m src.cli check google.com github.com

# Export to JSON
echo ""
echo "💾 Exporting results to JSON:"
python -m src.cli check --output demo_results.json google.com

echo ""
echo "📄 Results saved to demo_results.json"
cat demo_results.json | head -20

# Test with expiring certificate (using badssl.com)
echo ""
echo "⚠️  Testing with expiring certificate:"
python -m src.cli check --warning-days 60 expiring.badssl.com

echo ""
echo "✅ Demo complete! Try: python -m src.cli --help"