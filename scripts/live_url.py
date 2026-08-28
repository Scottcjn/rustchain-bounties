#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Parse and allowlist the `Live-URL:` line on distribution bounty claims.

WHY THIS EXISTS
---------------
An audit on 2026-08-28 of every distribution / human-funnel bounty (#315,
#16601, #16497, #282, #399, #2798, #14481) found roughly 45 claims that never
left GitHub and ZERO deliveries ever on X, YouTube, or Hackaday. "Posting now,
will update with the link" was never updated, thirteen times on #2798 alone.
The claim bot asked for nothing, so nothing is what it got.

A distribution bounty pays for a thing that exists OFF GitHub. This module is
the one place that decides what "off GitHub" means, so the claim bot
(`bounty_claim.py`) and the verifier (`verify_bounties.py`) cannot drift apart.

Shared by both scripts; no network, no side effects.
"""
from __future__ import annotations

import re
from urllib.parse import urlparse

# `Live-URL: https://...` on its own line. Case-insensitive on the key, tolerant
# of a bold/backtick-wrapped key and of surrounding whitespace, since people
# copy the field from the issue body in various renderings.
LIVE_URL_LINE_RE = re.compile(
    r"^[\s*_`]*live-url[\s*_`]*:[\s*_`<]*(https?://[^\s>*`]+)",
    re.IGNORECASE | re.MULTILINE,
)

# platform -> (host predicate, path regex). A URL is allowed only if BOTH match.
# Paths are anchored so `x.com/<user>` (a profile) or `youtube.com/@channel`
# (a channel) do not pass as a post or a video.
_ALLOWLIST: list[tuple[str, callable, re.Pattern]] = [
    ("bottube",
     lambda h: h in ("bottube.ai", "www.bottube.ai"),
     re.compile(r"^/watch/([A-Za-z0-9_-]+)/?$")),
    ("x",
     lambda h: h in ("x.com", "www.x.com", "twitter.com", "www.twitter.com",
                     "mobile.twitter.com"),
     re.compile(r"^/([A-Za-z0-9_]{1,15})/status/(\d+)/?$")),
    ("youtube",
     lambda h: h in ("youtube.com", "www.youtube.com", "m.youtube.com"),
     re.compile(r"^/(watch|shorts/[A-Za-z0-9_-]{6,})/?$")),
    ("youtube",
     lambda h: h == "youtu.be",
     re.compile(r"^/[A-Za-z0-9_-]{6,}/?$")),
    ("hackaday",
     lambda h: h in ("hackaday.io", "www.hackaday.io"),
     re.compile(r"^/project/\d+")),
    ("devto",
     lambda h: h in ("dev.to", "www.dev.to"),
     re.compile(r"^/[^/]+/[^/]+")),
    ("hashnode",
     lambda h: h.endswith(".hashnode.dev") and h.count(".") == 2,
     re.compile(r"^/.+")),
    ("medium",
     lambda h: h in ("medium.com", "www.medium.com") or h.endswith(".medium.com"),
     re.compile(r"^/.+")),
]


def classify_live_url(url: str) -> str | None:
    """Return the platform name for an allowlisted URL, else None."""
    if not url:
        return None
    try:
        p = urlparse(url.strip())
    except ValueError:
        return None
    if p.scheme not in ("http", "https") or not p.netloc:
        return None
    host = p.netloc.lower().split("@")[-1].split(":")[0]
    path = p.path or "/"
    for platform, host_ok, path_re in _ALLOWLIST:
        if host_ok(host) and path_re.match(path):
            # youtube.com/watch needs a v= parameter to be a video at all.
            if platform == "youtube" and path.rstrip("/") == "/watch" and "v=" not in p.query:
                return None
            return platform
    return None


def extract_live_urls(body: str) -> list[str]:
    """Every `Live-URL:` value in a comment body, in order, unfiltered."""
    if not body:
        return []
    return [m.group(1).rstrip(".,;)") for m in LIVE_URL_LINE_RE.finditer(body)]


def find_live_url(body: str) -> tuple[str | None, str | None, str]:
    """Return (url, platform, reason).

    reason is one of:
      "ok"       - an allowlisted Live-URL was found (url and platform set)
      "missing"  - no `Live-URL:` line at all (url None)
      "rejected" - a Live-URL line exists but no value is on the allowlist
                   (url is the first offending value, platform None)
    """
    urls = extract_live_urls(body)
    if not urls:
        return None, None, "missing"
    for u in urls:
        platform = classify_live_url(u)
        if platform:
            return u, platform, "ok"
    return urls[0], None, "rejected"


ALLOWED_HOSTS_HUMAN = (
    "bottube.ai/watch/…, x.com or twitter.com/<user>/status/<id>, "
    "youtube.com/watch?v=… or /shorts/…, youtu.be/…, hackaday.io/project/…, "
    "dev.to/<user>/<slug>, <you>.hashnode.dev/…, medium.com/…"
)
