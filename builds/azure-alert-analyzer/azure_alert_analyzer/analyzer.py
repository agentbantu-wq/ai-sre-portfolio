#!/usr/bin/env python3
"""
Azure Monitor Alert Analyzer
Advanced analysis and correlation of Azure Monitor alerts
"""

import os
import json
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any
from dataclasses import dataclass
from collections import defaultdict, Counter
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from rich.console import Console
from rich.table import Table
from rich.progress import Progress
from azure.identity import DefaultAzureCredential
from azure.monitor.query import LogsQueryClient, MetricsQueryClient
from azure.mgmt.monitor import MonitorManagementClient
from azure.mgmt.monitor.models import AlertRuleResource
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

@dataclass
class AlertInfo:
    """Azure Monitor alert information"""
    id: str
    name: str
    description: str
    severity: str
    status: str
    target_resource: str
    fired_at: datetime
    resolved_at: Optional[datetime]
    condition: Dict[str, Any]
    tags: Dict[str, str]

@dataclass
class AlertPattern:
    """Alert pattern analysis"""
    resource_type: str
    alert_type: str
    frequency: int
    avg_duration: float
    common_triggers: List[str]
    severity_distribution: Dict[str, int]

class AzureAlertAnalyzer:
    """Advanced Azure Monitor alert analyzer"""

    def __init__(self, subscription_id: Optional[str] = None):
        self.subscription_id = subscription_id or os.getenv('AZURE_SUBSCRIPTION_ID')
        if not self.subscription_id:
            raise ValueError("Azure subscription ID required")

        self.credential = DefaultAzureCredential()
        self.monitor_client = MonitorManagementClient(self.credential, self.subscription_id)
        self.logs_client = LogsQueryClient(self.credential)
        self.metrics_client = MetricsQueryClient(self.credential)
        self.console = Console()
        self.logger = logging.getLogger(__name__)

        # Severity mapping
        self.severity_map = {
            '0': 'Critical',
            '1': 'Error',
            '2': 'Warning',
            '3': 'Informational',
            '4': 'Verbose'
        }

    def get_alerts(self, resource_group: Optional[str] = None,
                  start_time: Optional[datetime] = None,
                  end_time: Optional[datetime] = None,
                  status: Optional[str] = None) -> List[AlertInfo]:
        """Retrieve alerts from Azure Monitor"""

        if not start_time:
            start_time = datetime.now() - timedelta(days=7)
        if not end_time:
            end_time = datetime.now()

        alerts = []

        try:
            # Query alerts using Logs
            query = """
            AzureActivity
            | where OperationName == "Microsoft.Insights/metricAlerts/write"
            | where TimeGenerated >= datetime({start_time})
            | where TimeGenerated <= datetime({end_time})
            | project TimeGenerated, Resource, OperationName, Properties
            """

            if resource_group:
                query += f"| where ResourceGroup == '{resource_group}'"

            if status:
                query += f"| where Properties.status == '{status}'"

            response = self.logs_client.query_workspace(
                os.getenv('LOG_ANALYTICS_WORKSPACE_ID'),
                query,
                timespan=(start_time, end_time)
            )

            for row in response.tables[0].rows:
                properties = json.loads(row[3]) if row[3] else {}

                alert = AlertInfo(
                    id=row[1],
                    name=properties.get('alertName', 'Unknown'),
                    description=properties.get('description', ''),
                    severity=self.severity_map.get(str(properties.get('severity', '2')), 'Warning'),
                    status=properties.get('status', 'Unknown'),
                    target_resource=row[1],
                    fired_at=row[0],
                    resolved_at=None,  # Would need additional query
                    condition=properties.get('condition', {}),
                    tags=properties.get('tags', {})
                )
                alerts.append(alert)

        except Exception as e:
            self.logger.error(f"Error retrieving alerts: {e}")

        return alerts

    def analyze_patterns(self, alerts: List[AlertInfo]) -> List[AlertPattern]:
        """Analyze alert patterns and correlations"""

        patterns = defaultdict(lambda: {
            'alerts': [],
            'durations': [],
            'triggers': Counter(),
            'severities': Counter()
        })

        for alert in alerts:
            # Extract resource type
            resource_parts = alert.target_resource.split('/')
            resource_type = resource_parts[-2] if len(resource_parts) > 1 else 'Unknown'

            key = f"{resource_type}:{alert.name}"

            patterns[key]['alerts'].append(alert)
            patterns[key]['severities'][alert.severity] += 1

            # Extract trigger conditions
            if 'metricName' in alert.condition:
                patterns[key]['triggers'][alert.condition['metricName']] += 1
            elif 'query' in alert.condition:
                patterns[key]['triggers']['Custom Query'] += 1

        alert_patterns = []
        for key, data in patterns.items():
            resource_type, alert_type = key.split(':', 1)

            durations = []
            for alert in data['alerts']:
                if alert.resolved_at:
                    duration = (alert.resolved_at - alert.fired_at).total_seconds() / 3600
                    durations.append(duration)

            pattern = AlertPattern(
                resource_type=resource_type,
                alert_type=alert_type,
                frequency=len(data['alerts']),
                avg_duration=sum(durations) / len(durations) if durations else 0,
                common_triggers=data['triggers'].most_common(3),
                severity_distribution=dict(data['severities'])
            )
            alert_patterns.append(pattern)

        return sorted(alert_patterns, key=lambda x: x.frequency, reverse=True)

    def correlate_alerts(self, alerts: List[AlertInfo], time_window_minutes: int = 30) -> List[Dict]:
        """Find correlated alerts within time windows"""

        correlations = []
        sorted_alerts = sorted(alerts, key=lambda x: x.fired_at)

        for i, alert in enumerate(sorted_alerts):
            window_start = alert.fired_at
            window_end = window_start + timedelta(minutes=time_window_minutes)

            correlated = []
            for j in range(i + 1, len(sorted_alerts)):
                other_alert = sorted_alerts[j]
                if other_alert.fired_at <= window_end:
                    correlated.append(other_alert)
                else:
                    break

            if len(correlated) > 1:
                correlations.append({
                    'trigger_alert': alert,
                    'correlated_alerts': correlated,
                    'time_window': time_window_minutes,
                    'correlation_strength': len(correlated)
                })

        return correlations

    def generate_recommendations(self, patterns: List[AlertPattern]) -> List[Dict]:
        """Generate actionable recommendations based on patterns"""

        recommendations = []

        for pattern in patterns:
            if pattern.frequency > 10:  # High frequency
                recommendations.append({
                    'type': 'alert_tuning',
                    'pattern': pattern,
                    'recommendation': f"Consider adjusting thresholds for {pattern.alert_type} on {pattern.resource_type}",
                    'impact': 'Reduce alert noise',
                    'priority': 'High'
                })

            if pattern.avg_duration > 2:  # Long resolution time
                recommendations.append({
                    'type': 'automation',
                    'pattern': pattern,
                    'recommendation': f"Implement automated remediation for {pattern.alert_type}",
                    'impact': 'Faster resolution',
                    'priority': 'Medium'
                })

            # Severity distribution analysis
            critical_count = pattern.severity_distribution.get('Critical', 0)
            if critical_count > pattern.frequency * 0.3:  # >30% critical
                recommendations.append({
                    'type': 'investigation',
                    'pattern': pattern,
                    'recommendation': f"Investigate root cause of frequent critical {pattern.alert_type} alerts",
                    'impact': 'Improve reliability',
                    'priority': 'High'
                })

        return recommendations

    def create_dashboard_data(self, alerts: List[AlertInfo], patterns: List[AlertPattern]) -> Dict:
        """Create data for dashboard visualization"""

        # Time series data
        df = pd.DataFrame([{
            'timestamp': alert.fired_at,
            'severity': alert.severity,
            'resource': alert.target_resource.split('/')[-1],
            'alert_type': alert.name
        } for alert in alerts])

        # Hourly aggregations
        hourly = df.set_index('timestamp').resample('H').size()

        # Severity distribution
        severity_counts = df['severity'].value_counts()

        # Top alerting resources
        top_resources = df['resource'].value_counts().head(10)

        # Pattern summary
        pattern_summary = [{
            'resource_type': p.resource_type,
            'alert_type': p.alert_type,
            'frequency': p.frequency,
            'avg_duration': p.avg_duration
        } for p in patterns[:10]]

        return {
            'time_series': hourly.to_dict(),
            'severity_distribution': severity_counts.to_dict(),
            'top_resources': top_resources.to_dict(),
            'patterns': pattern_summary
        }

    def export_report(self, alerts: List[AlertInfo], patterns: List[AlertPattern],
                     correlations: List[Dict], recommendations: List[Dict],
                     format: str = 'json', filename: Optional[str] = None) -> str:
        """Export comprehensive analysis report"""

        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"azure_alert_analysis_{timestamp}.{format}"

        data = {
            'summary': {
                'total_alerts': len(alerts),
                'date_range': {
                    'start': min(a.fired_at for a in alerts).isoformat() if alerts else None,
                    'end': max(a.fired_at for a in alerts).isoformat() if alerts else None
                },
                'severity_breakdown': dict(Counter(a.severity for a in alerts))
            },
            'patterns': [self._pattern_to_dict(p) for p in patterns],
            'correlations': correlations,
            'recommendations': recommendations,
            'alerts': [self._alert_to_dict(a) for a in alerts]
        }

        if format == 'json':
            with open(filename, 'w') as f:
                json.dump(data, f, indent=2, default=str)
        elif format == 'xlsx':
            # Create Excel with multiple sheets
            with pd.ExcelWriter(filename) as writer:
                # Summary
                summary_df = pd.DataFrame([data['summary']])
                summary_df.to_excel(writer, sheet_name='Summary', index=False)

                # Patterns
                patterns_df = pd.DataFrame(data['patterns'])
                patterns_df.to_excel(writer, sheet_name='Patterns', index=False)

                # Alerts
                alerts_df = pd.DataFrame(data['alerts'])
                alerts_df.to_excel(writer, sheet_name='Alerts', index=False)

        return filename

    def _alert_to_dict(self, alert: AlertInfo) -> Dict:
        """Convert AlertInfo to dictionary"""
        return {
            'id': alert.id,
            'name': alert.name,
            'description': alert.description,
            'severity': alert.severity,
            'status': alert.status,
            'target_resource': alert.target_resource,
            'fired_at': alert.fired_at.isoformat(),
            'resolved_at': alert.resolved_at.isoformat() if alert.resolved_at else None,
            'condition': alert.condition,
            'tags': alert.tags
        }

    def _pattern_to_dict(self, pattern: AlertPattern) -> Dict:
        """Convert AlertPattern to dictionary"""
        return {
            'resource_type': pattern.resource_type,
            'alert_type': pattern.alert_type,
            'frequency': pattern.frequency,
            'avg_duration_hours': pattern.avg_duration,
            'common_triggers': pattern.common_triggers,
            'severity_distribution': pattern.severity_distribution
        }

    def display_summary(self, alerts: List[AlertInfo], patterns: List[AlertPattern]):
        """Display analysis summary in rich table"""

        # Summary table
        summary_table = Table(title="Alert Analysis Summary")
        summary_table.add_column("Metric", style="cyan")
        summary_table.add_column("Value", style="green")

        summary_table.add_row("Total Alerts", str(len(alerts)))
        summary_table.add_row("Unique Patterns", str(len(patterns)))
        summary_table.add_row("Most Common Severity",
                             max(Counter(a.severity for a in alerts).items(),
                                 key=lambda x: x[1])[0] if alerts else "None")

        if alerts:
            date_range = f"{min(a.fired_at for a in alerts).date()} to {max(a.fired_at for a in alerts).date()}"
            summary_table.add_row("Date Range", date_range)

        self.console.print(summary_table)

        # Top patterns table
        if patterns:
            pattern_table = Table(title="Top Alert Patterns")
            pattern_table.add_column("Resource Type", style="cyan")
            pattern_table.add_column("Alert Type", style="yellow")
            pattern_table.add_column("Frequency", justify="right")
            pattern_table.add_column("Avg Duration (hrs)", justify="right")

            for pattern in patterns[:10]:
                pattern_table.add_row(
                    pattern.resource_type,
                    pattern.alert_type,
                    str(pattern.frequency),
                    ".1f"
                )

            self.console.print(pattern_table)