"""
Topic Modeling using BERTopic.

Extracts latent topics from content collections and tracks topic
distributions across different user personas.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Tuple, Optional
import logging
import numpy as np

try:
    from bertopic import BERTopic
    from sentence_transformers import SentenceTransformer
    BERTOPIC_AVAILABLE = True
except ImportError:
    BERTOPIC_AVAILABLE = False

from config import settings


logger = logging.getLogger(__name__)


@dataclass
class TopicInfo:
    """Information about a discovered topic."""
    topic_id: int
    label: str
    keywords: List[str]
    keyword_scores: List[float]
    size: int  # Number of documents in this topic
    coherence_score: float


@dataclass
class TopicResult:
    """Result of topic analysis for a document."""
    document_id: str
    topic_id: int
    topic_label: str
    confidence: float


@dataclass
class TopicAnalysisResult:
    """Complete topic analysis results."""
    topics: List[TopicInfo]
    document_topics: List[TopicResult]
    total_documents: int
    outlier_count: int  # Documents not assigned to any topic
    model_info: Dict


class TopicModeler:
    """
    BERTopic-based topic modeling for content analysis.
    
    Uses sentence embeddings and HDBSCAN clustering to discover
    semantically coherent topics in collected content.
    """
    
    def __init__(
        self,
        embedding_model: str = None,
        min_topic_size: int = 10,
        nr_topics: str = "auto"
    ):
        """
        Initialize the topic modeler.
        
        Args:
            embedding_model: Name of the sentence transformer model.
            min_topic_size: Minimum documents required to form a topic.
            nr_topics: Number of topics or "auto" for automatic detection.
        """
        if not BERTOPIC_AVAILABLE:
            raise ImportError(
                "BERTopic is not installed. "
                "Run: pip install bertopic sentence-transformers"
            )
        
        self.embedding_model_name = embedding_model or settings.embedding_model
        self._embedding_model = None
        self._topic_model = None
        self.min_topic_size = min_topic_size
        self.nr_topics = nr_topics
    
    def _get_embedding_model(self) -> SentenceTransformer:
        """Get or create embedding model."""
        if self._embedding_model is None:
            logger.info(f"Loading embedding model: {self.embedding_model_name}")
            self._embedding_model = SentenceTransformer(self.embedding_model_name)
        return self._embedding_model
    
    def _get_topic_model(self) -> BERTopic:
        """Get or create topic model."""
        if self._topic_model is None:
            self._topic_model = BERTopic(
                embedding_model=self._get_embedding_model(),
                min_topic_size=self.min_topic_size,
                nr_topics=self.nr_topics if self.nr_topics != "auto" else None,
                verbose=False
            )
        return self._topic_model
    
    def fit_transform(
        self,
        documents: List[str],
        document_ids: Optional[List[str]] = None
    ) -> TopicAnalysisResult:
        """
        Fit topic model and transform documents.
        
        Args:
            documents: List of document texts.
            document_ids: Optional list of document identifiers.
            
        Returns:
            TopicAnalysisResult with topics and assignments.
        """
        if not documents:
            raise ValueError("No documents provided for topic modeling")
        
        if document_ids is None:
            document_ids = [str(i) for i in range(len(documents))]
        
        logger.info(f"Fitting topic model on {len(documents)} documents")
        
        topic_model = self._get_topic_model()
        topics, probabilities = topic_model.fit_transform(documents)
        
        # Get topic info
        topic_info = topic_model.get_topic_info()
        
        # Build topic objects
        topics_list = []
        for _, row in topic_info.iterrows():
            topic_id = row["Topic"]
            if topic_id == -1:  # Outlier topic
                continue
            
            # Get topic keywords
            topic_words = topic_model.get_topic(topic_id)
            if topic_words:
                keywords = [word for word, _ in topic_words[:10]]
                scores = [score for _, score in topic_words[:10]]
            else:
                keywords = []
                scores = []
            
            topics_list.append(TopicInfo(
                topic_id=topic_id,
                label=row.get("Name", f"Topic {topic_id}"),
                keywords=keywords,
                keyword_scores=scores,
                size=row["Count"],
                coherence_score=0.0  # Would need additional computation
            ))
        
        # Build document-topic assignments
        document_topics = []
        for i, (doc_id, topic_id) in enumerate(zip(document_ids, topics)):
            prob = probabilities[i] if probabilities is not None else 0.0
            if isinstance(prob, np.ndarray):
                prob = float(prob.max()) if len(prob) > 0 else 0.0
            
            topic_label = topic_model.get_topic_info(topic_id)["Name"].values[0] if topic_id != -1 else "Outlier"
            
            document_topics.append(TopicResult(
                document_id=doc_id,
                topic_id=topic_id,
                topic_label=topic_label,
                confidence=float(prob)
            ))
        
        # Count outliers
        outlier_count = sum(1 for t in topics if t == -1)
        
        return TopicAnalysisResult(
            topics=topics_list,
            document_topics=document_topics,
            total_documents=len(documents),
            outlier_count=outlier_count,
            model_info={
                "embedding_model": self.embedding_model_name,
                "min_topic_size": self.min_topic_size,
                "num_topics": len(topics_list)
            }
        )
    
    def transform(
        self,
        documents: List[str],
        document_ids: Optional[List[str]] = None
    ) -> List[TopicResult]:
        """
        Transform new documents using fitted model.
        
        Args:
            documents: List of document texts.
            document_ids: Optional list of document identifiers.
            
        Returns:
            List of TopicResult for each document.
        """
        if self._topic_model is None:
            raise ValueError("Model not fitted. Call fit_transform first.")
        
        if document_ids is None:
            document_ids = [str(i) for i in range(len(documents))]
        
        topics, probabilities = self._topic_model.transform(documents)
        
        results = []
        for i, (doc_id, topic_id) in enumerate(zip(document_ids, topics)):
            prob = probabilities[i] if probabilities is not None else 0.0
            if isinstance(prob, np.ndarray):
                prob = float(prob.max()) if len(prob) > 0 else 0.0
            
            topic_label = (
                self._topic_model.get_topic_info(topic_id)["Name"].values[0] 
                if topic_id != -1 else "Outlier"
            )
            
            results.append(TopicResult(
                document_id=doc_id,
                topic_id=topic_id,
                topic_label=topic_label,
                confidence=float(prob)
            ))
        
        return results
    
    def get_topic_distribution(
        self,
        document_topics: List[TopicResult]
    ) -> Dict[str, float]:
        """
        Calculate topic distribution from document assignments.
        
        Args:
            document_topics: List of document-topic assignments.
            
        Returns:
            Dictionary mapping topic labels to proportions.
        """
        if not document_topics:
            return {}
        
        topic_counts = {}
        for dt in document_topics:
            label = dt.topic_label
            topic_counts[label] = topic_counts.get(label, 0) + 1
        
        total = len(document_topics)
        return {
            label: count / total 
            for label, count in topic_counts.items()
        }
    
    def save_model(self, path: str):
        """Save the fitted topic model."""
        if self._topic_model is None:
            raise ValueError("No model to save. Call fit_transform first.")
        self._topic_model.save(path)
        logger.info(f"Topic model saved to {path}")
    
    def load_model(self, path: str):
        """Load a previously saved topic model."""
        self._topic_model = BERTopic.load(path)
        logger.info(f"Topic model loaded from {path}")
