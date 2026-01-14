"""
Scraping API routes for triggering data collection.
"""

from typing import List, Optional
from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from enum import Enum


router = APIRouter()


class Platform(str, Enum):
    """Supported platforms for scraping."""
    REDDIT = "reddit"
    YOUTUBE = "youtube"


class ScrapeRequest(BaseModel):
    """Request model for starting a scrape job."""
    persona_ids: List[str]
    platform: Platform
    max_items: int = 100
    include_recommendations: bool = True


class ScrapeJobResponse(BaseModel):
    """Response model for scrape job status."""
    job_id: str
    status: str
    platform: str
    persona_ids: List[str]
    progress: float
    items_collected: int
    message: Optional[str] = None


class ScrapeJobsListResponse(BaseModel):
    """Response model for list of scrape jobs."""
    jobs: List[ScrapeJobResponse]
    total: int


# In-memory job storage (replace with Redis/DB in production)
_scrape_jobs = {}


@router.post("/reddit", response_model=ScrapeJobResponse)
async def start_reddit_scrape(request: ScrapeRequest, background_tasks: BackgroundTasks):
    """
    Start a Reddit scraping job for specified personas.
    
    This endpoint initiates an asynchronous scraping task that collects
    content from Reddit based on the specified user personas.
    
    Args:
        request: Scraping configuration including persona IDs and limits.
        
    Returns:
        Job status with tracking ID.
    """
    import uuid
    
    job_id = str(uuid.uuid4())
    
    job = ScrapeJobResponse(
        job_id=job_id,
        status="queued",
        platform="reddit",
        persona_ids=request.persona_ids,
        progress=0.0,
        items_collected=0,
        message="Job queued for processing"
    )
    
    _scrape_jobs[job_id] = job
    
    # TODO: Add actual Celery task
    # background_tasks.add_task(scrape_reddit_task, job_id, request)
    
    return job


@router.post("/youtube", response_model=ScrapeJobResponse)
async def start_youtube_scrape(request: ScrapeRequest, background_tasks: BackgroundTasks):
    """
    Start a YouTube scraping job for specified personas.
    
    This endpoint initiates an asynchronous scraping task that collects
    video recommendations from YouTube based on the specified user personas.
    
    Args:
        request: Scraping configuration including persona IDs and limits.
        
    Returns:
        Job status with tracking ID.
    """
    import uuid
    
    job_id = str(uuid.uuid4())
    
    job = ScrapeJobResponse(
        job_id=job_id,
        status="queued",
        platform="youtube",
        persona_ids=request.persona_ids,
        progress=0.0,
        items_collected=0,
        message="Job queued for processing"
    )
    
    _scrape_jobs[job_id] = job
    
    # TODO: Add actual Celery task
    # background_tasks.add_task(scrape_youtube_task, job_id, request)
    
    return job


@router.get("/jobs", response_model=ScrapeJobsListResponse)
async def list_scrape_jobs():
    """
    List all scraping jobs and their statuses.
    
    Returns:
        List of all scrape jobs with their current status.
    """
    jobs = list(_scrape_jobs.values())
    return ScrapeJobsListResponse(jobs=jobs, total=len(jobs))


@router.get("/jobs/{job_id}", response_model=ScrapeJobResponse)
async def get_scrape_job(job_id: str):
    """
    Get status of a specific scraping job.
    
    Args:
        job_id: The unique identifier of the scrape job.
        
    Returns:
        Current status of the scrape job.
        
    Raises:
        HTTPException: If job is not found.
    """
    if job_id not in _scrape_jobs:
        raise HTTPException(status_code=404, detail=f"Job '{job_id}' not found")
    
    return _scrape_jobs[job_id]


@router.delete("/jobs/{job_id}")
async def cancel_scrape_job(job_id: str):
    """
    Cancel a running scraping job.
    
    Args:
        job_id: The unique identifier of the scrape job to cancel.
        
    Returns:
        Confirmation of cancellation.
        
    Raises:
        HTTPException: If job is not found.
    """
    if job_id not in _scrape_jobs:
        raise HTTPException(status_code=404, detail=f"Job '{job_id}' not found")
    
    # TODO: Actually cancel the Celery task
    _scrape_jobs[job_id].status = "cancelled"
    _scrape_jobs[job_id].message = "Job cancelled by user"
    
    return {"message": f"Job '{job_id}' cancelled", "job_id": job_id}
