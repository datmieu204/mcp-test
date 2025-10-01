# app/schemas/build_registration.py

from pydantic import BaseModel, Field
from uuid import UUID
from datetime import datetime

class BuildRegistrationBase(BaseModel):
    build_id: str = Field(..., description="The unique identifier for the build")

class BuildRegistrationCreate(BuildRegistrationBase):
    pass

class BuildRegistration(BuildRegistrationBase):
    id: UUID
    mcp_server_id: UUID
    registered_at: datetime

    class Config:
        from_attributes = True
