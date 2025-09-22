# app/models/item.py

from sqlalchemy import Column, String, Integer, DateTime, JSON
from sqlalchemy.dialects.postgresql import UUID, ENUM
from datetime import datetime
from uuid import uuid4
from enum import Enum
from app.db.session import Base


class ItemType(str, Enum):
    TYPE_A = "TypeA"
    TYPE_B = "TypeB"
    TYPE_C = "TypeC"


class Item(Base):
    __tablename__ = "items"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    name = Column(String, nullable=False)
    description = Column(String)
    quantity = Column(Integer, default=0)

    item_type = Column(ENUM(ItemType, name="item_type"), nullable=False)

    item_metadata = Column(JSON, default=dict)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
