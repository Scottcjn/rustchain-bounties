# RustChain Multi-Node Health Dashboard

## Overview

The Multi-Node Health Dashboard is a comprehensive monitoring tool designed to track the health status of all three RustChain attestation nodes. It provides real-time insights into node availability, response times, and detailed health metrics.

## Features

- **Multi-Node Monitoring**: Simultaneously checks all 3 attestation nodes
- **Real-time Status**: Live health status for each node
- **Performance Metrics**: Response time tracking and analysis
- **Detailed Reporting**: Comprehensive health dashboard with recommendations
- **JSON Export**: Save health check results for further analysis
- **Command Line Interface**: Easy-to-use CLI with customizable node URLs

## Usage

### Basic Usage

```bash
python health-check.py
```

This will check the default set of nodes (configured in the script).

### Custom Node URLs

```bash
python health-check.py https://node1.yourdomain.com https://node2.yourdomain.com https://node3.yourdomain.com
```

### Expected Node Health Endpoint

Each node should expose a `/health` endpoint that returns JSON data with health information. Example response:

```json
{
  "status": "healthy",
  "version": "1.0.0",
  "uptime": 86400,
  "connections": 42,
  "last_block": 12345,
  "sync_status": "synced"
}
```

## Output Example

```
================================================================================
RUSTCHAIN MULTI-NODE HEALTH DASHBOARD
================================================================================

Generated: 2024-01-15 14:30:45

OVERALL STATUS: 2/3 nodes healthy

NODE_1 (https://node1.rustchain.com)
  Status: HEALTHY
  Response Time: 125.43ms
  Details:
    status: healthy
    version: 1.0.0
    uptime: 86400
    connections: 42
    last_block: 12345
    sync_status: synced

NODE_2 (https://node2.rustchain.com)
  Status: HEALTHY
  Response Time: 98.76ms
  Details:
    status: healthy
    version: 1.0.0
    uptime: 86400
    connections: 38
    last_block: 12345
    sync_status: synced

NODE_3 (https://node3.rustchain.com)
  Status: UNHEALTHY
  Error: HTTP 503: Service Unavailable

RECOMMENDATIONS:
⚠️  1 node(s) need attention

PERFORMANCE METRICS:
  Average Response Time: 112.10ms
  Max Response Time: 125.43ms
  Min Response Time: 98.76ms

================================================================================
```

## Integration

### Cron Jobs

Set up automated health checks:

```bash
# Check every 5 minutes
*/5 * * * * /usr/bin/python3 /path/to/health-check.py >> /var/log/rustchain-health.log 2>&1
```

### Monitoring Systems

The JSON output can be integrated with:
- Prometheus/Grafana
- Nagios
- Datadog
- Custom monitoring dashboards

## Error Handling

The tool handles various error conditions:
- **Timeout**: Nodes not responding within 10 seconds
- **Connection Errors**: Network connectivity issues
- **HTTP Errors**: Non-200 status codes
- **JSON Parsing**: Malformed responses

## Configuration

### Timeout Settings

Modify the `timeout` parameter in the `HealthChecker` class:

```python
self.timeout = 15  # Change from 10 to 15 seconds
```

### Node URLs

Update the default node list in `main()` or provide them as command line arguments.

## Contributing

To contribute to the health dashboard:

1. Fork the repository
2. Create a feature branch
3. Test your changes
4. Submit a pull request

## License

This project is part of the RustChain ecosystem and follows the same license terms.
