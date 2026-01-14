"""
Diversity Metrics for measuring filter bubble effects.

Calculates various diversity scores to quantify how filtered
or diverse the recommendations are for each persona.
"""

from dataclasses import dataclass
from typing import List, Dict, Optional, Set
import math
from collections import Counter
import logging

try:
    import numpy as np
    from sentence_transformers import SentenceTransformer
    from sklearn.metrics.pairwise import cosine_similarity
    ML_AVAILABLE = True
except ImportError:
    ML_AVAILABLE = False

from config import settings


logger = logging.getLogger(__name__)


@dataclass
class DiversityMetrics:
    """Diversity metrics for a set of recommendations."""
    topic_diversity: float  # 0-1, higher = more diverse topics
    stance_diversity: float  # 0-1, higher = more diverse stances
    source_diversity: float  # 0-1, higher = more diverse sources
    semantic_diversity: float  # 0-1, higher = more semantically diverse
    temporal_diversity: float  # 0-1, higher = more time range diversity
    
    # Derived metrics
    echo_chamber_score: float  # 0-1, higher = stronger echo chamber
    filter_bubble_severity: str  # low, medium, high, severe
    
    # Raw data
    unique_topics: int
    unique_sources: int
    total_items: int


@dataclass
class ComparativeDiversity:
    """Diversity comparison between personas."""
    persona_id: str
    metrics: DiversityMetrics
    comparison_to_baseline: Dict[str, float]  # Deltas from baseline
    percentile_rank: Dict[str, float]  # Where this persona ranks


