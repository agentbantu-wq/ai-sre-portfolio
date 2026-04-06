#!/usr/bin/env python3
"""
SSL Certificate Expiry Checker
Advanced tool for monitoring SSL certificate expiration dates
"""

import ssl
import socket
import datetime
import json
import csv
import logging
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from cryptography import x509
from cryptography.hazmat.backends import default_backend
import requests
import pandas as pd
from rich.console import Console
from rich.table import Table
from rich.progress import Progress
import schedule
import time
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

@dataclass
class SSLInfo:
    """SSL certificate information"""
    domain: str
    issuer: str
    subject: str
    valid_from: datetime.datetime
    valid_until: datetime.datetime
    days_remaining: int
    is_expired: bool
    is_expiring_soon: bool
    serial_number: str
    signature_algorithm: str
    key_size: Optional[int] = None

class SSLChecker:
    """Advanced SSL certificate checker"""

    def __init__(self, timeout: int = 10, warning_days: int = 30):
        self.timeout = timeout
        self.warning_days = warning_days
        self.console = Console()
        self.logger = logging.getLogger(__name__)

    def get_certificate_info(self, hostname: str, port: int = 443) -> Optional[SSLInfo]:
        """Get SSL certificate information for a domain"""
        try:
            # Create SSL context
            context = ssl.create_default_context()
            context.check_hostname = False
            context.verify_mode = ssl.CERT_NONE

            with socket.create_connection((hostname, port), timeout=self.timeout) as sock:
                with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                    cert_der = ssock.getpeercert(binary_form=True)

            # Parse certificate
            cert = x509.load_der_x509_certificate(cert_der, default_backend())

            # Extract information
            issuer = cert.issuer.rfc4514_string()
            subject = cert.subject.rfc4514_string()
            valid_from = cert.not_valid_before
            valid_until = cert.not_valid_after
            now = datetime.datetime.now()

            days_remaining = (valid_until - now).days
            is_expired = valid_until < now
            is_expiring_soon = days_remaining <= self.warning_days and not is_expired

            # Get key size if RSA
            key_size = None
            try:
                public_key = cert.public_key()
                if hasattr(public_key, 'key_size'):
                    key_size = public_key.key_size
            except:
                pass

            return SSLInfo(
                domain=hostname,
                issuer=issuer,
                subject=subject,
                valid_from=valid_from,
                valid_until=valid_until,
                days_remaining=days_remaining,
                is_expired=is_expired,
                is_expiring_soon=is_expiring_soon,
                serial_number=str(cert.serial_number),
                signature_algorithm=cert.signature_algorithm_oid._name,
                key_size=key_size
            )

        except Exception as e:
            self.logger.error(f"Error checking {hostname}: {e}")
            return None

    def check_domains(self, domains: List[str]) -> List[SSLInfo]:
        """Check multiple domains"""
        results = []

        with Progress() as progress:
            task = progress.add_task("Checking SSL certificates...", total=len(domains))

            for domain in domains:
                result = self.get_certificate_info(domain)
                if result:
                    results.append(result)
                progress.update(task, advance=1)

        return results

    def check_from_csv(self, csv_file: str) -> List[SSLInfo]:
        """Check domains from CSV file"""
        domains = []
        try:
            with open(csv_file, 'r') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if 'domain' in row:
                        domains.append(row['domain'])
        except Exception as e:
            self.logger.error(f"Error reading CSV: {e}")
            return []

        return self.check_domains(domains)

    def check_from_api(self, api_url: str) -> List[SSLInfo]:
        """Check domains from API endpoint"""
        try:
            response = requests.get(api_url, timeout=self.timeout)
            response.raise_for_status()
            data = response.json()

            domains = []
            if isinstance(data, list):
                domains = [item.get('domain') for item in data if item.get('domain')]
            elif isinstance(data, dict) and 'domains' in data:
                domains = data['domains']

            return self.check_domains(domains)
        except Exception as e:
            self.logger.error(f"Error fetching from API: {e}")
            return []

    def export_results(self, results: List[SSLInfo], format: str = 'json', filename: str = None) -> str:
        """Export results to file"""
        if not filename:
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"ssl_check_{timestamp}.{format}"

        data = [self._ssl_info_to_dict(r) for r in results]

        if format == 'json':
            with open(filename, 'w') as f:
                json.dump(data, f, indent=2, default=str)
        elif format == 'csv':
            if data:
                df = pd.DataFrame(data)
                df.to_csv(filename, index=False)
        elif format == 'xlsx':
            if data:
                df = pd.DataFrame(data)
                df.to_excel(filename, index=False)

        return filename

    def _ssl_info_to_dict(self, info: SSLInfo) -> Dict:
        """Convert SSLInfo to dictionary"""
        return {
            'domain': info.domain,
            'issuer': info.issuer,
            'subject': info.subject,
            'valid_from': info.valid_from.isoformat(),
            'valid_until': info.valid_until.isoformat(),
            'days_remaining': info.days_remaining,
            'is_expired': info.is_expired,
            'is_expiring_soon': info.is_expiring_soon,
            'serial_number': info.serial_number,
            'signature_algorithm': info.signature_algorithm,
            'key_size': info.key_size
        }

    def display_results(self, results: List[SSLInfo]):
        """Display results in a rich table"""
        table = Table(title="SSL Certificate Status")
        table.add_column("Domain", style="cyan")
        table.add_column("Days Left", justify="right")
        table.add_column("Valid Until", style="yellow")
        table.add_column("Status", style="green")

        expired = []
        expiring_soon = []

        for result in results:
            if result.is_expired:
                status = "[red]EXPIRED[/red]"
                expired.append(result)
            elif result.is_expiring_soon:
                status = "[orange]EXPIRING SOON[/orange]"
                expiring_soon.append(result)
            else:
                status = "[green]VALID[/green]"

            table.add_row(
                result.domain,
                str(result.days_remaining),
                result.valid_until.strftime("%Y-%m-%d"),
                status
            )

        self.console.print(table)

        if expired:
            self.console.print(f"\n[red]⚠️  {len(expired)} certificates have expired![/red]")
        if expiring_soon:
            self.console.print(f"\n[orange]⚠️  {len(expiring_soon)} certificates expiring within {self.warning_days} days![/orange]")

    def send_alert_email(self, results: List[SSLInfo], smtp_config: Dict):
        """Send alert email for expired/expiring certificates"""
        expired = [r for r in results if r.is_expired]
        expiring_soon = [r for r in results if r.is_expiring_soon]

        if not expired and not expiring_soon:
            return

        msg = MIMEMultipart()
        msg['From'] = smtp_config['from_email']
        msg['To'] = smtp_config['to_email']
        msg['Subject'] = "SSL Certificate Alert"

        body = "SSL Certificate Status Report\n\n"

        if expired:
            body += f"EXPIRED CERTIFICATES ({len(expired)}):\n"
            for cert in expired:
                body += f"- {cert.domain}: Expired on {cert.valid_until.strftime('%Y-%m-%d')}\n"
            body += "\n"

        if expiring_soon:
            body += f"CERTIFICATES EXPIRING SOON ({len(expiring_soon)}):\n"
            for cert in expiring_soon:
                body += f"- {cert.domain}: {cert.days_remaining} days remaining\n"
            body += "\n"

        msg.attach(MIMEText(body, 'plain'))

        try:
            server = smtplib.SMTP(smtp_config['smtp_server'], smtp_config['smtp_port'])
            server.starttls()
            server.login(smtp_config['username'], smtp_config['password'])
            server.send_message(msg)
            server.quit()
            self.logger.info("Alert email sent successfully")
        except Exception as e:
            self.logger.error(f"Failed to send alert email: {e}")

    def schedule_checks(self, domains: List[str], interval_hours: int = 24):
        """Schedule periodic checks"""
        def job():
            self.logger.info("Running scheduled SSL check")
            results = self.check_domains(domains)
            self.display_results(results)

            # Send alerts if configured
            smtp_config = self._get_smtp_config()
            if smtp_config:
                self.send_alert_email(results, smtp_config)

        schedule.every(interval_hours).hours.do(job)
        self.logger.info(f"Scheduled SSL checks every {interval_hours} hours")

        # Run initial check
        job()

        # Keep running
        while True:
            schedule.run_pending()
            time.sleep(60)

    def _get_smtp_config(self) -> Optional[Dict]:
        """Get SMTP configuration from environment"""
        required = ['SMTP_SERVER', 'SMTP_PORT', 'SMTP_USERNAME', 'SMTP_PASSWORD', 'FROM_EMAIL', 'TO_EMAIL']
        config = {}
        for key in required:
            value = os.getenv(key)
            if not value:
                return None
            config[key.lower()] = value

        return config