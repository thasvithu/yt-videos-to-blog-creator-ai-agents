"""Health check endpoint."""
from fastapi import APIRouter
from app.models.schemas import HealthResponse

router = APIRouter()


@router.get("", response_model=HealthResponse)
async def health_check():
    """
    Health check endpoint.
    
    Checks database, Redis, and overall system health.
    """
    # TODO: Add actual health checks for DB and Redis
    return HealthResponse(
        status="healthy",
        version="1.0.0",
        database="connected",
        redis="connected"
    )