class DiversityAnalyzer:
    """
    Analyzer for measuring content diversity and filter bubble effects.
    
    Uses multiple metrics to quantify how algorithmically filtered
    the content recommendations are.
    """
    
    def __init__(self):
        """Initialize diversity analyzer."""
        if not ML_AVAILABLE:
            raise ImportError(
                "Required libraries not installed. "
                "Run: pip install numpy sentence-transformers scikit-learn"
            )
        
        self._embedding_model = None
    
    def _get_embedding_model(self) -> SentenceTransformer:
        """Get sentence embedding model."""
        if self._embedding_model is None:
            logger.info(f"Loading embedding model: {settings.embedding_model}")
            self._embedding_model = SentenceTransformer(settings.embedding_model)
        return self._embedding_model
    
    def calculate_metrics(
        self,
        content_items: List[Dict],
        topic_labels: Optional[List[str]] = None,
        stance_labels: Optional[List[str]] = None
    ) -> DiversityMetrics:
        """
        Calculate diversity metrics for a set of content items.
        
        Args:
            content_items: List of content dictionaries with 'text', 'source', 'timestamp'.
            topic_labels: Optional pre-computed topic labels.
            stance_labels: Optional pre-computed stance labels.
            
        Returns:
            DiversityMetrics for the content set.
        """
        if not content_items:
            return DiversityMetrics(
                topic_diversity=0.0,
                stance_diversity=0.0,
                source_diversity=0.0,
                semantic_diversity=0.0,
                temporal_diversity=0.0,
                echo_chamber_score=1.0,
                filter_bubble_severity="severe",
                unique_topics=0,
                unique_sources=0,
                total_items=0
            )
        
        # Calculate topic diversity
        topic_div = self._calculate_topic_diversity(topic_labels) if topic_labels else 0.5
        
        # Calculate stance diversity
        stance_div = self._calculate_stance_diversity(stance_labels) if stance_labels else 0.5
        
        # Calculate source diversity
        sources = [item.get("source", "unknown") for item in content_items]
        source_div = self._calculate_source_diversity(sources)
        
        # Calculate semantic diversity using embeddings
        texts = [item.get("text", "") for item in content_items if item.get("text")]
        semantic_div = self._calculate_semantic_diversity(texts) if texts else 0.5
        
        # Calculate temporal diversity
        timestamps = [item.get("timestamp") for item in content_items if item.get("timestamp")]
        temporal_div = self._calculate_temporal_diversity(timestamps) if timestamps else 0.5
        
        # Calculate echo chamber score (inverse of average diversity)
        avg_diversity = (topic_div + stance_div + source_div + semantic_div) / 4
        echo_chamber_score = 1 - avg_diversity
        
        # Determine filter bubble severity
        if echo_chamber_score >= 0.8:
            severity = "severe"
        elif echo_chamber_score >= 0.6:
            severity = "high"
        elif echo_chamber_score >= 0.4:
            severity = "medium"
        else:
            severity = "low"
        
        return DiversityMetrics(
            topic_diversity=topic_div,
            stance_diversity=stance_div,
            source_diversity=source_div,
            semantic_diversity=semantic_div,
            temporal_diversity=temporal_div,
            echo_chamber_score=echo_chamber_score,
            filter_bubble_severity=severity,
            unique_topics=len(set(topic_labels)) if topic_labels else 0,
            unique_sources=len(set(sources)),
            total_items=len(content_items)
        )
    
    def _calculate_topic_diversity(self, topics: List[str]) -> float:
        """
        Calculate topic diversity using entropy.
        
        Returns:
            Normalized entropy score 0-1.
        """
        if not topics:
            return 0.0
        
        # Count topic frequencies
        counter = Counter(topics)
        total = len(topics)
        
        # Calculate entropy
        entropy = 0.0
        for count in counter.values():
            if count > 0:
                p = count / total
                entropy -= p * math.log2(p)
        
        # Normalize by maximum entropy
        max_entropy = math.log2(len(counter)) if len(counter) > 1 else 1
        return entropy / max_entropy if max_entropy > 0 else 0.0
    
    def _calculate_stance_diversity(self, stances: List[str]) -> float:
        """
        Calculate stance diversity.
        
        Returns:
            Diversity score 0-1.
        """
        if not stances:
            return 0.0
        
        counter = Counter(stances)
        
        # Ideal distribution would have equal favor/against/neutral
        favor = counter.get("favor", 0)
        against = counter.get("against", 0)
        neutral = counter.get("neutral", 0)
        total = favor + against + neutral
        
        if total == 0:
            return 0.0
        
        # Calculate deviation from ideal (1/3 each)
        ideal = total / 3
        deviation = (
            abs(favor - ideal) + 
            abs(against - ideal) + 
            abs(neutral - ideal)
        ) / (2 * total)  # Normalize
        
        return 1 - deviation
    
    def _calculate_source_diversity(self, sources: List[str]) -> float:
        """
        Calculate source diversity using entropy.
        
        Returns:
            Normalized entropy score 0-1.
        """
        if not sources:
            return 0.0
        
        counter = Counter(sources)
        total = len(sources)
        
        # Calculate entropy
        entropy = 0.0
        for count in counter.values():
            if count > 0:
                p = count / total
                entropy -= p * math.log2(p)
        
        # Normalize (max entropy would be if each item from different source)
        max_entropy = math.log2(min(len(sources), 20))  # Cap at 20 sources
        return min(1.0, entropy / max_entropy) if max_entropy > 0 else 0.0
    
    def _calculate_semantic_diversity(self, texts: List[str]) -> float:
        """
        Calculate semantic diversity using embedding similarity.
        
        Returns:
            Diversity score 0-1 (higher = more diverse).
        """
        if len(texts) < 2:
            return 0.0
        
        # Get embeddings
        model = self._get_embedding_model()
        embeddings = model.encode(texts[:100])  # Limit for efficiency
        
        # Calculate pairwise similarities
        similarities = cosine_similarity(embeddings)
        
        # Get average similarity (excluding self-similarity)
        n = len(embeddings)
        total_sim = 0
        count = 0
        for i in range(n):
            for j in range(i + 1, n):
                total_sim += similarities[i][j]
                count += 1
        
        avg_similarity = total_sim / count if count > 0 else 1.0
        
        # Convert to diversity (1 - similarity)
        return 1 - avg_similarity
    
    def _calculate_temporal_diversity(self, timestamps) -> float:
        """
        Calculate temporal diversity (how spread out the content is in time).
        
        Returns:
            Diversity score 0-1.
        """
        if len(timestamps) < 2:
            return 0.0
        
        # Convert to epoch if needed and sort
        sorted_ts = sorted(timestamps)
        
        # Calculate time range
        try:
            if hasattr(sorted_ts[0], 'timestamp'):
                earliest = sorted_ts[0].timestamp()
                latest = sorted_ts[-1].timestamp()
            else:
                earliest = float(sorted_ts[0])
                latest = float(sorted_ts[-1])
            
            time_range = latest - earliest
            
            # Normalize: 1 hour = 0, 1 week+ = 1
            max_range = 7 * 24 * 3600  # One week in seconds
            return min(1.0, time_range / max_range)
        except:
            return 0.5
    
    def compare_personas(
        self,
        persona_metrics: Dict[str, DiversityMetrics]
    ) -> Dict[str, ComparativeDiversity]:
        """
        Compare diversity metrics across personas.
        
        Args:
            persona_metrics: Dictionary mapping persona IDs to their metrics.
            
        Returns:
            Comparative analysis for each persona.
        """
        if not persona_metrics:
            return {}
        
        # Calculate baseline (average across all personas)
        all_metrics = list(persona_metrics.values())
        baseline = {
            "topic_diversity": sum(m.topic_diversity for m in all_metrics) / len(all_metrics),
            "stance_diversity": sum(m.stance_diversity for m in all_metrics) / len(all_metrics),
            "source_diversity": sum(m.source_diversity for m in all_metrics) / len(all_metrics),
            "semantic_diversity": sum(m.semantic_diversity for m in all_metrics) / len(all_metrics),
            "echo_chamber_score": sum(m.echo_chamber_score for m in all_metrics) / len(all_metrics)
        }
        
        # Calculate percentile ranks
        sorted_by_echo = sorted(
            persona_metrics.items(),
            key=lambda x: x[1].echo_chamber_score
        )
        
        comparisons = {}
        for i, (persona_id, metrics) in enumerate(sorted_by_echo):
            comparisons[persona_id] = ComparativeDiversity(
                persona_id=persona_id,
                metrics=metrics,
                comparison_to_baseline={
                    "topic_diversity": metrics.topic_diversity - baseline["topic_diversity"],
                    "stance_diversity": metrics.stance_diversity - baseline["stance_diversity"],
                    "source_diversity": metrics.source_diversity - baseline["source_diversity"],
                    "semantic_diversity": metrics.semantic_diversity - baseline["semantic_diversity"],
                    "echo_chamber_score": metrics.echo_chamber_score - baseline["echo_chamber_score"]
                },
                percentile_rank={
                    "echo_chamber": i / len(sorted_by_echo) * 100
                }
            )
        
        return comparisons
