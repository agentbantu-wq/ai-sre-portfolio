# Azure Monitor Alert Analyzer

> Advanced analytics and correlation of Azure Monitor alerts with patterns, correlations, and actionable recommendations.

## Problem

Azure Monitor generates many alerts, but teams struggle to:
- Identify alert patterns and root causes
- Correlate related alerts
- Reduce alert noise
- Understand which alerts need immediate attention

## Solution

Azure Alert Analyzer provides comprehensive alert analysis with:
- Pattern detection across resources
- Alert correlation within time windows
- Intelligent recommendations
- Rich reporting and visualization

## Features

✅ **Advanced Alert Retrieval**
- Query alerts from Azure Monitor
- Filter by resource group, status, time range
-oot cause analysis

✅ **Pattern Detection**
- Identify recurring alert patterns
- Analyze severity distributions
- Track common triggers
- Calculate average resolution times

✅ **Alert Correlation**
- Find related alerts within configurable time windows
- Measure correlation strength
- Identify cascade failures

✅ **Intelligent Recommendations**
- Alert tuning suggestions
- Automation opportunities
- Root cause investigation guidance
- Severity-based prioritization

✅ **Rich Reporting**
- JSON and Excel exports
- Dashboard data generation
- Trend analysis
- Severity breakdown

## Prerequisites

- Python 3.8+
- Azure subscription
- Azure CLI installed and authenticated
- Permissions to read from Log Analytics (optional)

## Installation

### 1. Install the Tool

```bash
# Clone or download
cd azure-alert-analyzer

# Install dependencies
pip install -r requirements.txt

# Or install as package
pip install -e .
```

### 2. Set Up Azure Authentication

```bash
# Login to Azure
az login

# Set your subscription
az account set --subscription "YOUR_SUBSCRIPTION_ID"
```

### 3. Configure Environment Variables

Create a `.env` file:

```env
AZURE_SUBSCRIPTION_ID=your-subscription-id
LOG_ANALYTICS_WORKSPACE_ID=your-workspace-id  # Optional
```

### How to Set up Correctly

#### Step 1: Get Your Subscription ID

```bash
# List subscriptions
az account list --output table

# Copy the ID and set in .env or environment
export AZURE_SUBSCRIPTION_ID="your-subscription-id"
```

#### Step 2: (Optional) Configure Log Analytics

```bash
# Find your Log Analytics workspace
az monitor log-analytics workspace list --resource-group your-rg

# Get workspace ID
az monitor log-analytics workspace show --resource-group your-rg --name your-workspace
```

## Usage

### Basic Alert Analysis

```bash
# Analyze last 7 days of alerts
azure-alert-analyzer analyze

# Analyze specific resource group
azure-alert-analyzer analyze --resource-group MyRG

# Look back 30 days
azure-alert-analyzer analyze --days 30

# Export to Excel
azure-alert-analyzer analyze --output alerts.xlsx --format xlsx
```

### Generate Dashboard Data

```bash
# Create visualization data
azure-alert-analyzer dashboard --output dashboard.json

# Analyze 14 days
azure-alert-analyzer dashboard --days 14 --output dashboard.json
```

### Create Alert Rules

```bash
# Create new alert
azure-alert-analyzer create-alert \
  --resource-group MyRG \
  --alert-name "High CPU" \
  --severity 2 \
  --query "Perf | where ObjectName=='Processor'"
```

## Output Examples

### Analysis Summary

```
Alert Analysis Summary
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Metric                         │ Value
───────────────────────────────┼──────────────
Total Alerts                   │ 245
Unique Patterns                │ 18
Most Common Severity           │ Warning
Date Range                     │ 2026-03-27 to 2026-04-03

Top Alert Patterns
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Resource Type    │ Alert Type          │ Frequency │ Avg Duration
─────────────────┼─────────────────────┼───────────┼──────────────
VirtualMachine   │ High CPU            │ 42        │ 2.3 hrs
StorageAccount   │ Low Throughput      │ 23        │ 1.1 hrs
AppServicePlan   │ Memory Threshold    │ 18        │ 0.5 hrs
```

### Recommendations

```
Top Recommendations:
1. [High] Consider adjusting thresholds for High CPU on VirtualMachine
2. [High] Investigate root cause of frequent critical Database Connection alerts
3. [Medium] Implement automated remediation for Low Throughput on StorageAccount
```

## Advanced Features

### Pattern-Based Insights
- Group alerts by resource type and condition
- Track which resources are problematic
- Identify temporal patterns (e.g., spikes during business hours)

### Correlation Analysis
- Find alerts that commonly occur together
- Identify cascade failures
- Measure correlation strength

### Severity Distribution
- Understand alert severity patterns
- Prioritize critical issues
- Track improvement over time

### Export Capabilities
- **JSON**: Complete structured data for processing
- **Excel**: Multi-sheet reports with summaries and details
- **Dashboard JSON**: Ready for visualization tools

## Configuration

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| AZURE_SUBSCRIPTION_ID | Azure subscription ID | Yes |
| LOG_ANALYTICS_WORKSPACE_ID | Log Analytics workspace ID | No |

### Alert Query Parameters

When using log queries:

```kusto
// Example alert condition query
AzureMetrics
| where ResourceType == "VIRTUALMACHINES"
| where MetricName == "Percentage CPU"
| where Average > 80
| summarize count() by Resource
```

## Integration Examples

### With GitLab

```yaml
# .gitlab-ci.yml
analyze_alerts:
  script:
    - azure-alert-analyzer analyze --days 7 --output report.json
    - # Process report.json
```

### With Jenkins

```groovy
stage('Analyze Alerts') {
    steps {
        sh 'azure-alert-analyzer analyze --output alerts.json --format json'
        // Send to dashboard
    }
}
```

## Testing

```bash
# Run tests
python -m pytest tests/

# With coverage
python -m pytest tests/ --cov=azure_alert_analyzer
```

## Contributing

1. Clone the repository
2. Create a feature branch
3. Add tests for new features
4. Ensure tests pass
5. Submit pull request

## License

MIT License

## Support

- Documentation: See docs/ folder
- Issues: GitHub issues
- Questions: Create a discussion