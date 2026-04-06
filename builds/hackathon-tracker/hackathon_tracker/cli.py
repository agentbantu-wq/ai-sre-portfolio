#!/usr/bin/env python3
"""
Hackathon Tracker CLI - Command Line Interface for Hackathon Opportunity Discovery
"""

import click
import json
import os
from pathlib import Path
from typing import Optional, List
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from hackathon_tracker.tracker import HackathonTracker, HackathonOpportunity

@click.group()
@click.version_option(version="1.0.0")
def cli():
    """Hackathon Opportunity Tracker - Discover and rank hackathons for maximum ROI"""
    pass

@cli.command()
@click.option('--subreddits', default='hackathons,programmingopportunities,gitlab,devops,python,javascript,opensource,indiegamedev,startups,datascience,machinelearning',
              help='Comma-separated list of subreddits to scan')
@click.option('--days', default=30, help='Number of days to look back for posts')
@click.option('--limit', default=100, help='Maximum posts to fetch per subreddit')
@click.option('--output', '-o', type=click.Path(), help='Save results to JSON file')
def search(subreddits: str, days: int, limit: int, output: Optional[str]):
    """Search for hackathon opportunities across Reddit"""

    # Parse subreddits
    subreddit_list = [s.strip() for s in subreddits.split(',') if s.strip()]

    click.echo(f"🔍 Scanning {len(subreddit_list)} subreddits for hackathon opportunities...")
    click.echo(f"📅 Looking back {days} days, fetching up to {limit} posts per subreddit")

    try:
        tracker = HackathonTracker()

        # Search for opportunities
        opportunities = tracker.fetch_reddit_hackathons(
            subreddits=subreddit_list,
            days_back=days,
            limit_per_subreddit=limit
        )

        if not opportunities:
            click.echo("❌ No hackathon opportunities found")
            return

        click.echo(f"✅ Found {len(opportunities)} potential opportunities")

        # Display top opportunities
        tracker.display_top_opportunities(opportunities, limit=10)

        # Save to file if requested
        if output:
            output_path = Path(output)
            tracker.export_opportunities(opportunities, str(output_path))
            click.echo(f"💾 Results saved to {output_path}")

    except Exception as e:
        click.echo(f"❌ Error during search: {str(e)}", err=True)
        raise click.Abort()

@cli.command()
@click.argument('input_file', type=click.Path(exists=True))
@click.option('--min-prize', type=float, help='Minimum prize pool in USD')
@click.option('--min-roi', type=float, help='Minimum ROI score (prize / effort)')
@click.option('--max-effort', type=int, help='Maximum effort hours')
@click.option('--exclude-keywords', help='Comma-separated keywords to exclude')
@click.option('--sort-by', type=click.Choice(['roi', 'prize', 'date']), default='roi',
              help='Sort criteria')
@click.option('--output', '-o', type=click.Path(), help='Save filtered results to file')
def filter(input_file: str, min_prize: Optional[float], max_effort: Optional[int],
           min_roi: Optional[float], exclude_keywords: Optional[str],
           sort_by: str, output: Optional[str]):
    """Filter and rank hackathon opportunities"""

    try:
        # Load opportunities from file
        with open(input_file, 'r') as f:
            data = json.load(f)

        opportunities = [HackathonOpportunity(**opp) for opp in data]

        click.echo(f"📊 Loaded {len(opportunities)} opportunities from {input_file}")

        # Apply filters
        filters = {}
        if min_prize is not None:
            filters['min_prize'] = min_prize
        if max_effort is not None:
            filters['max_effort'] = max_effort
        if min_roi is not None:
            filters['min_roi'] = min_roi
        if exclude_keywords:
            filters['exclude_keywords'] = [kw.strip() for kw in exclude_keywords.split(',')]

        filtered_opps = HackathonTracker.filter_opportunities(opportunities, **filters)

        if not filtered_opps:
            click.echo("❌ No opportunities match the filter criteria")
            return

        # Sort and display
        sorted_opps = HackathonTracker.rank_opportunities(filtered_opps, sort_by=sort_by)

        click.echo(f"✅ {len(sorted_opps)} opportunities match filters (sorted by {sort_by})")
        HackathonTracker.display_top_opportunities(sorted_opps, limit=20)

        # Save if requested
        if output:
            tracker = HackathonTracker()
            output_path = Path(output)
            tracker.export_opportunities(sorted_opps, str(output_path))
            click.echo(f"💾 Filtered results saved to {output_path}")

    except Exception as e:
        click.echo(f"❌ Error during filtering: {str(e)}", err=True)
        raise click.Abort()

