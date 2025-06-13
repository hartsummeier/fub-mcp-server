"""
Minimal MCP server example (Python 3.11+)

• Still uses cupcake-demo data so ChatGPT’s deep-research handshake works.
• Includes Follow Up Boss auth headers so you can swap in real API calls later.
"""

import json
import os
from pathlib import Path

import httpx                               # handy later for real FUB calls
from fastmcp.server import FastMCP
from starlette.responses import JSONResponse        # ⭐ starlette, not fastapi

# ───────────────────────────────────────────────────────────
#  Follow Up Boss auth headers (set as secrets in Render)
# ───────────────────────────────────────────────────────────
HEADERS = {
    "Authorization": f"Bearer {os.environ['FUB_API_KEY']}",
    "X-System":      os.environ.get("FUB_X_SYSTEM", ""),
    "X-System-Key":  os.environ.get("FUB_X_SYSTEM_KEY", ""),
    "Content-Type":  "application/json",
}

# cupcake demo data ----------------------------------------
RECORDS = json.loads(Path(__file__).with_name("records.json").read_text())
LOOKUP  = {r["id"]: r for r in RECORDS}


def create_server() -> FastMCP:
    """Build and return a FastMCP server instance."""
    mcp = FastMCP(name="Cupcake MCP", instructions="Search cupcake orders")

    # metadata endpoint so ChatGPT can discover the tools
    fastapi = mcp.app                       # FastAPI instance inside FastMCP
    @fastapi.get("/.well-known/mcp.json", include_in_schema=False)
    async def _metadata():
        return JSONResponse(mcp.schema())

    # ---------- search tool ----------
    @mcp.tool()
    async def search(query: str):
        toks = query.lower().split()
        ids: list[str] = []
        for r in RECORDS:
            hay = " ".join(
                [r.get("title", ""), r.get("text", ""),
                 " ".join(r.get("metadata", {}).values())]
            ).lower()
            if any(t in hay for t in toks):
                ids.append(r["id"])
        return {"ids": ids}

    # ---------- fetch tool -----------
    @mcp.tool()
    async def fetch(id: str):
        if id not in LOOKUP:
            raise ValueError("unknown id")
        return LOOKUP[id]

    return mcp


# ───────────────────────────────────────────────────────────
#  Run directly (works on Render free tier)
# ───────────────────────────────────────────────────────────
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))   # Render injects $PORT
    create_server().run(transport="sse", host="0.0.0.0", port=port)
