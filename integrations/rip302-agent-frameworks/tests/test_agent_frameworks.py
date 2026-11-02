"""Offline contract tests using the SDK and real optional framework runtimes."""

from __future__ import annotations

import builtins
import importlib.util
import json
import os
import unittest
from unittest.mock import patch

# These tests construct tools, not agents, and never use a model or live node.
os.environ["OTEL_SDK_DISABLED"] = "true"
os.environ["CREWAI_TELEMETRY_ENABLED"] = "false"

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey

from rustchain_agent_economy import (
    DEFAULT_BASE_URL,
    AgentEconomyApiError,
    AgentEconomyClient,
    AgentEconomyValidationError,
    Ed25519Signer,
)
from rustchain_agent_frameworks import (
    AgentEconomyToolkit,
    ToolkitConfig,
    ToolkitConfigurationError,
    build_crewai_tools,
    build_langchain_tools,
)


PRIVATE_KEY = "17" * 32  # Deterministic test fixture, never a funded identity.
TOOL_FIELDS = {
    "rustchain_agent_status": set(),
    "rustchain_list_jobs": {"status", "category", "min_reward", "limit", "offset"},
    "rustchain_get_job": {"job_id"},
    "rustchain_post_job": {
        "title", "description", "reward_rtc", "category", "ttl_seconds", "tags"
    },
    "rustchain_claim_job": {"job_id", "worker_wallet"},
    "rustchain_deliver_job": {
        "job_id", "worker_wallet", "deliverable_url", "deliverable_hash", "result_summary"
    },
    "rustchain_get_reputation": {"wallet_id"},
    "rustchain_marketplace_stats": set(),
}


class RecordingTransport:
    """Capture complete SDK requests without constructing an HTTP connection."""

    def __init__(self):
        self.calls = []
        self.error = None

    def request(self, method, path, **kwargs):
        self.calls.append((method, path, kwargs))
        if self.error is not None:
            raise self.error
        return {"ok": True, "request_number": len(self.calls)}


def make_toolkit(*, worker="default-worker", signed=True):
    transport = RecordingTransport()
    config = ToolkitConfig(
        worker_wallet=worker,
        poster_private_key_hex=PRIVATE_KEY if signed else None,
    )
    toolkit = AgentEconomyToolkit(
        config=config,
        client=AgentEconomyClient(transport=transport),
    )
    return toolkit, transport


def assert_create_signature(test, body, signer):
    """Independently render the server's message; do not reuse SDK helpers."""
    expected = {
        "action": "agent_post_job",
        "category": body["category"],
        "nonce": body["nonce"],
        "poster": signer.rtc_address,
        "reward_rtc": float(body["reward_rtc"]),
    }
    message = json.dumps(expected, sort_keys=True, separators=(",", ":")).encode()
    Ed25519PublicKey.from_public_bytes(bytes.fromhex(body["poster_pubkey"])).verify(
        bytes.fromhex(body["poster_sig"]), message
    )
    test.assertIn(b'"reward_rtc":5.0', message)
    test.assertEqual(body["poster_wallet"], signer.rtc_address)
    test.assertNotIn(PRIVATE_KEY, json.dumps(body))


