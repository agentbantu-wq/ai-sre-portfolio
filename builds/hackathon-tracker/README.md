# Hackathon Opportunity Tracker - Browser Edition

A comprehensive tool for discovering, analyzing, and ranking hackathon opportunities across multiple sources to maximize your earning potential and participation rewards.

**🚀 NEW: Uses headless browser with your cookies instead of Reddit API - no API keys needed!**

## 🎯 Problem Statement

Finding valuable hackathons that offer good prize money and reasonable effort requirements is challenging. Most developers miss out on high-ROI opportunities because:

- Hackathon announcements are scattered across Reddit, Twitter, email newsletters, and various websites
- No centralized way to compare prize pools, deadlines, and effort requirements
- Difficult to calculate which opportunities offer the best return on time investment
- Manual tracking of multiple sources is time-consuming

## 🚀 Solution

The Hackathon Opportunity Tracker automatically:

- **Scans multiple sources** including Reddit communities, RSS feeds, and web scraping
- **Extracts structured data** from unstructured announcements (prizes, deadlines, requirements)
- **Calculates ROI scores** based on prize money vs. estimated effort hours
- **Ranks opportunities** by profitability and feasibility
- **Filters results** by your criteria (min prize, max effort, ROI thresholds)
- **Exports data** for tracking and analysis

## ✨ Features

### 🔍 Multi-Source Discovery
- **Reddit Integration**: Scans 11+ programming/hackathon subreddits
- **RSS Feed Support**: Monitor newsletters and announcement feeds
- **Web Scraping Ready**: Framework for scraping DevPost, HackerNews, etc.
- **Email Parsing**: Extract opportunities from hackathon emails

### 📊 Intelligent Analysis
- **Prize Extraction**: Automatically identifies prize pools from text ($10,000, €5,000, etc.)
- **Date Parsing**: Extracts deadlines from various formats (March 15, 2024-04-01, etc.)
- **Effort Estimation**: Uses prize pool size and requirements to estimate time investment
- **ROI Calculation**: Prize money ÷ (estimated hours × hourly rate)

### 🎯 Smart Filtering & Ranking
- **Prize Thresholds**: Filter by minimum prize amounts
- **Effort Limits**: Exclude opportunities requiring too many hours
- **ROI Scoring**: Focus on high-return opportunities
- **Keyword Filtering**: Exclude irrelevant or unwanted opportunities
- **Multi-sort Options**: Rank by ROI, prize pool, or deadline

### 💾 Export & Integration
- **JSON Export**: Complete structured data for analysis
- **Excel Export**: Human-readable spreadsheets with key metrics
- **Scheduled Monitoring**: Background scanning for new opportunities
- **Rich Terminal UI**: Beautiful console display with color coding

## 🛠️ Installation

### Prerequisites

- Python 3.8+
- Reddit API credentials (for Reddit scanning)

### 1. Clone and Setup

```bash
git clone https://github.com/yourusername/ai-sre-portfolio.git
cd ai-sre-portfolio/builds/hackathon-tracker
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Reddit API Setup

Create a Reddit app at https://www.reddit.com/prefs/apps

1. Click "Create App" or "Create Another App"
2. Choose "script" as the app type
3. Fill in the details:
   - Name: "Hackathon Tracker"
   - Description: "Track hackathon opportunities"
   - Redirect URI: `http://localhost:8080` (not used for script apps)

4. Note your credentials:
   - **Client ID**: The string under "personal use script"
   - **Client Secret**: The "secret" string

### 4. Environment Configuration

Create a `.env` file in the project root:

```bash
# Reddit API Credentials
REDDIT_CLIENT_ID=your_client_id_here
REDDIT_CLIENT_SECRET=your_client_secret_here
REDDIT_USER_AGENT=HackathonTracker/1.0

# Optional: Your hourly rate for ROI calculations
HOURLY_RATE=50
```

## 🚀 Usage

### Quick Start

Search for hackathon opportunities:

```bash
python -m hackathon_tracker.cli search
```

### Command Reference

#### Search for Opportunities

```bash
# Basic search across default subreddits
hackathon-tracker search

# Custom subreddits and time range
hackathon-tracker search --subreddits hackathons,gitlab,devops --days 14 --limit 50

# Save results to file
hackathon-tracker search --output opportunities.json
```

#### Filter and Rank Results

```bash
# Load and filter saved opportunities
hackathon-tracker filter opportunities.json --min-prize 1000 --max-effort 20 --min-roi 5

# Sort by different criteria
hackathon-tracker filter opportunities.json --sort-by prize

# Exclude certain types of hackathons
hackathon-tracker filter opportunities.json --exclude-keywords "design,ui,ux"
```

#### Export Data

```bash
# Export to Excel (default)
hackathon-tracker export opportunities.json

# Export to JSON with custom filename
hackathon-tracker export opportunities.json --format json --output my_hackathons.json
```

#### Scheduled Monitoring

```bash
# Monitor for new opportunities every 12 hours
hackathon-tracker schedule --interval-hours 12 --subreddits hackathons,gitlab

# Save alerts to custom directory
hackathon-tracker schedule --output-dir ./my_alerts
```

### Example Workflow

