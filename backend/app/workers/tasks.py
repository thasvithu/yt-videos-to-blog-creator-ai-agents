"""Celery tasks for background processing."""
import asyncio
from uuid import UUID
from celery import Task
from app.workers.celery_app import celery_app
from app.services.youtube import YouTubeService
from app.services.llm_pipeline import LLMPipeline
from app.services.embeddings import EmbeddingService
from app.db.session import async_session_maker
from app.db.crud import JobRepository, BlogPostRepository
from app.models.database import JobStatus


def run_async(coro):
    """Helper to run async code in Celery task."""
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    
    try:
        return loop.run_until_complete(coro)
    finally:
        # Don't close the loop as it might be reused
        pass


async def async_generate_blog_post(task: Task, job_id: str, channel_name: str, video_title: str):
    """Async implementation of blog post generation."""
    import traceback
    
    youtube_service = YouTubeService()
    llm_pipeline = LLMPipeline()
    embedding_service = EmbeddingService()
    
    async with async_session_maker() as session:
        try:
            # Update: Starting
            task.update_state(state='PROGRESS', meta={'current': 0, 'total': 100, 'status': 'Starting...'})
            await JobRepository.update_status(session, UUID(job_id), JobStatus.RUNNING, 0)
            
            # Step 1: Search for video
            task.update_state(state='PROGRESS', meta={'current': 15, 'total': 100, 'status': 'Searching for video...'})
            
            print(f"[Task {job_id}] Searching for video: '{video_title}' on channel '{channel_name}'")
            video_data = youtube_service.search_video(channel_name, video_title)
            
            if not video_data:
                raise Exception(f"Could not find video '{video_title}' on channel '{channel_name}'. Make sure YOUTUBE_API_KEY is configured.")
            
            print(f"[Task {job_id}] Found video: {video_data.get('video_id')}")
            video_id = video_data['video_id']
            await JobRepository.update_video_id(session, UUID(job_id), video_id)
            
            # Step 2: Fetch transcript
            task.update_state(state='PROGRESS', meta={'current': 30, 'total': 100, 'status': 'Fetching transcript...'})
            transcript = youtube_service.get_transcript(video_id)
            
            if not transcript:
                raise Exception(f"Could not fetch transcript for video {video_id}")
            
            # Step 3: Get metadata
            task.update_state(state='PROGRESS', meta={'current': 45, 'total': 100, 'status': 'Extracting metadata...'})
            metadata = youtube_service.get_video_metadata(video_id)
            
            if not metadata:
                metadata = video_data  # Fallback to search data
            
            # Step 4: Generate blog with LangGraph
            task.update_state(state='PROGRESS', meta={'current': 60, 'total': 100, 'status': 'Generating blog post...'})
            
            blog_result = await llm_pipeline.generate_blog(
                video_id=video_id,
                video_title=video_data['title'],
                video_description=video_data['description'],
                channel_title=video_data['channel_title'],
                transcript=transcript,
                metadata=metadata
            )
            
            # Step 5: Save blog post
            task.update_state(state='PROGRESS', meta={'current': 80, 'total': 100, 'status': 'Saving blog post...'})
            
            blog_post = await BlogPostRepository.create(
                session,
                job_id=UUID(job_id),
                title=video_data['title'],
                content=blog_result['content'],
                video_metadata=blog_result['metadata']
            )
            
            # Step 6: Generate and save embeddings
            task.update_state(state='PROGRESS', meta={'current': 90, 'total': 100, 'status': 'Generating embeddings...'})
            
            await embedding_service.generate_and_store_embeddings(
                session,
                blog_post.id,
                blog_result['content']
            )
            
            # Step 7: Mark as completed
            task.update_state(state='PROGRESS', meta={'current': 100, 'total': 100, 'status': 'Completed!'})
            await JobRepository.update_status(session, UUID(job_id), JobStatus.COMPLETED, 100)
            
            return {
                'status': 'completed',
                'job_id': job_id,
                'blog_post_id': blog_post.id,
                'message': 'Blog post generated successfully'
            }
            
        except Exception as e:
            # Mark job as failed
            import traceback
            error_msg = f"{str(e)}\n{traceback.format_exc()}"
            print(f"[Task {job_id}] ERROR: {error_msg}")
            
            await JobRepository.update_status(
                session,
                UUID(job_id),
                JobStatus.FAILED,
                error=str(e)
            )
            raise


@celery_app.task(name="generate_blog_post", bind=True, autoretry_for=(Exception,), retry_kwargs={'max_retries': 0})
def generate_blog_post_task(self, job_id: str, channel_name: str, video_title: str, email: str = None):
    """
    Background task to generate a blog post from a YouTube video.
    
    Steps:
    1. Search for YouTube video
    2. Fetch video transcript
    3. Extract metadata
    4. Create embeddings
    5. Run LangGraph pipeline to generate blog post
    6. Save to database
    7. Send email if requested
    """
    import traceback
    try:
        result = run_async(async_generate_blog_post(self, job_id, channel_name, video_title))
        return result
        
    except Exception as e:
        error_msg = f"{str(e)}\n{traceback.format_exc()}"
        print(f"Task failed: {error_msg}")
        self.update_state(state='FAILURE', meta={'error': str(e), 'exc_type': type(e).__name__})
        raise
