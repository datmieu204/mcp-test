# app/models/client.py

from sqlalchemy import Column, String, Boolean, DateTime, func
from sqlalchemy.dialects.postgresql import UUID
from app.db.session import Base
import uuid


class Client(Base):
    """
    Client/Build model - represents applications/builds that can connect to this service
    and use MCP servers through it.
    """
    __tablename__ = "clients"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    client_name = Column(String, nullable=False, unique=True, index=True)
    client_id = Column(String, nullable=False, unique=True, index=True)  # Public client identifier
    api_key = Column(String, nullable=False, unique=True)  # Secret key for authentication
    description = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    is_deleted = Column(Boolean, default=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    last_accessed = Column(DateTime, nullable=True)
    
    # Rate limiting fields (optional)
    rate_limit = Column(String, default="1000/hour")  # Format: "count/period"
    
    def __repr__(self):
        return f"<Client {self.client_name} ({self.client_id})>"
