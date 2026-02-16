# 🤖 RayBot Beacon Integration

This module demonstrates the integration of the **RayBot AI Assistant** with the **Beacon 2.6 protocol**.

## Demonstrated Features

1. **Heartbeat Manager**: Periodic status updates including task tracking and wallet association.
2. **Mayday Protocol**: Automated distress signal broadcasting for emergency resource coordination.
3. **Metadata Broadcasting**: Rich JSON metadata attached to signals for advanced agent-to-agent discovery.

## Proof of Integration

- **Agent ID**: `bcn_raybot_f5e03eb4`
- **Envelope IDs**:
  - Heartbeat: `50`
  - Mayday: `51`
- **Miner ID**: `createker02140054RTC`

## Execution Logs

```text
🚀 Initializing RayBot Beacon Integration: bcn_raybot_f5e03eb4
💓 Sending proof-of-life heartbeat...
✅ Envelope (heartbeat) accepted! ID: 50
🆘 Triggering MAYDAY: Simulated Resource Depletion
✅ Envelope (mayday) accepted! ID: 51

✨ Beacon Integration Demo Complete.
```

## Source Code

The integration logic is contained in `raybot_beacon_agent.py`, which uses structured envelopes and non-repudiation nonces to interact with the Beacon relay.
