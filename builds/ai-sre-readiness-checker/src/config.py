"""
Configuration loading and parsing
"""

import yaml
from typing import Dict, Any
from pathlib import Path


def load_config(config_path: str) -> Dict[str, Any]:
    """Load YAML checklist configuration"""
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    return config


def get_default_checklist() -> Dict[str, Any]:
    """Return default production-ready checklist"""
    return {
        'context': [
            {'name': 'Accesses metrics', 'description': 'Can pull metrics from monitoring system (Prometheus, DataDog, etc.)'},
            {'name': 'Accesses logs', 'description': 'Can search and retrieve logs'},
            {'name': 'Accesses traces', 'description': 'Can access distributed traces'},
            {'name': 'Can fetch runbooks', 'description': 'Can retrieve playbooks/runbooks'},
            {'name': 'Understands context', 'description': 'Creates baseline of normal behavior'},
        ],
        'investigation': [
            {'name': 'Correlates logs+metrics', 'description': 'Can find relationships between signals'},
            {'name': 'Identifies patterns', 'description': 'Can spot recurring anomalies'},
            {'name': 'Suggests root cause', 'description': 'Points to likely root cause'},
            {'name': 'Articulates confidence', 'description': 'Gives confidence score on findings'},
        ],
        'actionability': [
            {'name': 'Can dry-run', 'description': 'Supports testing fixes without applying'},
            {'name': 'Auto-remediate', 'description': 'Can execute fixes autonomously'},
            {'name': 'Suggests remediation', 'description': 'Recommends specific actions'},
            {'name': 'Respects change windows', 'description': 'Won\'t act outside maintenance windows'},
        ],
        'safety': [
            {'name': 'Audit log', 'description': 'Records all decisions and actions'},
            {'name': 'Guardrails', 'description': 'Has configurable safety limits'},
            {'name': 'Requires approval', 'description': 'Can require human approval for actions'},
            {'name': 'Rate limiting', 'description': 'Prevents action spam'},
        ],
        'efficiency': [
            {'name': 'Fast response', 'description': 'Responds in < 10 seconds'},
            {'name': 'Low overhead', 'description': 'Uses < 5% additional resources'},
            {'name': 'Scales', 'description': 'Performance holds as incident volume grows'},
        ]
    }
