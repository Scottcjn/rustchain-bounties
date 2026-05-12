from scripts.node_miner_weekly_scan import (
    _aggregate_miners,
    _dedupe_preserve,
    _registry_rows_to_map,
    node_identity,
    normalize_base_url,
)


def test_normalize_base_url_adds_https_and_drops_path():
    assert normalize_base_url(" node.example.com/api/miners ") == "https://node.example.com"
    assert normalize_base_url("http://node.example.com:8080/health") == "http://node.example.com:8080"
    assert normalize_base_url("") == ""


def test_node_identity_uses_default_ports():
    assert node_identity("https://node.example.com") == "node.example.com:443"
    assert node_identity("http://node.example.com") == "node.example.com:80"
    assert node_identity("https://node.example.com:9443") == "node.example.com:9443"


def test_dedupe_preserve_normalizes_and_keeps_first_url():
    urls = [
        "node.example.com",
        "https://node.example.com/health",
        "http://node.example.com",
        "https://other.example.com:9443/api/miners",
        "",
    ]

    assert _dedupe_preserve(urls) == [
        "https://node.example.com",
        "http://node.example.com",
        "https://other.example.com:9443",
    ]


def test_registry_rows_to_map_accepts_dict_or_list_payloads():
    row_a = {"url": "node-a.example.com", "node_id": "node-a"}
    row_b = {"url": "https://node-b.example.com:9443/api", "node_id": "node-b"}

    mapped, rows = _registry_rows_to_map({"nodes": [row_a, "skip", row_b]})
    assert rows == [row_a, row_b]
    assert mapped["node-a.example.com:443"] is row_a
    assert mapped["node-b.example.com:9443"] is row_b

    mapped_from_list, rows_from_list = _registry_rows_to_map([row_a, 123])
    assert rows_from_list == [row_a]
    assert mapped_from_list == {"node-a.example.com:443": row_a}

    assert _registry_rows_to_map({"nodes": "not-a-list"}) == ({}, [])


def test_aggregate_miners_merges_latest_attest_and_unique_nodes():
    aggregate = _aggregate_miners(
        {
            "https://node-a.example.com": [
                {
                    "miner": " miner-1 ",
                    "last_attest": 100,
                    "first_attest": 10,
                    "device_family": "powerpc",
                    "device_arch": "ppc64",
                    "hardware_type": "g5",
                    "entropy_score": 0.9,
                    "antiquity_multiplier": 2.5,
                },
                {"miner": "", "last_attest": 999},
            ],
            "https://node-b.example.com": [
                {"miner": "miner-1", "last_attest": 250},
                {"miner": "miner-2", "last_attest": 0},
            ],
        }
    )

    assert aggregate["miner-1"]["last_attest"] == 250
    assert aggregate["miner-1"]["nodes_seen"] == [
        "https://node-a.example.com",
        "https://node-b.example.com",
    ]
    assert aggregate["miner-1"]["device_family"] == "powerpc"
    assert aggregate["miner-2"]["last_attest"] is None
