#!/usr/bin/env python3

"""
AI-SRE-Readiness-Checker
CLI entry point for evaluating AI SRE tools
"""

import click
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

from .evaluator import Evaluator
from .config import load_config


@click.command()
@click.option('--tool', prompt='Tool name', help='Name of AI SRE tool to evaluate')
@click.option('--config', type=click.Path(exists=True), help='Path to checklist config YAML')
@click.option('--output', type=click.Path(), default=None, help='Output file path')
@click.option('--format', type=click.Choice(['html', 'json', 'text']), default='html')
def main(tool: str, config: Optional[str], output: Optional[str], format: str):
    """
    Evaluate an AI SRE tool for production readiness.
    
    Example:
        ai-sre-readiness --tool "PagerDuty Event Intelligence"
        ai-sre-readiness --tool "DataDog Incident AI" --config checklists/production_ready.yaml
    """
    click.echo("\n🔍 AI/SRE Readiness Checker", fg='cyan', bold=True))
    click.echo("=" * 50)
    
    # Load config
    if config:
        checklist = load_config(config)
        click.echo(f"✅ Loaded config: {config}")
    else:
        # Use default
        default_config = Path(__file__).parent.parent / "checklists" / "production_ready.yaml"
        checklist = load_config(str(default_config))
        click.echo(f"ℹ️  Using default checklist")
    
    click.echo(f"📋 Evaluating: {tool}\n")
    
    # Interactive evaluation
    evaluator = Evaluator(tool, checklist)
    score = evaluator.run_interactive()
    
    # Generate report
    click.echo("\n" + "=" * 50)
    click.echo(f"✅ Evaluation Complete: {score['total']}/100\n")
    
    # Print summary
    click.echo("📊 Pillar Scores:")
    for pillar, pillar_score in score['pillars'].items():
        status = "✅" if pillar_score['score'] >= 15 else "⚠️ "
        click.echo(f"  {status} {pillar.title()}: {pillar_score['score']}/20")
    
    # Save report
    if output is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output = f"readiness_report_{tool.lower().replace(' ', '_')}_{timestamp}.json"
    
    with open(output, 'w') as f:
        json.dump(score, f, indent=2)
    
    click.echo(f"\n📁 Report saved: {output}")
    click.echo("=" * 50 + "\n")
    
    return 0 if score['total'] >= 60 else 1


if __name__ == '__main__':
    sys.exit(main())
