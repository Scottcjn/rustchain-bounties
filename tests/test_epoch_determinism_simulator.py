from scripts.epoch_determinism_simulator import run


def test_cross_node_replay_deterministic_when_same_events_different_order():
    evs_a = [
        {"epoch": 3, "height": 10, "txid": "b"},
        {"epoch": 3, "height": 9, "txid": "a"},
    ]
    evs_b = list(reversed(evs_a))
    payload = {
        "nodes": [
            {"node_id": "n1", "events": evs_a},
            {"node_id": "n2", "events": evs_b},
        ]
    }
    report = run(payload)
    assert report["deterministic"] is True
    assert report["mismatches"] == []


def test_cross_node_replay_detects_divergence():
    payload = {
        "nodes": [
            {"node_id": "n1", "events": [{"epoch": 1, "height": 1, "txid": "x"}]},
            {"node_id": "n2", "events": [{"epoch": 1, "height": 1, "txid": "y"}]},
        ]
    }
    report = run(payload)
    assert report["deterministic"] is False
    assert len(report["mismatches"]) == 1
