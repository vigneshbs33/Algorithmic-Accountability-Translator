"""
Sentiment Analysis module.

Provides sentiment analysis using both rule-based (VADER) and 
transformer-based approaches.
"""

from dataclasses import dataclass
from typing import List, Dict, Optional
from enum import Enum
import logging

try:
    from transformers import pipeline
    import torch
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False

try:
    from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
    VADER_AVAILABLE = True
except ImportError:
    VADER_AVAILABLE = False


logger = logging.getLogger(__name__)


class SentimentLabel(Enum):
    """Sentiment classification labels."""
    VERY_NEGATIVE = "very_negative"
    NEGATIVE = "negative"
    NEUTRAL = "neutral"
    POSITIVE = "positive"
    VERY_POSITIVE = "very_positive"


@dataclass
class SentimentResult:
    """Result of sentiment analysis."""
    text: str
    label: SentimentLabel
    confidence: float
    scores: Dict[str, float]  # Detailed scores
    
    # VADER-specific scores
    compound_score: Optional[float] = None


@dataclass
class SentimentSummary:
    """Summary of sentiment across multiple texts."""
    total_analyzed: int
    label_distribution: Dict[str, float]
    average_compound: float
    average_positive: float
    average_negative: float
    average_neutral: float


class SentimentAnalyzer:
    """
    Multi-method sentiment analysis.
    
    Combines VADER (rule-based) and transformer-based approaches
    for robust sentiment detection.
    """
    
    def __init__(self, use_transformer: bool = True):
        """
        Initialize sentiment analyzer.
        
        Args:
            use_transformer: Whether to use transformer model (slower but more accurate).
        """
        self.use_transformer = use_transformer and TRANSFORMERS_AVAILABLE
        self._vader = None
        self._transformer_pipeline = None
    
    def _get_vader(self):
        """Get VADER analyzer."""
        if not VADER_AVAILABLE:
            raise ImportError(
                "VADER is not installed. "
                "Run: pip install vaderSentiment"
            )
        
        if self._vader is None:
            self._vader = SentimentIntensityAnalyzer()
        return self._vader
    
    def _get_transformer_pipeline(self):
        """Get transformer sentiment pipeline."""
        if not TRANSFORMERS_AVAILABLE:
            raise ImportError(
                "Transformers is not installed. "
                "Run: pip install transformers torch"
            )
        
        if self._transformer_pipeline is None:
            logger.info("Loading sentiment transformer...")
            self._transformer_pipeline = pipeline(
                "sentiment-analysis",
                model="cardiffnlp/twitter-roberta-base-sentiment-latest",
                device=0 if torch.cuda.is_available() else -1
            )
        return self._transformer_pipeline
    
    def analyze(self, text: str) -> SentimentResult:
        """
        Analyze sentiment of a single text.
        
        Args:
            text: The text to analyze.
            
        Returns:
            SentimentResult with sentiment classification.
        """
        if self.use_transformer:
            return self._analyze_transformer(text)
        else:
            return self._analyze_vader(text)
    
    def _analyze_vader(self, text: str) -> SentimentResult:
        """Analyze using VADER."""
        vader = self._get_vader()
        scores = vader.polarity_scores(text)
        
        compound = scores["compound"]
        
        # Determine label based on compound score
        if compound >= 0.5:
            label = SentimentLabel.VERY_POSITIVE
        elif compound >= 0.1:
            label = SentimentLabel.POSITIVE
        elif compound <= -0.5:
            label = SentimentLabel.VERY_NEGATIVE
        elif compound <= -0.1:
            label = SentimentLabel.NEGATIVE
        else:
            label = SentimentLabel.NEUTRAL
        
        # Confidence based on how extreme the compound score is
        confidence = abs(compound)
        
        return SentimentResult(
            text=text[:200] + "..." if len(text) > 200 else text,
            label=label,
            confidence=confidence,
            scores={
                "positive": scores["pos"],
                "negative": scores["neg"],
                "neutral": scores["neu"]
            },
            compound_score=compound
        )
    
    def _analyze_transformer(self, text: str) -> SentimentResult:
        """Analyze using transformer model."""
        pipeline_model = self._get_transformer_pipeline()
        
        # Truncate text for transformer
        truncated = text[:512]
        result = pipeline_model(truncated)[0]
        
        label_str = result["label"].lower()
        confidence = result["score"]
        
        # Map to our labels
        label_mapping = {
            "positive": SentimentLabel.POSITIVE,
            "negative": SentimentLabel.NEGATIVE,
            "neutral": SentimentLabel.NEUTRAL
        }
        
        label = label_mapping.get(label_str, SentimentLabel.NEUTRAL)
        
        # Adjust for strong sentiments
        if confidence > 0.9:
            if label == SentimentLabel.POSITIVE:
                label = SentimentLabel.VERY_POSITIVE
            elif label == SentimentLabel.NEGATIVE:
                label = SentimentLabel.VERY_NEGATIVE
        
        # Also compute VADER score for compound
        compound = None
        if VADER_AVAILABLE:
            vader = self._get_vader()
            vader_scores = vader.polarity_scores(text)
            compound = vader_scores["compound"]
        
        return SentimentResult(
            text=text[:200] + "..." if len(text) > 200 else text,
            label=label,
            confidence=confidence,
            scores={
                "positive": confidence if "positive" in label_str else 0.0,
                "negative": confidence if "negative" in label_str else 0.0,
                "neutral": confidence if "neutral" in label_str else 0.0
            },
            compound_score=compound
        )
    
    def analyze_batch(self, texts: List[str]) -> List[SentimentResult]:
        """
        Analyze sentiment for multiple texts.
        
        Args:
            texts: List of texts to analyze.
            
        Returns:
            List of SentimentResult objects.
        """
        return [self.analyze(text) for text in texts]
    
    def summarize(self, results: List[SentimentResult]) -> SentimentSummary:
        """
        Summarize sentiment across multiple results.
        
        Args:
            results: List of sentiment results.
            
        Returns:
            SentimentSummary with aggregated statistics.
        """
        if not results:
            return SentimentSummary(
                total_analyzed=0,
                label_distribution={},
                average_compound=0.0,
                average_positive=0.0,
                average_negative=0.0,
                average_neutral=0.0
            )
        
        # Count labels
        label_counts = {}
        for r in results:
            label = r.label.value
            label_counts[label] = label_counts.get(label, 0) + 1
        
        total = len(results)
        
        # Calculate averages
        avg_compound = sum(
            r.compound_score for r in results if r.compound_score is not None
        ) / max(1, len([r for r in results if r.compound_score is not None]))
        
        avg_positive = sum(r.scores.get("positive", 0) for r in results) / total
        avg_negative = sum(r.scores.get("negative", 0) for r in results) / total
        avg_neutral = sum(r.scores.get("neutral", 0) for r in results) / total
        
        return SentimentSummary(
            total_analyzed=total,
            label_distribution={k: v / total for k, v in label_counts.items()},
            average_compound=avg_compound,
            average_positive=avg_positive,
            average_negative=avg_negative,
            average_neutral=avg_neutral
        )
    
    def compare_personas(
        self,
        persona_results: Dict[str, List[SentimentResult]]
    ) -> Dict[str, SentimentSummary]:
        """
        Compare sentiment patterns across personas.
        
        Args:
            persona_results: Dictionary mapping persona IDs to their results.
            
        Returns:
            Dictionary mapping persona IDs to sentiment summaries.
        """
        return {
            persona_id: self.summarize(results)
            for persona_id, results in persona_results.items()
        }
