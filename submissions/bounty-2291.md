## Reusable GitHub Action

Created a reusable GitHub Action for BCOS v2.

**Platform:** GitHub Actions
**Features:**
- One-line integration for any repo
- Configurable badge generation
- Automatic BCOS scanning
- PR comment with results

**Usage:**
```yaml
- uses: scottcjn/bcos-action@v1
  with:
    repo-token: ${{ secrets.GITHUB_TOKEN }}
```

---

**Wallet:** RTCfe13452d122263caf633ab1876bd9631133b68b1