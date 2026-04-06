#!/usr/bin/env python3
"""
Azure Cost Analyzer
Comprehensive cost tracking and optimization for Azure resources
"""

import os
import json
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any, Tuple
from dataclasses import dataclass
from collections import defaultdict, Counter
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
from rich.console import Console
from rich.table import Table
from rich.progress import Progress
from rich.panel import Panel
from azure.identity import DefaultAzureCredential
from azure.costmanagement import CostManagementClient
from azure.mgmt.billing import BillingManagementClient
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

@dataclass
class CostData:
    """Cost data point"""
    date: datetime
    resource_type: str
    resource_id: str
    resource_group: str
    subscription: str
    cost: float
    currency: str
    service_name: str
    meter_category: str
    location: str
    tags: Dict[str, str]

@dataclass
class CostTrend:
    """Cost trend analysis"""
    resource_type: str
    period_start: datetime
    period_end: datetime
    total_cost: float
    avg_daily_cost: float
    peak_daily_cost: float
    trend_direction: str  # "up", "down", "stable"
    mom_change_percent: float
    top_drivers: List[Tuple[str, float]]

@dataclass
class CostAnomaly:
    """Detected cost anomaly"""
    date: datetime
    resource: str
    normal_range: Tuple[float, float]
    actual_cost: float
    deviation_percent: float
    severity: str  # "low", "medium", "high", "critical"
    related_resources: List[str]