@cli.command()
@click.argument('input_file', type=click.Path(exists=True))
@click.option('--format', type=click.Choice(['json', 'excel']), default='excel',
              help='Export format')
@click.option('--output', '-o', type=click.Path(), help='Output file path')
def export(input_file: str, format: str, output: Optional[str]):
    """Export hackathon opportunities to JSON or Excel"""

    try:
        # Load opportunities
        with open(input_file, 'r') as f:
            data = json.load(f)

        opportunities = [HackathonOpportunity(**opp) for opp in data]

        # Determine output path
        if not output:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            if format == 'excel':
                output = f"hackathon_opportunities_{timestamp}.xlsx"
            else:
                output = f"hackathon_opportunities_{timestamp}.json"

        output_path = Path(output)

        # Export
        tracker = HackathonTracker()
        tracker.export_opportunities(opportunities, str(output_path), format=format)

        click.echo(f"✅ Exported {len(opportunities)} opportunities to {output_path}")

    except Exception as e:
        click.echo(f"❌ Error during export: {str(e)}", err=True)
        raise click.Abort()

@cli.command()
@click.option('--interval-hours', default=24, help='Scan interval in hours')
@click.option('--subreddits', default='hackathons,gitlab,programmingopportunities',
              help='Subreddits to monitor')
@click.option('--output-dir', default='./hackathon_alerts',
              type=click.Path(), help='Directory to save alerts')
def schedule(interval_hours: int, subreddits: str, output_dir: str):
    """Schedule continuous monitoring for new hackathon opportunities"""

    subreddit_list = [s.strip() for s in subreddits.split(',') if s.strip()]
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)

    click.echo(f"⏰ Starting scheduled monitoring every {interval_hours} hours")
    click.echo(f"📍 Monitoring subreddits: {', '.join(subreddit_list)}")
    click.echo(f"💾 Saving alerts to: {output_path}")

    try:
        tracker = HackathonTracker()

        def scan_and_alert():
            """Scan for new opportunities and save alerts"""
            try:
                opportunities = tracker.fetch_reddit_hackathons(
                    subreddits=subreddit_list,
                    days_back=7,  # Look back 1 week for new posts
                    limit_per_subreddit=50
                )

                if opportunities:
                    # Filter for high-value opportunities
                    high_value = tracker.filter_opportunities(
                        opportunities,
                        min_prize=500,
                        min_roi=10
                    )

                    if high_value:
                        # Save alert file
                        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                        alert_file = output_path / f"alert_{timestamp}.json"

                        tracker.export_opportunities(high_value, str(alert_file))

                        click.echo(f"🚨 Found {len(high_value)} high-value opportunities!")
                        click.echo(f"💾 Alert saved to {alert_file}")

                        # Display top 3
                        tracker.display_top_opportunities(high_value, limit=3)
                    else:
                        click.echo("ℹ️  No high-value opportunities found this scan")
                else:
                    click.echo("ℹ️  No new opportunities found this scan")

            except Exception as e:
                click.echo(f"❌ Scan error: {str(e)}", err=True)

        # Initial scan
        click.echo("🔄 Performing initial scan...")
        scan_and_alert()

        # Schedule future scans (in a real implementation, this would use a scheduler)
        click.echo(f"⏰ Next scan in {interval_hours} hours...")
        click.echo("💡 Use Ctrl+C to stop monitoring")

        # For demo purposes, just show what would happen
        # In production, this would use schedule library or similar
        import time
        try:
            while True:
                time.sleep(interval_hours * 3600)  # Sleep for specified hours
                scan_and_alert()
        except KeyboardInterrupt:
            click.echo("\n🛑 Monitoring stopped by user")

    except Exception as e:
        click.echo(f"❌ Error starting scheduled monitoring: {str(e)}", err=True)
        raise click.Abort()

if __name__ == '__main__':
    cli()