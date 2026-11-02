import asyncio
import hashlib
import json
import unittest

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey

from rustchain_agent_economy import (
    AgentEconomyClient,
    AgentEconomyValidationError,
    AsyncAgentEconomyClient,
    Ed25519Signer,
    canonical_create_message,
)


class RecordingTransport:
    def __init__(self, response=None):
        self.calls = []
        self.response = response or {"ok": True}

    def request(self, method, path, *, query=None, json_body=None, headers=None):
        self.calls.append((method, path, query, json_body, headers))
        return self.response


class AgentEconomyClientTests(unittest.TestCase):
    def setUp(self):
        self.transport = RecordingTransport()
        self.client = AgentEconomyClient(transport=self.transport)

    def last(self):
        return self.transport.calls[-1]

    def test_list_jobs_encodes_filters(self):
        self.client.list_jobs(status="completed", category="code", min_reward=2.5, limit=10, offset=3)
        method, path, query, _, _ = self.last()
        self.assertEqual((method, path), ("GET", "/agent/jobs"))
        self.assertEqual(query, {"status": "completed", "category": "code", "min_reward": 2.5, "limit": 10, "offset": 3})

    def test_get_job_escapes_id(self):
        self.client.get_job("job/a b")
        self.assertEqual(self.last()[1], "/agent/jobs/job%2Fa%20b")

    def test_signed_post_matches_rip302_canonical_message(self):
        signer = Ed25519Signer.from_private_key_hex("00" * 31 + "01")
        poster = signer.rtc_address
        self.client.post_job(
            poster_wallet=poster,
            title="Build SDK",
            description="Implement the current RIP-302 protocol.",
            reward_rtc=5,
            category="CODE",
            nonce="nonce-1",
            signer=signer,
        )
        _, _, _, body, headers = self.last()
        self.assertEqual(body["reward_rtc"], 5.0)
        self.assertEqual(body["category"], "code")
        self.assertEqual(body["nonce"], "nonce-1")
        self.assertEqual(headers, {})
        msg = canonical_create_message(poster, "code", 5, "nonce-1")
        Ed25519PublicKey.from_public_bytes(bytes.fromhex(body["poster_pubkey"])).verify(
            bytes.fromhex(body["poster_sig"]), msg
        )
        self.assertEqual(msg, json.dumps({
            "action": "agent_post_job",
            "category": "code",
            "nonce": "nonce-1",
            "poster": poster,
            "reward_rtc": 5.0,
        }, sort_keys=True, separators=(",", ":")).encode())

    def test_rtc_address_is_hash_of_public_key(self):
        signer = Ed25519Signer.from_private_key_hex("11" * 32)
        expected = "RTC" + hashlib.sha256(bytes.fromhex(signer.public_key_hex)).hexdigest()[:40]
        self.assertEqual(signer.rtc_address, expected)

    def test_rejects_wrong_signer_for_rtc_wallet(self):
        signer = Ed25519Signer.from_private_key_hex("22" * 32)
        with self.assertRaises(AgentEconomyValidationError):
            self.client.post_job(
                poster_wallet="RTC" + "0" * 40,
                title="Build SDK",
                description="Implement the current RIP-302 protocol.",
                reward_rtc=5,
                signer=signer,
            )

    def test_named_wallet_admin_header(self):
        self.client.post_job(
            poster_wallet="founder_community",
            title="Admin job",
            description="An operator-authorized named-wallet job.",
            reward_rtc=2,
            admin_key="secret",
        )
        self.assertEqual(self.last()[4], {"X-Admin-Key": "secret"})

    def test_claim_job(self):
        self.client.claim_job("job_1", "RTCworker")
        self.assertEqual(self.last()[3], {"worker_wallet": "RTCworker"})

    def test_deliver_job(self):
        self.client.deliver_job("job_1", worker_wallet="RTCworker", deliverable_url="https://example.test/x", result_summary="done")
        self.assertEqual(self.last()[1], "/agent/jobs/job_1/deliver")
        self.assertEqual(self.last()[3]["result_summary"], "done")

    def test_deliver_requires_output(self):
        with self.assertRaises(AgentEconomyValidationError):
            self.client.deliver_job("job_1", worker_wallet="RTCworker")

    def test_accept_passes_settlement_signature(self):
        self.client.accept_job("job_1", poster_wallet="RTCposter", settlement_sig="abcd", rating=5)
        self.assertEqual(self.last()[3], {"poster_wallet": "RTCposter", "settlement_sig": "abcd", "rating": 5})

    def test_dispute_passes_reason_and_settlement_signature(self):
        self.client.dispute_job("job_1", poster_wallet="RTCposter", reason="incomplete", settlement_sig="abcd")
        self.assertEqual(self.last()[3]["reason"], "incomplete")
        self.assertEqual(self.last()[3]["settlement_sig"], "abcd")

    def test_cancel_passes_settlement_signature(self):
        self.client.cancel_job("job_1", poster_wallet="RTCposter", settlement_sig="abcd")
        self.assertEqual(self.last()[1], "/agent/jobs/job_1/cancel")

    def test_reputation_escapes_wallet(self):
        self.client.get_reputation("wallet/a b")
        self.assertEqual(self.last()[1], "/agent/reputation/wallet%2Fa%20b")

    def test_stats_endpoint(self):
        self.client.get_stats()
        self.assertEqual(self.last()[:2], ("GET", "/agent/stats"))

    def test_validates_reward_category_and_rating(self):
        with self.assertRaises(AgentEconomyValidationError):
            self.client.post_job(poster_wallet="x", title="valid title", description="x" * 20, reward_rtc=float("nan"))
        with self.assertRaises(AgentEconomyValidationError):
            self.client.list_jobs(category="bogus")
        with self.assertRaises(AgentEconomyValidationError):
            self.client.accept_job("j", poster_wallet="p", settlement_sig="s", rating=6)

    def test_async_facade_uses_same_protocol(self):
        async_client = AsyncAgentEconomyClient(transport=self.transport)
        result = asyncio.run(async_client.get_stats())
        self.assertEqual(result, {"ok": True})
        self.assertEqual(self.last()[:2], ("GET", "/agent/stats"))


if __name__ == "__main__":
    unittest.main()
