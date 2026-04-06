# Azure Cost Analyzer

> Advanced cost tracking, analysis, optimization, and anomaly detection for Azure resources.

## Problem

Azure cloud costs are difficult to track and optimize because:
- Costs are scattered across multiple services and resources
- Cost trends are hard to visualize
- Anomalies and unusual spikes go unnoticed
- No automated recommendations for cost reduction

## Solution

Azure Cost Analyzer provides comprehensive cost visibility with:
- Real-time cost tracking across all resources
- Trend analysis and forecasting
- Anomaly detection with severity levels
- AI-powered optimization recommendations
- Multi-format reporting

## Features

✅ **Cost Data Collection**
- Retrieve costs from Azure Cost Management API
- Filter by subscription, resource group, location, tags
- Support for multiple grouping dimensions

✅ **Cost Breakdown Analysis**
- Break down by resource type, service, location
- Percentage allocation visualization
- Trend comparisons

✅ **Trend Analysis**
- Calculate monthly/weekly/daily trends
- Identify upward/downward trends
- Peak cost detection
- MoM (Month-over-Month) change calculation

✅ **Anomaly Detection**
- Statistical anomaly detection (Z-score)
- Severity classification (low to critical)
- Configurable threshold sensitivity
- Related resource correlation

✅ **Optimization Recommendations**
- Trend-based recommendations
- Peak shaving strategies
- Resource cleanup suggestions
- Estimated savings calculations

✅ **Multiple Export Formats**
- JSON for data processing
- Excel with multiple sheets
- HTML dashboards
- Summary statistics

## Prerequisites

- Python 3.8+
- Azure subscription
- Azure CLI with authentication
- Cost Management API enabled

## Installation

### 1. Install the Tool

```bash
# Download and navigate
cd azure-cost-analyzer

# Install dependencies
pip install -r requirements.txt

# Or install as package
pip install -e .
```

### 2. Authenticate with Azure

```bash
# Login to Azure
az login

# Set your subscription
az account set --subscription "YOUR_SUBSCRIPTION_ID"
```

### 3. Configure Environment

Create `.env` file:

```env
AZURE_SUBSCRIPTION_ID=your-subscription-id
AZURE_BILLING_ACCOUNT_ID=your-billing-account-id  # Optional
LOG_ANALYTICS_WORKSPACE_ID=your-workspace-id      # Optional
```

### Setup Instructions

#### Step 1: Get Subscription Details

```bash
# List all subscriptions
az account list --output table

# Copy the Subscription ID and set it:
export AZURE_SUBSCRIPTION_ID="xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
```

#### Step 2: Enable Cost Management API

```bash
# The API should be enabled by default, but verify:
az provider register --namespace Microsoft.CostManagement
az provider register --namespace Microsoft.Billing
```

#### Step 3: Verify Access

```bash
# Test authentication
az config set auto-upgrade.fetch_latest=true

# Check accessible subscriptions
az account list-locations
```

## Usage

### Basic Cost Analysis

```bash
# Analyze last 30 days of costs
azure-cost-analyzer analyze --days 30

# Analyze specific period (JSON export)
azure-cost-analyzer analyze --days 90 --output costs.json --format json

# Export to Excel
azure-cost-analyzer analyze --days 30 --output report.xlsx --format xlsx
```

### Detect Cost Anomalies

```bash
# Find all anomalies
azure-cost-analyzer anomalies --days 30

# Only critical anomalies
azure-cost-analyzer anomalies --severity critical

# Adjust sensitivity
azure-cost-analyzer anomalies --threshold 1.5
```

### View Cost Trends

```bash
# Display trends for last 30 days
azure-cost-analyzer trends --days 30

# Analyze 90-day trends
azure-cost-analyzer trends --days 90
```

### Generate Dashboard Data

```bash
# Create visualization data
azure-cost-analyzer dashboard --days 30 --output dashboard.json
```

## Output Examples

### Cost Summary

