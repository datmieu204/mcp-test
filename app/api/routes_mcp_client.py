# app/api/routes_mcp_client.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from typing import List, Dict, Any

from app.db.session import get_db
from app.services.mcp_client_services import MCPClientService

router = APIRouter()

@router.get("/{server_id}/tools", response_model=List[Dict[str, Any]])
async def list_server_tools(server_id: UUID, db: AsyncSession = Depends(get_db)):
    """
    Get the list of available tools from a specific MCP server.
    """
    return await MCPClientService.list_tools(db, server_id)

@router.get("/{server_id}/tools/{tool_name}", response_model=Dict[str, Any])
async def get_server_tool(server_id: UUID, tool_name: str, db: AsyncSession = Depends(get_db)):
    """
    Get the details of a specific tool from an MCP server.
    """
    return await MCPClientService.get_tool(db, server_id, tool_name)

@router.post("/{server_id}/tools/{tool_name}/execute", response_model=Dict[str, Any])
async def execute_server_tool(
    server_id: UUID,
    tool_name: str,
    parameters: Dict[str, Any],
    db: AsyncSession = Depends(get_db),
):
    """
    Execute a tool on a specific MCP server.
    """
    return await MCPClientService.execute_tool(db, server_id, tool_name, parameters)

@router.post("/{server_id}/reload", response_model=Dict[str, str])
async def reload_mcp_server(server_id: UUID, db: AsyncSession = Depends(get_db)):
    """
    Trigger a reload on a specific MCP server.
    """
    return await MCPClientService.reload_server(db, server_id)
