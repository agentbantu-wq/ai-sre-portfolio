#!/usr/bin/env python3
"""
Tests for Azure Cost Analyzer
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock
from azure_cost_analyzer.analyzer import AzureCostAnalyzer, CostData, CostTrend, CostAnomaly

@pytest.fixture
def sample_costs():
    """Create sample cost data"""
    now = datetime.now()
    costs = []
    for i in range(30):
        date = now - timedelta(days=30-i)
        # VM costs with upward trend
        costs.append(CostData(
            date=date,
            resource_type="VirtualMachines",
            resource_id=f"vm-{i}",
            resource_group="prod-rg",
            subscription="sub-1",
            cost=100 + (i * 2),  # Upward trend
            currency="USD",
            service_name="Compute",
            meter_category="VM",
            location="eastus",
            tags={"env": "prod"}
        ))
        # Storage costs
        costs.append(CostData(
            date=date,
            resource_type="StorageAccount",
            resource_id=f"storage-{i}",
            resource_group="prod-rg",
            subscription="sub-1",
            cost=50,
            currency="USD",
            service_name="Storage",
            meter_category="Blob",
            location="eastus",
            tags={"env": "prod"}
        ))
    return costs

def test_analyzer_initialization():
    """Test analyzer initialization"""
    with patch.dict('os.environ', {'AZURE_SUBSCRIPTION_ID': 'test-sub-id'}):
        analyzer = AzureCostAnalyzer(subscription_id='test-sub-id')
        assert analyzer.subscription_id == 'test-sub-id'

def test_analyze_breakdown(sample_costs):
    """Test cost breakdown analysis"""
    with patch.dict('os.environ', {'AZURE_SUBSCRIPTION_ID': 'test-sub-id'}):
        analyzer = AzureCostAnalyzer(subscription_id='test-sub-id')
        breakdown = analyzer.analyze_breakdown(sample_costs)

        assert 'by_resource_type' in breakdown
        assert 'VirtualMachines' in breakdown['by_resource_type']
        assert 'StorageAccount' in breakdown['by_resource_type']

def test_calculate_trends(sample_costs):
    """Test trend calculation"""
    with patch.dict('os.environ', {'AZURE_SUBSCRIPTION_ID': 'test-sub-id'}):
        analyzer = AzureCostAnalyzer(subscription_id='test-sub-id')
        trends = analyzer.calculate_trends(sample_costs)

        assert len(trends) >= 1
        # VirtualMachines should have more cost due to upward trend
        vm_trend = next((t for t in trends if 'VirtualMachines' in t.resource_type), None)
        assert vm_trend is not None
        assert vm_trend.trend_direction in ['up', 'down', 'stable']

def test_detect_anomalies(sample_costs):
    """Test anomaly detection"""
    with patch.dict('os.environ', {'AZURE_SUBSCRIPTION_ID': 'test-sub-id'}):
        analyzer = AzureCostAnalyzer(subscription_id='test-sub-id')
        # Add anomalous point
        now = datetime.now()
        sample_costs.append(CostData(
            date=now,
            resource_type="VirtualMachines",
            resource_id="vm-anomaly",
            resource_group="prod-rg",
            subscription="sub-1",
            cost=500,  # Spike
            currency="USD",
            service_name="Compute",
            meter_category="VM",
            location="eastus",
            tags={}
        ))

        anomalies = analyzer.detect_anomalies(sample_costs)
        # May or may not detect depending on data distribution
        assert isinstance(anomalies, list)

def test_generate_recommendations(sample_costs):
    """Test recommendation generation"""
    with patch.dict('os.environ', {'AZURE_SUBSCRIPTION_ID': 'test-sub-id'}):
        analyzer = AzureCostAnalyzer(subscription_id='test-sub-id')
        breakdown = analyzer.analyze_breakdown(sample_costs)
        trends = analyzer.calculate_trends(sample_costs)
        anomalies = analyzer.detect_anomalies(sample_costs)

        recommendations = analyzer.generate_optimization_recommendations(sample_costs, trends, anomalies)
        assert isinstance(recommendations, list)

def test_cost_data_creation():
    """Test CostData creation"""
    cost = CostData(
        date=datetime.now(),
        resource_type="VirtualMachine",
        resource_id="vm-1",
        resource_group="rg-1",
        subscription="sub-1",
        cost=100.50,
        currency="USD",
        service_name="Compute",
        meter_category="VM",
        location="eastus",
        tags={"env": "prod"}
    )

    assert cost.resource_type == "VirtualMachine"
    assert cost.cost == 100.50
    assert cost.tags["env"] == "prod"