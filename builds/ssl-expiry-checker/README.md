# SSL Certificate Expiry Checker

> Advanced SSL certificate monitoring tool with alerting, scheduling, and multi-format reporting.

## Problem

SSL certificates expire, and monitoring them manually is tedious. Teams often discover expired certificates too late, causing outages and security issues.

## Solution

SSL Expiry Checker provides comprehensive SSL certificate monitoring with:
- Batch checking from CLI, CSV, or API
- Real-time alerts for expiring certificates
- Scheduled monitoring
- Rich reporting in multiple formats
- Email notifications

## Features

✅ **Multi-Source Input**
- Check single domains via CLI
- Bulk check from CSV files
- Fetch domains from REST APIs
- Support for custom ports

✅ **Advanced Monitoring**
- Configurable warning thresholds
- Continuous monitoring with scheduling
- Real-time status display

✅ **Comprehensive Reporting**
- JSON, CSV, and Excel exports
- Detailed certificate information
- Issuer, subject, key size, signature algorithm

✅ **Alerting System**
- Email notifications for expiring/expired certs
- SMTP configuration via environment variables
- Customizable alert thresholds

✅ **Rich CLI Interface**
- Color-coded status display
- Progress bars for batch operations
- Verbose logging options

## Installation

### Prerequisites
- Python 3.8+
- pip

### Install from Source

```bash
# Clone or download the tool
cd ssl-expiry-checker

# Install dependencies
pip install -r requirements.txt

# Or install as package
pip install -e .
```

### Docker Installation

```bash
# Build Docker image
docker build -t ssl-checker .

# Run container
docker run -it ssl-checker ssl-check example.com
```

## Usage

### Basic Domain Check

```bash
# Check single domain
ssl-check check google.com

# Check multiple domains
ssl-check check google.com github.com reddit.com

# Custom warning days
ssl-check check --warning-days 60 google.com
```

### CSV Batch Checking

```bash
# Create CSV file (domains.csv)
domain
google.com
github.com
reddit.com

# Check from CSV
ssl-check check-csv domains.csv --output results.json
```

### API Integration

```bash
# Check domains from API (expects JSON array with 'domain' fields)
ssl-check check-api https://api.example.com/domains --format csv
```

### Continuous Monitoring

```bash
# Monitor every 6 hours
ssl-check monitor --interval 6 google.com github.com

# With custom warnings
ssl-check monitor --warning-days 14 --interval 12 google.com
```

### Export Options

```bash
# Export to different formats
ssl-check check google.com --output certs.xlsx --format xlsx
ssl-check check google.com --output certs.csv --format csv
```

## Email Alerts

Configure SMTP settings in `.env` file:

```env
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
FROM_EMAIL=your-email@gmail.com
TO_EMAIL=alerts@yourcompany.com
```

Alerts are sent automatically during monitoring for:
- Expired certificates
- Certificates expiring within warning threshold

## Output Example

```
SSL Certificate Status
┏━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━┳━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━┓
┃ Domain          ┃ Days Left ┃ Valid Until  ┃ Status            ┃
┡━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━╇━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━┩
│ google.com      │ 89        │ 2026-07-15   │ VALID             │
│ expired.badssl.com │ -45    │ 2025-12-01   │ EXPIRED           │
│ expiring.badssl.com│ 15     │ 2026-04-21   │ EXPIRING SOON     │
└─────────────────┴───────────┴──────────────┴───────────────────┘

⚠️  1 certificates have expired!
⚠️  1 certificates expiring within 30 days!
```

## Advanced Features

### Certificate Details
- Issuer and subject information
- Serial numbers and signature algorithms
- Public key sizes
- Exact validity periods

### Error Handling
- Graceful handling of unreachable domains
- Timeout configuration
- Detailed error logging

### Performance
- Concurrent checking (future enhancement)
- Efficient certificate parsing
- Minimal memory footprint

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| SSL_TIMEOUT | Connection timeout in seconds | 10 |
| WARNING_DAYS | Days before expiry to warn | 30 |

### SMTP Configuration

See Email Alerts section above.

## Testing

```bash
# Run tests
python -m pytest tests/

# Run with coverage
python -m pytest tests/ --cov=src
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new features
4. Ensure all tests pass
5. Submit a pull request

## License

MIT License - see LICENSE file for details.

## Support

For issues and questions:
- Create an issue on GitHub
- Check the documentation
- Review the test cases for usage examples