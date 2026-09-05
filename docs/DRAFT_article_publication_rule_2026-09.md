# DRAFT — rule change for #16497 long-form tier (and the article bounties that inherit from it: #282, #727)

## 1. Replace row 1 of "What earns RTC"

| # | Deliverable | RTC | Cap |
|---|---|---|---|
| 1 | **Long-form article or tutorial** — 500+ words, working code, links back to the repo it covers, **published on an allowlisted platform** (see *Where it has to live*). Paid in two parts: **13 RTC when the draft is accepted, 20 RTC when it is live off-platform and still up 7 days later.** | 33 | 2 per person |

## 2. New section, inserted after "What we will not pay for"

### Where it has to live

We pay for readers, not for files. An article nobody outside this repo can find has done its job for you and none for the project. So the article tier now has one hard requirement on top of the writing:

**The piece must be published on a platform where people who have never heard of RustChain can find it:**

- dev.to, Hashnode, Medium, Substack
- Hackaday.io (project pages)
- Your own blog on your own domain (we verify the byline and that it is indexed)

**These do not count as publication** — they are fine as *supporting material* linked from the article, not as the article's home:

- a GitHub repo, README, issue, gist, or wiki page
- a raw file on any CDN (raw.githubusercontent.com, cdn.shopify.com, cloudfront, S3, Drive, Dropbox, Pastebin)
- a BoTTube or YouTube *description* (video is its own tier)
- a page behind a login or a paywall

**How the money moves.** Post your `Live-URL:` line with the claim, exactly as the video and Shorts tiers already do. On acceptance of the writing you get 13 RTC. Seven days later the verifier re-checks the URL; if the piece is still up under your byline you get the remaining 20. If it is gone, the 20 lapses — we do not chase it, and you can post a new URL once.

**Reach bonus (optional, +5 RTC).** Thirty days after publication, if the piece shows real engagement on its platform (dev.to ≥ 25 reactions, Hashnode ≥ 250 views, Medium ≥ 50 claps, Substack ≥ 25 likes, or a Hacker News / Lobsters thread with ≥ 10 points), post the numbers and we add 5. One bonus per article. Screenshots count; we spot-check.

**Syndication still stacks.** The #16601 Type D add-on (+8 RTC when *we* cross-post you to the official Elyan blogs with your byline) is unchanged and combines with this.

**Not retroactive.** Everything accepted before 2026-09-08 stands under the old rule. From that date, claims without an allowlisted `Live-URL:` are held, not rejected, until one is posted.

## 3. Amend the "Evidence" paragraph

Replace: *"Every claim needs: a public URL we can open, …"*
With: *"Every claim needs: **a `Live-URL:` line pointing at an allowlisted platform** (articles, video, Shorts — see the platform list), your RTC wallet address, and one line on what it covers. GitHub and CDN links go in the body as supporting material; they are not the Live-URL."*

## 4. Why 13 / 20

Docstrings pay 0.01 per function and a README badge pays 2, so 13 for a 500-word accepted draft is already generous for the writing alone. Twenty on publication puts most of the reward behind the only part that brings a new person to the repo. Splitting also removes the incentive to publish to the cheapest URL and disappear.

## 5. What changes in the verifier (draft PR alongside this)

- Allowlist gains **Substack** (`<name>.substack.com/p/<slug>`) and a **`custom-domain`** class (any other host with an `https://` URL that is not on the denylist; classified as *manual* so a maintainer confirms byline and indexing once).
- New **denylist with reasons**, so a rejection says *why*: `github.com`, `gist.github.com`, `raw.githubusercontent.com`, `cdn.shopify.com`, `*.cloudfront.net`, `*.amazonaws.com`, `drive.google.com`, `dropbox.com`, `pastebin.com`.
- `find_live_url` returns a fourth state, **"denied"**, carrying the reason text for the claim reply.
