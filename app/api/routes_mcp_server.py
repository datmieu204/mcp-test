# app/api/routes_mcp_server.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from uuid import UUID

from app.db.session import get_db
from app.schemas.mcp_server import MCPServerCreate, MCPServerUpdate, MCPServerResponse
from app.services.mcp_server_services import MCPServerService

router = APIRouter()

@router.post("/", response_model=MCPServerResponse, status_code=status.HTTP_201_CREATED)
async def create_mcp_server(
    server: MCPServerCreate, db: AsyncSession = Depends(get_db)
):
    db_server = await MCPServerService.get_server_by_name(db, name=server.name)
    if db_server:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Server with this name already exists.",
        )
    return await MCPServerService.create_server(db=db, server=server)

@router.get("/", response_model=List[MCPServerResponse])
async def read_mcp_servers(
    skip: int = 0, limit: int = 10, db: AsyncSession = Depends(get_db)
):
    servers = await MCPServerService.get_all_servers(db, skip=skip, limit=limit)
    return servers

@router.get("/{server_id}", response_model=MCPServerResponse)
async def read_mcp_server(
    server_id: UUID, db: AsyncSession = Depends(get_db)
):
    db_server = await MCPServerService.get_server(db, server_id=server_id)
    if db_server is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Server not found")
    return db_server

@router.put("/{server_id}", response_model=MCPServerResponse)
async def update_mcp_server(
    server_id: UUID,
    server_update: MCPServerUpdate,
    db: AsyncSession = Depends(get_db),
):
    updated_server = await MCPServerService.update_server(
        db=db, server_id=server_id, server_update=server_update
    )
    if updated_server is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Server not found")
    return updated_server

@router.delete("/{server_id}", response_model=MCPServerResponse)
async def delete_mcp_server(
    server_id: UUID, db: AsyncSession = Depends(get_db)
):
    deleted_server = await MCPServerService.delete_server(db=db, server_id=server_id)
    if deleted_server is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Server not found")
    return deleted_server
