"""
Entity Extraction using SpaCy.

Extracts named entities (people, organizations, locations, events)
and links them to knowledge bases for context.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Set
from collections import Counter
import logging

try:
    import spacy
    from spacy.tokens import Doc
    SPACY_AVAILABLE = True
except ImportError:
    SPACY_AVAILABLE = False

from config import settings


logger = logging.getLogger(__name__)


@dataclass
class Entity:
    """Represents an extracted entity."""
    text: str
    label: str  # PERSON, ORG, GPE, EVENT, etc.
    start_char: int
    end_char: int
    confidence: float = 1.0
    
    # Knowledge base linking (optional)
    kb_id: Optional[str] = None  # e.g., Wikidata QID
    kb_url: Optional[str] = None


@dataclass
class EntityExtractionResult:
    """Result of entity extraction from a document."""
    document_id: str
    text: str
    entities: List[Entity]
    entity_counts: Dict[str, int]  # Label -> count
    unique_entities: Dict[str, Set[str]]  # Label -> set of unique entity texts


@dataclass
class EntityAnalysis:
    """Aggregated entity analysis across multiple documents."""
    total_documents: int
    total_entities: int
    entity_type_distribution: Dict[str, int]
    most_common_entities: Dict[str, List[tuple]]  # Label -> [(entity, count), ...]
    entity_co_occurrence: Dict[str, Dict[str, int]]  # entity1 -> {entity2: count}


class EntityExtractor:
    """
    SpaCy-based named entity recognition and analysis.
    
    Extracts entities from text and tracks patterns of entity
    amplification/suppression across content.
    """
    
    def __init__(self, model_name: str = None):
        """
        Initialize entity extractor.
        
        Args:
            model_name: SpaCy model to use.
        """
        if not SPACY_AVAILABLE:
            raise ImportError(
                "SpaCy is not installed. "
                "Run: pip install spacy && python -m spacy download en_core_web_sm"
            )
        
        self.model_name = model_name or settings.spacy_model
        self._nlp = None
        
        # Entity types we care about
        self.entity_types = [
            "PERSON",      # People
            "ORG",         # Organizations
            "GPE",         # Geo-political entities (countries, cities)
            "EVENT",       # Named events
            "WORK_OF_ART", # Titles of works
            "LAW",         # Laws/regulations
            "PRODUCT",     # Products
            "NORP",        # Nationalities, religious/political groups
        ]
    
    def _get_nlp(self):
        """Get or load SpaCy model."""
        if self._nlp is None:
            logger.info(f"Loading SpaCy model: {self.model_name}")
            try:
                self._nlp = spacy.load(self.model_name)
            except OSError:
                logger.warning(f"Model {self.model_name} not found, downloading...")
                spacy.cli.download(self.model_name)
                self._nlp = spacy.load(self.model_name)
        return self._nlp
    
    def extract_entities(
        self,
        text: str,
        document_id: str = None
    ) -> EntityExtractionResult:
        """
        Extract entities from a single document.
        
        Args:
            text: The text to process.
            document_id: Optional identifier for the document.
            
        Returns:
            EntityExtractionResult with extracted entities.
        """
        nlp = self._get_nlp()
        doc = nlp(text)
        
        entities = []
        entity_counts = Counter()
        unique_entities = {et: set() for et in self.entity_types}
        
        for ent in doc.ents:
            if ent.label_ in self.entity_types:
                entity = Entity(
                    text=ent.text,
                    label=ent.label_,
                    start_char=ent.start_char,
                    end_char=ent.end_char,
                    confidence=1.0  # SpaCy doesn't provide confidence by default
                )
                entities.append(entity)
                entity_counts[ent.label_] += 1
                unique_entities[ent.label_].add(ent.text)
        
        return EntityExtractionResult(
            document_id=document_id or "unknown",
            text=text[:200] + "..." if len(text) > 200 else text,
            entities=entities,
            entity_counts=dict(entity_counts),
            unique_entities={k: v for k, v in unique_entities.items() if v}
        )
    
    def extract_entities_batch(
        self,
        texts: List[str],
        document_ids: List[str] = None
    ) -> List[EntityExtractionResult]:
        """
        Extract entities from multiple documents efficiently.
        
        Args:
            texts: List of texts to process.
            document_ids: Optional list of document identifiers.
            
        Returns:
            List of EntityExtractionResult objects.
        """
        if document_ids is None:
            document_ids = [str(i) for i in range(len(texts))]
        
        nlp = self._get_nlp()
        results = []
        
        # Use pipe for efficient batch processing
        for doc_id, doc in zip(document_ids, nlp.pipe(texts, batch_size=50)):
            entities = []
            entity_counts = Counter()
            unique_entities = {et: set() for et in self.entity_types}
            
            for ent in doc.ents:
                if ent.label_ in self.entity_types:
                    entity = Entity(
                        text=ent.text,
                        label=ent.label_,
                        start_char=ent.start_char,
                        end_char=ent.end_char
                    )
                    entities.append(entity)
                    entity_counts[ent.label_] += 1
                    unique_entities[ent.label_].add(ent.text)
            
            results.append(EntityExtractionResult(
                document_id=doc_id,
                text=doc.text[:200] + "..." if len(doc.text) > 200 else doc.text,
                entities=entities,
                entity_counts=dict(entity_counts),
                unique_entities={k: v for k, v in unique_entities.items() if v}
            ))
        
        return results
    
    def analyze_corpus(
        self,
        extraction_results: List[EntityExtractionResult],
        top_n: int = 20
    ) -> EntityAnalysis:
        """
        Analyze entity patterns across a corpus.
        
        Args:
            extraction_results: List of extraction results from documents.
            top_n: Number of top entities to return per type.
            
        Returns:
            EntityAnalysis with aggregated statistics.
        """
        if not extraction_results:
            return EntityAnalysis(
                total_documents=0,
                total_entities=0,
                entity_type_distribution={},
                most_common_entities={},
                entity_co_occurrence={}
            )
        
        # Count entity types
        type_counts = Counter()
        entity_mentions = {et: Counter() for et in self.entity_types}
        total_entities = 0
        
        # Track co-occurrence
        co_occurrence = {}
        
        for result in extraction_results:
            # Count entities
            for entity in result.entities:
                type_counts[entity.label] += 1
                entity_mentions[entity.label][entity.text] += 1
                total_entities += 1
            
            # Track co-occurrence within documents
            doc_entities = [e.text for e in result.entities]
            for i, e1 in enumerate(doc_entities):
                if e1 not in co_occurrence:
                    co_occurrence[e1] = Counter()
                for e2 in doc_entities[i+1:]:
                    co_occurrence[e1][e2] += 1
        
        # Get most common entities per type
        most_common = {}
        for label, counter in entity_mentions.items():
            if counter:
                most_common[label] = counter.most_common(top_n)
        
        return EntityAnalysis(
            total_documents=len(extraction_results),
            total_entities=total_entities,
            entity_type_distribution=dict(type_counts),
            most_common_entities=most_common,
            entity_co_occurrence={
                k: dict(v.most_common(10))
                for k, v in co_occurrence.items()
                if v
            }
        )
    
    def compare_entity_coverage(
        self,
        persona_results: Dict[str, List[EntityExtractionResult]]
    ) -> Dict[str, Dict]:
        """
        Compare entity coverage across different personas.
        
        Identifies which entities are amplified or suppressed
        for different user profiles.
        
        Args:
            persona_results: Dictionary mapping persona IDs to their extraction results.
            
        Returns:
            Comparison analysis showing differences.
        """
        # Get global entity frequency
        all_results = []
        for results in persona_results.values():
            all_results.extend(results)
        
        global_analysis = self.analyze_corpus(all_results)
        global_entity_freq = {}
        for label, entities in global_analysis.most_common_entities.items():
            for entity, count in entities:
                global_entity_freq[entity] = count
        
        # Compare each persona to global
        comparisons = {}
        for persona_id, results in persona_results.items():
            persona_analysis = self.analyze_corpus(results)
            
            amplified = []
            suppressed = []
            
            # Compare entity frequencies
            for label, entities in persona_analysis.most_common_entities.items():
                for entity, count in entities:
                    global_count = global_entity_freq.get(entity, 0)
                    if global_count > 0:
                        ratio = count / (global_count / len(persona_results))
                        if ratio > 1.5:
                            amplified.append((entity, ratio))
                        elif ratio < 0.5:
                            suppressed.append((entity, ratio))
            
            comparisons[persona_id] = {
                "total_entities": sum(
                    persona_analysis.entity_type_distribution.values()
                ),
                "amplified_entities": sorted(amplified, key=lambda x: -x[1])[:10],
                "suppressed_entities": sorted(suppressed, key=lambda x: x[1])[:10],
                "type_distribution": persona_analysis.entity_type_distribution
            }
        
        return comparisons
