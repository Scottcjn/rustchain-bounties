#!/usr/bin/env python3
import json
import sys
import urllib.request

def query_chain(address):
    # Mocking RustChain API call
    return {"address": address, "balance": "100 RTC", "status": "active"}

def handle_request(req):
    if req.get("method") == "initialize":
        return {
            "protocolVersion": "2024-11-05",
            "capabilities": {},
            "serverInfo": {"name": "rustchain-mcp", "version": "1.0.0"}
        }
    elif req.get("method") == "tools/list":
        return {
            "tools": [{
                "name": "query_address",
                "description": "Query a RustChain address",
                "inputSchema": {
                    "type": "object",
                    "properties": {"address": {"type": "string"}},
                    "required": ["address"]
                }
            }]
        }
    elif req.get("method") == "tools/call":
        params = req.get("params", {})
        if params.get("name") == "query_address":
            addr = params.get("arguments", {}).get("address")
            result = query_chain(addr)
            return {"content": [{"type": "text", "text": json.dumps(result)}]}
    return {"error": "Method not found"}

def main():
    while True:
        line = sys.stdin.readline()
        if not line:
            break
        try:
            req = json.loads(line)
            # JsonRPC requires id to be returned
            req_id = req.get("id")
            result = handle_request(req)
            resp = {"jsonrpc": "2.0", "id": req_id}
            if "error" in result:
                resp["error"] = {"code": -32601, "message": result["error"]}
            else:
                resp["result"] = result
            print(json.dumps(resp))
            sys.stdout.flush()
        except Exception as e:
            pass

if __name__ == "__main__":
    main()