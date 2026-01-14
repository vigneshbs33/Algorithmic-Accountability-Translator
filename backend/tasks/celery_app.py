"""
Celery Application Configuration.

Sets up Celery with Redis as broker for async task processing.
"""

from celery import Celery

from config import settings


# Create Celery app
celery_app = Celery(
    "algorithmic_accountability",
    broker=settings.redis_url,
    backend=settings.redis_url,
    include=[
        "tasks.scraping_tasks",
        "tasks.analysis_tasks"
    ]
)

# Celery configuration
celery_app.conf.update(
    # Task settings
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    
    # Task execution settings
    task_acks_late=True,
    task_reject_on_worker_lost=True,
    
    # Result backend settings
    result_expires=3600,  # 1 hour
    
    # Worker settings
    worker_prefetch_multiplier=1,
    worker_concurrency=4,
    
    # Rate limiting
    task_annotations={
        "tasks.scraping_tasks.scrape_reddit_task": {
            "rate_limit": "10/m"  # 10 tasks per minute
        },
        "tasks.scraping_tasks.scrape_youtube_task": {
            "rate_limit": "5/m"  # 5 tasks per minute (stricter quota)
        }
    },
    
    # Task routes
    task_routes={
        "tasks.scraping_tasks.*": {"queue": "scraping"},
        "tasks.analysis_tasks.*": {"queue": "analysis"}
    }
)


# Optional: Beat schedule for periodic tasks
celery_app.conf.beat_schedule = {
    # Example: Run diversity analysis every hour
    # "hourly-diversity-check": {
    #     "task": "tasks.analysis_tasks.run_periodic_diversity_check",
    #     "schedule": 3600.0,
    # },
}


if __name__ == "__main__":
    celery_app.start()
