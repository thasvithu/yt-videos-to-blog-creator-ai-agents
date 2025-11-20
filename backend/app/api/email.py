"""Email delivery endpoints."""
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, EmailStr
from app.services.email import EmailService
from app.db.session import get_db
from app.db.crud import BlogPostRepository

router = APIRouter()


class EmailRequest(BaseModel):
    """Request to email a blog post."""
    blog_post_id: int
    email: EmailStr


@router.post("/send-email")
async def send_blog_email(
    request: EmailRequest,
    session: AsyncSession = Depends(get_db)
):
    """
    Send a blog post via email.
    
    Args:
        request: Blog post ID and recipient email
        session: Database session
        
    Returns:
        Success/failure message
    """
    try:
        # Fetch blog post
        blog_post = await BlogPostRepository.get_by_id(session, request.blog_post_id)
        
        if not blog_post:
            raise HTTPException(status_code=404, detail="Blog post not found")
        
        # Get metadata
        video_metadata = blog_post.video_metadata or {}
        video_title = video_metadata.get('video_title', 'Unknown Video')
        channel_title = video_metadata.get('channel_title', 'Unknown Channel')
        
        # Send email
        email_service = EmailService()
        success = email_service.send_blog_post_email(
            to_email=request.email,
            blog_title=blog_post.title,
            blog_content=blog_post.content,
            video_title=video_title,
            channel_name=channel_title
        )
        
        if success:
            return {"message": f"Blog post sent successfully to {request.email}"}
        else:
            raise HTTPException(status_code=500, detail="Failed to send email")
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Email delivery failed: {str(e)}")
