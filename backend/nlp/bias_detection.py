"""
Bias Detection Pipeline.

Multi-faceted bias analysis including political bias, emotional tone,
fact/opinion classification, and sensationalism detection.
"""

from dataclasses import dataclass
from typing import List, Dict, Optional
from enum import Enum
import logging
import re

try:
    import torch
    from transformers import pipeline
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False


logger = logging.getLogger(__name__)


class PoliticalBias(Enum):
    """Political bias classifications."""
    LEFT = "left"
    CENTER_LEFT = "center_left"
    CENTER = "center"
    CENTER_RIGHT = "center_right"
    RIGHT = "right"


class EmotionalTone(Enum):
    """Emotional tone categories."""
    FEAR = "fear"
    ANGER = "anger"
    HOPE = "hope"
    SADNESS = "sadness"
    JOY = "joy"
    NEUTRAL = "neutral"


@dataclass
class BiasAnalysisResult:
    """Complete bias analysis result."""
    text: str
    political_bias: PoliticalBias
    political_confidence: float
    emotional_tones: Dict[str, float]
    primary_emotion: EmotionalTone
    fact_opinion_ratio: float  # 0 = all opinion, 1 = all fact
    sensationalism_score: float  # 0-1, higher = more sensational
    clickbait_score: float  # 0-1, higher = more clickbait
    composite_bias_score: float  # Overall bias score 0-1


