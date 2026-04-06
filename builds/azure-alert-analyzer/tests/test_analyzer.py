#!/usr/bin/env python3
"""
Tests for Azure Alert Analyzer
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock
from azure_alert_analyzer.analyzer import AzureAlertAnalyzer, AlertInfo, AlertPattern

@pytest.fixture
def sample_alerts():
    """Create sample alert data"""
    now = datetime.now()
    return [
        AlertInfo(
            id="alert1",
            name="High CPU",
            description="CPU usage exceeds threshold",
            severity="Warning",
            status="Fired",
            target_resource="/subscriptions/sub1/resourceGroups/rg1/providers/Microsoft.Compute/virtualMachines/vm1",
            fired_at=now - timedelta(hours=2),
            resolved_at=now - timedelta(hours=1),
            condition={"metricName": "Percentage CPU", "operator": "GreaterThan", "threshold": 80},
            tags={"environment": "prod"}
        ),
        AlertInfo(
            id="alert2",
            name="High CPU",
            description="CPU usage exceeds threshold",
            severity="Error",
            status="Fired",
            target_resource="/subscriptions/sub1/resourceGroups/rg1/providers/Microsoft.Compute/virtualMachines/vm1",
            fired_at=now - timedelta(hours=1),
            resolved_at=None,
            condition={"metricName": "Percentage CPU", "operator": "GreaterThan", "threshold": 80},
            tags={"environment": "prod"}
        ),
        AlertInfo(
            id="alert3",
            name="Low Memory",
            description="Available memory low",
            severity="Warning",
            status="Fired",
            target_resource="/subscriptions/sub1/resourceGroups/rg1/providers/Microsoft.Compute/virtualMachines/vm2",
            fired_at=now - timedelta(minutes=30),
            resolved_at=None,
            condition={"metricName": "Available Memory", "operator": "LessThan", "threshold": 1024},
            tags={"environment": "dev"}
        ),
    ]

def test_analyzer_initialization():
    """Test analyzer initialization"""
    with patch.dict('os.environ', {'AZURE_SUBSCRIPTION_ID': 'test-sub-id'}):
        analyzer = AzureAlertAnalyzer(subscription_id='test-sub-id')
        assert analyzer.subscription_id == 'test-sub-id'

def test_severity_mapping():
    """Test severity level mapping"""
    with patch.dict('os.environ', {'AZURE_SUBSCRIPTION_ID': 'test-sub-id'}):
        analyzer = AzureAlertAnalyzer(subscription_id='test-sub-id')
        assert analyzer.severity_map['0'] == 'Critical'
        assert analyzer.severity_map['2'] == 'Warning'

def test_analyze_patterns(sample_alerts):
    """Test pattern analysis"""
    with patch.dict('os.environ', {'AZURE_SUBSCRIPTION_ID': 'test-sub-id'}):
        analyzer = AzureAlertAnalyzer(subscription_id='test-sub-id')
        patterns = analyzer.analyze_patterns(sample_alerts)

        assert len(patterns) >= 2
        # High CPU should be most frequent
        high_cpu_pattern = next((p for p in patterns if 'High CPU' in p.alert_type), None)
        assert high_cpu_pattern is not None
        assert high_cpu_pattern.frequency == 2

def test_correlate_alerts(sample_alerts):
    """Test alert correlation"""
    with patch.dict('os.environ', {'AZURE_SUBSCRIPTION_ID': 'test-sub-id'}):
        analyzer = AzureAlertAnalyzer(subscription_id='test-sub-id')
        # Adjust sample alerts to be within same time window
        now = datetime.now()
        sample_alerts[0].fired_at = now - timedelta(minutes=5)
        sample_alerts[1].fired_at = now - timedelta(minutes=3)
        sample_alerts[2].fired_at = now - timedelta(minutes=2)

        correlations = analyzer.correlate_alerts(sample_alerts, time_window_minutes=10)
        assert len(correlations) > 0

def test_generate_recommendations(sample_alerts):
    """Test recommendation generation"""
    with patch.dict('os.environ', {'AZURE_SUBSCRIPTION_ID': 'test-sub-id'}):
        analyzer = AzureAlertAnalyzer(subscription_id='test-sub-id')
        patterns = analyzer.analyze_patterns(sample_alerts)
        recommendations = analyzer.generate_recommendations(patterns)

        assert len(recommendations) > 0
        assert any(r['type'] == 'alert_tuning' for r in recommendations)

def test_alert_to_dict(sample_alerts):
    """Test alert serialization"""
    with patch.dict('os.environ', {'AZURE_SUBSCRIPTION_ID': 'test-sub-id'}):
        analyzer = AzureAlertAnalyzer(subscription_id='test-sub-id')
        alert_dict = analyzer._alert_to_dict(sample_alerts[0])

        assert alert_dict['id'] == "alert1"
        assert alert_dict['name'] == "High CPU"
        assert alert_dict['severity'] == "Warning"
        assert 'fired_at' in alert_dict

def test_pattern_to_dict():
    """Test pattern serialization"""
    pattern = AlertPattern(
        resource_type="VirtualMachine",
        alert_type="High CPU",
        frequency=10,
        avg_duration=2.5,
        common_triggers=[("CPU", 8), ("Memory", 2)],
        severity_distribution={"Warning": 8, "Error": 2}
    )

    with patch.dict('os.environ', {'AZURE_SUBSCRIPTION_ID': 'test-sub-id'}):
        analyzer = AzureAlertAnalyzer(subscription_id='test-sub-id')
        pattern_dict = analyzer._pattern_to_dict(pattern)

        assert pattern_dict['resource_type'] == "VirtualMachine"
        assert pattern_dict['frequency'] == 10
        assert pattern_dict['avg_duration_hours'] == 2.5

def test_create_dashboard_data(sample_alerts):
    """Test dashboard data generation"""
    with patch.dict('os.environ', {'AZURE_SUBSCRIPTION_ID': 'test-sub-id'}):
        analyzer = AzureAlertAnalyzer(subscription_id='test-sub-id')
        patterns = analyzer.analyze_patterns(sample_alerts)

        dashboard_data = analyzer.create_dashboard_data(sample_alerts, patterns)

        assert 'time_series' in dashboard_data
        assert 'severity_distribution' in dashboard_data
        assert 'top_resources' in dashboard_data
        assert 'patterns' in dashboard_data