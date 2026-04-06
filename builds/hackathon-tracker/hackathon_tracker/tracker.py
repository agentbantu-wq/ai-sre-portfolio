#!/usr/bin/env python3
"""
Hackathon Opportunity Tracker
Monitor and analyze hackathons for maximum earnings and opportunity ROI
"""

import os
import json
import logging
import re
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, asdict
from collections import defaultdict, Counter
import pandas as pd
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress
import praw
from praw.models import Subreddit
import feedparser
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import schedule
import time

# Load environment variables
load_dotenv()

@dataclass
class HackathonOpportunity:
    """Hackathon opportunity details"""
    title: str
    source: str  # reddit, twitter, email, etc.
    url: str
    start_date: datetime
    end_date: datetime
    deadline_register: Optional[datetime]
    description: str
    prizes: Dict[str, float]  # "1st place": 1000, "participation": 50
    total_prize_pool: float
    currency: str
    platform: str  # gitlab, github, devpost, etc.
    category: str  # web, mobile, ml, devops, etc.
    skill_level: str  # beginner, intermediate, advanced
    requires_team: bool
    team_size: str  # "1-5", "any", etc.
    requirements: List[str]
    extra_benefits: List[str]  # swag, portfolio, etc.
    tags: List[str]
    roi_score: float  # calculated: prize_pool / (hours_effort * hourly_rate)
    effort_hours: int  # estimated hours

