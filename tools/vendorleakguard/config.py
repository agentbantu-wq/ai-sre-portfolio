import os
from pathlib import Path

# Vendor credential patterns
VENDOR_PATTERNS = {
    'BrowserStack': ['browserstack_key', 'browserstack_user', 'browserstack_token', 'bs_key'],
    'AWS': ['aws_access_key', 'aws_secret_key', 'aws_session_token'],
    'DataDog': ['datadog_api_key', 'dd_api_key'],
    'New Relic': ['newrelic_api_key', 'nr_api_key'],
    'Slack': ['slack_token', 'slack_webhook'],
}

def load_config():
    """Load configuration from environment or defaults."""
    return {
        'scan_paths': [
            os.getenv('SCAN_PATH', '.'),
            os.path.expanduser('~/.aws/credentials'),
            os.path.expanduser('~/.config'),
            Path.cwd() / '.env',
            Path.cwd() / 'config.yml',
            Path.cwd() / 'config.yaml',
        ],
        'breach_db_url': os.getenv('BREACH_DB_URL', 'https://api.example.com/breaches'),
        'alert_email': os.getenv('ALERT_EMAIL', ''),
        'severity_threshold': os.getenv('SEVERITY_THRESHOLD', 'HIGH'),
    }