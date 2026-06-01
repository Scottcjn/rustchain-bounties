import asyncio
import json
from pathlib import Path


MANIFEST = Path(__file__).resolve().parents[1] / "integrations" / "rustchain-mcp" / "server.json"
PACKAGE_ROOT = MANIFEST.parent


def test_rustchain_mcp_manifest_is_registry_ready(monkeypatch):
    data = json.loads(MANIFEST.read_text(encoding="utf-8"))

    assert data["$schema"] == "https://static.modelcontextprotocol.io/schemas/2025-12-11/server.schema.json"
    assert data["name"] == "io.github.Scottcjn/rustchain-mcp"
    assert data["version"] == "0.3.0"
    assert len(data["description"]) <= 100
    assert data["repository"] == {
        "url": "https://github.com/Scottcjn/rustchain-mcp",
        "source": "github",
        "id": "1176373929",
    }

    [package] = data["packages"]
    assert package["registryType"] == "pypi"
    assert package["identifier"] == "rustchain-mcp"
    assert package["version"] == data["version"]
    assert package["transport"] == {"type": "stdio"}

    env_names = {entry["name"] for entry in package["environmentVariables"]}
    assert env_names == {
        "RUSTCHAIN_PRIMARY_URL",
        "RUSTCHAIN_FALLBACK_URLS",
        "BOTTUBE_API_BASE_URL",
        "BOTTUBE_API_KEY",
    }

    monkeypatch.syspath_prepend(str(PACKAGE_ROOT))
    monkeypatch.setenv("RUSTCHAIN_PRIMARY_URL", "https://primary.example.test/")
    monkeypatch.setenv("RUSTCHAIN_FALLBACK_URLS", "https://fallback-a.example.test/, https://fallback-b.example.test")

    from rustchain_mcp.client import RustChainClient

    client = RustChainClient.from_env()
    assert client.primary_url == "https://primary.example.test"
    assert client.fallback_urls == [
        "https://fallback-a.example.test",
        "https://fallback-b.example.test",
    ]

    monkeypatch.setenv("BOTTUBE_API_BASE_URL", "https://bottube.example.test/api/")
    monkeypatch.setenv("BOTTUBE_API_KEY", "bottube_sk_test")

    from rustchain_mcp.client import BoTTubeClient

    bottube_client = BoTTubeClient.from_env()
    assert bottube_client.base_url == "https://bottube.example.test/api"
    assert bottube_client.api_key == "bottube_sk_test"


def test_bottube_client_uses_documented_api_paths_and_headers(monkeypatch):
    monkeypatch.syspath_prepend(str(PACKAGE_ROOT))

    calls = []

    class FakeResponse:
        def raise_for_status(self):
            return None

        def json(self):
            return {"ok": True}

    class FakeAsyncClient:
        def __init__(self, **kwargs):
            self.kwargs = kwargs

        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            return False

        async def get(self, url, params=None, headers=None):
            calls.append({"url": url, "params": params, "headers": headers})
            return FakeResponse()

    from rustchain_mcp import client as client_module
    from rustchain_mcp.client import BoTTubeClient

    monkeypatch.setattr(client_module.httpx, "AsyncClient", FakeAsyncClient)

    client = BoTTubeClient(base_url="https://bottube.ai/api", api_key="bottube_sk_test")
    asyncio.run(client.trending(category="gaming", limit=5))
    asyncio.run(client.search(query="AI art", limit=3, page=2, sort="newest"))
    asyncio.run(client.video("vid_abc123"))
    asyncio.run(client.agent("creative-bot-42"))
    asyncio.run(client.stats())

    assert calls == [
        {
            "url": "https://bottube.ai/api/trending",
            "params": {"limit": 5, "category": "gaming"},
            "headers": {"X-API-Key": "bottube_sk_test"},
        },
        {
            "url": "https://bottube.ai/api/search",
            "params": {"q": "AI art", "limit": 3, "page": 2, "sort": "newest"},
            "headers": {"X-API-Key": "bottube_sk_test"},
        },
        {
            "url": "https://bottube.ai/api/videos/vid_abc123",
            "params": None,
            "headers": {"X-API-Key": "bottube_sk_test"},
        },
        {
            "url": "https://bottube.ai/api/agents/creative-bot-42",
            "params": None,
            "headers": {"X-API-Key": "bottube_sk_test"},
        },
        {
            "url": "https://bottube.ai/api/stats",
            "params": None,
            "headers": {"X-API-Key": "bottube_sk_test"},
        },
    ]
