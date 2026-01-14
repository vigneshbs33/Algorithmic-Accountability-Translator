"""
FastAPI application entry point for Algorithmic Accountability Translator.
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routes import analysis, contracts, personas, scraping


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for startup and shutdown events.
    """
    # Startup
    print("🚀 Starting Algorithmic Accountability Translator API...")
    # TODO: Initialize database connections
    # TODO: Load ML models
    yield
    # Shutdown
    print("👋 Shutting down API...")
    # TODO: Close database connections


# Create FastAPI application
app = FastAPI(
    title="Algorithmic Accountability Translator",
    description="""
    A sophisticated NLP system that reverse-engineers content recommendation algorithms,
    translates their behavior into plain language "contracts," and analyzes how these 
    algorithms create information bubbles and bias patterns.
    """,
    version="1.0.0",
    lifespan=lifespan,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ===================
# Health Check
# ===================

@app.get("/api/health", tags=["Health"])
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "algorithmic-accountability-translator",
        "version": "1.0.0"
    }


# ===================
# Route Registration
# ===================

app.include_router(personas.router, prefix="/api/personas", tags=["Personas"])
app.include_router(scraping.router, prefix="/api/scrape", tags=["Scraping"])
app.include_router(analysis.router, prefix="/api/analysis", tags=["Analysis"])
app.include_router(contracts.router, prefix="/api/contracts", tags=["Contracts"])


# ===================
# Root Endpoint
# ===================

@app.get("/", tags=["Root"])
async def root():
    """Root endpoint with API information."""
    return {
        "name": "Algorithmic Accountability Translator API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/api/health"
    }
