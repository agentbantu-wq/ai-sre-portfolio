#!/usr/bin/env python3
"""
SSL Certificate Expiry Checker - CLI
"""

import click
import json
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))
from ssl_checker import SSLChecker

@click.group()
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose logging')
def cli(verbose):
    """SSL Certificate Expiry Checker"""
    if verbose:
        import logging
        logging.basicConfig(level=logging.INFO)

@cli.command()
@click.argument('domains', nargs=-1)
@click.option('--output', '-o', help='Output file')
@click.option('--format', '-f', type=click.Choice(['json', 'csv', 'xlsx']), default='json')
@click.option('--warning-days', '-w', default=30, help='Days before expiry to warn')
def check(domains, output, format, warning_days):
    """Check SSL certificates for domains"""
    if not domains:
        click.echo("No domains provided. Use --help for usage.")
        sys.exit(1)

    checker = SSLChecker(warning_days=warning_days)
    results = checker.check_domains(list(domains))

    if results:
        checker.display_results(results)

        if output:
            filename = checker.export_results(results, format, output)
            click.echo(f"Results exported to {filename}")
    else:
        click.echo("No results obtained")

@cli.command()
@click.argument('csv_file')
@click.option('--output', '-o', help='Output file')
@click.option('--format', '-f', type=click.Choice(['json', 'csv', 'xlsx']), default='json')
@click.option('--warning-days', '-w', default=30, help='Days before expiry to warn')
def check_csv(csv_file, output, format, warning_days):
    """Check SSL certificates from CSV file"""
    checker = SSLChecker(warning_days=warning_days)
    results = checker.check_from_csv(csv_file)

    if results:
        checker.display_results(results)

        if output:
            filename = checker.export_results(results, format, output)
            click.echo(f"Results exported to {filename}")
    else:
        click.echo("No results obtained")

@cli.command()
@click.argument('api_url')
@click.option('--output', '-o', help='Output file')
@click.option('--format', '-f', type=click.Choice(['json', 'csv', 'xlsx']), default='json')
@click.option('--warning-days', '-w', default=30, help='Days before expiry to warn')
def check_api(api_url, output, format, warning_days):
    """Check SSL certificates from API endpoint"""
    checker = SSLChecker(warning_days=warning_days)
    results = checker.check_from_api(api_url)

    if results:
        checker.display_results(results)

        if output:
            filename = checker.export_results(results, format, output)
            click.echo(f"Results exported to {filename}")
    else:
        click.echo("No results obtained")

@cli.command()
@click.argument('domains', nargs=-1)
@click.option('--interval', '-i', default=24, help='Check interval in hours')
@click.option('--warning-days', '-w', default=30, help='Days before expiry to warn')
def monitor(domains, interval, warning_days):
    """Monitor SSL certificates continuously"""
    if not domains:
        click.echo("No domains provided. Use --help for usage.")
        sys.exit(1)

    checker = SSLChecker(warning_days=warning_days)
    click.echo(f"Starting SSL monitoring for {len(domains)} domains...")
    click.echo(f"Checks every {interval} hours. Press Ctrl+C to stop.")

    try:
        checker.schedule_checks(list(domains), interval)
    except KeyboardInterrupt:
        click.echo("\nMonitoring stopped.")

if __name__ == '__main__':
    cli()