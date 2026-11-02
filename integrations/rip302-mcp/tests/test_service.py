import unittest

from rustchain_agent_economy_mcp.service import (
    AgentEconomyMcpService,
    McpConfigurationError,
    RuntimeConfig,
)


class FakeSigner:
    rtc_address = "RTC" + "a" * 40


class FakeClient:
    def __init__(self):
        self.calls = []

    def _call(self, name, *args, **kwargs):
        self.calls.append((name, args, kwargs))
        return {"ok": True, "method": name}

    def list_jobs(self, **kwargs): return self._call("list_jobs", **kwargs)
    def get_job(self, *args, **kwargs): return self._call("get_job", *args, **kwargs)
    def post_job(self, **kwargs): return self._call("post_job", **kwargs)
    def claim_job(self, *args, **kwargs): return self._call("claim_job", *args, **kwargs)
    def deliver_job(self, *args, **kwargs): return self._call("deliver_job", *args, **kwargs)
    def get_reputation(self, *args, **kwargs): return self._call("get_reputation", *args, **kwargs)
    def get_stats(self): return self._call("get_stats")


class ServiceTests(unittest.TestCase):
    def setUp(self):
        self.client = FakeClient()
        self.config = RuntimeConfig(base_url="https://node.example", worker_wallet="RTCworker")

    def test_runtime_config_reads_environment_without_echoing_key(self):
        cfg = RuntimeConfig.from_env({
            "RUSTCHAIN_NODE_URL": "https://node.example/",
            "RUSTCHAIN_VERIFY_TLS": "false",
            "RUSTCHAIN_CA_FILE": "/tmp/ca.pem",
            "RUSTCHAIN_POSTER_PRIVATE_KEY": "11" * 32,
            "RUSTCHAIN_WORKER_WALLET": "RTCworker",
        })
        self.assertEqual(cfg.base_url, "https://node.example")
        self.assertFalse(cfg.verify_tls)
        self.assertEqual(cfg.ca_file, "/tmp/ca.pem")
        self.assertEqual(cfg.worker_wallet, "RTCworker")
        self.assertEqual(cfg.poster_private_key_hex, "11" * 32)

    def test_runtime_config_rejects_ambiguous_tls_flag(self):
        with self.assertRaises(McpConfigurationError):
            RuntimeConfig.from_env({"RUSTCHAIN_VERIFY_TLS": "maybe"})

    def test_status_is_non_secret(self):
        svc = AgentEconomyMcpService(config=self.config, client=self.client, signer=FakeSigner())
        status = svc.status()
        self.assertEqual(status["poster_wallet"], FakeSigner.rtc_address)
        self.assertTrue(status["signed_posting_enabled"])
        self.assertNotIn("private", " ".join(status.keys()).lower())

    def test_post_job_uses_configured_signer_and_derived_wallet(self):
        signer = FakeSigner()
        svc = AgentEconomyMcpService(config=self.config, client=self.client, signer=signer)
        svc.post_job(
            title="Research task",
            description="Produce a concise source-backed technical report.",
            reward_rtc=5,
            category="research",
            tags=["mcp"],
        )
        name, _, kwargs = self.client.calls[-1]
        self.assertEqual(name, "post_job")
        self.assertEqual(kwargs["poster_wallet"], signer.rtc_address)
        self.assertIs(kwargs["signer"], signer)
        self.assertNotIn("private_key", kwargs)

    def test_post_job_refuses_model_supplied_secret_fallback(self):
        svc = AgentEconomyMcpService(config=self.config, client=self.client, signer=None)
        with self.assertRaises(McpConfigurationError):
            svc.post_job(
                title="Research task",
                description="Produce a concise source-backed technical report.",
                reward_rtc=5,
            )

    def test_worker_defaults_from_process_config(self):
        svc = AgentEconomyMcpService(config=self.config, client=self.client, signer=None)
        svc.claim_job("job_1")
        self.assertEqual(self.client.calls[-1], ("claim_job", ("job_1", "RTCworker"), {}))

    def test_explicit_worker_overrides_default(self):
        svc = AgentEconomyMcpService(config=self.config, client=self.client, signer=None)
        svc.claim_job("job_1", worker_wallet="RTCother")
        self.assertEqual(self.client.calls[-1], ("claim_job", ("job_1", "RTCother"), {}))

    def test_missing_worker_is_rejected(self):
        cfg = RuntimeConfig(base_url="https://node.example")
        svc = AgentEconomyMcpService(config=cfg, client=self.client, signer=None)
        with self.assertRaises(McpConfigurationError):
            svc.claim_job("job_1")

    def test_deliver_forwards_only_public_job_fields(self):
        svc = AgentEconomyMcpService(config=self.config, client=self.client, signer=None)
        svc.deliver_job(
            "job_1",
            deliverable_url="https://example.test/pr/1",
            result_summary="Implemented and tested.",
        )
        name, args, kwargs = self.client.calls[-1]
        self.assertEqual(name, "deliver_job")
        self.assertEqual(args, ("job_1",))
        self.assertEqual(kwargs["worker_wallet"], "RTCworker")
        self.assertEqual(kwargs["result_summary"], "Implemented and tested.")

    def test_read_routes_delegate(self):
        svc = AgentEconomyMcpService(config=self.config, client=self.client, signer=None)
        svc.list_jobs(category="code", limit=7)
        svc.get_job("job_1")
        svc.get_reputation("RTCworker")
        svc.get_stats()
        self.assertEqual([c[0] for c in self.client.calls], [
            "list_jobs", "get_job", "get_reputation", "get_stats"
        ])


if __name__ == "__main__":
    unittest.main()
