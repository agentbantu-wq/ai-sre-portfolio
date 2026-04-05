"""
Core evaluation logic for AI SRE tool assessment
"""

import yaml
from typing import Dict, Any, List
from dataclasses import dataclass, asdict
import click


@dataclass
class PillarScore:
    """Single pillar evaluation result"""
    name: str
    score: int
    max_score: int
    passed: List[str]
    failed: List[str]
    notes: str


class Evaluator:
    """Main evaluation engine"""
    
    PILLARS = ['context', 'investigation', 'actionability', 'safety', 'efficiency']
    
    def __init__(self, tool_name: str, checklist: Dict[str, Any]):
        self.tool_name = tool_name
        self.checklist = checklist
        self.results = {}
    
    def run_interactive(self) -> Dict[str, Any]:
        """Run interactive evaluation with user prompts"""
        scores = {}
        total_score = 0
        max_total = 0
        
        for pillar in self.PILLARS:
            if pillar not in self.checklist:
                click.echo(f"⚠️  Pillar '{pillar}' not in checklist")
                continue
            
            criteria = self.checklist[pillar]
            click.echo(f"\n📋 {pillar.upper()}", fg='cyan')
            click.echo("-" * 40)
            
            pillar_score = 0
            max_pillar = len(criteria) if isinstance(criteria, list) else 0
            
            for i, criterion in enumerate(criteria, 1):
                if isinstance(criterion, dict):
                    name = criterion.get('name', f'Criterion {i}')
                    description = criterion.get('description', '')
                else:
                    name = criterion
                    description = ''
                
                click.echo(f"\n{i}. {name}")
                if description:
                    click.echo(f"   {description}")
                
                # Simple yes/no scoring
                response = click.confirm("   Pass?", default=False)
                if response:
                    pillar_score += 1
            
            scores[pillar] = {
                'score': pillar_score,
                'max': max_pillar,
                'percentage': (pillar_score / max_pillar * 100) if max_pillar > 0 else 0
            }
            total_score += pillar_score
            max_total += max_pillar
        
        # Calculate final score (0-100 scale)
        final_score = int((total_score / max_total * 100)) if max_total > 0 else 0
        
        return {
            'tool': self.tool_name,
            'total': final_score,
            'raw_score': total_score,
            'max_score': max_total,
            'pillars': scores,
            'recommendation': self._get_recommendation(final_score)
        }
    
    def _get_recommendation(self, score: int) -> Dict[str, Any]:
        """Generate recommendation based on score"""
        if score >= 80:
            return {
                'status': '✅ PRODUCTION READY',
                'message': 'Tool is suitable for production deployment',
                'risk': 'Low'
            }
        elif score >= 60:
            return {
                'status': '⚠️  CAUTION',
                'message': 'Tool is usable but has gaps; start with low-risk incidents',
                'risk': 'Medium'
            }
        else:
            return {
                'status': '❌ NOT READY',
                'message': 'Tool needs significant work before production use',
                'risk': 'High'
            }
