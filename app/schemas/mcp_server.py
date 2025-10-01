# app/schemas/mcp_server.py

from pydantic import BaseModel, Field, HttpUrl
from typing import Optional, Dict, Any
from uuid import UUID
from datetime import datetime

class MCPServerBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    server_url: HttpUrl
    api_key: Optional[str] = None
    transport_type: str = "HTTP"
    is_enabled: bool = True
    metadata_: Optional[Dict[str, Any]] = Field(None, alias="metadata")

class MCPServerCreate(MCPServerBase):
    pass

class MCPServerUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    server_url: Optional[HttpUrl] = None
    api_key: Optional[str] = None
    transport_type: Optional[str] = None
    is_enabled: Optional[bool] = None
    metadata_: Optional[Dict[str, Any]] = Field(None, alias="metadata")

class MCPServerInDB(MCPServerBase):
    id: UUID
    is_deleted: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    last_health_check: Optional[datetime] = None
    status: str

    class Config:
        from_attributes = True
        validate_by_name = True

class MCPServerResponse(BaseModel):
    id: UUID
    name: str
    description: Optional[str]
    server_url: HttpUrl
    is_enabled: bool
    status: str
    metadata: Optional[Dict[str, Any]] = Field(None, alias="metadata_")

    class Config:
        from_attributes = True
        validate_by_name = True
