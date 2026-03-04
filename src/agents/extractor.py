"""
Extraction Router Agent for Document Intelligence Refinery.

The Extraction Router routes documents to the appropriate extraction strategy
based on the DocumentProfile from the Triage Agent.
"""

import logging
from abc import ABC, abstractmethod
from typing import Optional

from src.models.document_profile import DocumentProfile, ExtractionCostHint, OriginType
from src.models.extracted_document import ExtractedDocument

logger = logging.getLogger(__name__)


class ExtractionStrategy(ABC):
    """Base class for extraction strategies."""
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Return the strategy name."""
        pass
    
    @abstractmethod
    def extract(self, file_path: str, profile: DocumentProfile) -> ExtractedDocument:
        """Extract content from the document."""
        pass


class ExtractionRouter:
    """
    Routes documents to appropriate extraction strategies based on DocumentProfile.
    
    Implements the escalation guard logic from DOMAIN_NOTES.md:
    - Strategy A (Fast Text) for simple native digital documents
    - Strategy B (Layout-Aware) for complex layouts
    - Strategy C (Vision) for scanned images
    """
    
    def __init__(self):
        """Initialize the router."""
        self.strategies: dict[str, ExtractionStrategy] = {}
    
    def register_strategy(self, strategy: ExtractionStrategy) -> None:
        """Register an extraction strategy."""
        self.strategies[strategy.name] = strategy
        logger.info(f"Registered extraction strategy: {strategy.name}")
    
    def route(self, file_path: str, profile: DocumentProfile) -> ExtractedDocument:
        """
        Route the document to the appropriate extraction strategy.
        
        Args:
            file_path: Path to the document
            profile: DocumentProfile from Triage Agent
            
        Returns:
            ExtractedDocument with extracted content
        """
        # Determine which strategy to use
        strategy_name = self._select_strategy(profile)
        
        if strategy_name not in self.strategies:
            raise ValueError(f"Strategy not registered: {strategy_name}")
        
        strategy = self.strategies[strategy_name]
        logger.info(f"Routing document {profile.doc_id} to {strategy_name}")
        
        # Extract content
        result = strategy.extract(file_path, profile)
        
        # Check confidence and escalate if needed
        result = self._check_escalation(result, profile, strategy_name)
        
        return result
    
    def _select_strategy(self, profile: DocumentProfile) -> str:
        """Select the appropriate strategy based on profile."""
        # Use extraction_cost_hint as primary selector
        if profile.extraction_cost_hint == ExtractionCostHint.NEEDS_VISION_MODEL:
            return "strategy_c"  # Vision
        
        if profile.extraction_cost_hint == ExtractionCostHint.NEEDS_LAYOUT_MODEL:
            return "strategy_b"  # Layout-aware
        
        # Default to fast text
        return "strategy_a"  # Fast text
    
    def _check_escalation(
        self,
        result: ExtractedDocument,
        profile: DocumentProfile,
        current_strategy: str
    ) -> ExtractedDocument:
        """
        Check if extraction needs escalation based on confidence.
        
        Implements the escalation guard logic from DOMAIN_NOTES.md.
        """
        confidence = result.metadata.confidence_score
        
        # Thresholds from DOMAIN_NOTES.md
        if current_strategy == "strategy_a":
            if confidence < 0.50 and "strategy_b" in self.strategies:
                logger.warning(
                    f"Low confidence ({confidence}) for Strategy A, escalating to Strategy B"
                )
                return self.strategies["strategy_b"].extract(profile.file_path, profile)
            elif confidence < 0.85 and confidence >= 0.50 and "strategy_b" in self.strategies:
                logger.info(
                    f"Medium confidence ({confidence}), could escalate to Strategy B"
                )
        
        elif current_strategy == "strategy_b":
            if confidence < 0.80 and "strategy_c" in self.strategies:
                logger.warning(
                    f"Low confidence ({confidence}) for Strategy B, escalating to Strategy C"
                )
                return self.strategies["strategy_c"].extract(profile.file_path, profile)
        
        return result


def create_router() -> ExtractionRouter:
    """Create and configure an extraction router."""
    from src.strategies.fast_text import FastTextStrategy
    from src.strategies.layout_aware import LayoutAwareStrategy
    from src.strategies.vision import VisionStrategy
    
    router = ExtractionRouter()
    router.register_strategy(FastTextStrategy())
    router.register_strategy(LayoutAwareStrategy())
    router.register_strategy(VisionStrategy())
    
    return router
