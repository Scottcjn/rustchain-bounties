import os
import shutil
import subprocess
import time

import pytest
import requests


CLI = shutil.which("clawrtc")
HEALTH_URL = os.getenv("CLAWRTC_HEALTH_URL", "https://50.28.86.131/health")


@pytest.mark.integration
@pytest.mark.skipif(CLI is None, reason="clawrtc CLI not installed")
def test_clawrtc_help():
    out = subprocess.run([CLI, "--help"], capture_output=True, text=True, timeout=30)
    assert out.returncode == 0
    assert out.stdout or out.stderr


@pytest.mark.integration
@pytest.mark.skipif(CLI is None, reason="clawrtc CLI not installed")
def test_wallet_show_and_status():
    wallet = subprocess.run([CLI, "wallet", "show"], capture_output=True, text=True, timeout=30)
    status = subprocess.run([CLI, "status"], capture_output=True, text=True, timeout=30)

    assert wallet.returncode == 0
    assert status.returncode == 0
    assert "wallet" in (wallet.stdout + wallet.stderr).lower() or wallet.stdout.strip()


@pytest.mark.integration
@pytest.mark.skipif(CLI is None, reason="clawrtc CLI not installed")
def test_service_lifecycle_and_logs():
    start = subprocess.run([CLI, "start", "--service"], capture_output=True, text=True, timeout=60)
    assert start.returncode == 0

    time.sleep(3)

    status = subprocess.run([CLI, "status"], capture_output=True, text=True, timeout=30)
    logs = subprocess.run([CLI, "logs"], capture_output=True, text=True, timeout=30)
    stop = subprocess.run([CLI, "stop"], capture_output=True, text=True, timeout=60)

    assert status.returncode == 0
    assert logs.returncode == 0
    assert stop.returncode == 0


@pytest.mark.integration
def test_health_endpoint_alive():
    r = requests.get(HEALTH_URL, timeout=10, verify=False)
    assert r.status_code == 200
    payload = r.json()
    assert payload.get("ok") is True