```
Cost Summary
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Metric                         │ Value
───────────────────────────────┼──────────────────────
Total Cost                     │ $12,345.67
Average Daily Cost             │ $410.86
Highest Cost Service           │ VirtualMachines
Cost Trend                     │ UP
Anomalies Detected             │ 3

Top Cost Resources
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Resource Type           │ Cost       │ Percentage
────────────────────────┼────────────┼────────────
Database                │ $3,450.20  │ 27.9%
AppService              │ $2,890.15  │ 23.4%
VirtualMachine          │ $2,345.77  │ 19.0%
Storage                 │ $1,890.85  │ 15.3%
Networking              │ $1,378.70  │ 11.2%
```

### Anomaly Detection

```
Found 3 anomalies:

[CRITICAL] /subscriptions/.../resources/vm-prod-01 on 2026-04-02
  Cost: $234.56 (deviation: +156.2%)
  
[HIGH] /subscriptions/.../resources/database-01 on 2026-03-30
  Cost: $567.89 (deviation: +78.5%)
  
[MEDIUM] /subscriptions/.../resources/app-service-01 on 2026-03-28
  Cost: $123.45 (deviation: +42.1%)
```

### Cost Trends

```
Cost Trends (Last 30 days):

VirtualMachines
  Total: $5,678.90
  Daily Avg: $189.30
  Trend: ↑ +23.4%

AppService
  Total: $2,890.15
  Daily Avg: $96.34
  Trend: → -1.2%

Database
  Total: $3,450.20
  Daily Avg: $115.01
  Trend: ↑ +45.8%
```

### Optimization Recommendations

```
Top Cost Optimization Opportunities:
1. [Critical] Investigate 2 critical cost anomalies
   Potential savings: $1,234.56

2. [High] Significant upward trend (+45.8%) in Database costs
   Potential savings: $517.53

3. [High] Significant upward trend (+23.4%) in VirtualMachines costs
   Potential savings: $851.84

4. [Medium] Implement peak shaving strategies for AppService
   Potential savings: $289.02
```

## Advanced Analysis

### Cost Breakdown Dimensions

The tool supports analysis by:
- **Resource Type**: VM, Database, AppService, Storage, etc.
- **Service Name**: Compute, Database, Storage, Networking
- **Location**: Region where resources are located
- **Resource Group**: Logical organization in Azure

### Anomaly Scoring

Anomalies are detected using Z-score methodology:
- **Standard Deviation < 1**: Normal variation
- **1-2 σ**: Borderline (Low severity)
- **2-3 σ**: Significant (Medium severity)
- **3+ σ**: Critical (High/Critical severity)

### Trend Analysis

- **Up**: Recent avg > historical avg by >5%
- **Down**: Recent avg < historical avg by >5%
- **Stable**: Changes within ±5%

## Integration Examples

### With GitLab CI

```yaml
analyze_costs:
  script:
    - azure-cost-analyzer analyze --days 7 --output costs.json
    - # Post to dashboard or send alerts
```

### With Jenkins

```groovy
stage('Cost Analysis') {
    steps {
        sh 'azure-cost-analyzer analyze --output report.xlsx --format xlsx'
        // Archive and distribute report
        archiveArtifacts artifacts: '*.xlsx'
    }
}
```

### Alert-Triggered Analysis

```bash
# Automated daily analysis
0 9 * * * azure-cost-analyzer analyze --days 1 --output daily.json
```

## Troubleshooting

### Authentication Issues

```bash
# Verify authentication
az account show

# Re-authenticate if needed
az logout
az login
```

### No Cost Data

- Costs may take 24-48 hours to appear after resource creation
- Verify subscription has active resources
- Check API permissions

### Anomaly Threshold Tuning

- Too aggressive (high threshold): Misses real anomalies
- Too sensitive (low threshold): Too many false positives
- Default (2.0 σ) is well-balanced for most use cases

## Contributing

1. Clone the repository
2. Create a feature branch
3. Add tests
4. Ensure tests pass
5. Submit pull request

## License

MIT License

## Support

- Documentation: See docs/ folder
- Issues: GitHub issue tracker
- Questions: create a discussion