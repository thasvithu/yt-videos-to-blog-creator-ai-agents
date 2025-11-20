"""Tests for YouTube service."""
import pytest
from app.services.youtube import YouTubeService


def test_extract_video_id():
    """Test video ID extraction."""
    service = YouTubeService()
    
    # Test various URL formats
    assert service.extract_video_id("https://www.youtube.com/watch?v=dQw4w9WgXcQ") == "dQw4w9WgXcQ"
    assert service.extract_video_id("https://youtu.be/dQw4w9WgXcQ") == "dQw4w9WgXcQ"
    assert service.extract_video_id("https://www.youtube.com/embed/dQw4w9WgXcQ") == "dQw4w9WgXcQ"
    assert service.extract_video_id("dQw4w9WgXcQ") == "dQw4w9WgXcQ"


@pytest.mark.skipif(True, reason="Requires YouTube API key")
def test_search_video():
    """Test video search (requires API key)."""
    service = YouTubeService()
    result = service.search_video("OpenAI", "GPT-4")
    assert result is not None


@pytest.mark.skipif(True, reason="Requires YouTube API or transcript availability")
def test_get_transcript():
    """Test transcript fetching."""
    service = YouTubeService()
    transcript = service.get_transcript("dQw4w9WgXcQ")
    # Transcript may or may not be available
    assert transcript is None or isinstance(transcript, str)
