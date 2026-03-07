# RustChain Health Check CLI Tool

A command-line tool to monitor the health status of RustChain attestation nodes.

## Features

- 🔍 **Real-time Monitoring** - Query all 3 attestation nodes instantly
- 🎨 **Color-coded Output** - Visual status indicators (green/yellow/red)
- 📊 **Key Metrics** - Version, uptime, database status, tip age
- 🔧 **JSON Mode** - Machine-readable output for automation
- ⚡ **Fast & Lightweight** - Single Python file, minimal dependencies

## Installation

```bash
# Clone or download the script
git clone <repository>
cd bounty-1111

# Install dependencies
pip install -r requirements.txt

# Make executable (optional)
chmod +x health_check.py
```

## Usage

### Basic Usage

```bash
python3 health_check.py
```

### JSON Output (for automation)

```bash
python3 health_check.py --json
# or
python3 health_check.py -j
```

## Sample Output

### Normal Mode

```
╔══════════════════════════════════════════════════════════════╗
║           🦀 RustChain Health Check CLI v1.0                 ║
╚══════════════════════════════════════════════════════════════╝
  Timestamp: 2026-03-07 23:58:21 UTC

┌─ Node Beta (50.28.86.153:8099)
│  Status:    ● ONLINE
│  Version:   2.2.1-rip200
│  Uptime:    4.1d
│  DB Status: ✓ readwrite
│  Tip Age:   0s
└

═══════════════════════════════════════════════════════════════
  Network Summary:
    Nodes Online: 1/3
    Status: ⚠ Degraded performance
═══════════════════════════════════════════════════════════════
```

### JSON Mode

```json
{
  "timestamp": "2026-03-07T23:58:21.049302",
  "nodes": [
    {
      "name": "Node Beta",
      "ip": "50.28.86.153",
      "port": 8099,
      "status": "online",
      "version": "2.2.1-rip200",
      "uptime": 357371,
      "db_rw": true,
      "tip_age": 0
    }
  ],
  "summary": {
    "total": 3,
    "online": 1,
    "offline": 1,
    "errors": 1
  }
}
```

## Monitored Nodes

| Name | IP Address | Port |
|------|------------|------|
| Node Alpha | 50.28.86.131 | 8099 |
| Node Beta | 50.28.86.153 | 8099 |
| Node Gamma | 76.8.228.245 | 8099 |

## Health Metrics

- **Version** - Software version running on the node
- **Uptime** - How long the node has been running
- **DB Status** - Database access mode (readwrite/readonly)
- **Tip Age** - Age of the latest block/slot in seconds
- **Backup Age** - Hours since last backup (if available)

## Status Indicators

| Status | Color | Meaning |
|--------|-------|---------|
| ● ONLINE | 🟢 Green | Node responding normally |
| ● OFFLINE | 🔴 Red | Connection refused |
| ● TIMEOUT | 🟡 Yellow | Connection timed out |
| ● ERROR | 🔴 Red | HTTP error or exception |

## Requirements

- Python 3.7+
- `requests` library

## License

MIT License - Created for RustChain Bounty #1111

## Wallet for RTC Payout

**sovereign-agent**
