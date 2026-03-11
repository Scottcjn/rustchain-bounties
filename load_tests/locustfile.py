# SPDX-License-Identifier: MIT
"""
RustChain API – Locust load-test suite.

Simulates realistic miner traffic against the RIP-200 endpoints:
  • health/epoch read traffic
  • full attestation lifecycle (challenge → submit → enroll)
  • wallet + lottery queries

Usage:
    # Web UI (graphs at http://localhost:8089):
    locust -f load_tests/locustfile.py --host https://50.28.86.131

    # Headless run with CSV output:
    locust -f load_tests/locustfile.py --host https://50.28.86.131 \
        --headless -u 50 -r 5 -t 120s \
        --csv load_tests/results/locust_report

    # Then generate standalone HTML graphs:
    python load_tests/graph_reporter.py load_tests/results/locust_report
"""

from locust import HttpUser, between, task, tag, events

from load_tests.miner_helpers import (
    make_miner,
    attestation_payload,
    enroll_payload,
)


# ---------------------------------------------------------------------------
# Locust user classes
# ---------------------------------------------------------------------------


class ReadOnlyUser(HttpUser):
    """Simulates lightweight read-only traffic (health, epoch, miners)."""

    weight = 3
    wait_time = between(1, 3)

    @tag("read", "health")
    @task(5)
    def get_health(self):
        self.client.get("/health", verify=False, name="/health")

    @tag("read", "epoch")
    @task(3)
    def get_epoch(self):
        self.client.get("/epoch", verify=False, name="/epoch")

    @tag("read", "miners")
    @task(2)
    def get_miners(self):
        self.client.get("/api/miners", verify=False, name="/api/miners")


class WalletQueryUser(HttpUser):
    """Simulates wallet balance and lottery eligibility queries."""

    weight = 2
    wait_time = between(2, 5)

    def on_start(self):
        self.miner = make_miner(prefix="locust")

    @tag("read", "wallet")
    @task(3)
    def get_balance(self):
        self.client.get(
            f"/wallet/balance?miner_id={self.miner['miner_id']}",
            verify=False,
            name="/wallet/balance",
        )

    @tag("read", "lottery")
    @task(1)
    def get_lottery(self):
        self.client.get(
            f"/lottery/eligibility?miner_id={self.miner['miner_id']}",
            verify=False,
            name="/lottery/eligibility",
        )


class AttestationUser(HttpUser):
    """Simulates full RIP-200 attestation lifecycle.

    Each iteration: challenge → submit → enroll  (three sequential requests).
    """

    weight = 5
    wait_time = between(3, 8)

    def on_start(self):
        self.miner = make_miner(prefix="locust")

    @tag("write", "attestation")
    @task
    def full_attestation_cycle(self):
        # Step 1: challenge
        with self.client.post(
            "/attest/challenge",
            json={},
            verify=False,
            name="/attest/challenge",
            catch_response=True,
        ) as resp:
            if resp.status_code == 429:
                resp.failure("Rate limited (429)")
                return
            if resp.status_code != 200:
                resp.failure(f"HTTP {resp.status_code}")
                return
            try:
                nonce = resp.json().get("nonce")
            except Exception:
                resp.failure("Invalid JSON response")
                return
            if not nonce:
                resp.failure("No nonce in response")
                return

        # Step 2: submit
        payload = attestation_payload(self.miner, nonce)
        with self.client.post(
            "/attest/submit",
            json=payload,
            verify=False,
            name="/attest/submit",
            catch_response=True,
        ) as resp:
            if resp.status_code == 429:
                resp.failure("Rate limited (429)")
                return
            if resp.status_code not in (200, 400, 403):
                resp.failure(f"HTTP {resp.status_code}")
                return

        # Step 3: enroll
        enroll = enroll_payload(self.miner)
        with self.client.post(
            "/epoch/enroll",
            json=enroll,
            verify=False,
            name="/epoch/enroll",
            catch_response=True,
        ) as resp:
            if resp.status_code == 429:
                resp.failure("Rate limited (429)")
                return
            if resp.status_code not in (200, 400, 403):
                resp.failure(f"HTTP {resp.status_code}")
                return
