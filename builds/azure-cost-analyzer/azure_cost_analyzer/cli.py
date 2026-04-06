#!/usr/bin/env python3
"""
Azure Cost Analyzer - CLI
"""

import click
import json
from datetime import datetime, timedelta
from azure_cost_analyzer.analyzer import AzureCostAnalyzer

@click.group()
@click.option('--subscription-id', envvar='AZURE_SUBSCRIPTION_ID', help='Azure subscription ID')
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose logging')
def cli(subscription_id, verbose):
    """Azure Cost Analyzer - Track and optimize Azure spending"""
    if verbose:
        import logging
        logging.basicConfig(level=logging.INFO)

    global analyzer
    analyzer = AzureCostAnalyzer(subscription_id)

@cli.command()
@click.option('--days', '-d', default=30, help='Days to analyze')
@click.option('--group-by', '-g', default='ResourceType', help='Group by dimension')
@click.option('--output', '-o', help='Output file')
@click.option('--format', '-f', type=click.Choice(['json', 'xlsx']), default='json')
def analyze(days, group_by, output, format):
    """Analyze Azure costs"""
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)

    click.echo(f"Analyzing costs from {start_date.date()} to {end_date.date()}...")

    costs = analyzer.get_costs(start_date, end_date, group_by)

    if not costs:
        click.echo("No cost data found for the specified period.")
        return

    click.echo(f"Retrieved {len(costs)} cost records. Analyzing...")

    # Analyze
    breakdown = analyzer.analyze_breakdown(costs)
    trends = analyzer.calculate_trends(costs)
    anomalies = analyzer.detect_anomalies(costs)
    recommendations = analyzer.generate_optimization_recommendations(costs, trends, anomalies)

    # Display
    analyzer.display_cost_summary(costs, breakdown, trends, anomalies)

    # Export
    if output:
        filename = analyzer.export_report(costs, breakdown, trends, anomalies, recommendations, format, output)
        click.echo(f"Report exported to {filename}")
    else:
        # Show top recommendations
        if recommendations:
            click.echo("\nTop Cost Optimization Opportunities:")
            for i, rec in enumerate(recommendations[:5], 1):
                click.echo(f"{i}. [{rec['priority']}] {rec['recommendation']}")
                click.echo(f"   Potential savings: ${rec['estimated_savings']:,.2f}")

@cli.command()
@click.option('--days', '-d', default=30, help='Days to analyze')
@click.option('--threshold', '-t', default=2.0, help='Anomaly threshold (std dev)')
@click.option('--severity', '-s', type=click.Choice(['all', 'high', 'critical']), default='all')
def anomalies(days, threshold, severity):
    """Detect cost anomalies"""
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)

    costs = analyzer.get_costs(start_date, end_date)

    if not costs:
        click.echo("No cost data found.")
        return

    anomaly_list = analyzer.detect_anomalies(costs, threshold_std_dev=threshold)

    # Filter by severity
    if severity != 'all':
        anomaly_list = [a for a in anomaly_list if a.severity == severity]

    if not anomaly_list:
        click.echo("No anomalies detected.")
        return

    click.echo(f"Found {len(anomaly_list)} anomalies:")
    for anomaly in anomaly_list[:10]:
        click.echo(f"\n[{anomaly.severity.upper()}] {anomaly.resource} on {anomaly.date.date()}")
        click.echo(f"  Cost: ${anomaly.actual_cost:,.2f} (deviation: {anomaly.deviation_percent:+.1f}%)")

@cli.command()
@click.option('--days', '-d', default=30, help='Days to analyze')
@click.option('--format', '-f', type=click.Choice(['json', 'html']), default='json')
@click.option('--output', '-o', required=True, help='Output file')
def dashboard(days, format, output):
    """Generate dashboard data"""
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)

    costs = analyzer.get_costs(start_date, end_date)

    if not costs:
        click.echo("No cost data found.")
        return

    breakdown = analyzer.analyze_breakdown(costs)
    
    dashboard_data = {
        'total_cost': sum(c.cost for c in costs),
        'period': {'start': start_date.isoformat(), 'end': end_date.isoformat()},
        'breakdown': {k: dict(list(v.items())[:10]) for k, v in breakdown.items()}
    }

    with open(output, 'w') as f:
        json.dump(dashboard_data, f, indent=2, default=str)

    click.echo(f"Dashboard data exported to {output}")

@cli.command()
@click.option('--days', '-d', default=30, help='Days to analyze')
def trends(days):
    """Show cost trends"""
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)

    costs = analyzer.get_costs(start_date, end_date)

    if not costs:
        click.echo("No cost data found.")
        return

    trend_list = analyzer.calculate_trends(costs, days)

    click.echo(f"\nCost Trends (Last {days} days):")
    for trend in trend_list[:10]:
        direction = "↑" if trend.trend_direction == "up" else "↓" if trend.trend_direction == "down" else "→"
        click.echo(f"\n{trend.resource_type}")
        click.echo(f"  Total: ${trend.total_cost:,.2f}")
        click.echo(f"  Daily Avg: ${trend.avg_daily_cost:,.2f}")
        click.echo(f"  Trend: {direction} {trend.mom_change_percent:+.1f}%")

if __name__ == '__main__':
    cli()