class ToolkitTests(unittest.TestCase):
    def test_empty_environment_defaults_to_verified_tls_node(self):
        config = ToolkitConfig.from_env({})
        self.assertEqual(config.base_url, DEFAULT_BASE_URL)
        self.assertTrue(config.verify_tls)
        self.assertIsNone(config.ca_file)
        self.assertIsNone(config.worker_wallet)
        self.assertIsNone(config.poster_private_key_hex)

    def test_environment_normalization_and_blank_optional_values(self):
        config = ToolkitConfig.from_env({
            "RUSTCHAIN_NODE_URL": " https://node.example/// ",
            "RUSTCHAIN_VERIFY_TLS": " OFF ",
            "RUSTCHAIN_CA_FILE": " /tmp/test-ca.pem ",
            "RUSTCHAIN_POSTER_PRIVATE_KEY": " " + PRIVATE_KEY + " ",
            "RUSTCHAIN_WORKER_WALLET": " worker-A ",
        })
        self.assertEqual(config.base_url, "https://node.example")
        self.assertFalse(config.verify_tls)
        self.assertEqual(config.ca_file, "/tmp/test-ca.pem")
        self.assertEqual(config.poster_private_key_hex, PRIVATE_KEY)
        self.assertEqual(config.worker_wallet, "worker-A")
        blank = ToolkitConfig.from_env({
            "RUSTCHAIN_CA_FILE": " ", "RUSTCHAIN_POSTER_PRIVATE_KEY": " ",
            "RUSTCHAIN_WORKER_WALLET": " ",
        })
        self.assertIsNone(blank.ca_file)
        self.assertIsNone(blank.poster_private_key_hex)
        self.assertIsNone(blank.worker_wallet)

    def test_tls_values_are_explicit_and_invalid_configuration_fails(self):
        for value in ("1", "true", "yes", "on", " TRUE "):
            with self.subTest(value=value):
                self.assertTrue(ToolkitConfig.from_env({"RUSTCHAIN_VERIFY_TLS": value}).verify_tls)
        for value in ("0", "false", "no", "off", " FALSE "):
            with self.subTest(value=value):
                self.assertFalse(ToolkitConfig.from_env({"RUSTCHAIN_VERIFY_TLS": value}).verify_tls)
        for env in ({"RUSTCHAIN_VERIFY_TLS": "maybe"}, {"RUSTCHAIN_NODE_URL": " "}):
            with self.subTest(env=env), self.assertRaises(ToolkitConfigurationError):
                ToolkitConfig.from_env(env)

    def test_private_key_is_absent_from_configuration_repr_and_status(self):
        toolkit, _ = make_toolkit()
        self.assertNotIn(PRIVATE_KEY, repr(toolkit.config))
        self.assertNotIn("poster_private_key_hex", repr(toolkit.config))
        status = toolkit.status()
        self.assertTrue(status["signed_posting_enabled"])
        self.assertEqual(status["poster_wallet"], toolkit.signer.rtc_address)
        self.assertEqual(status["default_worker_wallet"], "default-worker")
        self.assertNotIn(PRIVATE_KEY, json.dumps(status))

    def test_client_receives_tls_configuration(self):
        config = ToolkitConfig(base_url="https://node.example", verify_tls=True, ca_file="test-ca.pem")
        with patch("rustchain_agent_frameworks.core.AgentEconomyClient") as client:
            toolkit = AgentEconomyToolkit(config=config)
        client.assert_called_once_with("https://node.example", verify_tls=True, ca_file="test-ca.pem")
        self.assertIs(toolkit.client, client.return_value)

    def test_explicit_signer_overrides_environment_key(self):
        signer = Ed25519Signer.from_private_key_hex(PRIVATE_KEY)
        toolkit = AgentEconomyToolkit(
            config=ToolkitConfig(poster_private_key_hex="invalid-key"),
            client=AgentEconomyClient(transport=RecordingTransport()), signer=signer,
        )
        self.assertIs(toolkit.signer, signer)

    def test_unsigned_post_is_blocked_before_transport(self):
        toolkit, transport = make_toolkit(signed=False)
        with self.assertRaisesRegex(ToolkitConfigurationError, "Signed posting is disabled"):
            toolkit.post_job("A test job", "A sufficiently detailed test description.", 5)
        self.assertEqual(transport.calls, [])
        self.assertFalse(toolkit.status()["signed_posting_enabled"])

    def test_signed_posts_use_canonical_message_and_fresh_nonces(self):
        toolkit, transport = make_toolkit()
        for _ in range(2):
            toolkit.post_job("A test job", "A sufficiently detailed test description.", 5, "code")
            method, path, kwargs = transport.calls[-1]
            self.assertEqual((method, path), ("POST", "/agent/jobs"))
            self.assertEqual(kwargs["headers"], {})
            assert_create_signature(self, kwargs["json_body"], toolkit.signer)
        self.assertNotEqual(transport.calls[0][2]["json_body"]["nonce"], transport.calls[1][2]["json_body"]["nonce"])

    def test_worker_defaults_and_explicit_wallet_apply_to_claim_and_delivery(self):
        toolkit, transport = make_toolkit()
        toolkit.claim_job("job_1")
        self.assertEqual(transport.calls[-1][2]["json_body"], {"worker_wallet": "default-worker"})
        toolkit.claim_job("job_1", " explicit-worker ")
        self.assertEqual(transport.calls[-1][2]["json_body"], {"worker_wallet": "explicit-worker"})
        toolkit.deliver_job("job_1", result_summary="Done")
        self.assertEqual(transport.calls[-1][2]["json_body"], {"worker_wallet": "default-worker", "result_summary": "Done"})
        toolkit.deliver_job("job_1", "explicit-worker", "https://example.test/result", "abc", "Done")
        self.assertEqual(transport.calls[-1][2]["json_body"], {
            "worker_wallet": "explicit-worker", "deliverable_url": "https://example.test/result",
            "deliverable_hash": "abc", "result_summary": "Done",
        })

    def test_explicit_invalid_worker_never_falls_back_to_default(self):
        toolkit, transport = make_toolkit()
        for worker in ("", " ", 0, [], False):
            for operation in (toolkit.claim_job, toolkit.deliver_job):
                with self.subTest(worker=worker, operation=operation.__name__), self.assertRaises(ToolkitConfigurationError):
                    operation("job_1", worker)
        self.assertEqual(transport.calls, [])

    def test_missing_default_worker_blocks_mutation(self):
        toolkit, transport = make_toolkit(worker=None)
        with self.assertRaises(ToolkitConfigurationError):
            toolkit.claim_job("job_1")
        with self.assertRaises(ToolkitConfigurationError):
            toolkit.deliver_job("job_1", result_summary="Done")
        self.assertEqual(transport.calls, [])

    def test_sdk_validation_reaches_caller_before_transport(self):
        toolkit, transport = make_toolkit()
        with self.assertRaises(AgentEconomyValidationError):
            toolkit.list_jobs(limit=-1)
        with self.assertRaises(AgentEconomyValidationError):
            toolkit.deliver_job("job_1", deliverable_hash="hash-only-is-insufficient")
        with self.assertRaises(AgentEconomyValidationError):
            toolkit.post_job("short", "Too short", 5)
        self.assertEqual(transport.calls, [])

    def test_optional_framework_installation_errors_are_actionable(self):
        toolkit, _ = make_toolkit()
        original_import = builtins.__import__
        for builder, blocked, extra in (
            (build_langchain_tools, ("langchain_core",), "langchain"),
            (build_crewai_tools, ("crewai",), "crewai"),
        ):
            def without_framework(name, *args, **kwargs):
                if any(name == prefix or name.startswith(prefix + ".") for prefix in blocked):
                    raise ImportError("Framework unavailable for this test")
                return original_import(name, *args, **kwargs)
            with self.subTest(extra=extra), patch("builtins.__import__", side_effect=without_framework):
                with self.assertRaisesRegex(ImportError, r"rustchain-agent-frameworks\[" + extra + r"\]"):
                    builder(toolkit)


