# app/services/build_registration_services.py

from uuid import UUID
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.build_registration import BuildRegistration
from app.schemas.build_registration import BuildRegistrationCreate, BuildRegistration as BuildRegistrationSchema

class BuildRegistrationService:
    @staticmethod
    async def register_build(db: AsyncSession, server_id: UUID, build_info: BuildRegistrationCreate) -> BuildRegistration:
        """Registers a new build for a given MCP server."""
        registration = BuildRegistration(
            mcp_server_id=server_id,
            build_id=build_info.build_id
        )
        db.add(registration)
        await db.commit()
        await db.refresh(registration)
        return registration

    @staticmethod
    async def unregister_build(db: AsyncSession, server_id: UUID, build_id: str) -> None:
        """Unregisters a build from an MCP server."""
        result = await db.execute(
            select(BuildRegistration).filter_by(mcp_server_id=server_id, build_id=build_id)
        )
        registration = result.scalars().first()
        if not registration:
            raise HTTPException(status_code=404, detail="Build registration not found")
        
        await db.delete(registration)
        await db.commit()

    @staticmethod
    async def get_builds_for_server(db: AsyncSession, server_id: UUID) -> list[BuildRegistration]:
        """Lists all registered builds for a given MCP server."""
        result = await db.execute(
            select(BuildRegistration).filter_by(mcp_server_id=server_id)
        )
        return result.scalars().all()
