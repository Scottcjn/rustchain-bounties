# RustChain Health Check CLI

A simple CLI tool to query all RustChain attestation nodes and display their health status.

## Installation

```bash
pip install -r requirements.txt
chmod +x health-check.py
```

## Usage

### Human-readable table output:
```bash
./health-check.py
```

### JSON output:
```bash
./health-check.py --json
```

## Example Output

```
🦀 RustChain Node Health Status
============================================================
+----------------+------------+-----------+----------+--------+-----------+
| Node           | Status     | Version   | Uptime   | DB RW  | Tip Age   |
+================+============+===========+==========+========+===========+
| 50.28.86.131   | ✅ Online  | 1.0.0     | 12h34m   | ✅ RW  | 2s        |
+----------------+------------+-----------+----------+--------+-----------+
| 50.28.86.153   | ✅ Online  | 1.0.0     | 12h32m   | ✅ RW  | 1s        |
+----------------+------------+-----------+----------+--------+-----------+
| 76.8.228.245   | ✅ Online  | 1.0.0     | 12h30m   | ✅ RW  | 3s        |
+----------------+------------+-----------+----------+--------+-----------+
```

## Features
- Queries all 3 official attestation nodes
- Shows version, uptime, DB read/write status, and block tip age
- Supports both human-readable and JSON output formats
- Timeout handling for unresponsive nodes
