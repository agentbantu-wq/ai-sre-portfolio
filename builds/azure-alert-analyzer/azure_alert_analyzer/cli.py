#!/usr/bin/env python3
"""
Azure Alert Analyzer - CLI
"""

import click
import json
from datetime import datetime, timedelta
from azure_alert_analyzer.analyzer import AzureAlertAnalyzer

@click.group()
@click.option('--subscription-id', envvar='AZURE_SUBSCRIPTION_ID', help='Azure subscription ID')
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose logging')
def cli(subscription_id, verbose):
    """Azure Monitor Alert Analyzer"""
    if verbose:
        import logging
        logging.basicConfig(level=logging.INFO)

    global analyzer
    analyzer = AzureAlertAnalyzer(subscription_id)

@cli.command()
@click.option('--resource-group', '-g', help='Resource group filter')
@click.option('--days', '-d', default=7, help='Days to look back')
@click.option('--status', help='Alert status filter')
@click.option('--output', '-o', help='Output file')
@click.option('--format', '-f', type=click.Choice(['json', 'xlsx']), default='json')
def analyze(resource_group, days, status, output, format):
    """Analyze Azure Monitor alerts"""
    end_time = datetime.now()
    start_time = end_time - timedelta(days=days)

    click.echo(f"Analyzing alerts from {start_time.date()} to {end_time.date()}...")

    alerts = analyzer.get_alerts(resource_group, start_time, end_time, status)

    if not alerts:
        click.echo("No alerts found in the specified time range.")
        return

    click.echo(f"Found {len(alerts)} alerts. Analyzing patterns...")

    patterns = analyzer.analyze_patterns(alerts)
    correlations = analyzer.correlate_alerts(alerts)
    recommendations = analyzer.generate_recommendations(patterns)

    # Display summary
    analyzer.display_summary(alerts, patterns)

    # Export report
    if output:
        filename = analyzer.export_report(alerts, patterns, correlations, recommendations, format, output)
        click.echo(f"Report exported to {filename}")
    else:
        # Show top recommendations
        if recommendations:
            click.echo("\nTop Recommendations:")
            for i, rec in enumerate(recommendations[:5], 1):
                click.echo(f"{i}. [{rec['priority']}] {rec['recommendation']}")

@cli.command()
@click.option('--days', '-d', default=7, help='Days to look back')
@click.option('--output', '-o', help='Dashboard data output file')
def dashboard(days, output):
    """Generate dashboard data"""
    end_time = datetime.now()
    start_time = end_time - timedelta(days=days)

    alerts = analyzer.get_alerts(start_time=start_time, end_time=end_time)
    patterns = analyzer.analyze_patterns(alerts)

    dashboard_data = analyzer.create_dashboard_data(alerts, patterns)

    if output:
        with open(output, 'w') as f:
            json.dump(dashboard_data, f, indent=2, default=str)
        click.echo(f"Dashboard data exported to {output}")
    else:
        click.echo(json.dumps(dashboard_data, indent=2, default=str))

@cli.command()
@click.option('--resource-group', '-g', help='Resource group')
@click.option('--alert-name', help='Alert rule name')
@click.option('--description', help='Alert description')
@click.option('--severity', type=int, default=2, help='Severity (0-4)')
@click.option('--query', help='Log query for alert condition')
@click.option('--frequency', default='PT5M', help='Evaluation frequency')
@click.option('--window', default='PT5M', help='Time window')
def create_alert(resource_group, alert_name, description, severity, query, frequency, window):
    """Create a new alert rule"""
    # This would implement alert rule creation
    click.echo("Alert rule creation not yet implemented")
    click.echo(f"Would create alert: {alert_name} in {resource_group}")

if __name__ == '__main__':
    cli()