class RealFrameworkContracts(unittest.TestCase):
    """Exercise actual schemas and invocation paths, with no LLM or HTTP calls."""

    def builders(self):
        available = []
        for module, builder in (("langchain_core", build_langchain_tools), ("crewai", build_crewai_tools)):
            if importlib.util.find_spec(module) is not None:
                available.append((module, builder))
        if not available:
            self.skipTest("Install the langchain or crewai extra to run runtime contracts")
        return available

    @staticmethod
    def invoke(tool, arguments):
        # CrewAI hosts convert BaseTool to this structured, schema-validating form.
        if hasattr(tool, "to_structured_tool"):
            return tool.to_structured_tool().invoke(arguments)
        return tool.invoke(arguments)

    def test_exact_eight_tool_schema_surface_has_no_secrets_or_settlement_authority(self):
        for framework, builder in self.builders():
            toolkit, _ = make_toolkit()
            with self.subTest(framework=framework):
                tools = builder(toolkit)
                self.assertEqual({t.name for t in tools}, set(TOOL_FIELDS))
                self.assertEqual(len(tools), 8)
                for tool in tools:
                    with self.subTest(tool=tool.name):
                        schema = tool.args_schema.model_json_schema()
                        self.assertEqual(set(schema.get("properties", {})), TOOL_FIELDS[tool.name])
                        self.assertTrue(tool.description)
                        self.assertNotIn(PRIVATE_KEY, json.dumps(schema))
                names = {tool.name for tool in tools}
                self.assertFalse(names & {"rustchain_accept_job", "rustchain_dispute_job", "rustchain_cancel_job"})

    def test_every_real_tool_invokes_current_protocol_sdk(self):
        for framework, builder in self.builders():
            toolkit, transport = make_toolkit()
            tools = {tool.name: tool for tool in builder(toolkit)}
            with self.subTest(framework=framework):
                status = self.invoke(tools["rustchain_agent_status"], {})
                self.assertTrue(status["signed_posting_enabled"])
                self.assertEqual(transport.calls, [])
                calls = [
                    ("rustchain_list_jobs", {"category": "code", "min_reward": 2, "limit": 7, "offset": 3}, "GET", "/agent/jobs"),
                    ("rustchain_get_job", {"job_id": "job/with space"}, "GET", "/agent/jobs/job%2Fwith%20space"),
                    ("rustchain_post_job", {"title": "A test job", "description": "A sufficiently detailed test description.", "reward_rtc": 5, "category": "code", "tags": ["test"]}, "POST", "/agent/jobs"),
                    ("rustchain_claim_job", {"job_id": "job_1"}, "POST", "/agent/jobs/job_1/claim"),
                    ("rustchain_deliver_job", {"job_id": "job_1", "worker_wallet": "explicit-worker", "deliverable_url": "https://example.test/result", "deliverable_hash": "abc", "result_summary": "Done"}, "POST", "/agent/jobs/job_1/deliver"),
                    ("rustchain_get_reputation", {"wallet_id": "worker/with space"}, "GET", "/agent/reputation/worker%2Fwith%20space"),
                    ("rustchain_marketplace_stats", {}, "GET", "/agent/stats"),
                ]
                for number, (name, arguments, method, path) in enumerate(calls, 1):
                    result = self.invoke(tools[name], arguments)
                    self.assertEqual(result, {"ok": True, "request_number": number})
                    self.assertEqual(transport.calls[-1][:2], (method, path))
                self.assertEqual(transport.calls[0][2]["query"], {
                    "status": "open", "category": "code", "min_reward": 2.0, "limit": 7, "offset": 3,
                })
                assert_create_signature(self, transport.calls[2][2]["json_body"], toolkit.signer)
                self.assertEqual(transport.calls[2][2]["json_body"]["tags"], ["test"])
                self.assertEqual(transport.calls[3][2]["json_body"], {"worker_wallet": "default-worker"})
                self.assertEqual(transport.calls[4][2]["json_body"], {
                    "worker_wallet": "explicit-worker", "deliverable_url": "https://example.test/result",
                    "deliverable_hash": "abc", "result_summary": "Done",
                })

    def test_repeated_posts_are_fresh_signed_requests(self):
        for framework, builder in self.builders():
            toolkit, transport = make_toolkit()
            post = {tool.name: tool for tool in builder(toolkit)}["rustchain_post_job"]
            arguments = {"title": "A test job", "description": "A sufficiently detailed test description.", "reward_rtc": 5}
            with self.subTest(framework=framework):
                self.invoke(post, arguments)
                self.invoke(post, arguments)
                self.assertEqual(len(transport.calls), 2)
                bodies = [call[2]["json_body"] for call in transport.calls]
                self.assertNotEqual(bodies[0]["nonce"], bodies[1]["nonce"])
                for body in bodies:
                    assert_create_signature(self, body, toolkit.signer)

    def test_sdk_api_error_fields_survive_framework_invocation(self):
        for framework, builder in self.builders():
            toolkit, transport = make_toolkit()
            error = AgentEconomyApiError(409, "/agent/jobs/job_1/claim", {
                "error": "Job state changed under concurrent request", "code": "STATE_RACE",
            })
            transport.error = error
            claim = {tool.name: tool for tool in builder(toolkit)}["rustchain_claim_job"]
            with self.subTest(framework=framework):
                with self.assertRaises(AgentEconomyApiError) as raised:
                    self.invoke(claim, {"job_id": "job_1"})
                self.assertIs(raised.exception, error)
                self.assertEqual(raised.exception.status, 409)
                self.assertEqual(raised.exception.code, "STATE_RACE")
                self.assertEqual(raised.exception.body["error"], "Job state changed under concurrent request")

    def test_framework_schema_and_configuration_failures_do_not_make_requests(self):
        for framework, builder in self.builders():
            toolkit, transport = make_toolkit(signed=False, worker=None)
            tools = {tool.name: tool for tool in builder(toolkit)}
            with self.subTest(framework=framework):
                with self.assertRaises(ValueError):
                    self.invoke(tools["rustchain_post_job"], {"title": "Missing required arguments"})
                with self.assertRaises(ToolkitConfigurationError):
                    self.invoke(tools["rustchain_post_job"], {
                        "title": "A test job", "description": "A sufficiently detailed test description.", "reward_rtc": 5,
                    })
                with self.assertRaises(ToolkitConfigurationError):
                    self.invoke(tools["rustchain_claim_job"], {"job_id": "job_1"})
                with self.assertRaises(ToolkitConfigurationError):
                    self.invoke(tools["rustchain_claim_job"], {"job_id": "job_1", "worker_wallet": " "})
                self.assertEqual(transport.calls, [])

    @unittest.skipUnless(importlib.util.find_spec("crewai") is not None, "Install the crewai extra")
    def test_crewai_marketplace_tools_disable_host_caching(self):
        toolkit, _ = make_toolkit()
        for tool in build_crewai_tools(toolkit):
            with self.subTest(tool=tool.name):
                self.assertFalse(tool.cache_function({"sample": "arguments"}, {"ok": True}))
                structured = tool.to_structured_tool()
                self.assertFalse(structured.cache_function({}, {"ok": True}))


if __name__ == "__main__":
    unittest.main()
