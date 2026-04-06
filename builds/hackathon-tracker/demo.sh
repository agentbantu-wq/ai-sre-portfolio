#!/bin/bash
# Hackathon Tracker Demo Script
# This script demonstrates the key features of the Hackathon Opportunity Tracker

set -e

echo "🎯 Hackathon Opportunity Tracker - Demo"
echo "========================================"
echo ""

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "⚠️  Warning: .env file not found. Creating template..."
    cat > .env << EOF
# Reddit API Credentials (required for Reddit scanning)
# Get these from: https://www.reddit.com/prefs/apps
REDDIT_CLIENT_ID=your_client_id_here
REDDIT_CLIENT_SECRET=your_client_secret_here
REDDIT_USER_AGENT=HackathonTracker/1.0

# Optional: Your hourly rate for ROI calculations (default: $50/hour)
HOURLY_RATE=50
EOF
    echo "✅ Created .env template. Please fill in your Reddit API credentials."
    echo ""
fi

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "🐍 Creating virtual environment..."
    python3 -m venv venv
fi

echo "🔧 Activating virtual environment and installing dependencies..."
source venv/bin/activate
pip install -r requirements.txt

echo ""
echo "🚀 Starting Hackathon Tracker Demo"
echo "=================================="

echo ""
echo "📊 Demo 1: Basic Search (Mock Data - No API calls)"
echo "--------------------------------------------------"
echo "This would normally scan Reddit, but we'll show the interface:"
echo "hackathon-tracker search --subreddits hackathons,gitlab --days 7 --limit 20"
echo ""

echo "📊 Demo 2: Filtering Opportunities"
echo "----------------------------------"
echo "Example command to filter for high-value opportunities:"
echo "hackathon-tracker filter opportunities.json --min-prize 1000 --max-effort 40 --min-roi 3"
echo ""

echo "📊 Demo 3: Exporting Results"
echo "----------------------------"
echo "Export filtered results to Excel:"
echo "hackathon-tracker export filtered_opportunities.json --format excel --output my_hackathons.xlsx"
echo ""

echo "📊 Demo 4: Scheduled Monitoring"
echo "-------------------------------"
echo "Set up continuous monitoring (Ctrl+C to stop):"
echo "hackathon-tracker schedule --interval-hours 24 --subreddits hackathons,gitlab,devops"
echo ""

echo ""
echo "🧪 Running Unit Tests"
echo "===================="
python -m pytest tests/ -v --tb=short

echo ""
echo "✅ Demo Complete!"
echo "================="
echo ""
echo "🎯 What the Hackathon Tracker does:"
echo "• Scans Reddit for hackathon announcements"
echo "• Extracts prize amounts, deadlines, and requirements"
echo "• Calculates ROI based on prize vs. effort estimation"
echo "• Ranks opportunities by profitability"
echo "• Filters results by your criteria"
echo "• Exports data for analysis and tracking"
echo ""
echo "💡 Next Steps:"
echo "1. Get Reddit API credentials from https://www.reddit.com/prefs/apps"
echo "2. Fill in the .env file with your credentials"
echo "3. Run: hackathon-tracker search"
echo "4. Filter and export results based on your preferences"
echo ""
echo "📈 Goal: Maximize hackathon earnings and freebies through systematic opportunity discovery!"