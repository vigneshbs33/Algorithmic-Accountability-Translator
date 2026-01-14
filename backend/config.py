"""
Configuration management for Algorithmic Accountability Translator.
Uses Pydantic Settings for type-safe configuration with environment variable support.
"""

from functools import lru_cache
from typing import Literal
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )
    
    # ===================
    # API Keys
    # ===================
    
    # Reddit API
    reddit_client_id: str = ""
    reddit_client_secret: str = ""
    reddit_user_agent: str = "AlgorithmicAccountability/1.0"
    
    # YouTube API
    youtube_api_key: str = ""
    
    # LLM APIs
    openai_api_key: str = ""
    anthropic_api_key: str = ""
    llm_provider: Literal["openai", "anthropic"] = "openai"
    
    # ===================
    # Database
    # ===================
    
    # PostgreSQL
    postgres_host: str = "localhost"
    postgres_port: int = 5432
    postgres_db: str = "algorithmic_accountability"
    postgres_user: str = "postgres"
    postgres_password: str = ""
    
    @property
    def postgres_url(self) -> str:
        """Construct PostgreSQL connection URL."""
        return (
            f"postgresql://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )
    
    # MongoDB
    mongodb_uri: str = "mongodb://localhost:27017"
    mongodb_db: str = "algorithmic_accountability"
    
    # Redis
    redis_url: str = "redis://localhost:6379/0"
    
    # ===================
    # Application
    # ===================
    
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    debug: bool = True
    frontend_url: str = "http://localhost:3000"
    
    # ===================
    # Rate Limiting
    # ===================
    
    reddit_rate_limit: int = 60  # requests per minute
    youtube_daily_quota: int = 10000  # daily quota units
    
    # ===================
    # Model Configuration
    # ===================
    
    embedding_model: str = "all-MiniLM-L6-v2"
    spacy_model: str = "en_core_web_sm"
    stance_model: str = "bert-base-uncased"
    
    # ===================
    # Data Paths
    # ===================
    
    data_raw_path: str = "./data/raw"
    data_processed_path: str = "./data/processed"
    models_path: str = "./data/models"


@lru_cache()
def get_settings() -> Settings:
    """
    Get cached settings instance.
    Uses lru_cache to ensure settings are only loaded once.
    """
    return Settings()


# Export settings instance for easy import
settings = get_settings()
