"""
Analysis Background Tasks.

Celery tasks for NLP and ML analysis processing.
"""

import logging
from typing import List, Dict, Any, Optional
from datetime import datetime

from .celery_app import celery_app
from database.connection import get_mongo_db, get_session_factory
from database.postgres_models import AnalysisResultModel

logger = logging.getLogger(__name__)


@celery_app.task(bind=True, max_retries=2)
def run_topic_analysis(
    self,
    job_id: str,
    platform: str = "reddit",
    persona_ids: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Run topic modeling analysis on collected content.
    
    Args:
        job_id: The scraping job ID to analyze.
        platform: Platform to analyze.
        persona_ids: Optional filter for specific personas.
        
    Returns:
        Topic analysis results.
    """
    from nlp import TopicModeler
    
    results = {
        "task_id": self.request.id,
        "job_id": job_id,
        "analysis_type": "topic_modeling",
        "status": "running",
        "started_at": datetime.utcnow().isoformat()
    }
    
    try:
        # Fetch content from MongoDB
        db = get_mongo_db()
        query = {"job_id": job_id, "platform": platform}
        if persona_ids:
            query["persona_id"] = {"$in": persona_ids}
        
        content = list(db.content.find(query))
        
        if not content:
            results["status"] = "completed"
            results["message"] = "No content found for analysis"
            return results
        
        # Extract text
        texts = []
        doc_ids = []
        for item in content:
            text = f"{item.get('title', '')} {item.get('body', '')}"
            if text.strip():
                texts.append(text)
                doc_ids.append(item.get("content_id", str(item.get("_id"))))
        
        # Run topic modeling
        modeler = TopicModeler()
        analysis_result = modeler.fit_transform(texts, doc_ids)
        
        # Store results
        results["topics"] = [
            {
                "topic_id": t.topic_id,
                "label": t.label,
                "keywords": t.keywords[:5],
                "size": t.size
            }
            for t in analysis_result.topics
        ]
        results["total_documents"] = analysis_result.total_documents
        results["num_topics"] = len(analysis_result.topics)
        results["outlier_count"] = analysis_result.outlier_count
        results["status"] = "completed"
        results["completed_at"] = datetime.utcnow().isoformat()
        
        # Store in MongoDB
        db.analysis.insert_one({
            "task_id": self.request.id,
            "job_id": job_id,
            "analysis_type": "topic_modeling",
            "results": results,
            "created_at": datetime.utcnow()
        })
        
    except Exception as e:
        logger.error(f"Topic analysis failed: {e}")
        results["status"] = "failed"
        results["error"] = str(e)
        raise self.retry(exc=e)
    
    return results


@celery_app.task(bind=True, max_retries=2)
def run_bias_analysis(
    self,
    job_id: str,
    persona_id: str,
    platform: str = "reddit"
) -> Dict[str, Any]:
    """
    Run bias detection analysis on persona's content.
    
    Args:
        job_id: The scraping job ID to analyze.
        persona_id: Specific persona to analyze.
        platform: Platform to analyze.
        
    Returns:
        Bias analysis results.
    """
    from nlp import BiasDetector
    
    results = {
        "task_id": self.request.id,
        "job_id": job_id,
        "persona_id": persona_id,
        "analysis_type": "bias_detection",
        "status": "running",
        "started_at": datetime.utcnow().isoformat()
    }
    
    try:
        # Fetch content from MongoDB
        db = get_mongo_db()
        content = list(db.content.find({
            "job_id": job_id,
            "platform": platform,
            "persona_id": persona_id
        }))
        
        if not content:
            results["status"] = "completed"
            results["message"] = "No content found for analysis"
            return results
        
        # Extract text
        texts = [
            f"{item.get('title', '')} {item.get('body', '')}"
            for item in content
        ]
        
        # Run bias detection
        detector = BiasDetector()
        bias_results = detector.analyze_batch(texts[:100])  # Limit for performance
        
        # Aggregate results
        summary = detector.get_corpus_summary(bias_results)
        
        results.update({
            "total_analyzed": summary.get("total_analyzed", 0),
            "political_distribution": summary.get("political_distribution", {}),
            "average_sensationalism": summary.get("average_sensationalism", 0),
            "average_clickbait": summary.get("average_clickbait", 0),
            "average_composite_bias": summary.get("average_composite_bias", 0),
            "status": "completed",
            "completed_at": datetime.utcnow().isoformat()
        })
        
        # Store in MongoDB
        db.analysis.insert_one({
            "task_id": self.request.id,
            "job_id": job_id,
            "persona_id": persona_id,
            "analysis_type": "bias_detection",
            "results": results,
            "created_at": datetime.utcnow()
        })
        
    except Exception as e:
        logger.error(f"Bias analysis failed: {e}")
        results["status"] = "failed"
        results["error"] = str(e)
        raise self.retry(exc=e)
    
    return results


@celery_app.task(bind=True, max_retries=2)
def run_diversity_analysis(
    self,
    job_id: str,
    persona_id: str,
    platform: str = "reddit"
) -> Dict[str, Any]:
    """
    Run diversity metrics analysis on persona's content.
    
    Args:
        job_id: The scraping job ID to analyze.
        persona_id: Specific persona to analyze.
        platform: Platform to analyze.
        
    Returns:
        Diversity analysis results.
    """
    from ml import DiversityAnalyzer
    
    results = {
        "task_id": self.request.id,
        "job_id": job_id,
        "persona_id": persona_id,
        "analysis_type": "diversity",
        "status": "running",
        "started_at": datetime.utcnow().isoformat()
    }
    
    try:
        # Fetch content from MongoDB
        db = get_mongo_db()
        content = list(db.content.find({
            "job_id": job_id,
            "platform": platform,
            "persona_id": persona_id
        }))
        
        if not content:
            results["status"] = "completed"
            results["message"] = "No content found for analysis"
            return results
        
        # Prepare content items
        content_items = [
            {
                "text": f"{item.get('title', '')} {item.get('body', '')}",
                "source": item.get("metadata", {}).get("subreddit") or 
                         item.get("metadata", {}).get("channel_name") or "unknown",
                "timestamp": item.get("collected_at")
            }
            for item in content
        ]
        
        # Run diversity analysis
        analyzer = DiversityAnalyzer()
        metrics = analyzer.calculate_metrics(content_items)
        
        results.update({
            "topic_diversity": metrics.topic_diversity,
            "stance_diversity": metrics.stance_diversity,
            "source_diversity": metrics.source_diversity,
            "semantic_diversity": metrics.semantic_diversity,
            "temporal_diversity": metrics.temporal_diversity,
            "echo_chamber_score": metrics.echo_chamber_score,
            "filter_bubble_severity": metrics.filter_bubble_severity,
            "unique_sources": metrics.unique_sources,
            "total_items": metrics.total_items,
            "status": "completed",
            "completed_at": datetime.utcnow().isoformat()
        })
        
        # Store in MongoDB
        db.analysis.insert_one({
            "task_id": self.request.id,
            "job_id": job_id,
            "persona_id": persona_id,
            "analysis_type": "diversity",
            "results": results,
            "created_at": datetime.utcnow()
        })
        
    except Exception as e:
        logger.error(f"Diversity analysis failed: {e}")
        results["status"] = "failed"
        results["error"] = str(e)
        raise self.retry(exc=e)
    
    return results


@celery_app.task(bind=True)
def run_full_analysis_pipeline(
    self,
    job_id: str,
    persona_ids: List[str],
    platform: str = "reddit"
) -> Dict[str, Any]:
    """
    Run full analysis pipeline for a scraping job.
    
    Chains topic modeling, bias detection, and diversity analysis.
    """
    from celery import chain, group
    
    results = {
        "task_id": self.request.id,
        "job_id": job_id,
        "status": "running",
        "started_at": datetime.utcnow().isoformat()
    }
    
    try:
        # Create task workflow
        # First run topic modeling on all content
        topic_task = run_topic_analysis.s(job_id, platform, persona_ids)
        
        # Then run bias and diversity in parallel for each persona
        persona_tasks = group([
            group([
                run_bias_analysis.s(job_id, persona_id, platform),
                run_diversity_analysis.s(job_id, persona_id, platform)
            ])
            for persona_id in persona_ids
        ])
        
        # Chain: topics first, then persona analyses
        workflow = chain(topic_task, persona_tasks)
        workflow.apply_async()
        
        results["status"] = "submitted"
        results["message"] = f"Analysis pipeline started for {len(persona_ids)} personas"
        
    except Exception as e:
        logger.error(f"Full analysis pipeline failed: {e}")
        results["status"] = "failed"
        results["error"] = str(e)
    
    return results
