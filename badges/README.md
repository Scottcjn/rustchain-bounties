# Dynamic Badges v2 - Shields.io Endpoint

This directory contains shields.io-compatible JSON badges for the RustChain bounty hunter program.

## Generated Badges

### Community Badges
- `hunter-stats.json` - Total XP across all hunters
- `top-hunter.json` - Current #1 hunter
- `active-hunters.json` - Count of active hunters
- `legendary-hunters.json` - Count of Level
- `updated 10+ hunters-at.json` - Last update timestamp

### New v2 Badges
- `top-3-hunters.json` - Top 3 hunters summary
- `weekly-growth.json` - Estimated weekly XP growth
- `docs-champions.json` - Hunters with documentation badges
- `bug-slayers.json` - Hunters with bug-related badges
- `outreach-stars.json` - Hunters with outreach badges

### Per-Hunter Badges
- `hunters/<username>.json` - Individual hunter stats

## Embedding in GitHub README

### Community Badges (shields.io endpoint)

```markdown
![Total XP](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/Scottcjn/rustchain-bounties/main/badges/hunter-stats.json)
![Top Hunter](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/Scottcjn/rustchain-bounties/main/badges/top-hunter.json)
![Active Hunters](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/Scottcjn/rustchain-bounties/main/badges/active-hunters.json)
```

### New v2 Badges

```markdown
![Top 3](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/Scottcjn/rustchain-bounties/main/badges/top-3-hunters.json)
![Weekly Growth](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/Scottcjn/rustchain-bounties/main/badges/weekly-growth.json)
![Docs Champions](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/Scottcjn/rustchain-bounties/main/badges/docs-champions.json)
```

### Per-Hunter Badge

Replace `<username>` with the hunter's GitHub username:

```markdown
![Hunter Stats](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/Scottcjn/rustchain-bounties/main/badges/hunters/<username>.json)
```

Example for createkr:
```markdown
![createkr](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/Scottcjn/rustchain-bounties/main/badges/hunters/createkr.json)
```

## Running Locally

Generate badges from XP_TRACKER.md:

```bash
python3 .github/scripts/generate_dynamic_badges.py
```

With custom paths:
```bash
python3 .github/scripts/generate_dynamic_badges.py --tracker bounties/XP_TRACKER.md --out-dir badges
```

## JSON Schema

All badges follow the shields.io schema:

```json
{
  "schemaVersion": 1,
  "label": "Label",
  "message": "value",
  "color": "blue",
  "namedLogo": "logo-name",
  "logoColor": "white"
}
```

The script validates all generated JSON against this schema.
