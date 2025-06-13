"""
Minimal MCP server example   (Python 3.11+)

* Deep-research “search”  +  “fetch” tools still use demo data (records.json)
* Adds Follow Up Boss credentials in HEADERS so you can swap in real API calls
"""

import json
import os
from pathlib import Path

import httpx               # <- handy when you start calling FUB for real
from fastmcp.server import FastMCP

# ---------------------------------------------------------------------------
# Follow Up Boss auth headers
# (Render → Environment tab → Secret variables FUB_API_KEY, FUB_X_SYSTEM, FUB_X_SYSTEM_KEY)
# ---------------------------------------------------------------------------

HEADERS = {
    "Authorization": f"Bearer {os.environ['FUB_API_KEY']}",
    "X-System": os.environ.get("FUB_X_SYSTEM", ""),
    "X-System-Key": os.environ.get("FUB_X_SYSTEM_KEY", ""),
    "Content-Type": "application/json",
}

# ---------------------------------------------------------------------------
# Demo cupcake data so the connector has something to index
# ---------------------------------------------------------------------------

RECORDS = json.loads(Path(__file__).with_name("records.json").read_text())
LOOKUP = {r["id"]: r for r in RECORDS}


def create_server() -> FastMCP:
    """
    Build and return a FastMCP server instance.
    """
    mcp = FastMCP(name="Cupcake MCP", instructions="Search cupcake orders")

    # ----------------- search tool -----------------
    @mcp.tool()
    async def search(query: str):
        """
        Keyword match against demo cupcake orders.
        """
        toks = query.lower().split()
        ids: list[str] = []
        for r in RECORDS:
            haystack = " ".join(
                [
                    r.get("title", ""),
                    r.get("text", ""),
                    " ".join(r.get("metadata", {}).values()),
                ]
            ).lower()
            if any(t in haystack for t in toks):
                ids.append(r["id"])
        return {"ids": ids}

    # ----------------- fetch tool ------------------
    @mcp.tool()
    async def fetch(id: str):
        """
        Return full record for the given ID.
        """
        if id not in LOOKUP:
            raise ValueError("unknown id")
        return LOOKUP[id]

    return mcp


# ---------------------------------------------------------------------------
# When launched by a WSGI/ASGI runner (e.g. `uvicorn sample_mcp:app ...`)
# ---------------------------------------------------------------------------
app = create_server().asgi  

# ---------------------------------------------------------------------------
# When run directly (e.g. python sample_mcp.py) – local testing convenience
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    # Binds to localhost:8000 – good for “curl http://127.0.0.1:8000/.well-known/mcp.json”
    create_server().run(transport="sse", host="127.0.0.1", port=8000)
