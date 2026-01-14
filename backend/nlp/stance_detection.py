"""
Stance Detection using fine-tuned BERT.

Classifies content stance on various topics (favor, against, neutral)
and maps content to ideological spectrum.
"""

from dataclasses import dataclass
from typing import List, Dict, Optional, Tuple
from enum import Enum
import logging

try:
    import torch
    from transformers import (
        AutoModelForSequenceClassification,
        AutoTokenizer,
        pipeline
    )
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False

from config import settings


logger = logging.getLogger(__name__)


class Stance(Enum):
    """Stance classification labels."""
    FAVOR = "favor"
    AGAINST = "against"
    NEUTRAL = "neutral"


class IdeologicalLeaning(Enum):
    """Ideological spectrum positions."""
    FAR_LEFT = "far_left"
    LEFT = "left"
    CENTER_LEFT = "center_left"
    CENTER = "center"
    CENTER_RIGHT = "center_right"
    RIGHT = "right"
    FAR_RIGHT = "far_right"


@dataclass
class StanceResult:
    """Result of stance detection."""
    text: str
    target_topic: str
    stance: Stance
    confidence: float
    probabilities: Dict[str, float]


@dataclass
class IdeologicalResult:
    """Result of ideological mapping."""
    text: str
    leaning: IdeologicalLeaning
    confidence: float
    scores: Dict[str, float]


# Pre-defined topics for stance detection
STANCE_TOPICS = [
    "climate_change",
    "universal_healthcare",
    "gun_control",
    "immigration",
    "abortion",
    "minimum_wage",
    "free_trade",
    "cryptocurrency",
    "renewable_energy",
    "social_media_regulation"
]


