import logging
import os
import sys
from pathlib import Path
import json
from config import load_config, VENDOR_PATTERNS

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

def scan_credentials(config):
    """Scan local files and env vars for vendor credentials."""
    findings = []
    
    # Scan environment variables
    for vendor, patterns in VENDOR_PATTERNS.items():
        for pattern in patterns:
            for key, value in os.environ.items():
                if pattern.lower() in key.lower() and value:
                    findings.append({
                        'vendor': vendor,
                        'type': 'env_var',
                        'location': key,
                        'severity': 'HIGH'
                    })
    
    # Scan config files
    for config_path in config.get('scan_paths', []):
        path = Path(config_path)
        if path.exists():
            try:
                with open(path, 'r') as f:
                    content = f.read().lower()
                    for vendor, patterns in VENDOR_PATTERNS.items():
                        for pattern in patterns:
                            if pattern.lower() in content:
                                findings.append({
                                    'vendor': vendor,
                                    'type': 'config_file',
                                    'location': str(path),
                                    'severity': 'HIGH'
                                })
            except Exception as e:
                logger.warning(f"Could not scan {config_path}: {e}")
    
    return findings

def generate_report(findings):
    """Generate risk report with remediation steps."""
    if not findings:
        logger.info("No vendor credentials detected.")
        return
    
    logger.warning(f"\n🚨 VENDOR LEAK GUARD REPORT - {len(findings)} finding(s)\n")
    for finding in findings:
        logger.warning(f"[{finding['severity']}] {finding['vendor']} credential in {finding['type']}: {finding['location']}")
        logger.info(f"  → Remediation: Rotate {finding['vendor']} credentials immediately")
    
    return findings

def main():
    config = load_config()
    logger.info("Starting VendorLeakGuard scan...")
    
    findings = scan_credentials(config)
    report = generate_report(findings)
    
    if findings:
        print(json.dumps({'status': 'vulnerabilities_found', 'count': len(findings)}, indent=2))
        sys.exit(1)
    else:
        print(json.dumps({'status': 'clean'}, indent=2))
        sys.exit(0)

if __name__ == '__main__':
    main()