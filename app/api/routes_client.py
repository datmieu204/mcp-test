# app/api/routes_client.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from uuid import UUID

from app.db.session import get_db
from app.schemas.client import (
    ClientCreate,
    ClientUpdate,
    ClientResponse,
    ClientWithApiKey,
)
from app.services.client_services import ClientService
from app.api.dependencies import get_current_user  # Admin authentication

router = APIRouter()


@router.post("/", response_model=ClientWithApiKey, status_code=status.HTTP_201_CREATED)
async def create_client(
    client_data: ClientCreate,
    db: AsyncSession = Depends(get_db),
    # current_user = Depends(get_current_user)  # Uncomment to require admin auth
):
    """
    Create a new client/build registration.
    Returns the client credentials including API key (only shown once).
    
    **Important**: Save the API key securely as it won't be shown again!
    """
    client = await ClientService.create_client(db, client_data)
    return client


@router.get("/", response_model=List[ClientResponse])
async def list_clients(
    skip: int = 0,
    limit: int = 100,
    include_inactive: bool = False,
    db: AsyncSession = Depends(get_db),
    # current_user = Depends(get_current_user)  # Uncomment to require admin auth
):
    """
    List all registered clients with pagination.
    """
    clients = await ClientService.get_all_clients(
        db, skip=skip, limit=limit, include_inactive=include_inactive
    )
    return clients


@router.get("/{client_uuid}", response_model=ClientResponse)
async def get_client(
    client_uuid: UUID,
    db: AsyncSession = Depends(get_db),
    # current_user = Depends(get_current_user)  # Uncomment to require admin auth
):
    """
    Get details of a specific client by UUID.
    """
    client = await ClientService.get_client_by_uuid(db, client_uuid)
    if not client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Client not found"
        )
    return client


@router.put("/{client_uuid}", response_model=ClientResponse)
async def update_client(
    client_uuid: UUID,
    client_update: ClientUpdate,
    db: AsyncSession = Depends(get_db),
    # current_user = Depends(get_current_user)  # Uncomment to require admin auth
):
    """
    Update client information (name, description, status, etc.).
    """
    client = await ClientService.update_client(db, client_uuid, client_update)
    if not client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Client not found"
        )
    return client


@router.post("/{client_uuid}/rotate-key", response_model=ClientWithApiKey)
async def rotate_api_key(
    client_uuid: UUID,
    db: AsyncSession = Depends(get_db),
    # current_user = Depends(get_current_user)  # Uncomment to require admin auth
):
    """
    Rotate (regenerate) the API key for a client.
    Returns the new API key (save it securely as it won't be shown again!).
    
    **Warning**: The old API key will be immediately invalidated.
    """
    client = await ClientService.rotate_api_key(db, client_uuid)
    if not client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Client not found"
        )
    return client


@router.delete("/{client_uuid}", response_model=ClientResponse)
async def delete_client(
    client_uuid: UUID,
    db: AsyncSession = Depends(get_db),
    # current_user = Depends(get_current_user)  # Uncomment to require admin auth
):
    """
    Soft delete a client (marks as deleted and inactive).
    """
    client = await ClientService.delete_client(db, client_uuid)
    if not client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Client not found"
        )
    return client
