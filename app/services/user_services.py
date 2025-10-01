# app/services/user_services.py

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.user import User
from app.schemas.user import UserCreate
from app.core.security import get_password_hash

class UserService:
    @staticmethod
    async def get_user_by_username(db: AsyncSession, username: str):
        result = await db.execute(select(User).filter(User.username == username))
        return result.scalars().first()

    @staticmethod
    async def create_user(db: AsyncSession, user: UserCreate):
        hashed_password = get_password_hash(user.password)
        db_user = User(
            username=user.username,
            email=user.email,
            hashed_password=hashed_password
        )
        db.add(db_user)
        await db.commit()
        await db.refresh(db_user)
        return db_user
