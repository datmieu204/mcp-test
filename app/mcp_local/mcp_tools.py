# app/mcp/mcp_tools.py

from sqlalchemy import select
from typing import Optional, Dict, Any
from app.db.session import get_db
from app.models.item import Item
from fastmcp import FastMCP

mcp = FastMCP("item-mcp")


@mcp.tool()
async def list_items() -> list[dict]:
    """
    Get all items from the database.
    """
    async for session in get_db():
        result = await session.execute(select(Item))
        items = result.scalars().all()
        return [
            {
                "id": str(item.id),
                "name": item.name,
                "description": item.description,
                "quantity": item.quantity,
                "type": item.item_type,
                "metadata": item.item_metadata,
            }
            for item in items
        ]


@mcp.tool()
async def add_item(
    name: str,
    description: Optional[str] = None,
    quantity: int = 0,
    item_type: str = "TypeA",
    metadata: Optional[Dict[str, Any]] = None,
) -> dict:
    """
    Add a new item to the database.
    """
    async for session in get_db():
        item = Item(
            name=name,
            description=description,
            quantity=quantity,
            item_type=item_type,
            item_metadata=metadata or {},
        )
        session.add(item)
        await session.commit()
        await session.refresh(item)

        return {
            "status": "created",
            "id": str(item.id),
            "name": item.name,
            "type": item.item_type,
        }


@mcp.tool()
async def update_item(
    item_id: str,
    name: Optional[str] = None,
    description: Optional[str] = None,
    quantity: Optional[int] = None,
    item_type: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None,
) -> dict:
    """
    Update an existing item in the database.
    """
    async for session in get_db():
        result = await session.execute(select(Item).where(Item.id == item_id))
        item = result.scalar_one_or_none()

        if not item:
            return {"status": "error", "message": "Item not found"}

        if name is not None:
            item.name = name
        if description is not None:
            item.description = description
        if quantity is not None:
            item.quantity = quantity
        if item_type is not None:
            item.item_type = item_type
        if metadata is not None:
            item.item_metadata = metadata

        await session.commit()
        await session.refresh(item)

        return {
            "status": "updated",
            "id": str(item.id),
            "name": item.name,
            "type": item.item_type,
            "quantity": item.quantity,
        }


@mcp.tool()
async def delete_item(item_id: str) -> dict:
    """
    Delete an item from the database.
    """
    async for session in get_db():
        result = await session.execute(select(Item).where(Item.id == item_id))
        item = result.scalar_one_or_none()

        if not item:
            return {"status": "error", "message": "Item not found"}

        await session.delete(item)
        await session.commit()

        return {"status": "deleted", "id": item_id}


@mcp.tool()
async def search_items(
    name: Optional[str] = None,
    item_type: Optional[str] = None,
    min_quantity: Optional[int] = None,
) -> list[dict]:
    """
    Search items based on various criteria.
    """
    async for session in get_db():
        query = select(Item)

        if name:
            query = query.where(Item.name.ilike(f"%{name}%"))
        if item_type:
            query = query.where(Item.item_type == item_type)
        if min_quantity is not None:
            query = query.where(Item.quantity >= min_quantity)

        result = await session.execute(query)
        items = result.scalars().all()

        return [
            {
                "id": str(item.id),
                "name": item.name,
                "description": item.description,
                "quantity": item.quantity,
                "type": item.item_type,
                "metadata": item.item_metadata,
            }
            for item in items
        ]