@@ -13,12 +13,14 @@
 from typing import Any, Dict, List, Optional, Sequence

 import requests
 from agents import Agent, FunctionTool, function_tool

+from typing import Union
+
 DEFAULT_NODE_URL = "https://rustchain.org"
 DEFAULT_BOUNTIES_URL = (
     "https://api.github.com/repos/Scottcjn/rustchain-bounties/issues"
 )


 class RustChainClient:
     """Small HTTP client used by the agent tools."""

     def __init__(
         self,
         node_url: str = DEFAULT_NODE_URL,
         bounties_url:
@@ -47,6 +49,9 @@
                     description TEXT,
                     updated_at DATE,  # <--- Update date field to support SQLite 3.25+
                     is_active INTEGER DEFAULT 0,
                     id INTEGER PRIMARY KEY
                 )
             )
@@ -65,10 +70,24 @@
     return conn.cursor()

 def init_db():
+    cursor = conn.cursor()
     conn.execute("""
         CREATE TABLE IF NOT EXISTS repos (
             id INTEGER PRIMARY KEY,
             name TEXT UNIQUE NOT NULL,
             full_name TEXT,
             stars INTEGER,
             forks INTEGER,
             description TEXT,
             updated_at DATE,  # <--- Update date field to support SQLite 3.25+
             is_active INTEGER DEFAULT 0
         )
     """)
+    return conn
+
+def save_repos(conn: sqlite3.Connection):
+    # ... (unchanged save_repos function)

 def get_stats(repos: Sequence[Dict[str, Any]]) -> Dict[str, Any]:
     stats = {}
     for repo_data in repos:
@@ -81,14 +100,14 @@
 class RustChainTool(BaseTool):
     """
     LangChain tool for interacting with the RustChain blockchain.
     
     Provides native LangChain components for fetching data from the
     RustChain blockchain.
     """

     def fetch(
         self, query: str, params: Optional[Dict[str, Any]] = None
     ) -> Dict[str, Any]:
         """Fetch data via the RustChain API."""
         headers = self._get_headers()
         params = self._parse_positive_int_query(params)
+        return requests.get(f"{self.RUSTCHAIN_URL}/api/endpoint", headers=headers, params=params).json()
 