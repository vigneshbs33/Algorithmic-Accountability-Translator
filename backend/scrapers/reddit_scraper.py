"""
Reddit Scraper for collecting content recommendations.

Uses PRAW (Python Reddit API Wrapper) to collect posts and comments
based on user persona interests.
"""

import asyncio
from datetime import datetime
from typing import List, Optional
import logging

try:
    import praw
    from praw.models import Submission
    PRAW_AVAILABLE = True
except ImportError:
    PRAW_AVAILABLE = False

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


class RedditScraper(BaseScraper):
    """
    Reddit content scraper using PRAW.
    
    Collects posts from subreddits relevant to each persona and tracks
    how recommendations differ based on user interests.
    """
    
    def __init__(self):
        """Initialize Reddit scraper with API credentials."""
        self._reddit = None
        self._rate_limiter = RateLimiter(self.get_rate_limit_config())
    
    @property
    def platform_name(self) -> str:
        return "reddit"
    
    def _get_reddit_client(self):
        """Get or create Reddit API client."""
        if not PRAW_AVAILABLE:
            raise ImportError("PRAW is not installed. Run: pip install praw")
        
        if self._reddit is None:
            self._reddit = praw.Reddit(
                client_id=settings.reddit_client_id,
                client_secret=settings.reddit_client_secret,
                user_agent=settings.reddit_user_agent
            )
        return self._reddit
    
    def get_rate_limit_config(self) -> RateLimitConfig:
        return RateLimitConfig(
            requests_per_minute=settings.reddit_rate_limit,
            burst_limit=10
        )
    
    async def validate_credentials(self) -> bool:
        """Validate Reddit API credentials."""
        try:
            reddit = self._get_reddit_client()
            # Try to access a public subreddit
            subreddit = reddit.subreddit("test")
            _ = subreddit.display_name
            return True
        except Exception as e:
            logger.error(f"Reddit credential validation failed: {e}")
            return False
    
    async def collect_recommendations(
        self,
        persona: UserPersona,
        max_items: int = 100,
        include_trails: bool = True
    ) -> ScrapingResult:
        """
        Collect Reddit posts for a persona based on their subreddit interests.
        
        Args:
            persona: The user persona to collect for.
            max_items: Maximum number of posts to collect.
            include_trails: Whether to track cross-posts.
            
        Returns:
            ScrapingResult with collected recommendations.
        """
        started_at = datetime.now()
        recommendations = []
        errors = []
        
        try:
            reddit = self._get_reddit_client()
            items_per_subreddit = max(5, max_items // len(persona.subreddits))
            
            for subreddit_name in persona.subreddits:
                try:
                    # Rate limiting
                    await self._rate_limiter.acquire()
                    
                    # Remove 'r/' prefix if present
                    sub_name = subreddit_name.replace("r/", "")
                    subreddit = reddit.subreddit(sub_name)
                    
                    # Collect from different sorting methods
                    rank = 1
                    for sorting in ["hot", "top", "new"]:
                        if len(recommendations) >= max_items:
                            break
                        
                        await self._rate_limiter.acquire()
                        
                        if sorting == "hot":
                            posts = subreddit.hot(limit=items_per_subreddit // 3)
                        elif sorting == "top":
                            posts = subreddit.top(time_filter="week", limit=items_per_subreddit // 3)
                        else:
                            posts = subreddit.new(limit=items_per_subreddit // 3)
                        
                        for post in posts:
                            if len(recommendations) >= max_items:
                                break
                            
                            content = self._submission_to_metadata(post)
                            
                            recommendation = Recommendation(
                                content=content,
                                persona_id=persona.id,
                                rank=rank,
                                context=f"{sorting}:{sub_name}",
                                source_content_id=None,
                                recommendation_trail=[]
                            )
                            
                            recommendations.append(recommendation)
                            rank += 1
                            
                except Exception as e:
                    error_msg = f"Error collecting from {subreddit_name}: {str(e)}"
                    logger.warning(error_msg)
                    errors.append(error_msg)
                    
        except Exception as e:
            error_msg = f"Reddit scraping failed: {str(e)}"
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
    
    async def get_content_details(self, content_id: str) -> ContentMetadata:
        """
        Get detailed metadata for a Reddit post.
        
        Args:
            content_id: The Reddit post ID.
            
        Returns:
            ContentMetadata for the post.
        """
        await self._rate_limiter.acquire()
        
        reddit = self._get_reddit_client()
        submission = reddit.submission(id=content_id)
        
        return self._submission_to_metadata(submission)
    
    def _submission_to_metadata(self, submission) -> ContentMetadata:
        """
        Convert a PRAW Submission to ContentMetadata.
        
        Args:
            submission: PRAW Submission object.
            
        Returns:
            ContentMetadata for the submission.
        """
        return ContentMetadata(
            content_id=submission.id,
            platform="reddit",
            title=submission.title,
            body=submission.selftext if hasattr(submission, 'selftext') else None,
            author=str(submission.author) if submission.author else "[deleted]",
            created_at=datetime.fromtimestamp(submission.created_utc),
            url=f"https://reddit.com{submission.permalink}",
            upvotes=submission.score,
            downvotes=0,  # Reddit doesn't expose downvotes directly
            comments_count=submission.num_comments,
            subreddit=str(submission.subreddit),
            tags=[],
            category=str(submission.link_flair_text) if submission.link_flair_text else None,
            thumbnail_url=submission.thumbnail if submission.thumbnail.startswith('http') else None,
            raw_data={
                "upvote_ratio": submission.upvote_ratio,
                "is_original_content": submission.is_original_content,
                "is_self": submission.is_self,
                "is_video": submission.is_video,
                "over_18": submission.over_18,
                "spoiler": submission.spoiler,
                "awarded": submission.total_awards_received
            }
        )
    
    async def search_subreddit(
        self,
        subreddit_name: str,
        query: str,
        limit: int = 25
    ) -> List[ContentMetadata]:
        """
        Search within a specific subreddit.
        
        Args:
            subreddit_name: Name of the subreddit.
            query: Search query.
            limit: Maximum results.
            
        Returns:
            List of matching content.
        """
        await self._rate_limiter.acquire()
        
        reddit = self._get_reddit_client()
        subreddit = reddit.subreddit(subreddit_name.replace("r/", ""))
        
        results = []
        for submission in subreddit.search(query, limit=limit):
            results.append(self._submission_to_metadata(submission))
        
        return results
