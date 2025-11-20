"""YouTube data retrieval service."""
import re
from typing import Optional, Dict, List
from youtube_transcript_api import YouTubeTranscriptApi
from googleapiclient.discovery import build
from tenacity import retry, stop_after_attempt, wait_exponential
from app.config import settings


class YouTubeService:
    """Service for fetching YouTube video data and transcripts."""
    
    def __init__(self):
        self.api_key = settings.youtube_api_key
        if self.api_key:
            self.youtube = build('youtube', 'v3', developerKey=self.api_key)
        else:
            self.youtube = None
    
    def extract_video_id(self, url_or_id: str) -> Optional[str]:
        """Extract video ID from URL or return if already an ID."""
        patterns = [
            r'(?:v=|\/)([0-9A-Za-z_-]{11}).*',
            r'(?:embed\/)([0-9A-Za-z_-]{11})',
            r'^([0-9A-Za-z_-]{11})$'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url_or_id)
            if match:
                return match.group(1)
        return None
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(min=1, max=10))
    def search_video(self, channel_name: str, video_title: str) -> Optional[Dict]:
        """
        Search for a video on a channel.
        
        Args:
            channel_name: YouTube channel name or handle
            video_title: Video title to search for
            
        Returns:
            Dict with video_id, title, description, thumbnail, etc.
        """
        if not self.youtube:
            # Fallback: try to construct search query
            return None
        
        try:
            # Clean channel name
            channel_handle = channel_name.replace('@', '')
            
            # Search for the channel first
            channel_request = self.youtube.search().list(
                part='snippet',
                q=channel_handle,
                type='channel',
                maxResults=1
            )
            channel_response = channel_request.execute()
            
            if not channel_response.get('items'):
                return None
            
            channel_id = channel_response['items'][0]['id']['channelId']
            
            # Search for video in the channel
            video_request = self.youtube.search().list(
                part='snippet',
                channelId=channel_id,
                q=video_title,
                type='video',
                maxResults=5
            )
            video_response = video_request.execute()
            
            if not video_response.get('items'):
                return None
            
            # Find best match
            for item in video_response['items']:
                snippet = item['snippet']
                if video_title.lower() in snippet['title'].lower():
                    return {
                        'video_id': item['id']['videoId'],
                        'title': snippet['title'],
                        'description': snippet['description'],
                        'thumbnail': snippet['thumbnails']['high']['url'],
                        'channel_title': snippet['channelTitle'],
                        'published_at': snippet['publishedAt']
                    }
            
            # Return first result if no exact match
            first_item = video_response['items'][0]
            return {
                'video_id': first_item['id']['videoId'],
                'title': first_item['snippet']['title'],
                'description': first_item['snippet']['description'],
                'thumbnail': first_item['snippet']['thumbnails']['high']['url'],
                'channel_title': first_item['snippet']['channelTitle'],
                'published_at': first_item['snippet']['publishedAt']
            }
            
        except Exception as e:
            print(f"YouTube API search error: {e}")
            return None
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(min=1, max=10))
    def get_transcript(self, video_id: str) -> Optional[str]:
        """
        Get video transcript.
        
        Args:
            video_id: YouTube video ID
            
        Returns:
            Full transcript text or None
        """
        try:
            transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
            transcript_text = ' '.join([entry['text'] for entry in transcript_list])
            return transcript_text
        except Exception as e:
            print(f"Transcript fetch error for {video_id}: {e}")
            # Try to get auto-generated captions
            try:
                transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
                transcript = transcript_list.find_generated_transcript(['en'])
                transcript_data = transcript.fetch()
                transcript_text = ' '.join([entry['text'] for entry in transcript_data])
                return transcript_text
            except Exception as e2:
                print(f"Auto-generated transcript error: {e2}")
                return None
    
    def get_video_metadata(self, video_id: str) -> Optional[Dict]:
        """Get video metadata using API."""
        if not self.youtube:
            return None
        
        try:
            request = self.youtube.videos().list(
                part='snippet,statistics,contentDetails',
                id=video_id
            )
            response = request.execute()
            
            if not response.get('items'):
                return None
            
            item = response['items'][0]
            return {
                'title': item['snippet']['title'],
                'description': item['snippet']['description'],
                'channel_title': item['snippet']['channelTitle'],
                'published_at': item['snippet']['publishedAt'],
                'thumbnail': item['snippet']['thumbnails']['high']['url'],
                'tags': item['snippet'].get('tags', []),
                'view_count': item['statistics'].get('viewCount', '0'),
                'like_count': item['statistics'].get('likeCount', '0'),
                'duration': item['contentDetails']['duration']
            }
        except Exception as e:
            print(f"Metadata fetch error: {e}")
            return None
