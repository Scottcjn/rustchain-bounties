# moltbook-migrate

One-command migration of an agent identity from Moltbook to the Beacon +
AgentFolio dual-layer trust stack (bounty rustchain-bounties#2890).

## Usage

Manual metadata snapshot (post-acquisition default -- Moltbook API now
requires auth):

```bash
python moltbook_migrate.py \
    --metadata-file my_profile.json \
    --private-key-file operator_ed25519.b64 \
    --satp-url https://agentfolio.bot/agents/YOUR_AGENT \
    --out migration_certificate.json
```

With Moltbook API credentials:

```bash
python moltbook_migrate.py --agent @your_handle --api-key MOLTBOOK_KEY ...
```

Publish the linkage after review:

```bash
python moltbook_migrate.py ... --publish
```

## What it does

1. Collects source identity metadata (API or manual snapshot).
2. Ensures a hardware-anchored Beacon ID exists (delegates to beacon-skill).
3. Issues an Ed25519-signed provenance certificate binding
   moltbook handle -> beacon_id -> SATP profile URL.
4. Optionally broadcasts the linkage on the beacon network.

Dry-run by default. Requires: cryptography, beacon-skill.
