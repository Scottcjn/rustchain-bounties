# RustChain MCP Read Integration

This is a small MCP server for agents that need live RustChain network reads without touching consensus or wallet state.

## What it does

- Reads node health from `/health`
- Reads current epoch data from `/epoch`
- Reads miner list data from `/api/miners`

## Run

```bash
pip install -r requirements.txt
python mcp_server.py
```

Optional environment variable:

```bash
RUSTCHAIN_BASE_URL=http://rustchain.org:8088
```

## Live transcript

```text
$ curl http://rustchain.org:8088/health
{"backup_age_hours":13.890982509851456,"db_rw":true,"ok":true,"tip_age_slots":0,"uptime_s":178659,"version":"2.2.1-rip200"}

$ curl http://rustchain.org:8088/epoch
{"blocks_per_epoch":144,"enrolled_miners":23,"epoch":183,"epoch_pot":1.5,"slot":26477,"total_supply_rtc":8388608}

$ curl http://50.28.86.153:8088/api/miners
{"miners":[],"pagination":{"count":0,"limit":100,"offset":0,"total":0,"total_enrolled":0}}
```

## Notes

- This is a T1 read-only integration for bounty `#13040`.
- The server returns live HTTP responses from RustChain instead of simulated payloads.
