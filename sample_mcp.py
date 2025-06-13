"""
Minimal MCP server (Python 3.11+) – still uses cupcake demo data.

• Publishes /.well-known/mcp.json so ChatGPT can create the connector.
• Keeps HEADERS ready for real Follow Up Boss API calls later.
"""

import json
import os
from pathlib import Path

from fastmcp.server import FastMCP
from starlette.responses import JSONResponse   # starlette is already installed

# ────────── FUB headers (set as secrets in Render) ──────────
HEADERS = {
    "Authorization": f"Bearer {os.environ['FUB_API_KEY']}",
    "X-System":      os.environ.get("FUB_X_SYSTEM", ""),
    "X-System-Key":  os.environ.get("FUB_X_SYSTEM_KEY", ""),
    "Content-Type":  "application/json",
}

# cupcake demo data
RECORDS = json.loads(Path(__file__).with_name("records.json").read_text())
LOOKUP  = {r["id"]: r for r in RECORDS}

def create_server() -> FastMCP:
    mcp = FastMCP(name="Cupcake MCP", instructions="Search cupcake orders")

      # ── add this small block ───────────────────────────────
    api = mcp.fastapi              # ← works in FastMCP 2.5.x
    @api.get("/.well-known/mcp.json", include_in_schema=False)
    async def _metadata():
        return JSONResponse(mcp.schema())

    # ------------ search tool ------------
    @mcp.tool()
    async def search(query: str):
        tokens = query.lower().split()
        ids = [r["id"] for r in RECORDS
               if any(t in " ".join([r.get("title",""), r.get("text",""),
                                     " ".join(r.get("metadata",{}).values())]).lower()
                      for t in tokens)]
        return {"ids": ids}

    # ------------ fetch tool -------------
    @mcp.tool()
    async def fetch(id: str):
        if id not in LOOKUP:
            raise ValueError("unknown id")
        return LOOKUP[id]

    return mcp

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))      # Render injects $PORT
    create_server().run(transport="sse",
                        host="0.0.0.0", port=port)
