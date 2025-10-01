# app/api/routes_registration.py

from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.schemas.build_registration import BuildRegistrationCreate, BuildRegistration as BuildRegistrationSchema
from app.services.build_registration_services import BuildRegistrationService

router = APIRouter()

@router.post("/mcp-servers/{server_id}/register", response_model=BuildRegistrationSchema)
async def register_build(
    server_id: UUID,
    build_info: BuildRegistrationCreate,
    db: AsyncSession = Depends(get_db),
):
    """Register a build with an MCP server."""
    return await BuildRegistrationService.register_build(db, server_id, build_info)

@router.delete("/mcp-servers/{server_id}/register/{build_id}")
async def unregister_build(
    server_id: UUID,
    build_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Unregister a build from an MCP server."""
    await BuildRegistrationService.unregister_build(db, server_id, build_id)
    return {"ok": True}

@router.get("/mcp-servers/{server_id}/builds", response_model=list[BuildRegistrationSchema])
async def list_registered_builds(
    server_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """List all registered builds for an MCP server."""
    return await BuildRegistrationService.get_builds_for_server(db, server_id)
