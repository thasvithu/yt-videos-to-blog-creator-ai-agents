"""Generate blog post endpoint."""
import uuid
import traceback
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.schemas import GenerateRequest, JobResponse
from app.models.database import JobStatus
from app.workers.tasks import generate_blog_post_task
from app.db.session import get_db
from app.db.crud import JobRepository

router = APIRouter()


@router.post("", response_model=JobResponse)
async def generate_blog_post(request: GenerateRequest, session: AsyncSession = Depends(get_db)):
    """
    Generate a blog post from a YouTube video.
    
    Creates a background job to process the video and generate the blog post.
    """
    try:
        # Create unique job ID
        job_id = uuid.uuid4()
        
        # Save job to database
        await JobRepository.create(
            session,
            job_id=job_id,
            channel_name=request.channel_name,
            video_title=request.video_title
        )
        
        # Enqueue Celery task
        generate_blog_post_task.delay(
            job_id=str(job_id),
            channel_name=request.channel_name,
            video_title=request.video_title,
            email=request.email
        )
        
        return JobResponse(
            job_id=str(job_id),
            status=JobStatus.QUEUED.value,
            message="Blog post generation started. Check status using the job_id."
        )
        
    except Exception as e:
        print(f"❌ Error creating job: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Failed to create job: {str(e)}")
