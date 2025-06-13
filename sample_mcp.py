"""
WORKING MCP ─ copy / paste over the whole file.

• Publishes /.well-known/mcp.json so ChatGPT can add the connector.
• Uses only attributes guaranteed in FastMCP 2.5.x (no .app or .fastapi).
"""

import json, os
from pathlib import Path
from fastmcp.server import FastMCP
from starlette.responses import JSONResponse

# ───────────── demo data ─────────────
RECORDS = json.loads(Path(__file__).with_name("records.json").read_text())
LOOKUP  = {r["id"]: r for r in RECORDS}

def create_server() -> FastMCP:
    mcp = FastMCP(name="Cupcake MCP",
                  instructions="Search cupcake orders")

    # Metadata endpoint required by ChatGPT
    @mcp.get("/.well-known/mcp.json", include_in_schema=False)
    async def _meta():
        return JSONResponse(mcp.schema())

    # ── search tool ──
    @mcp.tool()
    async def search(query: str):
        toks = query.lower().split()
        ids = [
            r["id"] for r in RECORDS
            if any(
                t in " ".join(
                    [r.get("title",""), r.get("text",""),
                     " ".join(r.get("metadata",{}).values())]
                ).lower() for t in toks
            )
        ]
        return {"ids": ids}

    # ── fetch tool ──
    @mcp.tool()
    async def fetch(id: str):
        if id not in LOOKUP:
            raise ValueError("unknown id")
        return LOOKUP[id]

    return mcp

# Run on Render -------------------------------------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))   # Render injects $PORT
    create_server().run(transport="sse",
                        host="0.0.0.0", port=port)
