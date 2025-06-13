"""
Cupcake MCP – works with FastMCP 2.5.x
Publishes /.well-known/mcp.json so ChatGPT can discover the tools.
"""

import json, os
from pathlib import Path
from fastmcp.server import FastMCP
from starlette.responses import JSONResponse

# demo records -------------------------------------------------
RECORDS = json.loads(Path(__file__).with_name("records.json").read_text())
LOOKUP  = {r["id"]: r for r in RECORDS}

def create_server() -> FastMCP:
    mcp = FastMCP(name="Cupcake MCP",
                  instructions="Search cupcake orders")

    # metadata route (must exist for ChatGPT connector)
    @mcp.route("/.well-known/mcp.json", methods=["GET"], include_in_schema=False)
    async def _meta(req):
        return JSONResponse(mcp.schema())

    # ---------- search ----------
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

    # ---------- fetch -----------
    @mcp.tool()
    async def fetch(id: str):
        if id not in LOOKUP:
            raise ValueError("unknown id")
        return LOOKUP[id]

    return mcp

if __name__ == "__main__":
    # Render injects the port number via $PORT
    port = int(os.environ.get("PORT", 8000))
    create_server().run(transport="sse", host="0.0.0.0", port=port)
