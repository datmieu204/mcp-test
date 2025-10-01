# app/models/build_registration.py

from sqlalchemy import Column, String, ForeignKey, DateTime, func
from sqlalchemy.orm import relationship
from app.db.session import Base
import uuid
from sqlalchemy.dialects.postgresql import UUID

class BuildRegistration(Base):
    __tablename__ = "build_registrations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    build_id = Column(String, nullable=False, index=True)
    mcp_server_id = Column(UUID(as_uuid=True), ForeignKey("mcp_servers.id"), nullable=False)
    registered_at = Column(DateTime, server_default=func.now())
    
    server = relationship("MCPServer", back_populates="registrations")
