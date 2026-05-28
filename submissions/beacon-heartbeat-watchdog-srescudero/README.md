# Beacon for AI Agents: A Practical Heartbeat and Watchdog Tutorial

This article is a submission draft for RustChain bounty #160:
https://github.com/Scottcjn/rustchain-bounties/issues/160

Author: SrEscudero

## What Beacon Solves

Most agent systems fail quietly. A worker process stops, a remote model provider
times out, a payment tool hangs, or a coordinator assumes another agent is still
alive because the last task did not explicitly fail. That is acceptable for a
small script, but it is weak infrastructure for agents that coordinate work,
exchange value, or accept tasks from other agents.

Beacon adds a social and economic coordination layer for agents. The official
`beacon-skill` package describes Beacon as a protocol for agent-to-agent pings,
signed envelopes, identity, discovery, local UDP messages, webhooks, RustChain
payments, mayday notices, heartbeats, and Atlas registration. In practice, that
means an agent can say, "I am alive", "I am degraded", "I need help", or "I can
accept this kind of work" in a format that other agents can verify and route.

This tutorial focuses on the fastest useful path: create an agent identity, send
a signed local webhook message, inspect the inbox, and then turn that flow into a
watchdog pattern for real agent processes.

## Prerequisites

Use a virtual environment so the package install is isolated:

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install beacon-skill
```

Confirm that the CLI is available:

```bash
beacon --help
```

The commands below follow the public quick start from the `beacon-skill`
repository:

```bash
beacon identity new
beacon webhook serve --port 8402
beacon webhook send http://127.0.0.1:8402/beacon/inbox --kind hello
beacon inbox list --limit 1
```

## Step 1: Create an Agent Identity

Beacon identities are based on Ed25519 keys. The agent ID is derived from the
public key and is stored locally under the user's Beacon directory. Create one:

```bash
beacon identity new
beacon identity show
```

Keep private keys and mnemonic phrases private. For a bounty submission, only the
agent ID and non-secret output should be shared.

## Step 2: Run a Local Webhook Inbox

Open one terminal and start a local Beacon inbox:

```bash
beacon webhook serve --port 8402
```

This gives another process a place to deliver a signed envelope. For a real
internet-facing agent, the webhook would run behind HTTPS and expose
`/beacon/inbox`, `/beacon/health`, and `/.well-known/beacon.json`. For a first
test, loopback is enough.

## Step 3: Send a Signed Hello Message

In a second terminal, send a message to the local inbox:

```bash
beacon webhook send http://127.0.0.1:8402/beacon/inbox \
  --kind hello
```

Then inspect the inbox:

```bash
beacon inbox list --limit 1
```

At this point you have validated the core mechanism: identity exists, a receiver
is listening, an envelope can be sent, and the result can be inspected. The
installed PyPI CLI for `beacon-skill==2.16.0` accepts `--kind` for `webhook
send`; if a newer release adds message-body flags, keep this smoke test on the
minimal command so reviewers can reproduce it across versions.

## Step 4: Automate the Smoke Test

For reviewers and future maintainers, repeatable evidence is better than a
screenshot. The script in `examples/beacon_loopback_check.py` runs the local
flow from one command:

```bash
python examples/beacon_loopback_check.py
```

It checks for the `beacon` CLI, ensures an identity exists, starts a local
webhook receiver, sends a `hello` envelope, lists the latest inbox entry, and
then shuts the receiver down. This is not a replacement for a production
deployment, but it is a clean smoke test for onboarding and documentation.

## Step 5: Turn It Into a Watchdog

Once the loopback flow works, the next step is to attach Beacon to an agent
runner. A simple pattern is:

1. Send a `hello` message when the process starts.
2. Send a heartbeat or status message on a timer.
3. Use `status=degraded` when the agent can still respond but a dependency is
   failing.
4. Use a mayday signal when the agent is going offline or needs another agent to
   take over.
5. Keep the agent ID stable so peers can build trust over time.

In a production task queue, the coordinator can check recent Beacon activity
before assigning expensive work. If a worker has been silent for too long, the
coordinator can skip it, retry elsewhere, or ask a backup agent to take over.
The important shift is that liveness becomes explicit instead of guessed.

## Why This Matters

MCP lets an agent call tools. Task protocols let agents delegate work. Beacon
fills a different gap: it helps agents coordinate presence, provenance, status,
and value. That makes it useful for bounty agents, mining agents, content
agents, monitoring agents, and any workflow where "silent failure" is expensive.

The smallest useful Beacon integration is not a full platform. It is a verified
identity plus a repeatable signal. Start with the local webhook test, capture the
output, publish the agent ID, and then wire the same heartbeat idea into the
agent loop that does real work.

## Links

- Beacon GitHub repo: https://github.com/Scottcjn/beacon-skill
- PyPI package: https://pypi.org/project/beacon-skill/
- npm package: https://www.npmjs.com/package/beacon-skill
- RustChain bounty #160: https://github.com/Scottcjn/rustchain-bounties/issues/160
