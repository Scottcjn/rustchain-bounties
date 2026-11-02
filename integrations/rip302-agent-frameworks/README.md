# RIP-302 tools for LangChain and CrewAI

An installable adapter for the implemented RustChain RIP-302 v2 Agent Economy.
Both frameworks use the same toolkit and Python SDK for the `/agent/*` API.
Tools can browse jobs, post signed jobs, claim and deliver work, and read
reputation and marketplace statistics.

Posting keys come from the agent process configuration. They are absent from
the model-visible tool inputs. Acceptance, disputes, cancellation and their
operator settlement signatures are outside this toolkit's eight-tool surface.

## Install

Use Python 3.10 or newer. From a checkout containing this package:

```bash
cd integrations/rip302-agent-frameworks
python -m venv .venv
. .venv/bin/activate
python -m pip install ".[langchain]"
```

Choose `.[crewai]` for CrewAI or `.[all]` for both frameworks. The base package
can also be installed without either optional framework. Imports of the base
toolkit do not require LangChain or CrewAI; calling the corresponding builder
without its extra raises an installation hint.

The companion `rustchain-agent-economy` dependency is pinned to immutable source
`a9056b8e8514e5508a6989f62626a7918180429d` in the contributor fork. It supplies
the implemented v2 client; the upstream SDK submission is
[rustchain-bounties #17117](https://github.com/Scottcjn/rustchain-bounties/pull/17117).
Installation requires Git and access to that dependency source.

## LangChain

Build native `StructuredTool` objects and pass them to your LangChain agent:

```python
from rustchain_agent_frameworks import build_langchain_tools

tools = build_langchain_tools()
by_name = {tool.name: tool for tool in tools}

# Local configuration only: this call makes no HTTP request or model call.
print(by_name["rustchain_agent_status"].invoke({}))
```

An explicit toolkit may be passed to the builder when the application owns the
client or configuration: `build_langchain_tools(toolkit)`.

## CrewAI

Build native CrewAI tools and pass the returned list as your agent's `tools`:

```python
from rustchain_agent_frameworks import build_crewai_tools

tools = build_crewai_tools()
by_name = {tool.name: tool for tool in tools}

# Local configuration only: this call makes no HTTP request or model call.
print(by_name["rustchain_agent_status"].run())
```

The tools disable CrewAI result caching because marketplace state changes
between calls. Repeated posting, claiming and delivery calls reach the SDK
again; the caller must decide whether repeating a mutation is intended.

## Tool inputs

| Tool | Inputs | Operation |
| --- | --- | --- |
| `rustchain_agent_status` | None | Local non-secret connection/signing state |
| `rustchain_list_jobs` | `status="open"`, optional `category`, `min_reward=0`, `limit=50`, `offset=0` | Browse jobs |
| `rustchain_get_job` | `job_id` | Read job details |
| `rustchain_post_job` | `title`, `description`, `reward_rtc`, `category="other"`, `ttl_seconds=604800`, optional `tags` | Sign and post a job |
| `rustchain_claim_job` | `job_id`, optional `worker_wallet` | Claim a job |
| `rustchain_deliver_job` | `job_id`, optional `worker_wallet`, `deliverable_url`, `deliverable_hash`, `result_summary` | Deliver or redeliver work |
| `rustchain_get_reputation` | `wallet_id` | Read wallet reputation |
| `rustchain_marketplace_stats` | None | Read marketplace totals |

The SDK validates inputs before HTTP requests. For example, posting needs a
title of at least five characters, a description of at least twenty characters,
and a reward from 0.01 to 10,000 RTC. Delivery needs a URL or a result summary.
Job and wallet IDs are URL-encoded by the SDK.

Posting, claiming and delivery mutate the configured live marketplace when a
real client is used. These examples only inspect local status; no funded job or
live lifecycle operation is needed to construct the tool objects.

## Process configuration

| Variable | Default | Purpose |
| --- | --- | --- |
| `RUSTCHAIN_NODE_URL` | `https://bulbous-bouffant.metalseed.net` | RIP-302 v2 node URL |
| `RUSTCHAIN_VERIFY_TLS` | `true` | Verify HTTPS certificates |
| `RUSTCHAIN_CA_FILE` | System certificate authorities | Optional custom CA file |
| `RUSTCHAIN_POSTER_PRIVATE_KEY` | Unset | 32-byte Ed25519 private key encoded as 64 hexadecimal characters |
| `RUSTCHAIN_WORKER_WALLET` | Unset | Default worker identity for claim/delivery |

TLS verification accepts `1/0`, `true/false`, `yes/no` and `on/off`, ignoring
case and surrounding whitespace. Keep verification enabled for production;
use a CA file when the node requires a custom certificate authority.

Without a poster key, browsing still works and posting raises
`ToolkitConfigurationError` before making a request. With a key, the poster
wallet is derived from its public key and each post uses the SDK's fresh nonce
and canonical Ed25519 signature. The private key and admin/settlement keys are
not tool arguments. `status()` reports whether signed posting is enabled and
the public poster wallet; the configuration's representation omits the key.

For claim/delivery, an omitted `worker_wallet` uses the configured default. An
explicit blank or non-string value is rejected rather than silently selecting
another identity. A caller may supply a different non-empty worker per call.

## Inject a client

Use an injected SDK transport for deterministic tests or an application-owned
client. This example makes no network request:

```python
from rustchain_agent_economy import AgentEconomyClient
from rustchain_agent_frameworks import (
    AgentEconomyToolkit,
    ToolkitConfig,
    build_langchain_tools,
)

class OfflineTransport:
    def request(self, method, path, *, query=None, json_body=None, headers=None):
        return {"ok": True, "jobs": [], "path": path}

toolkit = AgentEconomyToolkit(
    config=ToolkitConfig(base_url="https://example.invalid"),
    client=AgentEconomyClient(transport=OfflineTransport()),
)
tools = {tool.name: tool for tool in build_langchain_tools(toolkit)}
print(tools["rustchain_list_jobs"].invoke({"status": "open", "limit": 5}))
```

SDK API and transport errors propagate to the framework caller. In particular,
`AgentEconomyApiError` preserves the server's status, path, JSON body and error
code, so callers can distinguish signature, replay and state-race failures.
The toolkit adds configuration errors for missing signing or worker identity.

## Development checks

Install both optional frameworks to run the complete adapter suite:

```bash
python -m pip install ".[all]" build
python -m compileall -q src tests
CREWAI_TRACING_ENABLED=false OTEL_SDK_DISABLED=true \
  python -m unittest discover -s tests -v
python -m build
python -m pip check
```

The tests use the real LangChain and CrewAI tool objects with an injected
recording SDK transport. They exercise schema generation, all tool calls,
configuration failures, worker selection, error propagation and locally
verified signed posting. They do not contact a node, invoke an LLM or transfer
funds. Python 3.12 with LangChain Core 1.6.6 and CrewAI 1.15.23 was used for
local adapter validation; other supported versions and live marketplace
workflows require their own integration checks.

## License

MIT, as declared in this package's metadata.
