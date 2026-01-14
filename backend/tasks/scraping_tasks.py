"""
Scraping Background Tasks.

Celery tasks for asynchronous data collection from Reddit and YouTube.
"""

import logging
from typing import List, Dict, Any
from datetime import datetime

from .celery_app import celery_app
from scrapers import RedditScraper, YouTubeScraper
from personas import get_persona
from database.connection import get_mongo_db

logger = logging.getLogger(__name__)


@celery_app.task(bind=True, max_retries=3, default_retry_delay=60)
def scrape_reddit_task(
    self,
    persona_ids: List[str],
    max_items: int = 100,
    include_recommendations: bool = True
) -> Dict[str, Any]:
    """
    Scrape Reddit content for specified personas.
    
    Args:
        persona_ids: List of persona IDs to scrape for.
        max_items: Maximum items per persona.
        include_recommendations: Whether to follow recommendation trails.
        
    Returns:
        Summary of scraping results.
    """
    job_id = self.request.id
    results = {
        "job_id": job_id,
        "platform": "reddit",
        "status": "running",
        "started_at": datetime.utcnow().isoformat(),
        "personas_processed": [],
        "total_items": 0,
        "errors": []
    }
    
    try:
        scraper = RedditScraper()
        
        if not scraper.validate_credentials():
            raise ValueError("Invalid Reddit credentials")
        
        for persona_id in persona_ids:
            try:
                persona = get_persona(persona_id)
                if not persona:
                    results["errors"].append(f"Persona not found: {persona_id}")
                    continue
                
                logger.info(f"Scraping Reddit for persona: {persona_id}")
                
                # Update task state
                self.update_state(
                    state="PROGRESS",
                    meta={
                        "current_persona": persona_id,
                        "progress": len(results["personas_processed"]) / len(persona_ids)
                    }
                )
                
                # Scrape content
                scrape_result = scraper.scrape_for_persona(
                    persona=persona,
                    max_items=max_items,
                    include_recommendations=include_recommendations
                )
                
                # Store results in MongoDB
                db = get_mongo_db()
                for item in scrape_result.content:
                    db.content.insert_one({
                        "job_id": job_id,
                        "persona_id": persona_id,
                        "platform": "reddit",
                        "content_id": item.content_id,
                        "title": item.title,
                        "body": item.body,
                        "author": item.author,
                        "url": item.url,
                        "metadata": item.metadata,
                        "collected_at": datetime.utcnow()
                    })
                
                results["personas_processed"].append({
                    "persona_id": persona_id,
                    "items_collected": len(scrape_result.content),
                    "recommendations_found": len(scrape_result.recommendations)
                })
                results["total_items"] += len(scrape_result.content)
                
            except Exception as e:
                logger.error(f"Error scraping for {persona_id}: {e}")
                results["errors"].append(f"{persona_id}: {str(e)}")
        
        results["status"] = "completed"
        results["completed_at"] = datetime.utcnow().isoformat()
        
    except Exception as e:
        logger.error(f"Scraping task failed: {e}")
        results["status"] = "failed"
        results["error"] = str(e)
        raise self.retry(exc=e)
    
    return results


@celery_app.task(bind=True, max_retries=3, default_retry_delay=120)
def scrape_youtube_task(
    self,
    persona_ids: List[str],
    max_items: int = 50,
    include_recommendations: bool = True
) -> Dict[str, Any]:
    """
    Scrape YouTube content for specified personas.
    
    Args:
        persona_ids: List of persona IDs to scrape for.
        max_items: Maximum items per persona.
        include_recommendations: Whether to follow related video trails.
        
    Returns:
        Summary of scraping results.
    """
    job_id = self.request.id
    results = {
        "job_id": job_id,
        "platform": "youtube",
        "status": "running",
        "started_at": datetime.utcnow().isoformat(),
        "personas_processed": [],
        "total_items": 0,
        "errors": []
    }
    
    try:
        scraper = YouTubeScraper()
        
        if not scraper.validate_credentials():
            raise ValueError("Invalid YouTube credentials")
        
        for persona_id in persona_ids:
            try:
                persona = get_persona(persona_id)
                if not persona:
                    results["errors"].append(f"Persona not found: {persona_id}")
                    continue
                
                logger.info(f"Scraping YouTube for persona: {persona_id}")
                
                # Update task state
                self.update_state(
                    state="PROGRESS",
                    meta={
                        "current_persona": persona_id,
                        "progress": len(results["personas_processed"]) / len(persona_ids)
                    }
                )
                
                # Scrape content
                scrape_result = scraper.scrape_for_persona(
                    persona=persona,
                    max_items=max_items,
                    include_recommendations=include_recommendations
                )
                
                # Store results in MongoDB
                db = get_mongo_db()
                for item in scrape_result.content:
                    db.content.insert_one({
                        "job_id": job_id,
                        "persona_id": persona_id,
                        "platform": "youtube",
                        "content_id": item.content_id,
                        "title": item.title,
                        "body": item.body,
                        "author": item.author,
                        "url": item.url,
                        "metadata": item.metadata,
                        "collected_at": datetime.utcnow()
                    })
                
                results["personas_processed"].append({
                    "persona_id": persona_id,
                    "items_collected": len(scrape_result.content),
                    "recommendations_found": len(scrape_result.recommendations)
                })
                results["total_items"] += len(scrape_result.content)
                
            except Exception as e:
                logger.error(f"Error scraping YouTube for {persona_id}: {e}")
                results["errors"].append(f"{persona_id}: {str(e)}")
        
        results["status"] = "completed"
        results["completed_at"] = datetime.utcnow().isoformat()
        
    except Exception as e:
        logger.error(f"YouTube scraping task failed: {e}")
        results["status"] = "failed"
        results["error"] = str(e)
        raise self.retry(exc=e)
    
    return results
