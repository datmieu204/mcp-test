# app/main.py

from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.api.routes_item import router as item_router

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
