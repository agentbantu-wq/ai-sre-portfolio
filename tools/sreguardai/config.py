import yaml
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

DEFAULT_CONFIG = {
    'ollama_url': 'http://localhost:11434',
    'model': 'mistral',
    'audit_log': 'audit.log',
    'blocked_patterns': [
        'delete from',
        'drop table',
        'exec(',
        'eval('
    ]
}

def load_config(config_path='config.yaml'):
    """Load configuration from YAML or return defaults."""
    if Path(config_path).exists():
        try:
            with open(config_path, 'r') as f:
                config = yaml.safe_load(f) or {}
            logger.info(f'Config loaded from {config_path}')
            return {**DEFAULT_CONFIG, **config}
        except Exception as e:
            logger.warning(f'Failed to load config: {e}. Using defaults.')
    else:
        logger.info('No config file found. Using defaults.')
    
    return DEFAULT_CONFIG