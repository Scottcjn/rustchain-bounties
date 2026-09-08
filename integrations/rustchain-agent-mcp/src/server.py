"""
RustChain RIP-302 Agent Economy Model Context Protocol (MCP) Server.
Provides autonomous agents (Claude Code, Cursor, Antigravity) with standard MCP tools
to post jobs, claim tasks, submit deliverables, and manage on-chain reputation.
"""

import sys
import json
import asyncio
from typing import Dict, Any, Optional

from sdk.python.rustchain_sdk.client import RustChainClient
from sdk.python.rustchain_sdk.agent_economy import (
    AgentEconomyClient,
    calculate_escrow,
    AGENT_CATEGORIES,
)


class RustChainAgentMCPServer:
    """
    Standard MCP stdio server implementing the Model Context Protocol
    for RustChain RIP-302 Agent Economy.
    """

    def __init__(self, node_url: str = "https://50.28.86.131", wallet: Optional[str] = None):
        self.node_url = node_url
        self.wallet = wallet
        self.client = AgentEconomyClient(base_url=node_url, wallet=wallet)

    def get_tool_definitions(self) -> list:
        return [
            {
                "name": "get_marketplace_stats",
                "description": "Get real-time statistics of the RustChain RIP-302 Agent Economy marketplace (active agents, volume, open jobs, fee rates).",
                "inputSchema": {
                    "type": "object",
                    "properties": {},
                },
            },
            {
                "name": "list_agent_jobs",
                "description": "Browse and filter open/active jobs in the RustChain Agent Economy marketplace.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "category": {
                            "type": "string",
                            "description": "Optional category filter (research, code, writing, video, data, design, etc.)",
                            "enum": AGENT_CATEGORIES,
                        },
                        "status": {
                            "type": "string",
                            "description": "Status filter: posted, claimed, delivered, completed, disputed, cancelled",
                        },
                        "min_reward": {
                            "type": "number",
                            "description": "Minimum reward threshold in RTC",
                        },
                        "limit": {
                            "type": "integer",
                            "description": "Max jobs to return (default 50)",
                            "default": 50,
                        },
                    },
                },
            },
            {
                "name": "post_agent_job",
                "description": "Post a new bounty/job to the RustChain Agent Economy. Escrow (reward + 5% platform fee) is locked until delivery and acceptance.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "title": {"type": "string", "description": "Clear, descriptive job title"},
                        "category": {
                            "type": "string",
                            "description": "Category",
                            "enum": AGENT_CATEGORIES,
                        },
                        "reward_rtc": {"type": "number", "description": "Reward in RTC offered to the worker"},
                        "description": {"type": "string", "description": "Detailed specification of the task and requirements"},
                        "poster_wallet": {"type": "string", "description": "Poster wallet address (optional if server configured with wallet)"},
                        "expires_at": {"type": "string", "description": "Optional ISO8601 expiration timestamp"},
                    },
                    "required": ["title", "category", "reward_rtc"],
                },
            },
            {
                "name": "claim_agent_job",
                "description": "Claim an open job in the Agent Economy to signal you are working on it.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "job_id": {"type": "string", "description": "The unique job identifier"},
                        "worker_wallet": {"type": "string", "description": "Worker wallet address (optional if configured)"},
                        "note": {"type": "string", "description": "Optional claim note / ETA"},
                    },
                    "required": ["job_id"],
                },
            },
            {
                "name": "deliver_agent_job",
                "description": "Submit completed deliverable work for a claimed job with proof/hash.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "job_id": {"type": "string", "description": "The unique job identifier"},
                        "worker_wallet": {"type": "string", "description": "Worker wallet address (optional if configured)"},
                        "deliverable_url": {"type": "string", "description": "URL to deliverable code, PR, or artifact"},
                        "summary": {"type": "string", "description": "Summary of work completed and execution details"},
                        "artifact_hash": {"type": "string", "description": "Cryptographic SHA256 hash of artifact or deliverable"},
                    },
                    "required": ["job_id", "summary"],
                },
            },
            {
                "name": "accept_agent_job",
                "description": "Accept delivered work for a job you posted, releasing locked escrow to the worker and submitting a rating.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "job_id": {"type": "string", "description": "The unique job identifier"},
                        "poster_wallet": {"type": "string", "description": "Poster wallet address (optional if configured)"},
                        "rating": {"type": "integer", "description": "Rating score from 1 to 5 stars (default 5)", "minimum": 1, "maximum": 5, "default": 5},
                        "review": {"type": "string", "description": "Optional review/feedback for the worker's reputation"},
                    },
                    "required": ["job_id"],
                },
            },
            {
                "name": "get_agent_reputation",
                "description": "Get trust score, reputation tier (legendary, trusted, neutral, risky), and stats for an agent wallet.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "wallet": {"type": "string", "description": "Agent wallet address to inspect"},
                    },
                    "required": ["wallet"],
                },
            },
            {
                "name": "calculate_job_escrow",
                "description": "Calculate required escrow amount and 5% platform fee for a given RTC reward.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "reward_rtc": {"type": "number", "description": "Proposed reward in RTC"},
                    },
                    "required": ["reward_rtc"],
                },
            },
        ]

    async def execute_tool(self, name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        if name == "get_marketplace_stats":
            stats = await self.client.get_stats()
            return {"content": [{"type": "text", "text": json.dumps(stats.raw_data or stats.__dict__, indent=2)}]}

        elif name == "list_agent_jobs":
            jobs = await self.client.list_jobs(
                category=arguments.get("category"),
                status=arguments.get("status"),
                min_reward=arguments.get("min_reward"),
                limit=arguments.get("limit", 50),
            )
            data = [j.__dict__ for j in jobs]
            return {"content": [{"type": "text", "text": json.dumps(data, indent=2)}]}

        elif name == "post_agent_job":
            job = await self.client.post_job(
                title=arguments["title"],
                category=arguments["category"],
                reward_rtc=float(arguments["reward_rtc"]),
                description=arguments.get("description", ""),
                poster_wallet=arguments.get("poster_wallet"),
                expires_at=arguments.get("expires_at"),
            )
            return {"content": [{"type": "text", "text": json.dumps(job.__dict__, indent=2)}]}

        elif name == "claim_agent_job":
            res = await self.client.claim_job(
                job_id=arguments["job_id"],
                worker_wallet=arguments.get("worker_wallet"),
                note=arguments.get("note", ""),
            )
            return {"content": [{"type": "text", "text": json.dumps(res, indent=2)}]}

        elif name == "deliver_agent_job":
            res = await self.client.deliver_job(
                job_id=arguments["job_id"],
                worker_wallet=arguments.get("worker_wallet"),
                deliverable_url=arguments.get("deliverable_url", ""),
                summary=arguments.get("summary", ""),
                artifact_hash=arguments.get("artifact_hash", ""),
            )
            return {"content": [{"type": "text", "text": json.dumps(res, indent=2)}]}

        elif name == "accept_agent_job":
            res = await self.client.accept_job(
                job_id=arguments["job_id"],
                poster_wallet=arguments.get("poster_wallet"),
                rating=arguments.get("rating", 5),
                review=arguments.get("review", ""),
            )
            return {"content": [{"type": "text", "text": json.dumps(res, indent=2)}]}

        elif name == "get_agent_reputation":
            rep = await self.client.get_reputation(wallet=arguments["wallet"])
            return {"content": [{"type": "text", "text": json.dumps(rep.__dict__, indent=2)}]}

        elif name == "calculate_job_escrow":
            calc = calculate_escrow(float(arguments["reward_rtc"]))
            return {"content": [{"type": "text", "text": json.dumps(calc.__dict__, indent=2)}]}

        raise ValueError(f"Unknown tool: {name}")

    async def handle_rpc(self, message: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        msg_id = message.get("id")
        method = message.get("method")
        params = message.get("params", {})

        if method == "tools/list":
            return {
                "jsonrpc": "2.0",
                "id": msg_id,
                "result": {"tools": self.get_tool_definitions()},
            }
        elif method == "tools/call":
            tool_name = params.get("name")
            tool_args = params.get("arguments", {})
            try:
                result = await self.execute_tool(tool_name, tool_args)
                return {"jsonrpc": "2.0", "id": msg_id, "result": result}
            except Exception as e:
                return {
                    "jsonrpc": "2.0",
                    "id": msg_id,
                    "error": {"code": -32603, "message": str(e)},
                }
        elif method == "initialize":
            return {
                "jsonrpc": "2.0",
                "id": msg_id,
                "result": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {"tools": {}},
                    "serverInfo": {"name": "rustchain-agent-mcp", "version": "0.1.0"},
                },
            }
        elif method == "notifications/initialized":
            return None

        return {
            "jsonrpc": "2.0",
            "id": msg_id,
            "error": {"code": -32601, "message": f"Method not found: {method}"},
        }

    async def run_stdio(self):
        reader = asyncio.StreamReader()
        protocol = asyncio.StreamReaderProtocol(reader)
        await asyncio.get_event_loop().connect_read_pipe(lambda: protocol, sys.stdin)

        while True:
            line = await reader.readline()
            if not line:
                break
            line_str = line.decode("utf-8").strip()
            if not line_str:
                continue
            try:
                msg = json.loads(line_str)
                resp = await self.handle_rpc(msg)
                if resp:
                    sys.stdout.write(json.dumps(resp) + "\n")
                    sys.stdout.flush()
            except Exception as err:
                sys.stderr.write(f"Error handling message: {err}\n")


if __name__ == "__main__":
    server = RustChainAgentMCPServer()
    asyncio.run(server.run_stdio())
