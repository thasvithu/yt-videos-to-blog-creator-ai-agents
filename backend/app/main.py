"""Main FastAPI application."""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.api import router as api_router
from app.db.session import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    # Startup
    print("🚀 Starting YouTube to Blog API...")
    print("📊 Initializing database...")
    await init_db()
    print("✅ Database initialized")
    yield
    # Shutdown
    print("👋 Shutting down...")


app = FastAPI(
    title="YouTube to Blog API",
    description="Generate beautiful blog posts from YouTube videos",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(api_router, prefix=settings.api_v1_prefix)


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "YouTube to Blog API",
        "version": "1.0.0",
        "docs": "/docs"
    }
