"""Database CRUD operations."""
from typing import Optional, List
from uuid import UUID
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.database import Job, BlogPost, Embedding, JobStatus


class JobRepository:
    """CRUD operations for Job model."""
    
    @staticmethod
    async def create(session: AsyncSession, job_id: UUID, channel_name: str, video_title: str) -> Job:
        """Create a new job."""
        job = Job(
            id=job_id,
            channel_name=channel_name,
            video_title=video_title,
            status=JobStatus.QUEUED
        )
        session.add(job)
        await session.commit()
        await session.refresh(job)
        return job
    
    @staticmethod
    async def get_by_id(session: AsyncSession, job_id: UUID) -> Optional[Job]:
        """Get job by ID."""
        result = await session.execute(
            select(Job).where(Job.id == job_id)
        )
        return result.scalar_one_or_none()
    
    @staticmethod
    async def update_status(
        session: AsyncSession,
        job_id: UUID,
        status: JobStatus,
        progress: Optional[int] = None,
        error: Optional[str] = None
    ) -> Optional[Job]:
        """Update job status and progress."""
        stmt = (
            update(Job)
            .where(Job.id == job_id)
            .values(status=status)
        )
        
        if progress is not None:
            stmt = stmt.values(progress=progress)
        if error is not None:
            stmt = stmt.values(error_message=error)
        
        await session.execute(stmt)
        await session.commit()
        
        return await JobRepository.get_by_id(session, job_id)
    
    @staticmethod
    async def update_video_id(session: AsyncSession, job_id: UUID, video_id: str) -> None:
        """Update job with video ID."""
        await session.execute(
            update(Job)
            .where(Job.id == job_id)
            .values(video_id=video_id)
        )
        await session.commit()


class BlogPostRepository:
    """CRUD operations for BlogPost model."""
    
    @staticmethod
    async def create(
        session: AsyncSession,
        job_id: UUID,
        title: str,
        content: str,
        video_metadata: dict
    ) -> BlogPost:
        """Create a new blog post."""
        blog_post = BlogPost(
            job_id=job_id,
            title=title,
            content=content,
            video_metadata=video_metadata
        )
        session.add(blog_post)
        await session.flush()
        return blog_post
    
    @staticmethod
    async def get_by_job_id(session: AsyncSession, job_id: UUID) -> Optional[BlogPost]:
        """Get blog post by job ID."""
        result = await session.execute(
            select(BlogPost).where(BlogPost.job_id == job_id)
        )
        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_by_id(session: AsyncSession, blog_id: int) -> Optional[BlogPost]:
        """Get blog post by ID."""
        result = await session.execute(
            select(BlogPost).where(BlogPost.id == blog_id)
        )
        return result.scalar_one_or_none()


class EmbeddingRepository:
    """CRUD operations for Embedding model."""
    
    @staticmethod
    async def create(
        session: AsyncSession,
        blog_post_id: int,
        chunk_text: str,
        embedding_vector: List[float],
        chunk_index: int
    ) -> Embedding:
        """Create a new embedding."""
        embedding = Embedding(
            blog_post_id=blog_post_id,
            chunk_text=chunk_text,
            embedding=embedding_vector,
            chunk_index=chunk_index
        )
        session.add(embedding)
        await session.flush()
        return embedding
    
    @staticmethod
    async def get_by_blog_post(session: AsyncSession, blog_post_id: int) -> List[Embedding]:
        """Get all embeddings for a blog post."""
        result = await session.execute(
            select(Embedding)
            .where(Embedding.blog_post_id == blog_post_id)
            .order_by(Embedding.chunk_index)
        )
        return list(result.scalars().all())
