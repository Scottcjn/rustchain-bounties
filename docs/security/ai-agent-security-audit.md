# AI Agent Security Audit (Automated Testing)

Static analyzer for Python-based AI-agent repositories.

## Checks
- dynamic code execution (`eval`, `exec`)
- subprocess with `shell=True`
- unsafe pickle deserialization
- HTTP requests missing explicit timeout
- hardcoded secret-like assignments

## Usage
```bash
python3 scripts/ai_agent_security_audit.py --target .
python3 scripts/ai_agent_security_audit.py --target . --output audit.json
```

## CI behavior
- exits with code `2` if any `high` severity findings are present
- exits `0` otherwise
