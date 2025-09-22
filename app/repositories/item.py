# app/repositories/item.py

from typing import List, Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.item import Item
from app.schemas.item import ItemCreate, ItemUpdate


class ItemRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, data: ItemCreate) -> Item:
        try:
            item = Item(**data.model_dump())
            self.db.add(item)
            await self.db.commit()
            await self.db.refresh(item)
            return item
        except Exception as e:
            await self.db.rollback()
            raise e

    async def get_all(self) -> List[Item]:
        try:
            stmt = select(Item).order_by(Item.name)
            result = await self.db.execute(stmt)
            return result.scalars().all()
        except Exception as e:
            await self.db.rollback()
            raise e

    async def get_by_id(self, item_id: UUID) -> Optional[Item]:
        try:
            result = await self.db.execute(select(Item).where(Item.id == item_id))
            return result.scalar_one_or_none()
        except Exception as e:
            await self.db.rollback()
            raise e

    async def update(self, item: Item, data: ItemUpdate) -> Item:
        try:
            for k, v in data.model_dump(exclude_unset=True).items():
                setattr(item, k, v)
            self.db.add(item)
            await self.db.commit()
            await self.db.refresh(item)
            return item
        except Exception as e:
            await self.db.rollback()
            raise e

    async def delete(self, item: Item) -> None:
        try:
            await self.db.delete(item)
            await self.db.commit()
        except Exception as e:
            await self.db.rollback()
            raise e
