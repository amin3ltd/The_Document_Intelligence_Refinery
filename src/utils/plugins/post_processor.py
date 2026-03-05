"""Post-processor plugin interface.

Provides the base interface for implementing custom post-processors.
Post-processors transform extracted content after initial extraction.
"""

from abc import ABC, abstractmethod
from enum import Enum
from pydantic import BaseModel, Field
from typing import Any, Dict, List, Optional, Callable

from src.utils.plugin_system import Plugin, PluginMetadata, PluginType


class PostProcessorType(str, Enum):
    """Types of post-processors."""
    TEXT_CLEANUP = "text_cleanup"
    FORMAT_CONVERSION = "format_conversion"
    LANGUAGE_DETECTION = "language_detection"
    ENTITY_EXTRACTION = "entity_extraction"
    SUMMARY = "summary"
    TRANSLATION = "translation"
    CUSTOM = "custom"


class PostProcessResult(BaseModel):
    """Result of post-processing."""
    content: Any = Field(..., description="Processed content")
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Processing metadata"
    )
    processing_time_ms: int = Field(default=0, description="Processing time")


class PostProcessor(Plugin, ABC):
    """Base class for post-processor plugins.
    
    Post-processors transform extracted content:
    - Text cleanup (remove artifacts, normalize)
    - Format conversion
    - Language detection
    - Entity extraction
    - Summarization
    - Translation
    """
    
    @property
    def plugin_type(self) -> PluginType:
        return PluginType.POST_PROCESSOR
    
    @property
    @abstractmethod
    def processor_type(self) -> PostProcessorType:
        """Return the type of post-processor."""
        pass
    
    @abstractmethod
    async def process(self, content: Any, **kwargs: Any) -> PostProcessResult:
        """Process content.
        
        Args:
            content: Content to process
            **kwargs: Additional processor-specific parameters
            
        Returns:
            PostProcessResult with processed content
        """
        pass
    
    def can_process(self, content: Any) -> bool:
        """Check if this processor can handle the content.
        
        Args:
            content: Content to check
            
        Returns:
            True if processor can handle this content
        """
        return True


class TextCleanupPostProcessor(PostProcessor):
    """Post-processor for cleaning up text."""
    
    def __init__(
        self,
        remove_extra_whitespace: bool = True,
        normalize_unicode: bool = True,
        remove_control_chars: bool = True,
        fix_broken_entities: bool = True
    ):
        self.remove_extra_whitespace = remove_extra_whitespace
        self.normalize_unicode = normalize_unicode
        self.remove_control_chars = remove_control_chars
        self.fix_broken_entities = fix_broken_entities
    
    @property
    def metadata(self) -> PluginMetadata:
        return PluginMetadata(
            name="text-cleanup-post-processor",
            version="1.0.0",
            description="Cleans up extracted text",
            author="Document Intelligence Team",
            plugin_type=PluginType.POST_PROCESSOR
        )
    
    @property
    def processor_type(self) -> PostProcessorType:
        return PostProcessorType.TEXT_CLEANUP
    
    def initialize(self) -> None:
        pass
    
    def shutdown(self) -> None:
        pass
    
    async def process(self, content: Any, **kwargs: Any) -> PostProcessResult:
        """Clean up text content."""
        import re
        import time
        
        start_time = time.time()
        
        if not isinstance(content, str):
            return PostProcessResult(content=content)
        
        text = content
        
        if self.remove_extra_whitespace:
            # Replace multiple spaces with single space
            text = re.sub(r' +', ' ', text)
            # Replace multiple newlines with double newline
            text = re.sub(r'\n\n+', '\n\n', text)
            # Remove leading/trailing whitespace from each line
            text = '\n'.join(line.strip() for line in text.split('\n'))
        
        if self.normalize_unicode:
            import unicodedata
            text = unicodedata.normalize('NFKC', text)
        
        if self.remove_control_chars:
            # Remove control characters except newlines and tabs
            text = re.sub(r'[\x00-\x08\x0b-\x0c\x0e-\x1f\x7f]', '', text)
        
        if self.fix_broken_entities:
            # Fix common OCR artifacts
            text = text.replace('�', '')
            text = re.sub(r'\s+', ' ', text)
        
        processing_time = int((time.time() - start_time) * 1000)
        
        return PostProcessResult(
            content=text,
            metadata={"operations_applied": ["whitespace", "unicode", "control_chars"]},
            processing_time_ms=processing_time
        )


