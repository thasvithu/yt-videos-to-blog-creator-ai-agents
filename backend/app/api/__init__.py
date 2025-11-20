"""API routes."""
from fastapi import APIRouter
from app.api import generate, status, health, email

router = APIRouter()

# Include sub-routers
router.include_router(generate.router, prefix="/generate", tags=["generate"])
router.include_router(status.router, prefix="/status", tags=["status"])
router.include_router(health.router, prefix="/health", tags=["health"])
router.include_router(email.router, prefix="/email", tags=["email"])
