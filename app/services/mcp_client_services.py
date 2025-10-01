# app/services/mcp_client_services.py

from uuid import UUID
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.mcp_server_services import MCPServerService
from typing import Dict, Any, List, Optional
from contextlib import AsyncExitStack
from mcp import ClientSession
from mcp.client.sse import sse_client

class MCPClientService:
    @staticmethod
    async def _create_session(server_url: str, api_key: Optional[str], stack: AsyncExitStack):
        try:
            headers = {}
            if api_key:
                headers["Authorization"] = f"Bearer {api_key}"
            
            transport = await stack.enter_async_context(sse_client(server_url, headers=headers))
            read, write = transport
            session = await stack.enter_async_context(ClientSession(read, write))
            await session.initialize()
            return session
        except Exception as e:
            raise HTTPException(status_code=503, detail=f"Error connecting to MCP Server: {e}")

    @staticmethod
    async def list_tools(db: AsyncSession, server_id: UUID) -> List[Dict[str, Any]]:
        """
        Retrieves the list of available tools from a specific MCP server.
        """
        server = await MCPServerService.get_server(db, server_id)
        if not server or not server.is_enabled:
            raise HTTPException(status_code=404, detail="MCP Server not found or is disabled.")

        async with AsyncExitStack() as stack:
            session = await MCPClientService._create_session(str(server.server_url), server.api_key, stack)
            response = await session.list_tools()
            return [tool.model_dump() for tool in response.tools]

    @staticmethod
    async def get_tool(db: AsyncSession, server_id: UUID, tool_name: str) -> Dict[str, Any]:
        """
        Retrieves the details of a specific tool from an MCP server.
        """
        server = await MCPServerService.get_server(db, server_id)
        if not server or not server.is_enabled:
            raise HTTPException(status_code=404, detail="MCP Server not found or is disabled.")

        async with AsyncExitStack() as stack:
            session = await MCPClientService._create_session(str(server.server_url), server.api_key, stack)
            response = await session.list_tools()
            for tool in response.tools:
                if tool.name == tool_name:
                    return tool.model_dump()
            raise HTTPException(status_code=404, detail=f"Tool '{tool_name}' not found on MCP Server.")

    @staticmethod
    async def execute_tool(db: AsyncSession, server_id: UUID, tool_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Executes a specific tool on an MCP server with the given parameters.
        """
        server = await MCPServerService.get_server(db, server_id)
        if not server or not server.is_enabled:
            raise HTTPException(status_code=404, detail="MCP Server not found or is disabled.")

        async with AsyncExitStack() as stack:
            session = await MCPClientService._create_session(str(server.server_url), server.api_key, stack)
            result = await session.call_tool(tool_name, parameters)
            return result.content

    @staticmethod
    async def reload_server(db: AsyncSession, server_id: UUID) -> Dict[str, Any]:
        """
        Sends a reload command to a specific MCP server.
        """
        server = await MCPServerService.get_server(db, server_id)
        if not server or not server.is_enabled:
            raise HTTPException(status_code=404, detail="MCP Server not found or is disabled.")

        async with AsyncExitStack() as stack:
            session = await MCPClientService._create_session(str(server.server_url), server.api_key, stack)

            try:
                await session.call_tool("reload", {})
                return {"status": "Reload command sent successfully."}
            except Exception as e:
                # This could fail if 'reload' tool doesn't exist.
                raise HTTPException(status_code=501, detail=f"Could not reload server: {e}")

