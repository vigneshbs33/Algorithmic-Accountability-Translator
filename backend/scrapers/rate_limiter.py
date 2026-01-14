"""
Rate Limiter for API calls.

Implements token bucket algorithm with configurable rates for different platforms.
"""

import asyncio
import time
from dataclasses import dataclass
from typing import Dict


@dataclass
class RateLimitConfig:
    """Configuration for rate limiting."""
    requests_per_minute: int
    daily_quota: int | None = None  # For APIs with daily limits (e.g., YouTube)
    burst_limit: int | None = None  # Maximum burst size


class RateLimiter:
    """
    Token bucket rate limiter for API calls.
    
    Ensures we don't exceed platform rate limits while maximizing throughput.
    """
    
    def __init__(self, config: RateLimitConfig):
        """
        Initialize rate limiter with configuration.
        
        Args:
            config: Rate limiting configuration.
        """
        self.config = config
        self.tokens = config.requests_per_minute
        self.max_tokens = config.burst_limit or config.requests_per_minute
        self.last_update = time.time()
        self.daily_used = 0
        self.daily_reset_time = time.time()
        self._lock = asyncio.Lock()
    
    async def acquire(self) -> bool:
        """
        Acquire permission to make an API call.
        
        Blocks until a token is available, respecting rate limits.
        
        Returns:
            True if permission was granted.
            
        Raises:
            Exception: If daily quota is exceeded.
        """
        async with self._lock:
            # Check daily quota
            if self.config.daily_quota:
                self._check_daily_reset()
                if self.daily_used >= self.config.daily_quota:
                    raise Exception("Daily API quota exceeded")
            
            # Refill tokens based on time elapsed
            await self._refill_tokens()
            
            # Wait for token if none available
            while self.tokens < 1:
                wait_time = 60.0 / self.config.requests_per_minute
                await asyncio.sleep(wait_time)
                await self._refill_tokens()
            
            # Consume token
            self.tokens -= 1
            if self.config.daily_quota:
                self.daily_used += 1
            
            return True
    
    async def _refill_tokens(self):
        """Refill tokens based on time elapsed since last update."""
        now = time.time()
        elapsed = now - self.last_update
        
        # Calculate tokens to add (tokens per second * elapsed seconds)
        tokens_per_second = self.config.requests_per_minute / 60.0
        tokens_to_add = elapsed * tokens_per_second
        
        self.tokens = min(self.max_tokens, self.tokens + tokens_to_add)
        self.last_update = now
    
    def _check_daily_reset(self):
        """Check if daily quota should be reset."""
        now = time.time()
        # Reset every 24 hours
        if now - self.daily_reset_time >= 86400:
            self.daily_used = 0
            self.daily_reset_time = now
    
    def get_status(self) -> Dict:
        """
        Get current rate limiter status.
        
        Returns:
            Dictionary with current status information.
        """
        return {
            "tokens_available": self.tokens,
            "requests_per_minute": self.config.requests_per_minute,
            "daily_used": self.daily_used if self.config.daily_quota else None,
            "daily_quota": self.config.daily_quota,
            "daily_remaining": (
                self.config.daily_quota - self.daily_used 
                if self.config.daily_quota else None
            )
        }


# Pre-configured rate limiters for each platform
REDDIT_RATE_LIMITER = RateLimiter(RateLimitConfig(
    requests_per_minute=60,
    burst_limit=10
))

YOUTUBE_RATE_LIMITER = RateLimiter(RateLimitConfig(
    requests_per_minute=100,  # API allows more per minute
    daily_quota=10000,  # But has strict daily quota
    burst_limit=20
))
