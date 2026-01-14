"""
API dependencies for dependency injection.
"""

from functools import lru_cache
from typing import Generator

from config import Settings, get_settings


def get_config() -> Settings:
    """Dependency to get application settings."""
    return get_settings()
