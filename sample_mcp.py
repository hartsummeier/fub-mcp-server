"""
Works with fastmcp 2.5.x      Python ≥ 3.11

* CUPCAKE demo data so ChatGPT’s deep-research handshake succeeds
* /.well-known/mcp.json is now served            ← ⭐ THIS FIXES 404
* HEADERS ready for real Follow Up Boss calls
"""

from pathlib import Path
import json, os

from fastapi import FastAPI
from starlette.responses import JSONResponse
from fastmcp.server import FastMCP     # pip install fastmcp (already in requirements)

# ── FUB secrets (add these in Render ▸ Environment) ────────────────────
HEADERS = {
    "Authorization": f"Bearer {os.environ.get('FUB_API_KEY', '')}",
    "X-System":      os.environ.get("FUB_X_SYSTEM", ""),
    "X-System-Key":  os.environ.get("FUB_X_SYSTEM_KEY", ""),
    "Content-Type":  "application/json",
}

# demo cupcake orders ---------------------------------------------------
RECORDS = json.loads(Path(__file__).with_name("records.json").read_text())
LOOKUP  = {r["id"]: r for r in RECORDS}

# ── build the MCP server ───────────────────────────────────────────────
mcp = FastMCP(name="Cupcake MCP", instructions="Search cupcake orders")

@mcp.tool()
async def search(query: str):
    """Very dumb keyword search over demo cupcake orders."""
    tokens = query.lower().split()
    ids = [
        r["id"] for r in RECORDS
        if any(tok in " ".join([r.get("title",""), r.get("text",""),
                               " ".join(r.get("metadata",{}).values())]).lower()
               for tok in tokens)
    ]
    return {"ids": ids}

@mcp.tool()
async def fetch(id: str):
    """Return a full cupcake order by ID."""
    if id not in LOOKUP:
        raise ValueError("unknown id")
    return LOOKUP[id]

# ── expose metadata + mount MCP under FastAPI ──────────────────────────
app = FastAPI(title="Wrapped MCP server")
app.mount("/", mcp)                                   # mounts SSE + messages
@app.get("/.well-known/mcp.json", include_in_schema=False)
async def _metadata():
    return JSONResponse(mcp.schema())                 # ← ChatGPT reads this

# ── local run (Render uses the uvicorn command we’ll set below) ────────
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app,
                host="0.0.0.0",
                port=int(os.environ.get("PORT", 8000)))
