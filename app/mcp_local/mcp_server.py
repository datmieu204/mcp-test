# app/mcp/mcp_server.py

import asyncio
from app.mcp_local.mcp_tools import mcp  

if __name__ == "__main__":
    # asyncio.run(mcp.run(transport='stdio'))
    asyncio.run(mcp.run(transport='sse', host='127.0.0.1', port=8099))
