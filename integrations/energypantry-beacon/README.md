# Energypantry Beacon Integration (Issue #158)

This package is a minimal, verifiable Beacon integration proof for:
- https://github.com/Scottcjn/rustchain-bounties/issues/158

Implemented features:
- Heartbeat (`send_heartbeat`)
- Mayday (`send_mayday`)
- Contract offer (`create_contract_offer`)

## Files

- `energypantry_beacon_agent.py`: integration implementation
- `test_beacon_integration.py`: offline reproducible tests
- `demo_output.json`: captured demo output from local run
- `test_output.txt`: captured unit test output

## Run

```bash
cd integrations/energypantry-beacon
python3 test_beacon_integration.py
python3 energypantry_beacon_agent.py --bridge memory > demo_output.json
```

## Notes

- Default bridge is `InMemoryBeaconBridge` for deterministic testing and CI friendliness.
- Optional live mode is available via `--bridge beacon-skill` (requires `pip install beacon-skill`).
