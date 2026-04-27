# Self-Audit: integrations/rustchain-mcp/rustchain_mcp/server.py

## Wallet
RTC-floyd000000000000000000000000000000000000

## Module reviewed
- Path: integrations/rustchain-mcp/rustchain_mcp/server.py
- Commit reviewed: HEAD (main branch)
- Language: Python
- Role: MCP (Model Context Protocol) server exposing Rustchain GitHub data to AI agents

---

## 1. Module Overview

`server.py` implements an MCP server that wraps the GitHub API to expose Rustchain bounty data (issues, pull-requests, XP ledger, etc.) as tools and resources callable by LLM agents. It is the primary attack surface for any agent-facing deployment of Rustchain.

Key responsibilities:
- Authenticate to GitHub API via `GITHUB_TOKEN`
- Expose tools: `get_issues`, `get_pull_requests`, `submit_bounty_claim`, `get_leaderboard`, etc.
- Serve resources: repository metadata, open bounties list
- Parse and relay structured JSON/Markdown responses back to agents

---

## 2. Findings

### FINDING-01 — No input validation on `submit_bounty_claim` arguments
**Severity:** HIGH  
**Confidence:** 90%

**Description:**  
The `submit_bounty_claim` tool accepts free-form text fields (wallet address, submission URL, description) and forwards them directly into a GitHub issue comment or PR body via the GitHub API. There is no sanitisation, length-cap, or format-enforcement before the string is interpolated into the API payload.

**Consequence:**  
- Prompt injection: a malicious agent (or user controlling an agent) can embed markdown/HTML that manipulates how the issue body renders, potentially tricking human reviewers.  
- Wallet address is never validated against the `RTC-prefix-40-hex` schema defined in the submission grammar, so garbage wallet strings are silently accepted and stored on-chain in the ledger.  
- Unbounded strings can trigger GitHub API 422 errors that are not caught, leaving the agent in an undefined state.

**Code path (reconstructed):**
