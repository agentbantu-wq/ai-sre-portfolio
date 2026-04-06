#!/usr/bin/env python3
"""
Quick script to scan for GitLab hackathons
"""
from hackathon_tracker.tracker import HackathonTracker
import os

os.environ['HEADLESS'] = 'true'
tracker = HackathonTracker()

print('Scanning for GitLab hackathons...')
try:
    opportunities = tracker.fetch_reddit_hackathons(subreddits=['hackathons'])
    gitlab_hacks = [opp for opp in opportunities if 'gitlab' in opp.get('title', '').lower() or 'gitlab' in opp.get('description', '').lower()]

    print(f'Found {len(gitlab_hacks)} GitLab-related hackathons:')
    for opp in gitlab_hacks[:3]:  # Show first 3
        print(f'- {opp.get("title", "Unknown")}')
        print(f'  Prize: ${opp.get("total_prize_pool", 0)}')
        print(f'  URL: {opp.get("url", "N/A")}')
        print()

except Exception as e:
    print(f'Error scanning: {e}')
finally:
    tracker._close_browser()