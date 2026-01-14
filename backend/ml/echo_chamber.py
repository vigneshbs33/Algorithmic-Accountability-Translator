"""
Echo Chamber Detection.

Identifies and quantifies echo chamber effects in content recommendations
by analyzing content similarity and ideological clustering.
"""

from dataclasses import dataclass
from typing import List, Dict, Optional, Tuple
import logging

try:
    import numpy as np
    from sentence_transformers import SentenceTransformer
    from sklearn.cluster import KMeans
    from sklearn.metrics.pairwise import cosine_similarity
    from sklearn.decomposition import PCA
    ML_AVAILABLE = True
except ImportError:
    ML_AVAILABLE = False

from config import settings


logger = logging.getLogger(__name__)


@dataclass
class EchoChamberResult:
    """Result of echo chamber detection."""
    is_echo_chamber: bool
    confidence: float
    echo_chamber_score: float  # 0-1, higher = stronger echo chamber
    
    # Detailed metrics
    content_similarity: float  # Average pairwise similarity
    ideological_clustering: float  # How clustered ideologically
    viewpoint_suppression: float  # How much alternative views are suppressed
    
    # Cluster info
    num_clusters: int
    dominant_cluster_size: float  # Proportion in largest cluster
    
    # Recommendations
    severity: str  # low, medium, high, severe
    description: str


@dataclass
class ContentCluster:
    """Represents a cluster of similar content."""
    cluster_id: int
    size: int
    proportion: float
    centroid_text: str  # Representative text
    dominant_stance: Optional[str]
    keywords: List[str]


