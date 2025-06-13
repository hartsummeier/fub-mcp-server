"""
Minimal MCP server – works with FastMCP 2.5.x as-is.
Still uses cupcake demo data so ChatGPT can connect.

Put your Follow Up Boss secrets in Render ➜ Environment:
  • FUB_API_KEY
  • FUB_CLIENT_ID
  • FUB_CLIENT_SECRET
  • FUB_X_SYSTEM  (if you have it)
  • FUB_X_SYSTEM_KEY (if you have it)
"""

import json, os
from pathlib import Path
from fastmcp.server import FastMCP

# --- optional FUB header holder (unused until you add real API calls) ----
HEADERS = {
    "Authorization": f"Bearer {os.getenv('FUB_API_KEY', '')}",
    "X-System":      os.getenv("FUB_X_SYSTEM", ""),
    "X-System-Key":  os.getenv("FUB_X_SYSTEM_KEY", ""),
    "Content-Type":  "application/json",
}

# cupcake demo data -------------------------------------------------------
RECORDS = json.loads(Path(__file__).with_name("records.json").read_text())
LOOKUP  = {r["id"]: r for r in RECORDS}

mcp = FastMCP(name="Cupcake MCP", instructions="Search cupcake orders")

@mcp.tool()
async def search(query: str):
    """Very dumb keyword search over demo data"""
    needles = query.lower().split()
    ids = [
        r["id"]
        for r in RECORDS
        if any(n in " ".join([r.get("title",""), r.get("text",""),
                              " ".join(r.get("metadata",{}).values())]).lower()
               for n in needles)
    ]
    return {"ids": ids}

@mcp.tool()
async def fetch(id: str):
    """Return full record for the id ChatGPT asks for."""
    if id not in LOOKUP:
        raise ValueError("unknown id")
    return LOOKUP[id]

# -------------------------------------------------------------------------
#  Render (or local) entry-point
# -------------------------------------------------------------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))   # Render injects $PORT
    mcp.run(transport="sse", host="0.0.0.0", port=port)