1. **Initial Discovery**:
   ```bash
   hackathon-tracker search --output all_opportunities.json
   ```

2. **Filter for High-Value Opportunities**:
   ```bash
   hackathon-tracker filter all_opportunities.json \
     --min-prize 500 \
     --max-effort 40 \
     --min-roi 2 \
     --output high_value.json
   ```

3. **Export for Review**:
   ```bash
   hackathon-tracker export high_value.json --format excel
   ```

4. **Set Up Monitoring**:
   ```bash
   hackathon-tracker schedule --interval-hours 24
   ```

## 📊 Sample Output

```
🔍 Scanning 11 subreddits for hackathon opportunities...
📅 Looking back 30 days, fetching up to 100 posts per subreddit
✅ Found 24 potential opportunities

┌─────────────────────────────────────────────────────────────────────────────┐
│ 🏆 Top Hackathon Opportunities (ROI Ranked)                                │
├─────────────────────────────────────────────────────────────────────────────┤
│ 1. GitLab Ultimate Hackathon 2024                                         │
│    💰 Prize: $15,000 | ⏱️ Effort: 60h | 📈 ROI: 5.0                     │
│    📅 Deadline: 2024-04-15 | 🏷️ Tags: gitlab, devops, kubernetes         │
│    🔗 https://reddit.com/r/gitlab/hackathon-post                          │
│                                                                             │
│ 2. Open Source AI Challenge                                                │
│    💰 Prize: $8,000 | ⏱️ Effort: 30h | 📈 ROI: 5.3                       │
│    📅 Deadline: 2024-03-30 | 🏷️ Tags: ai, python, open-source             │
│    🔗 https://reddit.com/r/opensource/ai-challenge                         │
├─────────────────────────────────────────────────────────────────────────────┤
```

## 🔧 Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `REDDIT_CLIENT_ID` | Reddit API client ID | Required |
| `REDDIT_CLIENT_SECRET` | Reddit API client secret | Required |
| `REDDIT_USER_AGENT` | User agent string | `HackathonTracker/1.0` |
| `HOURLY_RATE` | Your hourly rate for ROI calc | `50` |

### Default Subreddits

The tool scans these subreddits by default:
- `hackathons`
- `programmingopportunities`
- `gitlab`
- `devops`
- `python`
- `javascript`
- `opensource`
- `indiegamedev`
- `startups`
- `datascience`
- `machinelearning`

## 🧪 Testing

Run the test suite:

```bash
python -m pytest tests/
```

Run with coverage:

```bash
python -m pytest tests/ --cov=hackathon_tracker --cov-report=html
```

## 🏗️ Architecture

```
hackathon_tracker/
├── cli.py              # Command-line interface
├── tracker.py          # Core tracking logic
└── __init__.py         # Package initialization

tests/
└── test_tracker.py     # Unit tests

requirements.txt        # Python dependencies
pyproject.toml         # Package configuration
README.md              # This documentation
```

### Key Components

- **HackathonOpportunity**: Data class for structured opportunity data
- **HackathonTracker**: Main orchestrator with Reddit integration and analysis
- **CLI Module**: Click-based command interface
- **Export System**: JSON/Excel output with proper formatting

## 🔮 Future Enhancements

### Phase 2: Multi-Source Integration
- [ ] Twitter/X API integration via Tweepy
- [ ] Email parsing for hackathon newsletters
- [ ] Web scraping for DevPost, HackerNews, AngelList
- [ ] RSS feed monitoring

### Phase 3: Intelligence Layer
- [ ] Machine learning classification (difficulty, category)
- [ ] Success rate prediction based on your skills
- [ ] Personalized recommendations
- [ ] Historical performance tracking

### Phase 4: Automation & Alerts
- [ ] Slack/Discord notifications
- [ ] Calendar integration (Google Calendar, Outlook)
- [ ] Email alerts for high-ROI opportunities
- [ ] Mobile app companion

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

## 📄 License

MIT License - see LICENSE file for details.

## ⚠️ Disclaimer

This tool is for educational and informational purposes. Always verify hackathon details directly from official sources before participating. Prize amounts and requirements may change, and this tool makes reasonable estimates but cannot guarantee accuracy.

## 🆘 Troubleshooting

### Reddit API Issues

**"Invalid client_id" error**:
- Verify your Reddit app credentials in `.env`
- Ensure the app type is "script"
- Check that you're using the correct client ID (not the app name)

**Rate limiting**:
- Reddit API has rate limits; the tool includes delays between requests
- If you hit limits, wait a few minutes before retrying

### Data Quality Issues

**Missing prize information**:
- The tool uses regex patterns to extract prizes
- Some posts may not follow standard formats
- Manual review recommended for important opportunities

**Inaccurate effort estimates**:
- Effort estimation is based on prize pool size and keywords
- This is an approximation; use your judgment for actual time requirements

### Performance Issues

**Slow scanning**:
- Reduce `--limit` parameter
- Scan fewer subreddits
- Increase `--days` to reduce result volume

## 📞 Support

For issues, questions, or feature requests:

1. Check the troubleshooting section above
2. Review existing GitHub issues
3. Create a new issue with:
   - Your environment (OS, Python version)
   - Command you ran
   - Full error output
   - Expected vs. actual behavior