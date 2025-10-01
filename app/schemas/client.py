# app/schemas/client.py

from pydantic import BaseModel, Field
from typing import Optional
from uuid import UUID
from datetime import datetime


class ClientBase(BaseModel):
    client_name: str = Field(..., min_length=1, max_length=100, description="Human-readable client name")
    description: Optional[str] = Field(None, description="Description of the client application")
    rate_limit: Optional[str] = Field("1000/hour", description="Rate limit in format 'count/period'")


class ClientCreate(ClientBase):
    """Schema for creating a new client"""
    pass


class ClientUpdate(BaseModel):
    """Schema for updating an existing client"""
    client_name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    is_active: Optional[bool] = None
    rate_limit: Optional[str] = None


class ClientResponse(ClientBase):
    """Schema for client response (without sensitive data)"""
    id: UUID
    client_id: str
    is_active: bool
    created_at: datetime
    last_accessed: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class ClientWithApiKey(ClientResponse):
    """Schema for client response with API key (only shown once during creation)"""
    api_key: str
    
    class Config:
        from_attributes = True


class ClientAuth(BaseModel):
    """Schema for client authentication"""
    client_id: str = Field(..., description="Client ID")
    api_key: str = Field(..., description="Client API Key")


class ClientToken(BaseModel):
    """Schema for client JWT token response"""
    access_token: str
    token_type: str = "bearer"
    expires_in: int = 3600  # seconds
