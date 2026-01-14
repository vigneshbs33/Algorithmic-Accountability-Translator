"""
Abstract Base Scraper for content collection.

Defines the interface that all platform-specific scrapers must implement.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional, Dict, Any

from personas.profiles import UserPersona
from .rate_limiter import RateLimitConfig


@dataclass
class ContentMetadata:
    """Metadata about a piece of content."""
    content_id: str
    platform: str
    title: str
    body: Optional[str] = None
    author: Optional[str] = None
    created_at: Optional[datetime] = None
    url: Optional[str] = None
    
    # Engagement metrics
    upvotes: int = 0
    downvotes: int = 0
    comments_count: int = 0
    shares_count: int = 0
    views_count: int = 0
    
    # Content classification
    subreddit: Optional[str] = None  # Reddit-specific
    channel_id: Optional[str] = None  # YouTube-specific
    channel_name: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    category: Optional[str] = None
    
    # Additional metadata
    duration_seconds: Optional[int] = None  # For videos
    thumbnail_url: Optional[str] = None
    raw_data: Optional[Dict[str, Any]] = None


@dataclass
class Recommendation:
    """
    Represents a content recommendation from a platform.
    
    Captures not just the content, but the context in which it was recommended.
    """
    content: ContentMetadata
    persona_id: str
    
    # Recommendation context
    rank: int  # Position in recommendation list (1-indexed)
    context: str  # Where it was recommended (home, search, related, etc.)
    source_content_id: Optional[str] = None  # What content led to this recommendation
    
    # Timing
    collected_at: datetime = field(default_factory=datetime.now)
    
    # Recommendation trail
    recommendation_trail: List[str] = field(default_factory=list)  # IDs of content that led here


@dataclass
class ScrapingResult:
    """Result of a scraping session."""
    persona_id: str
    platform: str
    recommendations: List[Recommendation]
    total_collected: int
    started_at: datetime
    completed_at: datetime
    errors: List[str] = field(default_factory=list)
    
    @property
    def duration_seconds(self) -> float:
        """Calculate scraping duration in seconds."""
        return (self.completed_at - self.started_at).total_seconds()


class BaseScraper(ABC):
    """
    Abstract base class for platform-specific scrapers.
    
    All scrapers must implement these methods to ensure consistent
    data collection across platforms.
    """
    
    @property
    @abstractmethod
    def platform_name(self) -> str:
        """Return the name of the platform this scraper targets."""
        pass
    
    @abstractmethod
    async def collect_recommendations(
        self, 
        persona: UserPersona, 
        max_items: int = 100,
        include_trails: bool = True
    ) -> ScrapingResult:
        """
        Collect content recommendations for a given persona.
        
        Args:
            persona: The user persona to collect recommendations for.
            max_items: Maximum number of recommendations to collect.
            include_trails: Whether to track recommendation trails.
            
        Returns:
            ScrapingResult containing all collected recommendations.
        """
        pass
    
    @abstractmethod
    async def get_content_details(self, content_id: str) -> ContentMetadata:
        """
        Get detailed metadata for a specific piece of content.
        
        Args:
            content_id: The platform-specific content identifier.
            
        Returns:
            ContentMetadata for the requested content.
        """
        pass
    
    @abstractmethod
    def get_rate_limit_config(self) -> RateLimitConfig:
        """
        Get rate limiting configuration for this platform.
        
        Returns:
            RateLimitConfig specifying rate limits.
        """
        pass
    
    @abstractmethod
    async def validate_credentials(self) -> bool:
        """
        Validate that API credentials are configured and working.
        
        Returns:
            True if credentials are valid, False otherwise.
        """
        pass
    
    async def collect_for_multiple_personas(
        self,
        personas: List[UserPersona],
        max_items_per_persona: int = 100
    ) -> List[ScrapingResult]:
        """
        Collect recommendations for multiple personas.
        
        Args:
            personas: List of personas to collect for.
            max_items_per_persona: Maximum items per persona.
            
        Returns:
            List of ScrapingResult for each persona.
        """
        results = []
        for persona in personas:
            result = await self.collect_recommendations(
                persona=persona,
                max_items=max_items_per_persona
            )
            results.append(result)
        return results
