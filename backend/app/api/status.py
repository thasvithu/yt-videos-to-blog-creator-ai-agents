"""Job status endpoint."""
from uuid import UUID
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.schemas import JobStatusResponse, BlogPostResponse
from app.models.database import JobStatus
from app.db.session import get_db
from app.db.crud import JobRepository, BlogPostRepository

router = APIRouter()


@router.get("/{job_id}", response_model=JobStatusResponse)
async def get_job_status(job_id: str, session: AsyncSession = Depends(get_db)):
    """
    Get the status of a blog generation job.
    
    Returns job progress and result if completed.
    """
    try:
        # Parse UUID
        job_uuid = UUID(job_id)
        
        # Fetch job from database
        job = await JobRepository.get_by_id(session, job_uuid)
        
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")
        
        # Base response
        response = JobStatusResponse(
            job_id=str(job.id),
            status=job.status,
            progress=job.progress,
            created_at=job.created_at.isoformat(),
            message=f"Job {job.status}"
        )
        
        # If completed, fetch blog post
        if job.status == JobStatus.COMPLETED.value:
            blog_post = await BlogPostRepository.get_by_job_id(session, job_uuid)
            
            if blog_post:
                response.blog_post = BlogPostResponse(
                    id=blog_post.id,
                    title=blog_post.title,
                    content=blog_post.content,
                    video_metadata=blog_post.video_metadata,
                    created_at=blog_post.created_at.isoformat()
                )
        
        # If failed, include error
        if job.status == JobStatus.FAILED and job.error_message:
            response.message = job.error_message
        
        return response
        
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid job ID format")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get job status: {str(e)}")
