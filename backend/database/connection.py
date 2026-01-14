"""
Database Connection Management.

Handles connections to PostgreSQL and MongoDB databases.
"""

from typing import Generator
import logging

try:
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker, Session
    SQLALCHEMY_AVAILABLE = True
except ImportError:
    SQLALCHEMY_AVAILABLE = False

try:
    from pymongo import MongoClient
    from pymongo.database import Database
    PYMONGO_AVAILABLE = True
except ImportError:
    PYMONGO_AVAILABLE = False

from config import settings


logger = logging.getLogger(__name__)


# ===================
# PostgreSQL
# ===================

_postgres_engine = None
_SessionLocal = None


def get_postgres_engine():
    """Get or create PostgreSQL engine."""
    global _postgres_engine
    
    if not SQLALCHEMY_AVAILABLE:
        raise ImportError("SQLAlchemy not installed. Run: pip install sqlalchemy psycopg2-binary")
    
    if _postgres_engine is None:
        logger.info(f"Creating PostgreSQL connection to {settings.postgres_host}")
        _postgres_engine = create_engine(
            settings.postgres_url,
            pool_size=5,
            max_overflow=10,
            pool_pre_ping=True
        )
    
    return _postgres_engine


def get_session_factory():
    """Get SQLAlchemy session factory."""
    global _SessionLocal
    
    if _SessionLocal is None:
        engine = get_postgres_engine()
        _SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    return _SessionLocal


def get_db_session() -> Generator[Session, None, None]:
    """
    Get database session for dependency injection.
    
    Usage:
        @app.get("/items")
        def read_items(db: Session = Depends(get_db_session)):
            ...
    """
    SessionLocal = get_session_factory()
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ===================
# MongoDB
# ===================

_mongo_client = None
_mongo_db = None


def get_mongo_client() -> MongoClient:
    """Get or create MongoDB client."""
    global _mongo_client
    
    if not PYMONGO_AVAILABLE:
        raise ImportError("PyMongo not installed. Run: pip install pymongo")
    
    if _mongo_client is None:
        logger.info(f"Creating MongoDB connection to {settings.mongodb_uri}")
        _mongo_client = MongoClient(settings.mongodb_uri)
    
    return _mongo_client


def get_mongo_db() -> Database:
    """Get MongoDB database instance."""
    global _mongo_db
    
    if _mongo_db is None:
        client = get_mongo_client()
        _mongo_db = client[settings.mongodb_db]
    
    return _mongo_db


def get_content_collection():
    """Get MongoDB collection for raw content."""
    db = get_mongo_db()
    return db["content"]


def get_analysis_collection():
    """Get MongoDB collection for analysis results."""
    db = get_mongo_db()
    return db["analysis"]


def get_contracts_collection():
    """Get MongoDB collection for generated contracts."""
    db = get_mongo_db()
    return db["contracts"]


# ===================
# Health Checks
# ===================

def check_postgres_connection() -> bool:
    """Check PostgreSQL connection health."""
    try:
        engine = get_postgres_engine()
        with engine.connect() as conn:
            conn.execute("SELECT 1")
        return True
    except Exception as e:
        logger.error(f"PostgreSQL connection failed: {e}")
        return False


def check_mongo_connection() -> bool:
    """Check MongoDB connection health."""
    try:
        client = get_mongo_client()
        client.admin.command('ping')
        return True
    except Exception as e:
        logger.error(f"MongoDB connection failed: {e}")
        return False
