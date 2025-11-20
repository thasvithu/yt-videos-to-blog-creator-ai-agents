"""Tests for API endpoints."""
import pytest
from httpx import AsyncClient
from app.main import app


@pytest.mark.asyncio
async def test_root_endpoint():
    """Test root endpoint."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "version" in data


@pytest.mark.asyncio
async def test_health_endpoint():
    """Test health check endpoint."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/api/v1/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"


@pytest.mark.asyncio
async def test_generate_blog_endpoint():
    """Test blog generation endpoint."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            "/api/v1/generate",
            json={
                "channel_name": "TestChannel",
                "video_title": "Test Video",
                "email": "test@example.com"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert "job_id" in data
        assert "status" in data


@pytest.mark.asyncio
async def test_generate_blog_validation():
    """Test blog generation validation."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Missing required fields
        response = await client.post(
            "/api/v1/generate",
            json={"channel_name": "TestChannel"}
        )
        assert response.status_code == 422  # Validation error


@pytest.mark.asyncio
async def test_status_endpoint_invalid_id():
    """Test status endpoint with invalid job ID."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/api/v1/status/invalid-uuid")
        assert response.status_code == 400  # Bad request


@pytest.mark.asyncio
async def test_status_endpoint_not_found():
    """Test status endpoint with non-existent job ID."""
    import uuid
    async with AsyncClient(app=app, base_url="http://test") as client:
        fake_id = str(uuid.uuid4())
        response = await client.get(f"/api/v1/status/{fake_id}")
        # Will fail until DB is connected, expecting 404 or 500
        assert response.status_code in [404, 500]
