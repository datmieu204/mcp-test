# app/services/mcp_server_services.py

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.mcp_server import MCPServer
from app.schemas.mcp_server import MCPServerCreate, MCPServerUpdate
from uuid import UUID
from typing import List, Optional

class MCPServerService:
    @staticmethod
    async def create_server(db: AsyncSession, server: MCPServerCreate) -> MCPServer:
        server_data = server.model_dump()
        if 'server_url' in server_data and server_data['server_url'] is not None:
            server_data['server_url'] = str(server_data['server_url'])
        db_server = MCPServer(**server_data)
        db.add(db_server)
        await db.commit()
        await db.refresh(db_server)
        return db_server

    @staticmethod
    async def get_server(db: AsyncSession, server_id: UUID) -> Optional[MCPServer]:
        result = await db.execute(select(MCPServer).filter(MCPServer.id == server_id, MCPServer.is_deleted == False))
        return result.scalar_one_or_none()

    @staticmethod
    async def get_server_by_name(db: AsyncSession, name: str) -> Optional[MCPServer]:
        result = await db.execute(select(MCPServer).filter(MCPServer.name == name, MCPServer.is_deleted == False))
        return result.scalar_one_or_none()

    @staticmethod
    async def get_all_servers(db: AsyncSession, skip: int = 0, limit: int = 100) -> List[MCPServer]:
        result = await db.execute(select(MCPServer).filter(MCPServer.is_deleted == False).offset(skip).limit(limit))
        return result.scalars().all()

    @staticmethod
    async def update_server(db: AsyncSession, server_id: UUID, server_update: MCPServerUpdate) -> Optional[MCPServer]:
        db_server = await MCPServerService.get_server(db, server_id)
        if db_server:
            update_data = server_update.model_dump(exclude_unset=True)
            for key, value in update_data.items():
                setattr(db_server, key, value)
            await db.commit()
            await db.refresh(db_server)
        return db_server

    @staticmethod
    async def delete_server(db: AsyncSession, server_id: UUID) -> Optional[MCPServer]:
        db_server = await MCPServerService.get_server(db, server_id)
        if db_server:
            db_server.is_deleted = True
            await db.commit()
            await db.refresh(db_server)
        return db_server