class LanguageDetectionPostProcessor(PostProcessor):
    """Post-processor for language detection."""
    
    def __init__(self, min_confidence: float = 0.8):
        self.min_confidence = min_confidence
    
    @property
    def metadata(self) -> PluginMetadata:
        return PluginMetadata(
            name="language-detection-post-processor",
            version="1.0.0",
            description="Detects language of extracted text",
            author="Document Intelligence Team",
            plugin_type=PluginType.POST_PROCESSOR
        )
    
    @property
    def processor_type(self) -> PostProcessorType:
        return PostProcessorType.LANGUAGE_DETECTION
    
    def initialize(self) -> None:
        pass
    
    def shutdown(self) -> None:
        pass
    
    async def process(self, content: Any, **kwargs: Any) -> PostProcessResult:
        """Detect language of text."""
        import time
        from collections import Counter
        
        start_time = time.time()
        
        if not isinstance(content, str):
            return PostProcessResult(content=content)
        
        # Simple language detection based on character patterns
        # In production, use langdetect or fasttext
        
        text = content.lower()
        
        # Language indicators
        languages = {
            "english": ["the", "is", "are", "was", "were", "and", "of", "to", "a", "in"],
            "german": ["der", "die", "das", "und", "ist", "sein", "haben", "werden"],
            "french": ["le", "la", "les", "est", "sont", "et", "que", "qui", "dans"],
            "spanish": ["el", "la", "los", "las", "es", "son", "y", "que", "de", "en"],
        }
        
        words = text.split()
        scores = {}
        
        for lang, indicators in languages.items():
            count = sum(1 for w in words if w in indicators)
            scores[lang] = count / max(len(words), 1)
        
        detected = max(scores, key=scores.get) if scores else "unknown"
        confidence = scores[detected] if scores else 0.0
        
        processing_time = int((time.time() - start_time) * 1000)
        
        return PostProcessResult(
            content=content,
            metadata={
                "detected_language": detected,
                "confidence": confidence,
                "all_scores": scores
            },
            processing_time_ms=processing_time
        )


class EntityExtractionPostProcessor(PostProcessor):
    """Post-processor for extracting entities."""
    
    def __init__(self, entity_types: List[str] = None):
        self.entity_types = entity_types or ["persons", "organizations", "locations"]
    
    @property
    def metadata(self) -> PluginMetadata:
        return PluginMetadata(
            name="entity-extraction-post-processor",
            version="1.0.0",
            description="Extracts named entities from text",
            author="Document Intelligence Team",
            plugin_type=PluginType.POST_PROCESSOR
        )
    
    @property
    def processor_type(self) -> PostProcessorType:
        return PostProcessorType.ENTITY_EXTRACTION
    
    def initialize(self) -> None:
        pass
    
    def shutdown(self) -> None:
        pass
    
    async def process(self, content: Any, **kwargs: Any) -> PostProcessResult:
        """Extract entities from text."""
        import re
        import time
        
        start_time = time.time()
        
        if not isinstance(content, str):
            return PostProcessResult(content=content)
        
        entities = {
            "persons": [],
            "organizations": [],
            "locations": [],
            "dates": [],
            "emails": [],
            "urls": []
        }
        
        # Email regex
        emails = re.findall(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', content)
        entities["emails"] = emails
        
        # URL regex
        urls = re.findall(r'https?://[^\s]+', content)
        entities["urls"] = urls
        
        # Date patterns
        dates = re.findall(r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b', content)
        dates += re.findall(r'\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]* \d{1,2},? \d{4}\b', content, re.IGNORECASE)
        entities["dates"] = list(set(dates))
        
        # Capitalized words (potential proper nouns)
        capitalized = re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b', content)
        # Filter out common sentence starters
        filtered = [w for w in capitalized if w not in ["The", "This", "That", "These", "Those"]]
        entities["potential_proper_nouns"] = filtered[:20]  # Limit
        
        processing_time = int((time.time() - start_time) * 1000)
        
        return PostProcessResult(
            content=content,
            metadata={"entities": entities},
            processing_time_ms=processing_time
        )


# Registry for post-processors
_post_processors: Dict[PostProcessorType, type[PostProcessor]] = {
    PostProcessorType.TEXT_CLEANUP: TextCleanupPostProcessor,
    PostProcessorType.LANGUAGE_DETECTION: LanguageDetectionPostProcessor,
    PostProcessorType.ENTITY_EXTRACTION: EntityExtractionPostProcessor,
}


def get_post_processor(processor_type: PostProcessorType, **kwargs: Any) -> PostProcessor:
    """Get a post-processor by type.
    
    Args:
        processor_type: Type of post-processor
        **kwargs: Additional configuration
        
    Returns:
        PostProcessor instance
    """
    processor_class = _post_processors.get(processor_type)
    if processor_class is None:
        raise ValueError(f"Unknown post-processor type: {processor_type}")
    return processor_class(**kwargs)


def register_post_processor(
    processor_type: PostProcessorType,
    processor_class: type[PostProcessor]
) -> None:
    """Register a custom post-processor.
    
    Args:
        processor_type: Type identifier for the processor
        processor_class: PostProcessor class to register
    """
    _post_processors[processor_type] = processor_class
