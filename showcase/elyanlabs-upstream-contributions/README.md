# Elyan Labs Upstream Contributions Showcase

Submission-ready first pass for RustChain bounty issue #2958.

## Files

- `index.html` — mobile-responsive showcase page for `elyanlabs.ai`
- `data.json` — generated dataset backing the page

## What is included

- 44 verified merged upstream PRs authored by `Scottcjn` and merged outside the Elyan Labs org
- Grouped repository cards with owner avatars, repo descriptions, repository links, direct PR links, and star counts
- Separate section for 5 higher-profile PRs with status labels refreshed as of 2026-04-12
- Mobile-responsive layout

## Data provenance

- Merged list was generated on **2026-04-11** from GitHub search: `author:Scottcjn is:pr is:merged -user:Scottcjn`
- Tracked PR statuses were refreshed on **2026-04-12** based on the latest review snapshot
- Star counts were captured from the GitHub repository API on **2026-04-11**

## Final QA still recommended

1. Open `index.html` locally and check visual polish on desktop + mobile widths
2. Re-verify the tracked PR statuses if publishing after 2026-04-12
3. Re-check repo star counts if the page will be publicly deployed later than this week
4. Optionally add Elyan Labs site header/footer wrapper so it matches production branding
5. Spot-check a few representative PR links after deployment to confirm the host/site pathing did not change asset loading