class HackathonTracker:
    """Advanced hackathon opportunity tracker"""

    def __init__(self, hourly_rate: float = 50.0):
        """Initialize tracker with hourly rate for ROI calculation"""
        self.hourly_rate = hourly_rate
        self.console = Console()
        self.logger = logging.getLogger(__name__)

        # Reddit API setup
        self.reddit = None
        if os.getenv('REDDIT_CLIENT_ID'):
            self.reddit = praw.Reddit(
                client_id=os.getenv('REDDIT_CLIENT_ID'),
                client_secret=os.getenv('REDDIT_CLIENT_SECRET'),
                user_agent=os.getenv('REDDIT_USER_AGENT', 'hackathon-tracker/1.0')
            )

        # Target subreddits
        self.subreddits = [
            'hackathons',
            'gitlab',
            'github',
            'devops',
            'golang',
            'python',
            'programming',
            'webdev',
            'learnprogramming',
            'opensource',
            'startups'
        ]

        # Keywords to search for
        self.hackathon_keywords = [
            'hackathon', 'competition', 'contest', 'challenge',
            'coding challenge', 'bug bounty', 'building challenge'
        ]

    def fetch_reddit_hackathons(self, subreddits: Optional[List[str]] = None,
                               time_filter: str = 'week') -> List[Dict]:
        """Fetch hackathon posts from Reddit"""
        opportunities = []

        if not self.reddit:
            self.logger.warning("Reddit API not configured")
            return opportunities

        subs = subreddits or self.subreddits

        with Progress() as progress:
            task = progress.add_task("Scanning Reddit...", total=len(subs))

            for sub_name in subs:
                try:
                    subreddit = self.reddit.subreddit(sub_name)

                    # Search for hackathon posts
                    for post in subreddit.top(time_filter=time_filter, limit=50):
                        # Check if post is about hackathon
                        text = (post.title + " " + post.selftext).lower()
                        if any(keyword in text for keyword in self.hackathon_keywords):
                            opp = self._parse_post(post)
                            if opp:
                                opportunities.append(opp)

                except Exception as e:
                    self.logger.error(f"Error fetching from r/{sub_name}: {e}")

                progress.update(task, advance=1)

        return opportunities

    def _parse_post(self, post) -> Optional[Dict]:
        """Parse Reddit post for hackathon details"""
        try:
            content = post.title + "\n" + post.selftext

            # Extract dates
            start_date = self._extract_date_pattern(content, keywords=['starts', 'begins', 'April', 'May'])
            end_date = self._extract_date_pattern(content, keywords=['ends', 'until', 'deadline'])

            if not start_date or not end_date:
                return None

            # Extract prize information
            prizes = self._extract_prizes(content)
            total_pool = sum(prizes.values()) if prizes else 0

            # Extract requirements
            requirements = self._extract_requirements(content)

            return {
                'title': post.title,
                'source': 'reddit',
                'url': post.url,
                'start_date': start_date,
                'end_date': end_date,
                'description': post.selftext[:500],
                'prizes': prizes,
                'total_prize_pool': total_pool,
                'subreddit': post.subreddit.display_name,
                'posted_by': post.author.name if post.author else 'deleted',
                'upvotes': post.score,
                'requirements': requirements,
                'raw_content': content
            }

        except Exception as e:
            self.logger.error(f"Error parsing post: {e}")
            return None

    def _extract_date_pattern(self, content: str, keywords: List[str]) -> Optional[datetime]:
        """Extract dates from content"""
        # Very basic date extraction - in production, use proper NLP
        date_patterns = [
            r'(\d{4}-\d{2}-\d{2})',  # YYYY-MM-DD
            r'(April|May|June)\s+(\d{1,2})(?:st|nd|rd|th)?',  # Month Day
            r'(\d{1,2})-(\d{1,2})\s+(April|May|June)',  # Day-Day Month
        ]

        for pattern in date_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            if matches:
                try:
                    # Try to parse first match
                    if len(matches[0]) == 1:
                        return datetime.strptime(matches[0][0], '%Y-%m-%d')
                    else:
                        # Handle month/day formats
                        date_str = ' '.join(matches[0])
                        # Simple heuristic
                        if 'April' in date_str:
                            day = int(re.findall(r'\d+', date_str)[0])
                            return datetime(2026, 4, day)
                        elif 'May' in date_str:
                            day = int(re.findall(r'\d+', date_str)[0])
                            return datetime(2026, 5, day)
                except:
                    pass

        return None

    def _extract_prizes(self, content: str) -> Dict[str, float]:
        """Extract prize information from content"""
        prizes = {}

        # Pattern: "prize", "$100", etc.
        prize_pattern = r'\$[\d,]+(?:\s*(?:cash|prize|reward|USD))?'
        matches = re.findall(prize_pattern, content, re.IGNORECASE)

        # Extract amounts
        amounts = []
        for match in matches:
            amount_str = match.replace('$', '').replace(',', '')
            try:
                amount = float(amount_str.split()[0])
                amounts.append(amount)
            except:
                pass

        # Assign to places if possible
        if amounts:
            amounts.sort(reverse=True)
            places = ['1st place', '2nd place', '3rd place', 'participation']
            for i, amount in enumerate(amounts[:len(places)]):
                prizes[places[i]] = amount

        return prizes

    def _extract_requirements(self, content: str) -> List[str]:
        """Extract requirements from content"""
        requirements = []

        req_patterns = [
            r'require[s]*:?\s*([^\n\.]+)',
            r'requirement[s]*:?\s*([^\n\.]+)',
            r'must\s+([^\n\.]+)',
        ]

        for pattern in req_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            requirements.extend(matches)

        return list(set(requirements))[:5]  # Top 5 unique

    def calculate_roi(self, opportunity: Dict) -> float:
        """Calculate ROI (return on investment) for opportunity"""
        total_prize = opportunity.get('total_prize_pool', 0)

        # Estimate effort (in hours)
        prize_to_effort = {
            0: 2,          # < $100 = 2 hours
            100: 4,        # $100-500 = 4 hours
            500: 8,        # $500-1000 = 8 hours
            1000: 16,      # $1000-5000 = 16 hours
            5000: 40,      # $5000+ = 40 hours
        }

        effort_hours = 8  # Default
        for threshold, hours in sorted(prize_to_effort.items()):
            if total_prize >= threshold:
                effort_hours = hours

        # ROI = (Total Prize / Effort Hours) / Hourly Rate
        roi = (total_prize / effort_hours) / self.hourly_rate if effort_hours > 0 else 0

        return roi

    def rank_opportunities(self, opportunities: List[Dict],
                          sort_by: str = 'roi') -> List[Dict]:
        """Rank opportunities by various metrics"""
        ranked = []

        for opp in opportunities:
            roi = self.calculate_roi(opp)
            opp['roi_score'] = roi
            opp['prize_per_hour'] = opp.get('total_prize_pool', 0) / max(1, self._estimate_effort(opp))
            ranked.append(opp)

        # Sort by requested metric
        if sort_by == 'roi':
            ranked.sort(key=lambda x: x['roi_score'], reverse=True)
        elif sort_by == 'prize':
            ranked.sort(key=lambda x: x['total_prize_pool'], reverse=True)
        elif sort_by == 'time':
            ranked.sort(key=lambda x: x['start_date'])

        return ranked

    def _estimate_effort(self, opportunity: Dict) -> int:
        """Estimate effort hours for an opportunity"""
        prize = opportunity.get('total_prize_pool', 0)

        if prize < 100:
            return 2
        elif prize < 500:
            return 4
        elif prize < 1000:
            return 8
        elif prize < 5000:
            return 16
        else:
            return 40

    def filter_opportunities(self, opportunities: List[Dict],
                            min_prize: float = 0,
                            min_roi: float = 0,
                            max_effort_hours: int = 40,
                            exclude_keywords: Optional[List[str]] = None) -> List[Dict]:
        """Filter opportunities by criteria"""
        filtered = []

        for opp in opportunities:
            roi = opp.get('roi_score', self.calculate_roi(opp))
            effort = self._estimate_effort(opp)

            # Check filters
            if opp.get('total_prize_pool', 0) < min_prize:
                continue
            if roi < min_roi:
                continue
            if effort > max_effort_hours:
                continue

            # Check excluded keywords
            if exclude_keywords:
                content = (opp.get('title', '') + ' ' + opp.get('description', '')).lower()
                if any(kw in content for kw in exclude_keywords):
                    continue

            filtered.append(opp)

        return filtered

    def export_opportunities(self, opportunities: List[Dict],
                           format: str = 'json',
                           filename: Optional[str] = None) -> str:
        """Export opportunities to file"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"hackathons_{timestamp}.{format}"

        if format == 'json':
            # Convert datetime objects
            data = []
            for opp in opportunities:
                opp_copy = opp.copy()
                opp_copy['start_date'] = opp_copy['start_date'].isoformat() if isinstance(opp_copy['start_date'], datetime) else str(opp_copy['start_date'])
                opp_copy['end_date'] = opp_copy['end_date'].isoformat() if isinstance(opp_copy['end_date'], datetime) else str(opp_copy['end_date'])
                data.append(opp_copy)

            with open(filename, 'w') as f:
                json.dump(data, f, indent=2, default=str)

        elif format == 'xlsx':
            # Create simplified dataframe for Excel
            export_data = []
            for opp in opportunities:
                export_data.append({
                    'Title': opp.get('title'),
                    'Platform': opp.get('source'),
                    'Total Prize': opp.get('total_prize_pool', 0),
                    'Start Date': opp.get('start_date'),
                    'End Date': opp.get('end_date'),
                    'ROI Score': opp.get('roi_score', 0),
                    'Effort (hrs)': self._estimate_effort(opp),
                    'URL': opp.get('url')
                })

            df = pd.DataFrame(export_data)
            df.to_excel(filename, index=False)

        return filename

    def display_top_opportunities(self, opportunities: List[Dict], count: int = 10):
        """Display top opportunities in rich table"""
        table = Table(title=f"Top {count} Hackathon Opportunities")
        table.add_column("Title", style="cyan", max_width=30)
        table.add_column("Prize", style="green", justify="right")
        table.add_column("ROI Score", style="yellow", justify="right")
        table.add_column("Effort (hrs)", justify="right")
        table.add_column("Dates", style="magenta")

        for i, opp in enumerate(opportunities[:count]):
            roi = opp.get('roi_score', 0)
            roi_style = "green" if roi > 10 else "yellow" if roi > 5 else "red"

            start = opp.get('start_date')
            end = opp.get('end_date')
            date_str = f"{start.strftime('%m/%d')}-{end.strftime('%m/%d')}" if start and end else "N/A"

            table.add_row(
                opp.get('title', '')[:30],
                f"${opp.get('total_prize_pool', 0):,.0f}",
                f"{roi:.1f}",
                str(self._estimate_effort(opp)),
                date_str
            )

        self.console.print(table)

        # Summary stats
        if opportunities:
            total_prize = sum(o.get('total_prize_pool', 0) for o in opportunities[:count])
            avg_roi = sum(o.get('roi_score', 0) for o in opportunities[:count]) / count

            summary = Panel(
                f"[green]Total Prize Pool (Top {count}[/green]): ${total_prize:,.0f}\n"
                f"[yellow]Average ROI Score[/yellow]: {avg_roi:.1f}",
                title="Summary"
            )
            self.console.print(summary)