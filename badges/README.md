# Dynamic Badges

This directory contains shields.io endpoint badges for the RustChain Bounty program, generated automatically from the XP tracker.

## Available Badges

### Global Stats

| Badge | Description | Endpoint |
|-------|-------------|----------|
| ![Total XP](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/Scottcjn/rustchain-bounties/main/badges/hunter-stats.json) | Total bounty hunter XP | `badges/hunter-stats.json` |
| ![Top Hunter](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/Scottcjn/rustchain-bounties/main/badges/top-hunter.json) | Current top hunter | `badges/top-hunter.json` |
| ![Top 3](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/Scottcjn/rustchain-bounties/main/badges/top-3-hunters.json) | Top 3 hunters | `badges/top-3-hunters.json` |
| ![Active](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/Scottcjn/rustchain-bounties/main/badges/active-hunters.json) | Number of active hunters | `badges/active-hunters.json` |
| ![Legendary](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/Scottcjn/rustchain-bounties/main/badges/legendary-hunters.json) | Legendary hunters (L10+) | `badges/legendary-hunters.json` |
| ![Growth](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/Scottcjn/rustchain-bounties/main/badges/weekly-growth.json) | Weekly XP growth | `badges/weekly-growth.json` |
| ![Updated](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/Scottcjn/rustchain-bounties/main/badges/updated-at.json) | Last update date | `badges/updated-at.json` |

### Category Badges (if data available)

| Badge | Description | Endpoint |
|-------|-------------|----------|
| ![Docs](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/Scottcjn/rustchain-bounties/main/badges/category-docs.json) | Documentation bounties | `badges/category-docs.json` |
| ![Outreach](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/Scottcjn/rustchain-bounties/main/badges/category-outreach.json) | Outreach bounties | `badges/category-outreach.json` |
| ![Bug](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/Scottcjn/rustchain-bounties/main/badges/category-bug.json) | Bug bounty count | `badges/category-bug.json` |

### Per-Hunter Badges

Each hunter has their own badge at `badges/hunters/<slug>.json`.

Example: `badges/hunters/tianlin-rtc.json`

## Embedding Badges

### In GitHub README

```markdown
![Bounty Hunter XP](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/Scottcjn/rustchain-bounties/main/badges/hunter-stats.json)
```

### In External Profiles

Replace ` hunter-stats.json` with any badge endpoint:

```markdown
![Top Hunter](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/Scottcjn/rustchain-bounties/main/badges/top-hunter.json)
```

### Hunter-Specific Badge

```markdown
![My XP](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/Scottcjn/rustchain-bounties/main/badges/hunters/YOUR-SLUG.json)
```

Find your slug by looking at the `badges/hunters/` directory or running the badge generator.

## Badge Generator

To regenerate badges locally:

```bash
python .github/scripts/generate_dynamic_badges.py
```

With custom paths:

```bash
python .github/scripts/generate_dynamic_badges.py \
  --tracker bounties/XP_TRACKER.md \
  --history bounties/XP_HISTORY.md \
  --ledger bounties/LEDGER.md \
  --out-dir badges
```

## Badge Schema

All badges follow the [shields.io endpoint schema](https://shields.io/endpoint):

```json
{
  "schemaVersion": 1,
  "label": "Badge Label",
  "message": "Badge Message",
  "color": "badge-color",
  "namedLogo": "logo-name",
  "logoColor": "logo-color"
}
```

## Colors

| Level | Color | Description |
|-------|-------|-------------|
| 1-3 | blue | Starting/Basic/Priority Hunter |
| 4 | orange | Rising Hunter |
| 5-6 | yellow | Multiplier/Featured Hunter |
| 7-9 | purple | Veteran/Elite/Master Hunter |
| 10+ | gold | Legendary Hunter |

## Automation

Badges are automatically regenerated when:
- XP tracker is updated
- New bounties are claimed
- Weekly summary runs

See `.github/workflows/xp-badge-tests.yml` for CI configuration.
