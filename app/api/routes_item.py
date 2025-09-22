# app/api/routes_item.py

from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.repositories.item import ItemRepository
from app.schemas.item import ItemCreate, ItemRead, ItemUpdate

router = APIRouter(prefix="/items", tags=["items"])


@router.post("/", response_model=ItemRead, status_code=status.HTTP_201_CREATED)
async def create_item(payload: ItemCreate, db: AsyncSession = Depends(get_db)):
    repo = ItemRepository(db)
    item = await repo.create(payload)
    return ItemRead.model_validate(item)


@router.get("/", response_model=List[ItemRead])
async def list_items(db: AsyncSession = Depends(get_db)):
    repo = ItemRepository(db)
    items = await repo.get_all()
    return [ItemRead.model_validate(item) for item in items]


@router.get("/{item_id}", response_model=ItemRead)
async def get_item(item_id: UUID, db: AsyncSession = Depends(get_db)):
    repo = ItemRepository(db)
    item = await repo.get_by_id(item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return ItemRead.model_validate(item)


@router.put("/{item_id}", response_model=ItemRead)
async def update_item(item_id: UUID, payload: ItemUpdate, db: AsyncSession = Depends(get_db)):
    repo = ItemRepository(db)
    item = await repo.get_by_id(item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    updated = await repo.update(item, payload)
    return ItemRead.model_validate(updated)


@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_item(item_id: UUID, db: AsyncSession = Depends(get_db)):
    repo = ItemRepository(db)
    item = await repo.get_by_id(item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    await repo.delete(item)
    return
