#!/usr/bin/env python3
"""Run a local Beacon webhook smoke test using the official CLI."""

from __future__ import annotations

import shutil
import subprocess
import sys
import time


PORT = "8402"
INBOX_URL = f"http://127.0.0.1:{PORT}/beacon/inbox"


def run(command: list[str], check: bool = True) -> subprocess.CompletedProcess[str]:
    print("$ " + " ".join(command))
    result = subprocess.run(
        command,
        check=False,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    if result.stdout.strip():
        print(result.stdout.strip())
    if check and result.returncode != 0:
        raise SystemExit(result.returncode)
    return result


def ensure_beacon_cli() -> None:
    if shutil.which("beacon") is None:
        raise SystemExit(
            "beacon CLI not found. Install it with: pip install beacon-skill"
        )


def ensure_identity() -> None:
    shown = run(["beacon", "identity", "show"], check=False)
    if shown.returncode == 0:
        return
    run(["beacon", "identity", "new"])
    run(["beacon", "identity", "show"])


def main() -> int:
    ensure_beacon_cli()
    ensure_identity()

    server = subprocess.Popen(
        ["beacon", "webhook", "serve", "--port", PORT],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )
    try:
        time.sleep(2)
        if server.poll() is not None:
            output = server.stdout.read() if server.stdout else ""
            print(output.strip())
            raise SystemExit("Webhook server exited before the smoke test ran.")

        run(
            [
                "beacon",
                "webhook",
                "send",
                INBOX_URL,
                "--kind",
                "hello",
            ]
        )
        run(["beacon", "inbox", "list", "--limit", "1"])
        return 0
    finally:
        server.terminate()
        try:
            server.wait(timeout=5)
        except subprocess.TimeoutExpired:
            server.kill()
            server.wait(timeout=5)


if __name__ == "__main__":
    sys.exit(main())
