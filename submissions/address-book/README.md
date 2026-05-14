# 📒 RustChain Address Book Manager

Manage frequently-used cryptocurrency addresses with groups, tags, and search. Supports import/export (JSON, CSV) and auto chain detection.

## Features

- **Groups**: Organize addresses into groups (personal, exchange, friend, contract...)
- **Tags**: Flexible tagging system for cross-group categorization
- **Search**: Full-text search across name, address, memo, and tags
- **Auto-detection**: Automatically detect chain from address prefix
- **Import/Export**: JSON and CSV formats
- **Duplicate detection**: Prevents duplicate addresses
- **CRUD**: Full create, read, update, delete operations

## Quick Start

```bash
# Add an address
python addressbook.py add "My Wallet" rtc1qexample... --group personal --tags main,backup

# List all
python addressbook.py list

# Search
python addressbook.py search "wallet"

# Export
python addressbook.py export --format json --output my_addresses.json
```

## Commands

### Add Address
```bash
python addressbook.py add "Name" rtc1q... --group personal --tags tag1,tag2 --memo "Notes"
```

### List Addresses
```bash
# All addresses
python addressbook.py list

# Filter by group
python addressbook.py list --group personal

# Filter by chain
python addressbook.py list --chain rtc

# Filter by tag
python addressbook.py list --tag main
```

### Search
```bash
python addressbook.py search "wallet"
python addressbook.py search "rtc1q..."
```

### Update
```bash
python addressbook.py update 1 --name "New Name" --group exchange --tags updated
```

### Delete
```bash
python addressbook.py delete 1
```

### Groups
```bash
python addressbook.py groups
```

### Export
```bash
# JSON format
python addressbook.py export --format json --output addresses.json

# CSV format
python addressbook.py export --format csv --output addresses.csv
```

### Import
```bash
# Auto-detect format
python addressbook.py import --file addresses.json

# Force format
python addressbook.py import --file data.csv --format csv
```

## Supported Chains (Auto-detected)

| Prefix | Chain |
|--------|-------|
| `rtc1` | RustChain |
| `0x` | Ethereum |
| `1`/`3`/`bc1` | Bitcoin |
| `cosmos1` | Cosmos |

## Data Storage

Addresses are stored in `addressbook.json` in the same directory:

```json
{
  "version": "1.0",
  "addresses": [
    {
      "id": 1,
      "name": "My Wallet",
      "address": "rtc1q...",
      "chain": "rtc",
      "group": "personal",
      "tags": ["main"],
      "memo": "",
      "created": "2025-01-15T10:00:00",
      "updated": "2025-01-15T10:00:00"
    }
  ],
  "groups": ["personal", "exchange", "friend", "contract", "other"]
}
```

## Dependencies

- Python 3.7+
- No external dependencies

## License

MIT License - Part of the RustChain Ecosystem
