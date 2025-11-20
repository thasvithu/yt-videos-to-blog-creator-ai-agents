"""Pydantic schemas for API requests and responses."""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field


# Request Schemas
class GenerateRequest(BaseModel):
    """Request to generate a blog post."""
    channel_name: str = Field(..., min_length=1, max_length=255, description="YouTube channel name or handle")
    video_title: str = Field(..., min_length=1, max_length=500, description="Video title to search for")
    email: Optional[EmailStr] = Field(None, description="Optional email to send the blog post")


class SendEmailRequest(BaseModel):
    """Request to send blog post via email."""
    job_id: str = Field(..., description="Job ID of the completed blog generation")
    email: EmailStr = Field(..., description="Email address to send the blog post")


# Response Schemas
class JobResponse(BaseModel):
    """Job creation response."""
    job_id: str
    status: str
    message: str


class JobStatusResponse(BaseModel):
    """Job status response."""
    job_id: str
    status: str
    progress: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    result: Optional["BlogPostResponse"] = None


class BlogPostResponse(BaseModel):
    """Blog post response."""
    title: str
    markdown_content: str
    html_content: Optional[str] = None
    video_metadata: Optional[dict] = None
    created_at: datetime


class EmailResponse(BaseModel):
    """Email sending response."""
    success: bool
    message: str


class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    version: str
    database: str
    redis: str
