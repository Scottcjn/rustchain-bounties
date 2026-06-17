import os
import shutil
import subprocess
import json
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
ACTION_ENTRYPOINT = ROOT / "actions" / "rtc-reward" / "dist" / "index.js"


@pytest.mark.skipif(shutil.which("node") is None, reason="Node.js is required")
def test_action_reads_github_hyphenated_input_environment(tmp_path):
    event_path = tmp_path / "event.json"
    event_path.write_text("{}", encoding="utf-8")

    env = os.environ.copy()
    env.update(
        {
            "INPUT_NODE-URL": "https://example.invalid",
            "INPUT_AMOUNT": "5",
            "INPUT_WALLET-FROM": "founder_community",
            "INPUT_ADMIN-KEY": "test-only-key",
            "GITHUB_TOKEN": "test-token",
            "GITHUB_EVENT_PATH": str(event_path),
            "GITHUB_REPOSITORY": "owner/repo",
        }
    )

    result = subprocess.run(
        [shutil.which("node"), str(ACTION_ENTRYPOINT)],
        check=False,
        capture_output=True,
        text=True,
        env=env,
    )

    assert result.returncode == 0, result.stderr
    assert "No merged PR found for this event. Skipping." in result.stdout


@pytest.mark.skipif(shutil.which("node") is None, reason="Node.js is required")
def test_action_sends_safe_transfer_idempotency_key(tmp_path):
    event_path = tmp_path / "event.json"
    event_path.write_text(json.dumps({"pull_request": {"number": 7484}}), encoding="utf-8")
    output_path = tmp_path / "github-output.txt"

    runner = tmp_path / "run-action.js"
    runner.write_text(
        f"""
const calls = [];
global.fetch = async (url, options = {{}}) => {{
  calls.push({{url, options}});
  if (url.includes('/pulls/7484')) {{
    return {{
      ok: true,
      headers: {{get: () => 'application/json'}},
      json: async () => ({{
        merged: true,
        body: '',
        head: {{sha: 'abc123'}},
        html_url: 'https://github.com/Scottcjn/Rustchain/pull/7484',
        user: {{login: 'z272258483', type: 'User'}},
      }}),
    }};
  }}
  if (url.includes('/contents/')) {{
    return {{
      ok: false,
      headers: {{get: () => 'application/json'}},
      json: async () => ({{message: 'Not Found'}}),
    }};
  }}
  if (url.includes('/wallet/transfer')) {{
    const payload = JSON.parse(options.body);
    if (!/^[0-9a-f]{{24}}$/.test(payload.idempotency_key)) {{
      throw new Error(`bad idempotency key: ${{payload.idempotency_key}}`);
    }}
    if (payload.memo !== 'https://github.com/Scottcjn/Rustchain/pull/7484') {{
      throw new Error(`memo changed: ${{payload.memo}}`);
    }}
    return {{
      ok: true,
      headers: {{get: () => 'application/json'}},
      json: async () => ({{ok: true, pending_id: 'p1'}}),
    }};
  }}
  if (url.includes('/issues/7484/comments')) {{
    return {{
      ok: true,
      headers: {{get: () => 'application/json'}},
      json: async () => ({{id: 1}}),
    }};
  }}
  throw new Error(`unexpected fetch URL: ${{url}}`);
}};

require({json.dumps(str(ACTION_ENTRYPOINT))});
""",
        encoding="utf-8",
    )

    env = os.environ.copy()
    env.update(
        {
            "INPUT_NODE-URL": "https://rustchain.example",
            "INPUT_AMOUNT": "5",
            "INPUT_WALLET-FROM": "founder_community",
            "INPUT_ADMIN-KEY": "test-only-key",
            "GITHUB_TOKEN": "test-token",
            "GITHUB_EVENT_PATH": str(event_path),
            "GITHUB_OUTPUT": str(output_path),
            "GITHUB_REPOSITORY": "Scottcjn/Rustchain",
        }
    )

    result = subprocess.run(
        [shutil.which("node"), str(runner)],
        check=False,
        capture_output=True,
        text=True,
        env=env,
    )

    assert result.returncode == 0, result.stderr
    assert "Transfer result" in result.stdout
