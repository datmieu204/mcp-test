# app/schemas/item.py

from pydantic import BaseModel
from typing import Optional
from uuid import UUID
from datetime import datetime
from app.models.item import ItemType


class ItemBase(BaseModel):
    name: str
    description: Optional[str] = None
    quantity: int = 0
    item_type: ItemType
    item_metadata: Optional[dict] = None


class ItemCreate(ItemBase):
    pass


class ItemUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    quantity: Optional[int] = None
    item_type: Optional[ItemType] = None
    item_metadata: Optional[dict] = None


class ItemReadLite(BaseModel):
    id: UUID
    name: str
    item_type: ItemType

    class Config:
        from_attributes = True
        populate_by_name = True


class ItemRead(ItemBase):
    id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
        populate_by_name = True
        orm_mode = True
        allow_population_by_field_name = True
