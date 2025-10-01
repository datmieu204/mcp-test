# app/models/mcp_server.py

from sqlalchemy import (
    Column,
    String,
    Integer,
    Boolean,
    DateTime,
    JSON,
    func,
)
from sqlalchemy.orm import relationship
from app.db.session import Base
from sqlalchemy.dialects.postgresql import UUID
from app.models.build_registration import BuildRegistration
import uuid


class MCPServer(Base):
    __tablename__ = "mcp_servers"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False, unique=True, index=True)
    description = Column(String, nullable=True)
    server_url = Column(String, nullable=False)
    api_key = Column(String, nullable=True)
    transport_type = Column(String, default="HTTP")
    is_enabled = Column(Boolean, default=True)
    is_deleted = Column(Boolean, default=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    last_health_check = Column(DateTime, nullable=True)
    status = Column(String, default="UNKNOWN")
    metadata_ = Column("metadata", JSON, nullable=True)

    registrations = relationship("BuildRegistration", back_populates="server")
