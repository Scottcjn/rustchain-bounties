# BCOS v2 GitHub Action

A reusable GitHub Action for integrating BCOS v2 into any repository.

## Features

- 🔐 Secure API key management
- ⚡ Fast setup with automatic CLI installation
- 📊 Detailed execution results and metrics
- ⏱️ Configurable timeout
- 📝 GitHub Step Summary support

## Usage

### Basic Example

```yaml
name: BCOS Integration
on: [push, pull_request]

jobs:
  bcos-verify:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Run BCOS v2
        uses: Scottcjn/rustchain-bounties/bcos-action@v1
        with:
          api-key: ${{ secrets.BCOS_API_KEY }}
          endpoint: 'https://api.bcos.dev/v2'
          command: 'verify'
```

### Advanced Example

```yaml
name: BCOS Deployment
on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Deploy to BCOS
        id: bcos
        uses: Scottcjn/rustchain-bounties/bcos-action@v1
        with:
          api-key: ${{ secrets.BCOS_API_KEY }}
          endpoint: ${{ vars.BCOS_ENDPOINT }}
          command: 'deploy'
          config-path: './bcos-config.json'
          timeout: '600'
      
      - name: Use Results
        run: |
          echo "Status: ${{ steps.bcos.outputs.status }}"
          echo "Duration: ${{ steps.bcos.outputs.duration }}ms"
          echo "Result: ${{ steps.bcos.outputs.result }}"
```

## Inputs

| Input | Description | Required | Default |
|-------|-------------|----------|---------|
| `api-key` | BCOS API key for authentication | Yes | - |
| `endpoint` | BCOS endpoint URL | No | `https://api.bcos.dev/v2` |
| `command` | Command to execute (deploy, verify, test) | No | `verify` |
| `config-path` | Path to BCOS configuration file | No | `./bcos.json` |
| `timeout` | Request timeout in seconds | No | `300` |

## Outputs

| Output | Description |
|--------|-------------|
| `result` | Command execution result (JSON) |
| `status` | Execution status (success/failure) |
| `timestamp` | Execution timestamp (ISO 8601) |
| `duration` | Execution duration in milliseconds |

## Setup

1. Get your BCOS API key from [BCOS Dashboard](https://dashboard.bcos.dev)
2. Add it to your repository secrets as `BCOS_API_KEY`
3. Create a `bcos.json` config file (optional)

### Example bcos.json

```json
{
  "project": "my-project",
  "environment": "production",
  "settings": {
    "auto_verify": true,
    "notify_on_complete": true
  }
}
```

## Supported Commands

- `verify` - Verify project configuration and credentials
- `deploy` - Deploy project to BCOS
- `test` - Run BCOS tests
- `status` - Check BCOS service status

## Error Handling

The action will:
- Exit with code 1 on failure
- Provide detailed error messages in GitHub Step Summary
- Include full error output for debugging

## License

MIT License - See [LICENSE](../../LICENSE) for details.

## Contributing

Contributions welcome! Please read our [Contributing Guide](../../CONTRIBUTING.md).

## Support

- 📖 [Documentation](https://docs.bcos.dev)
- 💬 [Discord](https://discord.gg/bcos)
- 🐛 [Issue Tracker](https://github.com/Scottcjn/rustchain-bounties/issues)

---

Built with ❤️ by the RustChain community