class StanceDetector:
    """
    BERT-based stance detection and ideological mapping.
    
    Classifies content stance on predefined topics and maps
    overall ideological leaning.
    """
    
    def __init__(self, model_name: str = None):
        """
        Initialize stance detector.
        
        Args:
            model_name: Name of the pre-trained model to use.
        """
        if not TRANSFORMERS_AVAILABLE:
            raise ImportError(
                "Transformers is not installed. "
                "Run: pip install transformers torch"
            )
        
        self.model_name = model_name or settings.stance_model
        self._model = None
        self._tokenizer = None
        self._classifier = None
        
        # Topic-specific keywords for zero-shot classification
        self._topic_templates = {
            "climate_change": "This text expresses {stance} regarding climate change action",
            "universal_healthcare": "This text expresses {stance} regarding universal healthcare",
            "gun_control": "This text expresses {stance} regarding gun control measures",
            "immigration": "This text expresses {stance} regarding immigration policy",
            "abortion": "This text expresses {stance} regarding abortion rights",
            "minimum_wage": "This text expresses {stance} regarding raising minimum wage",
            "free_trade": "This text expresses {stance} regarding free trade agreements",
            "cryptocurrency": "This text expresses {stance} regarding cryptocurrency adoption",
            "renewable_energy": "This text expresses {stance} regarding renewable energy",
            "social_media_regulation": "This text expresses {stance} regarding social media regulation"
        }
    
    def _get_classifier(self):
        """Get or create the zero-shot classifier."""
        if self._classifier is None:
            logger.info("Loading zero-shot classification pipeline...")
            # Use a zero-shot classification model for flexibility
            self._classifier = pipeline(
                "zero-shot-classification",
                model="facebook/bart-large-mnli",
                device=0 if torch.cuda.is_available() else -1
            )
        return self._classifier
    
    def detect_stance(
        self,
        text: str,
        topic: str,
        threshold: float = 0.4
    ) -> StanceResult:
        """
        Detect stance on a specific topic.
        
        Args:
            text: The text to analyze.
            topic: The topic to detect stance for.
            threshold: Confidence threshold for non-neutral classification.
            
        Returns:
            StanceResult with stance and confidence.
        """
        classifier = self._get_classifier()
        
        # Candidate labels for stance
        candidate_labels = [
            f"supports {topic.replace('_', ' ')}",
            f"opposes {topic.replace('_', ' ')}",
            f"neutral about {topic.replace('_', ' ')}"
        ]
        
        result = classifier(
            text,
            candidate_labels,
            multi_label=False
        )
        
        # Map results to stance
        label_to_stance = {
            candidate_labels[0]: Stance.FAVOR,
            candidate_labels[1]: Stance.AGAINST,
            candidate_labels[2]: Stance.NEUTRAL
        }
        
        probabilities = {
            "favor": 0.0,
            "against": 0.0,
            "neutral": 0.0
        }
        
        for label, score in zip(result["labels"], result["scores"]):
            stance = label_to_stance.get(label)
            if stance:
                probabilities[stance.value] = score
        
        # Determine final stance
        top_label = result["labels"][0]
        top_score = result["scores"][0]
        
        if top_score < threshold:
            final_stance = Stance.NEUTRAL
            confidence = probabilities["neutral"]
        else:
            final_stance = label_to_stance[top_label]
            confidence = top_score
        
        return StanceResult(
            text=text[:200] + "..." if len(text) > 200 else text,
            target_topic=topic,
            stance=final_stance,
            confidence=confidence,
            probabilities=probabilities
        )
    
    def detect_stance_batch(
        self,
        texts: List[str],
        topic: str,
        threshold: float = 0.4
    ) -> List[StanceResult]:
        """
        Detect stance for multiple texts.
        
        Args:
            texts: List of texts to analyze.
            topic: The topic to detect stance for.
            threshold: Confidence threshold.
            
        Returns:
            List of StanceResult objects.
        """
        return [
            self.detect_stance(text, topic, threshold)
            for text in texts
        ]
    
    def detect_ideological_leaning(
        self,
        text: str
    ) -> IdeologicalResult:
        """
        Map content to ideological spectrum.
        
        Args:
            text: The text to analyze.
            
        Returns:
            IdeologicalResult with leaning and confidence.
        """
        classifier = self._get_classifier()
        
        # Candidate labels for ideology
        candidate_labels = [
            "progressive liberal left-wing",
            "moderate centrist",
            "conservative right-wing"
        ]
        
        result = classifier(
            text,
            candidate_labels,
            multi_label=False
        )
        
        # Map to ideological positions
        scores = {
            "left": 0.0,
            "center": 0.0,
            "right": 0.0
        }
        
        for label, score in zip(result["labels"], result["scores"]):
            if "liberal" in label or "progressive" in label:
                scores["left"] = score
            elif "centrist" in label or "moderate" in label:
                scores["center"] = score
            elif "conservative" in label or "right" in label:
                scores["right"] = score
        
        # Determine position on spectrum
        max_score = max(scores.values())
        if scores["left"] == max_score:
            if max_score > 0.7:
                leaning = IdeologicalLeaning.LEFT
            else:
                leaning = IdeologicalLeaning.CENTER_LEFT
        elif scores["right"] == max_score:
            if max_score > 0.7:
                leaning = IdeologicalLeaning.RIGHT
            else:
                leaning = IdeologicalLeaning.CENTER_RIGHT
        else:
            leaning = IdeologicalLeaning.CENTER
        
        return IdeologicalResult(
            text=text[:200] + "..." if len(text) > 200 else text,
            leaning=leaning,
            confidence=max_score,
            scores=scores
        )
    
    def analyze_corpus_stance(
        self,
        texts: List[str],
        topics: List[str] = None
    ) -> Dict[str, Dict[str, float]]:
        """
        Analyze stance distribution across a corpus.
        
        Args:
            texts: List of texts to analyze.
            topics: Topics to analyze (defaults to all predefined topics).
            
        Returns:
            Dictionary mapping topics to stance distributions.
        """
        topics = topics or STANCE_TOPICS
        
        results = {}
        for topic in topics:
            stance_counts = {"favor": 0, "against": 0, "neutral": 0}
            
            for text in texts:
                result = self.detect_stance(text, topic)
                stance_counts[result.stance.value] += 1
            
            total = len(texts)
            results[topic] = {
                stance: count / total
                for stance, count in stance_counts.items()
            }
        
        return results
