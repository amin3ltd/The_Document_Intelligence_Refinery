"""
Extraction Router Agent for Document Intelligence Refinery.

The Extraction Router routes documents to the appropriate extraction strategy
based on the DocumentProfile from the Triage Agent.
"""

import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Optional, Dict, Any, List
from enum import Enum

from src.models.document_profile import DocumentProfile, ExtractionCostHint, OriginType
from src.models.extracted_document import ExtractedDocument
from src.utils.config import get_config

logger = logging.getLogger(__name__)


class EscalationResult(str, Enum):
    """Result of extraction with escalation tracking."""
    SUCCESS = "success"
    ESCALATED = "escalated"
    FAILED = "failed"
    LOW_CONFIDENCE = "low_confidence"


@dataclass
class ExtractionResult:
    """Result of extraction with metadata about which strategy ran."""
    document: ExtractedDocument
    strategy_used: str
    escalation_result: EscalationResult
    original_strategy: Optional[str] = None
    confidence: float = 0.0
    requires_review: bool = False
    review_reason: Optional[str] = None
    strategy_sequence: List[str] = field(default_factory=list)


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
    
    @abstractmethod
    def get_confidence(self, result: ExtractedDocument) -> float:
        """Get confidence score from extraction result."""
        pass


class ExtractionRouter:
    """
    Routes documents to appropriate extraction strategies based on DocumentProfile.
    
    Implements the escalation guard logic from DOMAIN_NOTES.md:
    - Strategy A (Fast Text) for simple native digital documents
    - Strategy B (Layout-Aware) for complex layouts
    - Strategy C (Vision) for scanned images
    
    All thresholds are read from config.
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize the router with config-driven thresholds."""
        self.config = get_config(config_path)
        self.strategies: Dict[str, ExtractionStrategy] = {}
        self._load_thresholds()
    
    def _load_thresholds(self):
        """Load escalation thresholds from configuration."""
        extraction_config = self.config.extraction_config
        
        # Strategy A thresholds
        strategy_a = extraction_config.get("strategy_a", {})
        self.strategy_a_high = strategy_a.get("high_confidence", 0.85)
        self.strategy_a_medium = strategy_a.get("medium_confidence", 0.50)
        self.strategy_a_escalate = strategy_a.get("escalate_to_b", True)
        
        # Strategy B thresholds
        strategy_b = extraction_config.get("strategy_b", {})
        self.strategy_b_high = strategy_b.get("high_confidence", 0.80)
        self.strategy_b_escalate = strategy_b.get("escalate_to_c", True)
        
        # Strategy C thresholds
        strategy_c = extraction_config.get("strategy_c", {})
        self.strategy_c_high = strategy_c.get("high_confidence", 0.75)
    
    def register_strategy(self, strategy: ExtractionStrategy) -> None:
        """Register an extraction strategy."""
        self.strategies[strategy.name] = strategy
        logger.info(f"Registered extraction strategy: {strategy.name}")
    
    def route(self, file_path: str, profile: DocumentProfile) -> ExtractionResult:
        """
        Route the document to the appropriate extraction strategy.
        
        Args:
            file_path: Path to the document
            profile: DocumentProfile from Triage Agent
            
        Returns:
            ExtractionResult with extraction results and strategy metadata
        """
        # Determine which strategy to use
        strategy_name = self._select_strategy(profile)
        original_strategy = strategy_name
        strategy_sequence = [strategy_name]
        
        if strategy_name not in self.strategies:
            raise ValueError(f"Strategy not registered: {strategy_name}")
        
        # Perform extraction
        result = self._extract_with_strategy(
            file_path, profile, strategy_name, strategy_sequence
        )
        
        return result
    
    def _extract_with_strategy(
        self,
        file_path: str,
        profile: DocumentProfile,
        strategy_name: str,
        strategy_sequence: List[str]
    ) -> ExtractionResult:
        """
        Extract using a specific strategy and handle escalation.
        
        Returns:
            ExtractionResult with metadata about the extraction process
        """
        strategy = self.strategies[strategy_name]
        logger.info(f"Routing document {profile.doc_id} to {strategy_name}")
        
        # Extract content
        document = strategy.extract(file_path, profile)
        confidence = strategy.get_confidence(document)
        
        # Check confidence and escalate if needed
        escalation_result, final_document, final_strategy = self._check_escalation(
            document, profile, strategy_name, confidence, strategy_sequence
        )
        
        # Determine if review is required
        requires_review, review_reason = self._determine_review_status(
            final_document, confidence, escalation_result, final_strategy
        )
        
        return ExtractionResult(
            document=final_document,
            strategy_used=final_strategy,
            escalation_result=escalation_result,
            original_strategy=strategy_name,
            confidence=confidence,
            requires_review=requires_review,
            review_reason=review_reason,
            strategy_sequence=strategy_sequence
        )
    
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
        document: ExtractedDocument,
        profile: DocumentProfile,
        current_strategy: str,
        confidence: float,
        strategy_sequence: List[str]
    ) -> tuple[EscalationResult, ExtractedDocument, str]:
        """
        Check if extraction needs escalation based on confidence.
        
        Implements the escalation guard logic from DOMAIN_NOTES.md
        using config-driven thresholds.
        
        Returns:
            Tuple of (escalation_result, final_document, final_strategy)
        """
        # Strategy A escalation
        if current_strategy == "strategy_a":
            if confidence < self.strategy_a_medium and self.strategy_a_escalate:
                if "strategy_b" in self.strategies:
                    logger.warning(
                        f"Low confidence ({confidence:.2f}) for Strategy A "
                        f"(threshold: {self.strategy_a_medium}), escalating to Strategy B"
                    )
                    strategy_sequence.append("strategy_b")
                    return self._escalate_to_b(document, profile, strategy_sequence)
            elif confidence < self.strategy_a_high and self.strategy_a_escalate:
                logger.info(
                    f"Medium confidence ({confidence:.2f}) for Strategy A, "
                    f"could escalate to Strategy B"
                )
                # Surface this information but don't automatically escalate
                document.metadata.flags = getattr(document.metadata, 'flags', {})
                document.metadata.flags['consider_escalation'] = True
                document.metadata.flags['escalation_reason'] = f"Confidence {confidence:.2f} below high threshold {self.strategy_a_high}"
        
        # Strategy B escalation
        elif current_strategy == "strategy_b":
            if confidence < self.strategy_b_high and self.strategy_b_escalate:
                if "strategy_c" in self.strategies:
                    logger.warning(
                        f"Low confidence ({confidence:.2f}) for Strategy B "
                        f"(threshold: {self.strategy_b_high}), escalating to Strategy C"
                    )
                    strategy_sequence.append("strategy_c")
                    return self._escalate_to_c(document, profile, strategy_sequence)
        
        # No escalation needed
        return EscalationResult.SUCCESS, document, current_strategy
    
    def _escalate_to_b(
        self,
        document: ExtractedDocument,
        profile: DocumentProfile,
        strategy_sequence: List[str]
    ) -> tuple[EscalationResult, ExtractedDocument, str]:
        """Escalate from Strategy A to Strategy B."""
        strategy_b = self.strategies["strategy_b"]
        new_document = strategy_b.extract(profile.file_path, profile)
        new_confidence = strategy_b.get_confidence(new_document)
        
        # Check if we need to escalate further
        if new_confidence < self.strategy_b_high and self.strategy_b_escalate:
            if "strategy_c" in self.strategies:
                logger.warning(
                    f"Low confidence ({new_confidence:.2f}) for Strategy B after escalation, "
                    f"escalating to Strategy C"
                )
                strategy_sequence.append("strategy_c")
                return self._escalate_to_c(new_document, profile, strategy_sequence)
        
        return EscalationResult.ESCALATED, new_document, "strategy_b"
    
    def _escalate_to_c(
        self,
        document: ExtractedDocument,
        profile: DocumentProfile,
        strategy_sequence: List[str]
    ) -> tuple[EscalationResult, ExtractedDocument, str]:
        """Escalate to Strategy C (Vision)."""
        strategy_c = self.strategies["strategy_c"]
        new_document = strategy_c.extract(profile.file_path, profile)
        
        return EscalationResult.ESCALATED, new_document, "strategy_c"
    
    def _determine_review_status(
        self,
        document: ExtractedDocument,
        confidence: float,
        escalation_result: EscalationResult,
        strategy_used: str
    ) -> tuple[bool, Optional[str]]:
        """
        Determine if the extraction requires human review.
        
        Returns:
            Tuple of (requires_review, review_reason)
        """
        # Flag for review if confidence is very low after all escalations
        if strategy_used == "strategy_c" and confidence < self.strategy_c_high:
            return True, f"Very low confidence ({confidence:.2f}) even after Vision strategy"
        
        # Flag for review if escalation was needed
        if escalation_result == EscalationResult.ESCALATED and confidence < 0.70:
            return True, f"Escalation occurred but final confidence ({confidence:.2f}) is low"
        
        return False, None
    
    def get_strategy_info(self) -> Dict[str, Any]:
        """Get information about registered strategies and thresholds."""
        return {
            "registered_strategies": list(self.strategies.keys()),
            "thresholds": {
                "strategy_a": {
                    "high_confidence": self.strategy_a_high,
                    "medium_confidence": self.strategy_a_medium,
                    "escalate_to_b": self.strategy_a_escalate,
                },
                "strategy_b": {
                    "high_confidence": self.strategy_b_high,
                    "escalate_to_c": self.strategy_b_escalate,
                },
                "strategy_c": {
                    "high_confidence": self.strategy_c_high,
                },
            },
        }


def create_router(config_path: Optional[str] = None) -> ExtractionRouter:
    """Create and configure an extraction router."""
    from src.strategies.fast_text import FastTextStrategy
    from src.strategies.layout_aware import LayoutAwareStrategy
    from src.strategies.vision import VisionStrategy
    
    router = ExtractionRouter(config_path)
    router.register_strategy(FastTextStrategy())
    router.register_strategy(LayoutAwareStrategy())
    router.register_strategy(VisionStrategy())
    
    return router