class AzureCostAnalyzer:
    """Advanced Azure Cost analyzer"""

    def __init__(self, subscription_id: Optional[str] = None,
                 billing_account_id: Optional[str] = None):
        self.subscription_id = subscription_id or os.getenv('AZURE_SUBSCRIPTION_ID')
        self.billing_account_id = billing_account_id or os.getenv('AZURE_BILLING_ACCOUNT_ID')

        if not self.subscription_id:
            raise ValueError("Azure subscription ID required")

        self.credential = DefaultAzureCredential()
        self.cost_client = CostManagementClient(self.credential)
        self.billing_client = BillingManagementClient(self.credential)
        self.console = Console()
        self.logger = logging.getLogger(__name__)

    def get_costs(self, start_date: datetime, end_date: datetime,
                  group_by: str = 'ResourceType',
                  filter_criteria: Optional[Dict] = None) -> List[CostData]:
        """Retrieve cost data from Azure Cost Management"""

        costs = []

        try:
            # Query scope
            scope = f"subscriptions/{self.subscription_id}"

            # Build query
            dataset = {
                "aggregation": {
                    " totalCost": {
                        "name": "PreTaxCost",
                        "function": "Sum"
                    }
                },
                "granularity": "Daily",
                "grouping": [
                    {
                        "type": "Dimension",
                        "name": group_by
                    }
                ],
                "timeframe": "Custom",
                "timePeriod": {
                    "from": start_date.strftime("%Y-%m-%dT00:00:00Z"),
                    "to": end_date.strftime("%Y-%m-%dT23:59:59Z")
                }
            }

            # Execute query
            response = self.cost_client.query.usage(scope, dataset)

            # Parse results
            if response.rows:
                for row in response.rows:
                    # Row format: [date, group_by_value, cost]
                    cost_data = CostData(
                        date=datetime.strptime(row[0], "%Y%m%d"),
                        resource_type=row[1] if len(row) > 1 else "Unknown",
                        resource_id="",
                        resource_group="",
                        subscription=self.subscription_id,
                        cost=float(row[2]) if len(row) > 2 else 0.0,
                        currency="USD",
                        service_name="",
                        meter_category="",
                        location="",
                        tags={}
                    )
                    costs.append(cost_data)

        except Exception as e:
            self.logger.error(f"Error retrieving costs: {e}")

        return costs

    def analyze_breakdown(self, costs: List[CostData]) -> Dict[str, Dict[str, float]]:
        """Analyze costs by various dimensions"""

        breakdown = {
            'by_resource_type': defaultdict(float),
            'by_service': defaultdict(float),
            'by_location': defaultdict(float),
            'by_resource_group': defaultdict(float)
        }

        for cost in costs:
            breakdown['by_resource_type'][cost.resource_type] += cost.cost
            breakdown['by_service'][cost.service_name] += cost.cost
            breakdown['by_location'][cost.location] += cost.cost
            breakdown['by_resource_group'][cost.resource_group] += cost.cost

        # Convert defaultdicts to regular dicts and sort
        result = {}
        for key, values in breakdown.items():
            result[key] = dict(sorted(values.items(), key=lambda x: x[1], reverse=True))

        return result

    def calculate_trends(self, costs: List[CostData],
                        lookback_days: int = 30) -> List[CostTrend]:
        """Calculate cost trends"""

        trends = []

        if not costs:
            return trends

        # Group by resource type
        grouped = defaultdict(list)
        for cost in costs:
            grouped[cost.resource_type].append(cost)

        # Calculate trends for each group
        for resource_type, type_costs in grouped.items():
            type_costs.sort(key=lambda x: x.date)

            if len(type_costs) < 2:
                continue

            total_cost = sum(c.cost for c in type_costs)
            avg_daily = total_cost / len(type_costs) if type_costs else 0
            peak_daily = max(c.cost for c in type_costs) if type_costs else 0

            # Determine trend direction
            recent_costs = [c.cost for c in type_costs[-7:]] if len(type_costs) >= 7 else type_costs
            old_costs = [c.cost for c in type_costs[:7]] if len(type_costs) >= 7 else type_costs

            recent_avg = sum(recent_costs) / len(recent_costs) if recent_costs else 0
            old_avg = sum(old_costs) / len(old_costs) if old_costs else 0

            if recent_avg > old_avg * 1.05:
                trend_direction = "up"
            elif recent_avg < old_avg * 0.95:
                trend_direction = "down"
            else:
                trend_direction = "stable"

            # Calculate MoM change
            mom_change = ((recent_avg - old_avg) / old_avg * 100) if old_avg > 0 else 0

            # Top drivers
            top_costs = sorted([(c.date.isoformat(), c.cost) for c in type_costs],
                             key=lambda x: x[1], reverse=True)[:5]

            trend = CostTrend(
                resource_type=resource_type,
                period_start=type_costs[0].date,
                period_end=type_costs[-1].date,
                total_cost=total_cost,
                avg_daily_cost=avg_daily,
                peak_daily_cost=peak_daily,
                trend_direction=trend_direction,
                mom_change_percent=mom_change,
                top_drivers=top_costs
            )
            trends.append(trend)

        return sorted(trends, key=lambda x: x.total_cost, reverse=True)

    def detect_anomalies(self, costs: List[CostData],
                        threshold_std_dev: float = 2.0) -> List[CostAnomaly]:
        """Detect cost anomalies using statistical methods"""

        anomalies = []

        if not costs:
            return anomalies

        # Group by resource
        grouped = defaultdict(list)
        for cost in costs:
            grouped[cost.resource_id].append(cost)

        # Detect anomalies for each resource
        for resource_id, resource_costs in grouped.items():
            if len(resource_costs) < 3:  # Need minimum data points
                continue

            costs_values = [c.cost for c in resource_costs]

            # Calculate statistics
            import numpy as np
            mean_cost = np.mean(costs_values)
            std_dev = np.std(costs_values)

            # Find anomalies
            for cost in resource_costs:
                if std_dev > 0:
                    z_score = abs((cost.cost - mean_cost) / std_dev)

                    if z_score > threshold_std_dev:
                        deviation_percent = ((cost.cost - mean_cost) / mean_cost * 100) if mean_cost > 0 else 0

                        # Determine severity
                        if deviation_percent > 100:
                            severity = "critical"
                        elif deviation_percent > 50:
                            severity = "high"
                        elif deviation_percent > 25:
                            severity = "medium"
                        else:
                            severity = "low"

                        anomaly = CostAnomaly(
                            date=cost.date,
                            resource=resource_id,
                            normal_range=(mean_cost - std_dev, mean_cost + std_dev),
                            actual_cost=cost.cost,
                            deviation_percent=deviation_percent,
                            severity=severity,
                            related_resources=[]
                        )
                        anomalies.append(anomaly)

        return sorted(anomalies, key=lambda x: x.deviation_percent, reverse=True)

    def generate_optimization_recommendations(self, costs: List[CostData],
                                             trends: List[CostTrend],
                                             anomalies: List[CostAnomaly]) -> List[Dict]:
        """Generate cost optimization recommendations"""

        recommendations = []

        # High trend recommendations
        for trend in trends:
            if trend.trend_direction == "up" and trend.mom_change_percent > 20:
                recommendations.append({
                    'type': 'trend_reversal',
                    'resource_type': trend.resource_type,
                    'recommendation': f"Significant upward trend ({trend.mom_change_percent:.1f}%) in {trend.resource_type} costs",
                    'estimated_savings': trend.total_cost * 0.15,  # Estimate 15% potential savings
                    'priority': 'High'
                })

            if trend.peak_daily_cost > trend.avg_daily_cost * 2:
                recommendations.append({
                    'type': 'peak_shaving',
                    'resource_type': trend.resource_type,
                    'recommendation': f"Implement peak shaving strategies for {trend.resource_type}",
                    'estimated_savings': trend.total_cost * 0.10,
                    'priority': 'Medium'
                })

        # Anomaly-based recommendations
        critical_anomalies = [a for a in anomalies if a.severity == 'critical']
        if critical_anomalies:
            total_anomaly_cost = sum(a.actual_cost for a in critical_anomalies)
            recommendations.append({
                'type': 'anomaly_investigation',
                'resource_type': 'Multiple',
                'recommendation': f"Investigate {len(critical_anomalies)} critical cost anomalies",
                'estimated_savings': total_anomaly_cost * 0.8,
                'priority': 'Critical'
            })

        # Unused resources
        zero_cost_resources = [c.resource_type for c in costs if c.cost == 0]
        if zero_cost_resources:
            recommendations.append({
                'type': 'resource_cleanup',
                'resource_type': 'Multiple',
                'recommendation': f"Review and remove {len(set(zero_cost_resources))} unused resources",
                'estimated_savings': 100,  # Savings from reduced overhead
                'priority': 'Low'
            })

        return sorted(recommendations, key=lambda x: x.get('priority') == 'Critical', reverse=True)

    def export_report(self, costs: List[CostData], breakdown: Dict,
                     trends: List[CostTrend], anomalies: List[CostAnomaly],
                     recommendations: List[Dict], format: str = 'json',
                     filename: Optional[str] = None) -> str:
        """Export comprehensive cost report"""

        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"azure_cost_analysis_{timestamp}.{format}"

        data = {
            'summary': {
                'total_cost': sum(c.cost for c in costs),
                'average_daily_cost': sum(c.cost for c in costs) / len(costs) if costs else 0,
                'period_start': min(c.date for c in costs).isoformat() if costs else None,
                'period_end': max(c.date for c in costs).isoformat() if costs else None,
                'currency': costs[0].currency if costs else 'USD'
            },
            'breakdown': {
                key: {str(k): v for k, v in value.items()}
                for key, value in breakdown.items()
            },
            'trends': [self._trend_to_dict(t) for t in trends],
            'anomalies': [self._anomaly_to_dict(a) for a in anomalies],
            'recommendations': recommendations
        }

        if format == 'json':
            with open(filename, 'w') as f:
                json.dump(data, f, indent=2, default=str)
        elif format == 'xlsx':
            with pd.ExcelWriter(filename) as writer:
                # Summary
                summary_df = pd.DataFrame([data['summary']])
                summary_df.to_excel(writer, sheet_name='Summary', index=False)

                # Breakdown sheets
                for breakdown_type, breakdown_data in data['breakdown'].items():
                    df = pd.DataFrame(list(breakdown_data.items()), columns=[breakdown_type.replace('by_', ''), 'Cost'])
                    df.to_excel(writer, sheet_name=breakdown_type[:30], index=False)

                # Trends
                if data['trends']:
                    trends_df = pd.DataFrame(data['trends'])
                    trends_df.to_excel(writer, sheet_name='Trends', index=False)

                # Recommendations
                if data['recommendations']:
                    rec_df = pd.DataFrame(data['recommendations'])
                    rec_df.to_excel(writer, sheet_name='Recommendations', index=False)

        return filename

    def _trend_to_dict(self, trend: CostTrend) -> Dict:
        """Convert trend to dictionary"""
        return {
            'resource_type': trend.resource_type,
            'period_start': trend.period_start.isoformat(),
            'period_end': trend.period_end.isoformat(),
            'total_cost': trend.total_cost,
            'avg_daily_cost': trend.avg_daily_cost,
            'peak_daily_cost': trend.peak_daily_cost,
            'trend_direction': trend.trend_direction,
            'mom_change_percent': trend.mom_change_percent
        }

    def _anomaly_to_dict(self, anomaly: CostAnomaly) -> Dict:
        """Convert anomaly to dictionary"""
        return {
            'date': anomaly.date.isoformat(),
            'resource': anomaly.resource,
            'actual_cost': anomaly.actual_cost,
            'deviation_percent': anomaly.deviation_percent,
            'severity': anomaly.severity
        }

    def display_cost_summary(self, costs: List[CostData], breakdown: Dict,
                            trends: List[CostTrend], anomalies: List[CostAnomaly]):
        """Display cost analysis summary"""

        # Summary statistics
        total_cost = sum(c.cost for c in costs)
        avg_daily = total_cost / len(costs) if costs else 0

        summary_table = Table(title="Cost Summary")
        summary_table.add_column("Metric", style="cyan")
        summary_table.add_column("Value", style="green")

        summary_table.add_row("Total Cost", f"${total_cost:,.2f}")
        summary_table.add_row("Average Daily Cost", f"${avg_daily:,.2f}")

        if trends:
            summary_table.add_row("Highest Cost Service", trends[0].resource_type)
            summary_table.add_row("Cost Trend", trends[0].trend_direction.upper())

        summary_table.add_row("Anomalies Detected", str(len(anomalies)))

        self.console.print(summary_table)

        # Top resource types
        if breakdown['by_resource_type']:
            top_types = Table(title="Top Cost Resources")
            top_types.add_column("Resource Type", style="cyan")
            top_types.add_column("Cost", style="yellow", justify="right")
            top_types.add_column("Percentage", justify="right")

            total = sum(breakdown['by_resource_type'].values())
            for resource_type, cost in list(breakdown['by_resource_type'].items())[:5]:
                pct = (cost / total * 100) if total > 0 else 0
                top_types.add_row(resource_type, f"${cost:,.2f}", f"{pct:.1f}%")

            self.console.print(top_types)