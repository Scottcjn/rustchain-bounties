import json
from pathlib import Path


MANIFEST = Path(__file__).resolve().parents[1] / "integrations" / "rustchain-mcp" / "server.json"


def test_rustchain_mcp_manifest_is_registry_ready():
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
    assert env_names == {"RUSTCHAIN_NODE", "BOTTUBE_URL", "BEACON_URL"}
