"""Database models."""
from datetime import datetime
from enum import Enum
from typing import Optional
from uuid import UUID
from sqlalchemy import Column, String, Text, DateTime, Integer, JSON, ForeignKey
from sqlalchemy.dialects.postgresql import UUID as PostgreSQLUUID
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy.sql import func
from pgvector.sqlalchemy import Vector


Base = declarative_base()


class JobStatus(str, Enum):
    """Job status enumeration."""
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class Job(Base):
    """Job tracking model."""
    __tablename__ = "jobs"
    
    id = Column(PostgreSQLUUID(as_uuid=True), primary_key=True)
    channel_name = Column(String, nullable=False)
    video_title = Column(String, nullable=False)
    video_id = Column(String, nullable=True)
    email = Column(String, nullable=True)
    status = Column(String, default=JobStatus.QUEUED.value)
    progress = Column(Integer, default=0)
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationship
    blog_post = relationship("BlogPost", back_populates="job", uselist=False)
    embeddings = relationship("Embedding", back_populates="job")


class BlogPost(Base):
    """Generated blog post model."""
    __tablename__ = "blog_posts"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    job_id = Column(String, ForeignKey("jobs.id"), unique=True, nullable=False)
    title = Column(String, nullable=False)
    markdown_content = Column(Text, nullable=False)
    html_content = Column(Text, nullable=True)
    video_metadata = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationship
    job = relationship("Job", back_populates="blog_post")


class Embedding(Base):
    """Vector embeddings for RAG."""
    __tablename__ = "embeddings"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    job_id = Column(String, ForeignKey("jobs.id"), nullable=False)
    content = Column(Text, nullable=False)
    vector = Column(Vector(1536))  # OpenAI text-embedding-3 dimension
    chunk_metadata = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationship
    job = relationship("Job", back_populates="embeddings")
