import json
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

def load_config(config_path='config.json'):
    try:
        path = Path(config_path)
        if path.exists():
            with open(path) as f:
                config = json.load(f)
        else:
            # Default config with 5 agentic pillars
            config = {
                'pillars': {
                    'context': {'weight': 0.2, 'criteria': ['log_access', 'metric_correlation']},
                    'investigation': {'weight': 0.25, 'criteria': ['root_cause_speed', 'accuracy']},
                    'actionability': {'weight': 0.25, 'criteria': ['remediation_plans', 'mttr_reduction']},
                    'safety': {'weight': 0.15, 'criteria': ['blast_radius', 'human_approval']},
                    'efficiency': {'weight': 0.15, 'criteria': ['escalation_avoidance', 'insight_speed']}
                },
                'scenarios': ['high_cpu', 'db_connection_loss']
            }
            with open(path, 'w') as f:
                json.dump(config, f, indent=2)
        logger.info(f'Config loaded: {len(config.get("pillars", {}))} pillars')
        return config
    except Exception as e:
        logger.error(f'Config load failed: {e}')
        raise
