# app/api/dependencies.py

from fastapi import Depends, HTTPException, status, Header
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from jose import JWTError, jwt
from typing import Optional

from app.core.config import settings
from app.schemas.user import TokenData
from app.services.user_services import UserService
from app.services.client_services import ClientService
from app.db.session import get_db

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/token")

async def get_current_user(db: AsyncSession = Depends(get_db), token: str = Depends(oauth2_scheme)):
    """Dependency for user authentication (existing users)"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    
    user = await UserService.get_user_by_username(db, username=token_data.username)
    if user is None:
        raise credentials_exception
    
    return user


async def get_current_client(
    db: AsyncSession = Depends(get_db),
    x_client_id: Optional[str] = Header(None, description="Client ID"),
    x_api_key: Optional[str] = Header(None, description="Client API Key")
):
    """
    Dependency for client authentication (Layer 1)
    Clients authenticate using X-Client-ID and X-API-Key headers
    """
    if not x_client_id or not x_api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing client credentials (X-Client-ID and X-API-Key headers required)",
            headers={"WWW-Authenticate": "ApiKey"},
        )
    
    client = await ClientService.authenticate_client(db, x_client_id, x_api_key)
    
    if not client:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid client credentials",
            headers={"WWW-Authenticate": "ApiKey"},
        )
    
    return client


async def verify_mcp_server_access(
    server_id: str,
    db: AsyncSession = Depends(get_db),
    client = Depends(get_current_client)
):
    """
    Dependency for verifying client has access to MCP server (Layer 2)
    This can be extended to check permissions, subscriptions, etc.
    """
    # For now, we just verify the client is authenticated
    # You can add more logic here to check if client has access to specific server
    return client