class BiasDetector:
    """
    Multi-faceted bias detection pipeline.
    
    Analyzes content for political bias, emotional manipulation,
    factuality, and sensationalism.
    """
    
    def __init__(self):
        """Initialize bias detection components."""
        if not TRANSFORMERS_AVAILABLE:
            raise ImportError(
                "Transformers is not installed. "
                "Run: pip install transformers torch"
            )
        
        self._emotion_classifier = None
        self._zero_shot_classifier = None
        
        # Clickbait patterns
        self._clickbait_patterns = [
            r"you won't believe",
            r"what happens next",
            r"shocking",
            r"mind-blowing",
            r"this is why",
            r"here's why",
            r"the truth about",
            r"they don't want you to know",
            r"\d+ reasons",
            r"\d+ things",
            r"number \d+ will",
            r"!!+",
            r"\?\?+",
            r"BREAKING",
            r"URGENT",
            r"SECRET",
        ]
        
        # Sensationalism indicators
        self._sensational_words = [
            "shocking", "explosive", "bombshell", "devastating",
            "incredible", "unbelievable", "terrifying", "horrifying",
            "outrageous", "scandalous", "catastrophic", "unprecedented",
            "massive", "huge", "enormous", "epic", "insane", "crazy"
        ]
        
        # Opinion indicators
        self._opinion_indicators = [
            "i think", "i believe", "in my opinion", "seems to me",
            "arguably", "perhaps", "maybe", "could be", "might be",
            "should", "must", "ought to", "need to"
        ]
    
    def _get_emotion_classifier(self):
        """Get emotion classification pipeline."""
        if self._emotion_classifier is None:
            logger.info("Loading emotion classifier...")
            self._emotion_classifier = pipeline(
                "text-classification",
                model="j-hartmann/emotion-english-distilroberta-base",
                top_k=None,
                device=0 if torch.cuda.is_available() else -1
            )
        return self._emotion_classifier
    
    def _get_zero_shot_classifier(self):
        """Get zero-shot classifier for political bias."""
        if self._zero_shot_classifier is None:
            logger.info("Loading zero-shot classifier...")
            self._zero_shot_classifier = pipeline(
                "zero-shot-classification",
                model="facebook/bart-large-mnli",
                device=0 if torch.cuda.is_available() else -1
            )
        return self._zero_shot_classifier
    
    def analyze(self, text: str) -> BiasAnalysisResult:
        """
        Perform comprehensive bias analysis on text.
        
        Args:
            text: The text to analyze.
            
        Returns:
            BiasAnalysisResult with all bias metrics.
        """
        # Political bias detection
        political_bias, political_confidence = self._detect_political_bias(text)
        
        # Emotional tone analysis
        emotional_tones = self._analyze_emotional_tone(text)
        primary_emotion = EmotionalTone(
            max(emotional_tones.items(), key=lambda x: x[1])[0]
        )
        
        # Fact/opinion analysis
        fact_opinion_ratio = self._analyze_fact_opinion(text)
        
        # Sensationalism detection
        sensationalism_score = self._detect_sensationalism(text)
        
        # Clickbait detection
        clickbait_score = self._detect_clickbait(text)
        
        # Calculate composite bias score
        # Higher = more biased/manipulative
        composite_bias_score = self._calculate_composite_score(
            political_confidence=political_confidence,
            emotional_intensity=1 - emotional_tones.get("neutral", 0),
            opinion_ratio=1 - fact_opinion_ratio,
            sensationalism=sensationalism_score,
            clickbait=clickbait_score
        )
        
        return BiasAnalysisResult(
            text=text[:200] + "..." if len(text) > 200 else text,
            political_bias=political_bias,
            political_confidence=political_confidence,
            emotional_tones=emotional_tones,
            primary_emotion=primary_emotion,
            fact_opinion_ratio=fact_opinion_ratio,
            sensationalism_score=sensationalism_score,
            clickbait_score=clickbait_score,
            composite_bias_score=composite_bias_score
        )
    
    def _detect_political_bias(self, text: str) -> tuple:
        """
        Detect political bias in text.
        
        Returns:
            Tuple of (PoliticalBias, confidence)
        """
        classifier = self._get_zero_shot_classifier()
        
        candidate_labels = [
            "liberal progressive left-wing",
            "moderate centrist",
            "conservative right-wing"
        ]
        
        result = classifier(
            text[:512],  # Limit length for efficiency
            candidate_labels,
            multi_label=False
        )
        
        # Map to political bias
        label = result["labels"][0]
        confidence = result["scores"][0]
        
        if "liberal" in label or "left" in label:
            if confidence > 0.7:
                return PoliticalBias.LEFT, confidence
            else:
                return PoliticalBias.CENTER_LEFT, confidence
        elif "conservative" in label or "right" in label:
            if confidence > 0.7:
                return PoliticalBias.RIGHT, confidence
            else:
                return PoliticalBias.CENTER_RIGHT, confidence
        else:
            return PoliticalBias.CENTER, confidence
    
    def _analyze_emotional_tone(self, text: str) -> Dict[str, float]:
        """
        Analyze emotional tone of text.
        
        Returns:
            Dictionary mapping emotions to scores.
        """
        classifier = self._get_emotion_classifier()
        
        # Process text (may need to chunk for long texts)
        result = classifier(text[:512])
        
        # Convert to dictionary
        emotions = {}
        for item in result[0]:
            label = item["label"].lower()
            # Map to our emotion categories
            if label in ["fear"]:
                emotions["fear"] = item["score"]
            elif label in ["anger"]:
                emotions["anger"] = item["score"]
            elif label in ["joy", "love"]:
                emotions["hope"] = emotions.get("hope", 0) + item["score"]
            elif label in ["sadness"]:
                emotions["sadness"] = item["score"]
            elif label in ["surprise"]:
                # Distribute to other categories
                pass
            else:
                emotions["neutral"] = emotions.get("neutral", 0) + item["score"]
        
        # Normalize
        total = sum(emotions.values())
        if total > 0:
            emotions = {k: v / total for k, v in emotions.items()}
        
        # Ensure all categories present
        for emotion in ["fear", "anger", "hope", "sadness", "joy", "neutral"]:
            if emotion not in emotions:
                emotions[emotion] = 0.0
        
        return emotions
    
    def _analyze_fact_opinion(self, text: str) -> float:
        """
        Analyze fact vs opinion ratio.
        
        Returns:
            Float 0-1 where 1 = all facts, 0 = all opinion.
        """
        text_lower = text.lower()
        
        # Count opinion indicators
        opinion_count = sum(
            1 for pattern in self._opinion_indicators
            if pattern in text_lower
        )
        
        # Simple heuristic based on sentence count and opinion markers
        sentences = text.split('.')
        sentence_count = len([s for s in sentences if len(s.strip()) > 10])
        
        if sentence_count == 0:
            return 0.5
        
        opinion_ratio = min(1.0, opinion_count / sentence_count)
        return 1 - opinion_ratio
    
    def _detect_sensationalism(self, text: str) -> float:
        """
        Detect sensationalism in text.
        
        Returns:
            Float 0-1 where 1 = highly sensational.
        """
        text_lower = text.lower()
        words = text_lower.split()
        
        if not words:
            return 0.0
        
        # Count sensational words
        sensational_count = sum(
            1 for word in words
            if any(sw in word for sw in self._sensational_words)
        )
        
        # Check for excessive punctuation
        exclamation_count = text.count('!')
        caps_ratio = sum(1 for c in text if c.isupper()) / max(1, len(text))
        
        # Calculate score
        word_score = min(1.0, sensational_count / max(1, len(words)) * 10)
        punct_score = min(1.0, exclamation_count / 5)
        caps_score = min(1.0, caps_ratio * 5)
        
        return (word_score * 0.5 + punct_score * 0.25 + caps_score * 0.25)
    
    def _detect_clickbait(self, text: str) -> float:
        """
        Detect clickbait patterns in text.
        
        Returns:
            Float 0-1 where 1 = highly clickbait.
        """
        text_lower = text.lower()
        
        # Count clickbait pattern matches
        matches = sum(
            1 for pattern in self._clickbait_patterns
            if re.search(pattern, text_lower, re.IGNORECASE)
        )
        
        # Normalize by number of patterns
        return min(1.0, matches / 3)
    
    def _calculate_composite_score(
        self,
        political_confidence: float,
        emotional_intensity: float,
        opinion_ratio: float,
        sensationalism: float,
        clickbait: float
    ) -> float:
        """
        Calculate composite bias score.
        
        Returns:
            Float 0-1 representing overall bias/manipulation level.
        """
        # Weighted average
        weights = {
            "political": 0.2,
            "emotional": 0.25,
            "opinion": 0.2,
            "sensational": 0.2,
            "clickbait": 0.15
        }
        
        # Political confidence only counts if not center
        adjusted_political = political_confidence * 0.5
        
        composite = (
            adjusted_political * weights["political"] +
            emotional_intensity * weights["emotional"] +
            opinion_ratio * weights["opinion"] +
            sensationalism * weights["sensational"] +
            clickbait * weights["clickbait"]
        )
        
        return min(1.0, composite)
    
    def analyze_batch(self, texts: List[str]) -> List[BiasAnalysisResult]:
        """
        Analyze multiple texts for bias.
        
        Args:
            texts: List of texts to analyze.
            
        Returns:
            List of BiasAnalysisResult objects.
        """
        return [self.analyze(text) for text in texts]
    
    def get_corpus_summary(
        self,
        results: List[BiasAnalysisResult]
    ) -> Dict:
        """
        Summarize bias analysis across a corpus.
        
        Args:
            results: List of analysis results.
            
        Returns:
            Summary statistics.
        """
        if not results:
            return {}
        
        # Political bias distribution
        political_counts = {}
        for r in results:
            bias = r.political_bias.value
            political_counts[bias] = political_counts.get(bias, 0) + 1
        
        total = len(results)
        
        return {
            "total_analyzed": total,
            "political_distribution": {
                k: v / total for k, v in political_counts.items()
            },
            "average_sensationalism": sum(r.sensationalism_score for r in results) / total,
            "average_clickbait": sum(r.clickbait_score for r in results) / total,
            "average_composite_bias": sum(r.composite_bias_score for r in results) / total,
            "average_fact_ratio": sum(r.fact_opinion_ratio for r in results) / total
        }
