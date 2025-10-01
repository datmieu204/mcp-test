# app/services/client_services.py

import secrets
from datetime import datetime
from typing import Optional, List
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fastapi import HTTPException, status

from app.models.client import Client
from app.schemas.client import ClientCreate, ClientUpdate


class ClientService:
    """Service for managing client authentication and authorization"""
    
    @staticmethod
    def generate_client_id(client_name: str) -> str:
        """Generate a unique client ID based on client name"""
        # Format: clientname_randomstring
        random_suffix = secrets.token_urlsafe(8)
        safe_name = client_name.lower().replace(" ", "_").replace("-", "_")
        return f"{safe_name}_{random_suffix}"
    
    @staticmethod
    def generate_api_key() -> str:
        """Generate a secure API key"""
        return f"mcp_{secrets.token_urlsafe(32)}"
    
    @staticmethod
    async def create_client(db: AsyncSession, client_data: ClientCreate) -> Client:
        """Create a new client with generated credentials"""
        # Check if client name already exists
        existing = await ClientService.get_client_by_name(db, client_data.client_name)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Client with this name already exists"
            )
        
        # Generate credentials
        client_id = ClientService.generate_client_id(client_data.client_name)
        api_key = ClientService.generate_api_key()
        
        # Create client
        db_client = Client(
            client_name=client_data.client_name,
            client_id=client_id,
            api_key=api_key,
            description=client_data.description,
            rate_limit=client_data.rate_limit or "1000/hour"
        )
        
        db.add(db_client)
        await db.commit()
        await db.refresh(db_client)
        
        return db_client
    
    @staticmethod
    async def get_client_by_id(db: AsyncSession, client_id: str) -> Optional[Client]:
        """Get client by client_id"""
        result = await db.execute(
            select(Client).filter(
                Client.client_id == client_id,
                Client.is_deleted == False
            )
        )
        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_client_by_name(db: AsyncSession, client_name: str) -> Optional[Client]:
        """Get client by name"""
        result = await db.execute(
            select(Client).filter(
                Client.client_name == client_name,
                Client.is_deleted == False
            )
        )
        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_client_by_uuid(db: AsyncSession, uuid: UUID) -> Optional[Client]:
        """Get client by UUID"""
        result = await db.execute(
            select(Client).filter(
                Client.id == uuid,
                Client.is_deleted == False
            )
        )
        return result.scalar_one_or_none()
    
    @staticmethod
    async def authenticate_client(db: AsyncSession, client_id: str, api_key: str) -> Optional[Client]:
        """Authenticate a client using client_id and api_key"""
        client = await ClientService.get_client_by_id(db, client_id)
        
        if not client:
            return None
        
        if not client.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Client is inactive"
            )
        
        # Verify API key
        if client.api_key != api_key:
            return None
        
        # Update last accessed time
        client.last_accessed = datetime.utcnow()
        await db.commit()
        
        return client
    
    @staticmethod
    async def get_all_clients(
        db: AsyncSession, 
        skip: int = 0, 
        limit: int = 100,
        include_inactive: bool = False
    ) -> List[Client]:
        """Get all clients with pagination"""
        query = select(Client).filter(Client.is_deleted == False)
        
        if not include_inactive:
            query = query.filter(Client.is_active == True)
        
        query = query.offset(skip).limit(limit)
        result = await db.execute(query)
        return result.scalars().all()
    
    @staticmethod
    async def update_client(
        db: AsyncSession, 
        uuid: UUID, 
        client_update: ClientUpdate
    ) -> Optional[Client]:
        """Update client information"""
        client = await ClientService.get_client_by_uuid(db, uuid)
        
        if not client:
            return None
        
        update_data = client_update.model_dump(exclude_unset=True)
        
        for key, value in update_data.items():
            setattr(client, key, value)
        
        await db.commit()
        await db.refresh(client)
        
        return client
    
    @staticmethod
    async def rotate_api_key(db: AsyncSession, uuid: UUID) -> Optional[Client]:
        """Rotate (regenerate) API key for a client"""
        client = await ClientService.get_client_by_uuid(db, uuid)
        
        if not client:
            return None
        
        # Generate new API key
        client.api_key = ClientService.generate_api_key()
        
        await db.commit()
        await db.refresh(client)
        
        return client
    
    @staticmethod
    async def delete_client(db: AsyncSession, uuid: UUID) -> Optional[Client]:
        """Soft delete a client"""
        client = await ClientService.get_client_by_uuid(db, uuid)
        
        if not client:
            return None
        
        client.is_deleted = True
        client.is_active = False
        
        await db.commit()
        await db.refresh(client)
        
        return client
