"""
PostgreSQL Models using SQLAlchemy.

Defines relational models for structured data storage.
"""

from datetime import datetime
from typing import Optional, List
import json

try:
    from sqlalchemy import (
        Column, Integer, String, Float, Boolean, DateTime, 
        Text, ForeignKey, JSON, Enum as SQLEnum
    )
    from sqlalchemy.orm import declarative_base, relationship
    from sqlalchemy.dialects.postgresql import ARRAY
    SQLALCHEMY_AVAILABLE = True
except ImportError:
    SQLALCHEMY_AVAILABLE = False
    # Create dummy base for import
    class Base:
        pass


if SQLALCHEMY_AVAILABLE:
    Base = declarative_base()
else:
    Base = object


class UserPersonaModel(Base):
    """Database model for user personas."""
    
    __tablename__ = "user_personas"
    
    id = Column(String(50), primary_key=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    interests = Column(JSON)  # List of interests
    ideological_leaning = Column(String(50))
    subreddits = Column(JSON)  # List of subreddits
    youtube_channels = Column(JSON)
    search_terms = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    recommendations = relationship("RecommendationModel", back_populates="persona")
    analysis_results = relationship("AnalysisResultModel", back_populates="persona")


class ContentModel(Base):
    """Database model for collected content."""
    
    __tablename__ = "content"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    content_id = Column(String(100), unique=True, nullable=False)  # Platform-specific ID
    platform = Column(String(50), nullable=False)  # reddit, youtube
    
    # Content details
    title = Column(Text)
    body = Column(Text)
    author = Column(String(200))
    url = Column(Text)
    
    # Engagement metrics
    upvotes = Column(Integer, default=0)
    downvotes = Column(Integer, default=0)
    comments_count = Column(Integer, default=0)
    views_count = Column(Integer, default=0)
    
    # Platform-specific
    subreddit = Column(String(100))  # Reddit
    channel_id = Column(String(100))  # YouTube
    channel_name = Column(String(200))
    
    # Metadata
    tags = Column(JSON)
    category = Column(String(100))
    duration_seconds = Column(Integer)  # For videos
    thumbnail_url = Column(Text)
    
    # Timestamps
    published_at = Column(DateTime)
    collected_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    recommendations = relationship("RecommendationModel", back_populates="content")


class RecommendationModel(Base):
    """Database model for recommendation events."""
    
    __tablename__ = "recommendations"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Foreign keys
    persona_id = Column(String(50), ForeignKey("user_personas.id"), nullable=False)
    content_id = Column(Integer, ForeignKey("content.id"), nullable=False)
    
    # Recommendation context
    rank = Column(Integer)  # Position in recommendation list
    context = Column(String(100))  # Where recommended (home, search, related)
    source_content_id = Column(String(100))  # What led to this recommendation
    
    # Trail tracking
    recommendation_trail = Column(JSON)  # List of content IDs in trail
    
    # Timestamps
    collected_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    persona = relationship("UserPersonaModel", back_populates="recommendations")
    content = relationship("ContentModel", back_populates="recommendations")


class AnalysisResultModel(Base):
    """Database model for analysis results."""
    
    __tablename__ = "analysis_results"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Foreign keys
    persona_id = Column(String(50), ForeignKey("user_personas.id"))
    
    # Analysis type
    analysis_type = Column(String(50), nullable=False)  # topic, stance, bias, diversity
    platform = Column(String(50))
    
    # Results (stored as JSON)
    results = Column(JSON)
    
    # Metrics
    confidence_score = Column(Float)
    sample_size = Column(Integer)
    
    # Timestamps
    analysis_date = Column(DateTime, default=datetime.utcnow)
    data_start_date = Column(DateTime)
    data_end_date = Column(DateTime)
    
    # Relationships
    persona = relationship("UserPersonaModel", back_populates="analysis_results")


class ContractModel(Base):
    """Database model for generated contracts."""
    
    __tablename__ = "contracts"
    
    id = Column(String(50), primary_key=True)
    platform = Column(String(50), nullable=False)
    title = Column(Text)
    format = Column(String(50))  # detailed, summary, legal
    
    # Content
    executive_summary = Column(Text)
    sections = Column(JSON)  # List of section dictionaries
    methodology_note = Column(Text)
    
    # Metadata
    personas_analyzed = Column(JSON)  # List of persona IDs
    raw_statistics = Column(JSON)
    model_used = Column(String(100))
    tokens_used = Column(Integer)
    
    # Timestamps
    generation_date = Column(DateTime, default=datetime.utcnow)


class ScrapingJobModel(Base):
    """Database model for scraping job tracking."""
    
    __tablename__ = "scraping_jobs"
    
    id = Column(String(50), primary_key=True)
    platform = Column(String(50), nullable=False)
    
    # Job details
    persona_ids = Column(JSON)  # List of persona IDs to scrape for
    max_items = Column(Integer, default=100)
    include_recommendations = Column(Boolean, default=True)
    
    # Status
    status = Column(String(50), default="queued")  # queued, running, completed, failed
    progress = Column(Float, default=0.0)
    items_collected = Column(Integer, default=0)
    errors = Column(JSON)  # List of error messages
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    started_at = Column(DateTime)
    completed_at = Column(DateTime)


# ===================
# Helper Functions
# ===================

def init_db(engine):
    """Initialize database tables."""
    Base.metadata.create_all(bind=engine)


def drop_db(engine):
    """Drop all database tables."""
    Base.metadata.drop_all(bind=engine)
