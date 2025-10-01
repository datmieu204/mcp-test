# app/main.py

from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.api.routes_item import router as item_router
from app.api.routes_user import router as user_router
from app.api.routes_auth import router as auth_router
from app.api.routes_mcp_server import router as mcp_server_router
from app.api.routes_mcp_client import router as mcp_client_router
from app.api.routes_registration import router as registration_router
from app.api.routes_client import router as client_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Code chạy khi khởi động (startup)
    print("🚀 App is starting...")
    yield
    # Code chạy khi shutdown
    print("👋 App is shutting down...")

app = FastAPI(title="MCP Test API", lifespan=lifespan)

# Include routers
app.include_router(item_router)
app.include_router(user_router, prefix="/api/v1/users", tags=["users"])
app.include_router(auth_router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(client_router, prefix="/api/v1/clients", tags=["clients"])
app.include_router(mcp_server_router, prefix="/api/v1/mcp-servers", tags=["mcp-servers"])
app.include_router(mcp_client_router, prefix="/api/v1/mcp-clients", tags=["mcp-clients"])
app.include_router(registration_router, prefix="/api/v1", tags=["registrations"])
