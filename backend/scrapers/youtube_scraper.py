"""
YouTube Scraper for collecting video recommendations.

Uses the YouTube Data API v3 to collect videos and recommendations
based on user persona interests.
"""

import asyncio
from datetime import datetime
from typing import List, Optional
import logging

try:
    from googleapiclient.discovery import build
    from googleapiclient.errors import HttpError
    YOUTUBE_API_AVAILABLE = True
except ImportError:
    YOUTUBE_API_AVAILABLE = False

from config import settings
from personas.profiles import UserPersona
from .base_scraper import (
    BaseScraper,
    ContentMetadata,
    Recommendation,
    ScrapingResult
)
from .rate_limiter import RateLimitConfig, RateLimiter


logger = logging.getLogger(__name__)


class YouTubeScraper(BaseScraper):
    """
    YouTube content scraper using the Data API v3.
    
    Collects videos based on search terms and tracks recommendations
    to understand how the algorithm shapes content discovery.
    """
    
    def __init__(self):
        """Initialize YouTube scraper with API credentials."""
        self._youtube = None
        self._rate_limiter = RateLimiter(self.get_rate_limit_config())
    
    @property
    def platform_name(self) -> str:
        return "youtube"
    
    def _get_youtube_client(self):
        """Get or create YouTube API client."""
        if not YOUTUBE_API_AVAILABLE:
            raise ImportError(
                "Google API Client is not installed. "
                "Run: pip install google-api-python-client"
            )
        
        if self._youtube is None:
            self._youtube = build(
                "youtube",
                "v3",
                developerKey=settings.youtube_api_key
            )
        return self._youtube
    
    def get_rate_limit_config(self) -> RateLimitConfig:
        return RateLimitConfig(
            requests_per_minute=100,
            daily_quota=settings.youtube_daily_quota,
            burst_limit=20
        )
    
    async def validate_credentials(self) -> bool:
        """Validate YouTube API credentials."""
        try:
            youtube = self._get_youtube_client()
            # Try a simple search
            request = youtube.search().list(
                q="test",
                part="snippet",
                maxResults=1,
                type="video"
            )
            request.execute()
            return True
        except Exception as e:
            logger.error(f"YouTube credential validation failed: {e}")
            return False
    
    async def collect_recommendations(
        self,
        persona: UserPersona,
        max_items: int = 100,
        include_trails: bool = True
    ) -> ScrapingResult:
        """
        Collect YouTube videos for a persona based on their search interests.
        
        Args:
            persona: The user persona to collect for.
            max_items: Maximum number of videos to collect.
            include_trails: Whether to track related videos.
            
        Returns:
            ScrapingResult with collected recommendations.
        """
        started_at = datetime.now()
        recommendations = []
        errors = []
        
        try:
            youtube = self._get_youtube_client()
            items_per_term = max(5, max_items // len(persona.search_terms))
            
            for search_term in persona.search_terms:
                if len(recommendations) >= max_items:
                    break
                
                try:
                    await self._rate_limiter.acquire()
                    
                    # Search for videos
                    search_response = youtube.search().list(
                        q=search_term,
                        part="snippet",
                        maxResults=items_per_term,
                        type="video",
                        order="relevance"
                    ).execute()
                    
                    video_ids = [
                        item["id"]["videoId"] 
                        for item in search_response.get("items", [])
                        if item["id"].get("videoId")
                    ]
                    
                    if video_ids:
                        await self._rate_limiter.acquire()
                        
                        # Get video details
                        videos_response = youtube.videos().list(
                            id=",".join(video_ids),
                            part="snippet,statistics,contentDetails"
                        ).execute()
                        
                        rank = len(recommendations) + 1
                        for video in videos_response.get("items", []):
                            if len(recommendations) >= max_items:
                                break
                            
                            content = self._video_to_metadata(video)
                            
                            recommendation = Recommendation(
                                content=content,
                                persona_id=persona.id,
                                rank=rank,
                                context=f"search:{search_term}",
                                source_content_id=None,
                                recommendation_trail=[]
                            )
                            
                            recommendations.append(recommendation)
                            rank += 1
                            
                            # Optionally collect related videos
                            if include_trails and len(recommendations) < max_items:
                                related = await self._get_related_videos(
                                    video["id"],
                                    limit=3
                                )
                                for related_video in related:
                                    if len(recommendations) >= max_items:
                                        break
                                    
                                    related_content = self._video_to_metadata(related_video)
                                    related_rec = Recommendation(
                                        content=related_content,
                                        persona_id=persona.id,
                                        rank=rank,
                                        context="related",
                                        source_content_id=video["id"],
                                        recommendation_trail=[video["id"]]
                                    )
                                    recommendations.append(related_rec)
                                    rank += 1
                
                except HttpError as e:
                    error_msg = f"YouTube API error for '{search_term}': {str(e)}"
                    logger.warning(error_msg)
                    errors.append(error_msg)
                except Exception as e:
                    error_msg = f"Error searching '{search_term}': {str(e)}"
                    logger.warning(error_msg)
                    errors.append(error_msg)
        
        except Exception as e:
            error_msg = f"YouTube scraping failed: {str(e)}"
            logger.error(error_msg)
            errors.append(error_msg)
        
        completed_at = datetime.now()
        
        return ScrapingResult(
            persona_id=persona.id,
            platform=self.platform_name,
            recommendations=recommendations,
            total_collected=len(recommendations),
            started_at=started_at,
            completed_at=completed_at,
            errors=errors
        )
    
    async def _get_related_videos(
        self,
        video_id: str,
        limit: int = 5
    ) -> List[dict]:
        """
        Get videos related to a specific video.
        
        Args:
            video_id: The source video ID.
            limit: Maximum related videos to fetch.
            
        Returns:
            List of video data dictionaries.
        """
        try:
            await self._rate_limiter.acquire()
            
            youtube = self._get_youtube_client()
            
            # Search for related content using the video as a seed
            # Note: relatedToVideoId is deprecated, using search instead
            search_response = youtube.search().list(
                part="snippet",
                maxResults=limit,
                type="video",
                relatedToVideoId=video_id
            ).execute()
            
            video_ids = [
                item["id"]["videoId"]
                for item in search_response.get("items", [])
                if item["id"].get("videoId")
            ]
            
            if not video_ids:
                return []
            
            await self._rate_limiter.acquire()
            
            videos_response = youtube.videos().list(
                id=",".join(video_ids),
                part="snippet,statistics,contentDetails"
            ).execute()
            
            return videos_response.get("items", [])
            
        except Exception as e:
            logger.warning(f"Error getting related videos for {video_id}: {e}")
            return []
    
    async def get_content_details(self, content_id: str) -> ContentMetadata:
        """
        Get detailed metadata for a YouTube video.
        
        Args:
            content_id: The YouTube video ID.
            
        Returns:
            ContentMetadata for the video.
        """
        await self._rate_limiter.acquire()
        
        youtube = self._get_youtube_client()
        
        response = youtube.videos().list(
            id=content_id,
            part="snippet,statistics,contentDetails"
        ).execute()
        
        items = response.get("items", [])
        if not items:
            raise ValueError(f"Video not found: {content_id}")
        
        return self._video_to_metadata(items[0])
    
    def _video_to_metadata(self, video: dict) -> ContentMetadata:
        """
        Convert YouTube API video response to ContentMetadata.
        
        Args:
            video: YouTube API video object.
            
        Returns:
            ContentMetadata for the video.
        """
        snippet = video.get("snippet", {})
        statistics = video.get("statistics", {})
        content_details = video.get("contentDetails", {})
        
        # Parse duration (ISO 8601 format: PT1H2M3S)
        duration_str = content_details.get("duration", "PT0S")
        duration_seconds = self._parse_duration(duration_str)
        
        # Parse published date
        published_at = snippet.get("publishedAt")
        created_at = None
        if published_at:
            try:
                created_at = datetime.fromisoformat(
                    published_at.replace("Z", "+00:00")
                )
            except:
                pass
        
        return ContentMetadata(
            content_id=video["id"],
            platform="youtube",
            title=snippet.get("title", ""),
            body=snippet.get("description", ""),
            author=snippet.get("channelTitle", ""),
            created_at=created_at,
            url=f"https://www.youtube.com/watch?v={video['id']}",
            upvotes=int(statistics.get("likeCount", 0)),
            comments_count=int(statistics.get("commentCount", 0)),
            views_count=int(statistics.get("viewCount", 0)),
            channel_id=snippet.get("channelId"),
            channel_name=snippet.get("channelTitle"),
            tags=snippet.get("tags", []),
            category=snippet.get("categoryId"),
            duration_seconds=duration_seconds,
            thumbnail_url=snippet.get("thumbnails", {}).get("high", {}).get("url"),
            raw_data={
                "definition": content_details.get("definition"),
                "caption": content_details.get("caption"),
                "licensed_content": content_details.get("licensedContent"),
                "favorite_count": statistics.get("favoriteCount")
            }
        )
    
    def _parse_duration(self, duration_str: str) -> int:
        """
        Parse ISO 8601 duration to seconds.
        
        Args:
            duration_str: Duration in ISO 8601 format (e.g., PT1H2M3S).
            
        Returns:
            Duration in seconds.
        """
        import re
        
        # Remove PT prefix
        duration_str = duration_str.replace("PT", "")
        
        hours = 0
        minutes = 0
        seconds = 0
        
        # Extract hours
        hour_match = re.search(r"(\d+)H", duration_str)
        if hour_match:
            hours = int(hour_match.group(1))
        
        # Extract minutes
        min_match = re.search(r"(\d+)M", duration_str)
        if min_match:
            minutes = int(min_match.group(1))
        
        # Extract seconds
        sec_match = re.search(r"(\d+)S", duration_str)
        if sec_match:
            seconds = int(sec_match.group(1))
        
        return hours * 3600 + minutes * 60 + seconds
