import importlib.util
import pathlib
import sys
import types
import unittest


class FakeMCPServer:
    def __init__(self, name, instructions=None):
        self.name = name
        self.instructions = instructions
        self.tools = {}
        self.ran = None

    def tool(self):
        def decorate(fn):
            self.tools[fn.__name__] = fn
            return fn
        return decorate

    def run(self, transport="stdio"):
        self.ran = transport


class FakeToolError(RuntimeError):
    pass


class FakeService:
    def status(self): return {"ok": True}
    def list_jobs(self, **kwargs): return {"op": "list", **kwargs}
    def get_job(self, job_id): return {"op": "get", "job_id": job_id}
    def post_job(self, **kwargs): return {"op": "post", **kwargs}
    def claim_job(self, job_id, **kwargs): return {"op": "claim", "job_id": job_id, **kwargs}
    def deliver_job(self, job_id, **kwargs): return {"op": "deliver", "job_id": job_id, **kwargs}
    def get_reputation(self, wallet_id): return {"op": "rep", "wallet_id": wallet_id}
    def get_stats(self): return {"op": "stats"}


class ServerContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        fake_mcp = types.ModuleType("mcp")
        fake_server = types.ModuleType("mcp.server")
        fake_server.MCPServer = FakeMCPServer
        fake_exc = types.ModuleType("mcp.server.mcpserver.exceptions")
        fake_exc.ToolError = FakeToolError
        sys.modules.setdefault("mcp", fake_mcp)
        sys.modules["mcp.server"] = fake_server
        sys.modules["mcp.server.mcpserver.exceptions"] = fake_exc

        path = pathlib.Path(__file__).parents[1] / "src" / "rustchain_agent_economy_mcp" / "server.py"
        spec = importlib.util.spec_from_file_location(
            "rustchain_agent_economy_mcp._contract_server", path
        )
        cls.module = importlib.util.module_from_spec(spec)
        assert spec.loader is not None
        spec.loader.exec_module(cls.module)

    def test_registers_expected_mcp_tools(self):
        server = self.module.build_server(FakeService())
        self.assertEqual(set(server.tools), {
            "agent_status",
            "list_jobs",
            "get_job",
            "post_job",
            "claim_job",
            "deliver_job",
            "get_reputation",
            "get_marketplace_stats",
        })

    def test_tool_surface_contains_no_private_key_argument(self):
        import inspect
        server = self.module.build_server(FakeService())
        for fn in server.tools.values():
            names = set(inspect.signature(fn).parameters)
            self.assertFalse({"private_key", "private_key_hex", "poster_private_key"} & names)

    def test_tools_delegate_structured_results(self):
        server = self.module.build_server(FakeService())
        self.assertEqual(server.tools["get_job"]("job_1"), {"op": "get", "job_id": "job_1"})
        result = server.tools["list_jobs"](category="code", limit=3)
        self.assertEqual(result["op"], "list")
        self.assertEqual(result["category"], "code")
        self.assertEqual(result["limit"], 3)

    def test_instructions_explain_settlement_boundary(self):
        server = self.module.build_server(FakeService())
        self.assertIn("Settlement", server.instructions)
        self.assertIn("not exposed", server.instructions)


if __name__ == "__main__":
    unittest.main()
