"""Tests for database CRUD operations."""
import pytest
from uuid import uuid4
from app.db.crud import JobRepository, BlogPostRepository
from app.models.database import JobStatus


@pytest.mark.asyncio
async def test_create_job(db_session):
    """Test creating a job."""
    job_id = uuid4()
    job = await JobRepository.create(
        db_session,
        job_id=job_id,
        channel_name="TestChannel",
        video_title="Test Video"
    )
    
    assert job.id == job_id
    assert job.channel_name == "TestChannel"
    assert job.video_title == "Test Video"
    assert job.status == JobStatus.QUEUED


@pytest.mark.asyncio
async def test_get_job_by_id(db_session):
    """Test getting a job by ID."""
    job_id = uuid4()
    await JobRepository.create(
        db_session,
        job_id=job_id,
        channel_name="TestChannel",
        video_title="Test Video"
    )
    
    job = await JobRepository.get_by_id(db_session, job_id)
    assert job is not None
    assert job.id == job_id


@pytest.mark.asyncio
async def test_update_job_status(db_session):
    """Test updating job status."""
    job_id = uuid4()
    await JobRepository.create(
        db_session,
        job_id=job_id,
        channel_name="TestChannel",
        video_title="Test Video"
    )
    
    updated_job = await JobRepository.update_status(
        db_session,
        job_id=job_id,
        status=JobStatus.PROCESSING,
        progress=50
    )
    
    assert updated_job.status == JobStatus.PROCESSING
    assert updated_job.progress == 50


@pytest.mark.asyncio
async def test_create_blog_post(db_session):
    """Test creating a blog post."""
    job_id = uuid4()
    await JobRepository.create(
        db_session,
        job_id=job_id,
        channel_name="TestChannel",
        video_title="Test Video"
    )
    
    blog_post = await BlogPostRepository.create(
        db_session,
        job_id=job_id,
        title="Test Blog",
        content="# Test Content",
        metadata={"test": "data"}
    )
    
    assert blog_post.job_id == job_id
    assert blog_post.title == "Test Blog"
    assert blog_post.metadata["test"] == "data"


@pytest.mark.asyncio
async def test_get_blog_post_by_job_id(db_session):
    """Test getting blog post by job ID."""
    job_id = uuid4()
    await JobRepository.create(
        db_session,
        job_id=job_id,
        channel_name="TestChannel",
        video_title="Test Video"
    )
    
    await BlogPostRepository.create(
        db_session,
        job_id=job_id,
        title="Test Blog",
        content="# Test Content",
        metadata={}
    )
    
    blog_post = await BlogPostRepository.get_by_job_id(db_session, job_id)
    assert blog_post is not None
    assert blog_post.job_id == job_id
