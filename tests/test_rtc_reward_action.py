import os
import shutil
import subprocess
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