class EchoChamberDetector:
    """
    Detects echo chamber effects in content recommendations.
    
    Uses clustering and similarity analysis to identify when
    recommendations form ideologically homogeneous bubbles.
    """
    
    def __init__(self):
        """Initialize echo chamber detector."""
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
    
    def detect(
        self,
        content_texts: List[str],
        content_stances: Optional[List[str]] = None,
        expected_stance_distribution: Optional[Dict[str, float]] = None
    ) -> EchoChamberResult:
        """
        Detect echo chamber effects in a set of content.
        
        Args:
            content_texts: List of content texts.
            content_stances: Optional stance labels for each content.
            expected_stance_distribution: Expected balanced distribution of stances.
            
        Returns:
            EchoChamberResult with detection details.
        """
        if len(content_texts) < 5:
            return EchoChamberResult(
                is_echo_chamber=False,
                confidence=0.0,
                echo_chamber_score=0.0,
                content_similarity=0.0,
                ideological_clustering=0.0,
                viewpoint_suppression=0.0,
                num_clusters=0,
                dominant_cluster_size=0.0,
                severity="low",
                description="Insufficient content for analysis"
            )
        
        # Get embeddings
        model = self._get_embedding_model()
        embeddings = model.encode(content_texts)
        
        # Calculate content similarity
        content_similarity = self._calculate_content_similarity(embeddings)
        
        # Perform clustering
        clusters, cluster_labels = self._cluster_content(embeddings)
        
        # Calculate ideological clustering
        if content_stances:
            ideological_clustering = self._calculate_ideological_clustering(
                cluster_labels, content_stances
            )
        else:
            ideological_clustering = self._estimate_ideological_clustering(
                embeddings, cluster_labels
            )
        
        # Calculate viewpoint suppression
        viewpoint_suppression = self._calculate_viewpoint_suppression(
            content_stances, expected_stance_distribution
        )
        
        # Calculate dominant cluster size
        cluster_sizes = np.bincount(cluster_labels)
        dominant_cluster_size = max(cluster_sizes) / len(cluster_labels)
        
        # Calculate echo chamber score
        echo_chamber_score = (
            content_similarity * 0.3 +
            ideological_clustering * 0.3 +
            viewpoint_suppression * 0.2 +
            dominant_cluster_size * 0.2
        )
        
        # Determine if echo chamber
        is_echo_chamber = echo_chamber_score >= 0.6
        confidence = min(1.0, echo_chamber_score + 0.2) if is_echo_chamber else 1 - echo_chamber_score
        
        # Determine severity
        if echo_chamber_score >= 0.8:
            severity = "severe"
            description = "Strong echo chamber detected. Content is highly homogeneous with minimal alternative viewpoints."
        elif echo_chamber_score >= 0.6:
            severity = "high"
            description = "Significant echo chamber effects. Most content reinforces similar perspectives."
        elif echo_chamber_score >= 0.4:
            severity = "medium"
            description = "Moderate echo chamber tendencies. Some diversity exists but dominant viewpoints prevail."
        else:
            severity = "low"
            description = "Low echo chamber effects. Content shows reasonable diversity."
        
        return EchoChamberResult(
            is_echo_chamber=is_echo_chamber,
            confidence=confidence,
            echo_chamber_score=echo_chamber_score,
            content_similarity=content_similarity,
            ideological_clustering=ideological_clustering,
            viewpoint_suppression=viewpoint_suppression,
            num_clusters=len(cluster_sizes),
            dominant_cluster_size=dominant_cluster_size,
            severity=severity,
            description=description
        )
    
    def _calculate_content_similarity(self, embeddings: np.ndarray) -> float:
        """Calculate average pairwise content similarity."""
        similarities = cosine_similarity(embeddings)
        
        # Get upper triangle (excluding diagonal)
        n = len(embeddings)
        total_sim = 0
        count = 0
        for i in range(n):
            for j in range(i + 1, n):
                total_sim += similarities[i][j]
                count += 1
        
        return total_sim / count if count > 0 else 0.0
    
    def _cluster_content(
        self,
        embeddings: np.ndarray,
        max_clusters: int = 5
    ) -> Tuple[List[ContentCluster], np.ndarray]:
        """
        Cluster content embeddings.
        
        Returns:
            Tuple of (cluster info, cluster labels for each item).
        """
        # Determine optimal number of clusters (simple heuristic)
        n_samples = len(embeddings)
        n_clusters = min(max_clusters, max(2, n_samples // 10))
        
        # Perform k-means clustering
        kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
        labels = kmeans.fit_predict(embeddings)
        
        # Build cluster info
        clusters = []
        for cluster_id in range(n_clusters):
            mask = labels == cluster_id
            size = mask.sum()
            proportion = size / len(labels)
            
            clusters.append(ContentCluster(
                cluster_id=cluster_id,
                size=size,
                proportion=proportion,
                centroid_text="",  # Would need original texts
                dominant_stance=None,
                keywords=[]
            ))
        
        return clusters, labels
    
    def _calculate_ideological_clustering(
        self,
        cluster_labels: np.ndarray,
        stances: List[str]
    ) -> float:
        """
        Calculate how ideologically clustered the content is.
        
        Higher score = content with same stance tends to cluster together.
        """
        if not stances or len(stances) != len(cluster_labels):
            return 0.5
        
        # For each cluster, calculate stance homogeneity
        unique_clusters = np.unique(cluster_labels)
        total_homogeneity = 0
        
        for cluster_id in unique_clusters:
            mask = cluster_labels == cluster_id
            cluster_stances = [s for s, m in zip(stances, mask) if m]
            
            if cluster_stances:
                # Calculate proportion of dominant stance
                stance_counts = {}
                for s in cluster_stances:
                    stance_counts[s] = stance_counts.get(s, 0) + 1
                
                dominant_count = max(stance_counts.values())
                homogeneity = dominant_count / len(cluster_stances)
                total_homogeneity += homogeneity
        
        return total_homogeneity / len(unique_clusters) if unique_clusters.size > 0 else 0.0
    
    def _estimate_ideological_clustering(
        self,
        embeddings: np.ndarray,
        cluster_labels: np.ndarray
    ) -> float:
        """
        Estimate ideological clustering without explicit stance labels.
        
        Uses within-cluster vs between-cluster similarity.
        """
        similarities = cosine_similarity(embeddings)
        
        # Calculate within-cluster similarity
        within_sim = 0
        within_count = 0
        
        # Calculate between-cluster similarity
        between_sim = 0
        between_count = 0
        
        n = len(embeddings)
        for i in range(n):
            for j in range(i + 1, n):
                if cluster_labels[i] == cluster_labels[j]:
                    within_sim += similarities[i][j]
                    within_count += 1
                else:
                    between_sim += similarities[i][j]
                    between_count += 1
        
        avg_within = within_sim / within_count if within_count > 0 else 0
        avg_between = between_sim / between_count if between_count > 0 else 0
        
        # Higher ratio = stronger clustering = more echo chamber
        if avg_between > 0:
            ratio = avg_within / avg_between
            return min(1.0, (ratio - 1) / 2)  # Normalize
        return 0.5
    
    def _calculate_viewpoint_suppression(
        self,
        stances: Optional[List[str]],
        expected_distribution: Optional[Dict[str, float]]
    ) -> float:
        """
        Calculate how much alternative viewpoints are suppressed.
        
        Compares actual stance distribution to expected balanced distribution.
        """
        if not stances:
            return 0.5
        
        # Default expected distribution
        if expected_distribution is None:
            expected_distribution = {
                "favor": 0.33,
                "against": 0.33,
                "neutral": 0.34
            }
        
        # Calculate actual distribution
        stance_counts = {}
        for s in stances:
            stance_counts[s] = stance_counts.get(s, 0) + 1
        
        total = len(stances)
        actual_distribution = {
            k: v / total for k, v in stance_counts.items()
        }
        
        # Calculate deviation from expected
        total_deviation = 0
        for stance, expected_prop in expected_distribution.items():
            actual_prop = actual_distribution.get(stance, 0)
            total_deviation += abs(actual_prop - expected_prop)
        
        # Normalize (max deviation = 2.0)
        return min(1.0, total_deviation / 2)
    
    def compare_personas(
        self,
        persona_results: Dict[str, EchoChamberResult]
    ) -> Dict[str, Dict]:
        """
        Compare echo chamber effects across personas.
        
        Returns:
            Comparison summary for each persona.
        """
        if not persona_results:
            return {}
        
        # Calculate baseline
        all_scores = [r.echo_chamber_score for r in persona_results.values()]
        avg_score = sum(all_scores) / len(all_scores)
        
        # Rank personas
        sorted_personas = sorted(
            persona_results.items(),
            key=lambda x: x[1].echo_chamber_score,
            reverse=True
        )
        
        comparisons = {}
        for rank, (persona_id, result) in enumerate(sorted_personas, 1):
            comparisons[persona_id] = {
                "rank": rank,
                "echo_chamber_score": result.echo_chamber_score,
                "severity": result.severity,
                "delta_from_average": result.echo_chamber_score - avg_score,
                "is_echo_chamber": result.is_echo_chamber,
                "description": result.description
            }
        
        return comparisons
