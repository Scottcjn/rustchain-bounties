"""MCP stdio server for RustChain."""
import sys
import json
import threading
from .client import RustChainClient, RustChainError


class RustChainMCPServer:
    """Model Context Protocol server for RustChain."""
    
    def __init__(self, node_url: str = "https://50.28.86.131"):
        self.client = RustChainClient(node_url)
        self.tools = {
            "rustchain_health": self.tool_health,
            "rustchain_balance": self.tool_balance,
            "rustchain_epoch": self.tool_epoch,
            "rustchain_miners": self.tool_miners,
            "rustchain_create_wallet": self.tool_create_wallet,
            "rustchain_submit_attestation": self.tool_attestation,
        }
    
    def handle_request(self, req: dict) -> dict:
        """Handle incoming MCP request."""
        method = req.get("method", "")
        params = req.get("params", {})
        req_id = req.get("id")
        
        if method == "initialize":
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {"tools": {}},
                    "serverInfo": {"name": "rustchain-mcp", "version": "1.0.0"}
                }
            }
        
        if method == "tools/list":
            tools = [
                {"name": name, "description": self._get_description(name), "inputSchema": self._get_schema(name)}
                for name, _ in self.tools.items()
            ]
            return {"jsonrpc": "2.0", "id": req_id, "result": {"tools": tools}}
        
        if method == "tools/call":
            tool_name = params.get("name")
            tool_args = params.get("arguments", {})
            
            if tool_name not in self.tools:
                return {
                    "jsonrpc": "2.0", "id": req_id,
                    "error": {"code": -32602, "message": f"Unknown tool: {tool_name}"}
                }
            
            try:
                result = self.tools[tool_name](**tool_args)
                return {
                    "jsonrpc": "2.0", "id": req_id,
                    "result": {
                        "content": [{"type": "text", "text": json.dumps(result, indent=2)}]
                    }
                }
            except RustChainError as e:
                return {
                    "jsonrpc": "2.0", "id": req_id,
                    "error": {"code": -32000, "message": str(e)}
                }
            except Exception as e:
                return {
                    "jsonrpc": "2.0", "id": req_id,
                    "error": {"code": -32000, "message": f"Internal error: {e}"}
                }
        
        return {
            "jsonrpc": "2.0", "id": req_id,
            "error": {"code": -32601, "message": f"Method not found: {method}"}
        }
    
    def tool_health(self) -> dict:
        """Check node health."""
        return self.client.health()
    
    def tool_balance(self, miner_id: str) -> dict:
        """Query wallet balance."""
        return self.client.wallet_balance(miner_id)
    
    def tool_epoch(self) -> dict:
        """Get current epoch info."""
        return self.client.epoch()
    
    def tool_miners(self, limit: int = 100) -> dict:
        """List active miners."""
        return self.client.miners(limit)
    
    def tool_create_wallet(self, miner_id: str, public_key: str) -> dict:
        """Register a new wallet."""
        return self.client.create_wallet(miner_id, public_key)
    
    def tool_attestation(self, miner_id: str, fingerprint: str, signature: str, epoch: int) -> dict:
        """Submit attestation."""
        return self.client.submit_attestation(miner_id, fingerprint, signature, epoch)
    
    def _get_description(self, tool: str) -> str:
        descs = {
            "rustchain_health": "Check RustChain node health status",
            "rustchain_balance": "Query wallet balance for a miner",
            "rustchain_epoch": "Get current epoch information",
            "rustchain_miners": "List active miners on the network",
            "rustchain_create_wallet": "Register a new agent wallet",
            "rustchain_submit_attestation": "Submit hardware fingerprint attestation",
        }
        return descs.get(tool, "")
    
    def _get_schema(self, tool: str) -> dict:
        schemas = {
            "rustchain_health": {"type": "object", "properties": {}},
            "rustchain_balance": {"type": "object", "properties": {"miner_id": {"type": "string"}}},
            "rustchain_epoch": {"type": "object", "properties": {}},
            "rustchain_miners": {"type": "object", "properties": {"limit": {"type": "integer", "default": 100}}},
            "rustchain_create_wallet": {"type": "object", "properties": {"miner_id": {"type": "string"}, "public_key": {"type": "string"}}},
            "rustchain_submit_attestation": {"type": "object", "properties": {"miner_id": {"type": "string"}, "fingerprint": {"type": "string"}, "signature": {"type": "string"}, "epoch": {"type": "integer"}}},
        }
        return schemas.get(tool, {"type": "object"})
    
    def run(self):
        """Run the MCP server on stdio."""
        for line in sys.stdin:
            line = line.strip()
            if not line:
                continue
            try:
                req = json.loads(line)
                resp = self.handle_request(req)
                print(json.dumps(resp), flush=True)
            except json.JSONDecodeError:
                pass


def main():
    server = RustChainMCPServer()
    server.run()


if __name__ == "__main__":
    main()
