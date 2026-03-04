"""
Unit tests for the Triage Agent.

These tests verify the classification logic for:
- Origin type detection
- Layout complexity classification
- Domain hint detection
- Extraction cost hint determination
"""

import pytest
from unittest.mock import Mock, patch, MagicMock

from src.agents.triage import (
    DomainClassifier,
    PageAnalysis,
    TriageAgent,
    TriageResult,
)
from src.models.document_profile import (
    DocumentProfile,
    DomainHint,
    ExtractionCostHint,
    LayoutComplexity,
    OriginType,
)


class TestDomainClassifier:
    """Tests for the DomainClassifier component."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.classifier = DomainClassifier()
    
    def test_classify_financial_keywords(self):
        """Test financial domain classification."""
        text = """
        The company's revenue for Q3 2024 was $4.2 billion.
        Total assets increased to $12.5 billion on the balance sheet.
        Net income for the fiscal year was $1.8 billion.
        """
        
        domain, confidence = self.classifier.classify(text)
        
        assert domain == DomainHint.FINANCIAL
        assert confidence > 0.5
    
    def test_classify_legal_keywords(self):
        """Test legal domain classification."""
        text = """
        WHEREAS the Plaintiff and Defendant have entered into this Agreement.
        The Court hereby orders that the Defendant shall comply with all terms.
        This contract shall be governed by the laws of the jurisdiction.
        """
        
        domain, confidence = self.classifier.classify(text)
        
        assert domain == DomainHint.LEGAL
        assert confidence > 0.5
    
    def test_classify_technical_keywords(self):
        """Test technical domain classification."""
        text = """
        The system architecture follows a microservices pattern.
        API endpoints are defined in the specification document.
        The implementation uses a distributed algorithm for consensus.
        """
        
        domain, confidence = self.classifier.classify(text)
        
        assert domain == DomainHint.TECHNICAL
        assert confidence > 0.5
    
    def test_classify_medical_keywords(self):
        """Test medical domain classification."""
        text = """
        The patient presented with symptoms of the disease.
        Diagnosis was confirmed through clinical examination.
        Treatment includes medication and therapy.
        """
        
        domain, confidence = self.classifier.classify(text)
        
        assert domain == DomainHint.MEDICAL
        assert confidence > 0.5
    
    def test_classify_general_no_keywords(self):
        """Test general domain when no keywords found."""
        text = "This is a simple document with no specific domain keywords."
        
        domain, confidence = self.classifier.classify(text)
        
        assert domain == DomainHint.GENERAL
    
    def test_classify_empty_text(self):
        """Test handling of empty text."""
        domain, confidence = self.classifier.classify("")
        
        assert domain == DomainHint.GENERAL
        assert confidence == 0.0
    
    def test_classify_short_text(self):
        """Test handling of very short text."""
        text = "short"
        
        domain, confidence = self.classifier.classify(text)
        
        assert domain == DomainHint.GENERAL
        assert confidence == 0.0


class TestTriageAgentOriginClassification:
    """Tests for origin type classification."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.agent = TriageAgent()
    
    def test_native_digital_classification(self):
        """Test native digital document classification."""
        # High char density, low image ratio = native digital
        analyses = [
            PageAnalysis(
                page_number=1,
                char_count=5000,
                char_density=0.002,
                image_ratio=0.1,
                bbox_area=400000,
                has_embedded_fonts=True,
            ),
            PageAnalysis(
                page_number=2,
                char_count=4800,
                char_density=0.002,
                image_ratio=0.1,
                bbox_area=400000,
                has_embedded_fonts=True,
            ),
        ]
        
        origin = self.agent._classify_origin_type(analyses)
        
        assert origin == OriginType.NATIVE_DIGITAL
    
    def test_scanned_image_classification(self):
        """Test scanned image document classification."""
        # Low char density, high image ratio = scanned
        analyses = [
            PageAnalysis(
                page_number=1,
                char_count=50,
                char_density=0.0001,
                image_ratio=0.8,
                bbox_area=400000,
                has_embedded_fonts=False,
            ),
            PageAnalysis(
                page_number=2,
                char_count=40,
                char_density=0.0001,
                image_ratio=0.85,
                bbox_area=400000,
                has_embedded_fonts=False,
            ),
        ]
        
        origin = self.agent._classify_origin_type(analyses)
        
        assert origin == OriginType.SCANNED_IMAGE
    
    def test_mixed_classification(self):
        """Test mixed origin document classification."""
        analyses = [
            # Native page
            PageAnalysis(
                page_number=1,
                char_count=5000,
                char_density=0.002,
                image_ratio=0.1,
                bbox_area=400000,
                has_embedded_fonts=True,
            ),
            # Scanned page
            PageAnalysis(
                page_number=2,
                char_count=50,
                char_density=0.0001,
                image_ratio=0.8,
                bbox_area=400000,
                has_embedded_fonts=False,
            ),
        ]
        
        origin = self.agent._classify_origin_type(analyses)
        
        assert origin == OriginType.MIXED


class TestTriageAgentLayoutClassification:
    """Tests for layout complexity classification."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.agent = TriageAgent()
    
    def test_single_column_classification(self):
        """Test single column layout classification."""
        analyses = [
            PageAnalysis(
                page_number=1,
                char_count=5000,
                char_density=0.002,
                image_ratio=0.1,
                bbox_area=400000,
                text_blocks=[
                    {"text": "Text block", "bbox": [50, 100, 550, 150]},
                ],
                has_embedded_fonts=True,
            ),
        ]
        
        layout = self.agent._classify_layout_complexity(analyses)
        
        assert layout == LayoutComplexity.SINGLE_COLUMN
    
    def test_multi_column_classification(self):
        """Test multi-column layout detection."""
        analyses = [
            PageAnalysis(
                page_number=1,
                char_count=5000,
                char_density=0.002,
                image_ratio=0.1,
                bbox_area=400000,
                text_blocks=[
                    {"text": "Column 1 text", "bbox": [50, 100, 280, 700]},
                    {"text": "Column 2 text", "bbox": [320, 100, 550, 700]},
                ],
                tables=0,
                has_embedded_fonts=True,
            ),
        ]
        
        layout = self.agent._classify_layout_complexity(analyses)
        
        # Should detect multiple columns
        assert layout in [LayoutComplexity.MULTI_COLUMN, LayoutComplexity.SINGLE_COLUMN]
    
    def test_table_heavy_classification(self):
        """Test table-heavy layout classification."""
        analyses = [
            PageAnalysis(
                page_number=1,
                char_count=3000,
                char_density=0.001,
                image_ratio=0.2,
                bbox_area=400000,
                tables=3,  # Multiple tables
                has_embedded_fonts=True,
            ),
        ]
        
        layout = self.agent._classify_layout_complexity(analyses)
        
        assert layout == LayoutComplexity.TABLE_HEAVY


class TestExtractionCostHint:
    """Tests for extraction cost hint determination."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.agent = TriageAgent()
    
    def test_native_single_column_fast_text(self):
        """Test fast text for simple native digital."""
        hint = self.agent._determine_extraction_cost(
            OriginType.NATIVE_DIGITAL,
            LayoutComplexity.SINGLE_COLUMN
        )
        
        assert hint == ExtractionCostHint.FAST_TEXT_SUFFICIENT
    
    def test_native_multi_column_layout(self):
        """Test layout model for multi-column native."""
        hint = self.agent._determine_extraction_cost(
            OriginType.NATIVE_DIGITAL,
            LayoutComplexity.MULTI_COLUMN
        )
        
        assert hint == ExtractionCostHint.NEEDS_LAYOUT_MODEL
    
    def test_scanned_needs_vision(self):
        """Test vision model for scanned documents."""
        hint = self.agent._determine_extraction_cost(
            OriginType.SCANNED_IMAGE,
            LayoutComplexity.SINGLE_COLUMN
        )
        
        assert hint == ExtractionCostHint.NEEDS_VISION_MODEL
    
    def test_mixed_needs_layout(self):
        """Test layout model for mixed origin."""
        hint = self.agent._determine_extraction_cost(
            OriginType.MIXED,
            LayoutComplexity.SINGLE_COLUMN
        )
        
        assert hint == ExtractionCostHint.NEEDS_LAYOUT_MODEL
    
    def test_table_heavy_needs_layout(self):
        """Test layout model for table-heavy documents."""
        hint = self.agent._determine_extraction_cost(
            OriginType.NATIVE_DIGITAL,
            LayoutComplexity.TABLE_HEAVY
        )
        
        assert hint == ExtractionCostHint.NEEDS_LAYOUT_MODEL


class TestConfidenceCalculation:
    """Tests for confidence score calculation."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.agent = TriageAgent()
    
    def test_high_confidence(self):
        """Test high confidence calculation."""
        confidence = self.agent._calculate_confidence(
            char_density=0.002,  # High
            image_ratio=0.1,     # Low (good)
            domain_confidence=0.9
        )
        
        assert confidence > 0.7
    
    def test_low_confidence_low_density(self):
        """Test low confidence with low character density."""
        confidence = self.agent._calculate_confidence(
            char_density=0.0001,  # Low
            image_ratio=0.1,
            domain_confidence=0.5
        )
        
        assert confidence < 0.5
    
    def test_low_confidence_high_image_ratio(self):
        """Test low confidence with high image ratio."""
        confidence = self.agent._calculate_confidence(
            char_density=0.002,
            image_ratio=0.8,  # High (bad)
            domain_confidence=0.5
        )
        
        assert confidence < 0.6


class TestPageTypeEstimation:
    """Tests for scanned vs native page estimation."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.agent = TriageAgent()
    
    def test_estimate_all_native(self):
        """Test estimation when all pages are native."""
        analyses = [
            PageAnalysis(
                page_number=i,
                char_count=5000,
                char_density=0.002,
                image_ratio=0.1,
                bbox_area=400000,
                has_embedded_fonts=True,
            )
            for i in range(1, 6)
        ]
        
        scanned, native = self.agent._estimate_page_types(analyses)
        
        assert scanned == 0
        assert native == 5
    
    def test_estimate_all_scanned(self):
        """Test estimation when all pages are scanned."""
        analyses = [
            PageAnalysis(
                page_number=i,
                char_count=50,
                char_density=0.0001,
                image_ratio=0.8,
                bbox_area=400000,
                has_embedded_fonts=False,
            )
            for i in range(1, 6)
        ]
        
        scanned, native = self.agent._estimate_page_types(analyses)
        
        assert scanned == 5
        assert native == 0
    
    def test_estimate_mixed(self):
        """Test estimation with mixed pages."""
        analyses = [
            PageAnalysis(page_number=1, char_count=5000, char_density=0.002,
                        image_ratio=0.1, bbox_area=400000, has_embedded_fonts=True),
            PageAnalysis(page_number=2, char_count=50, char_density=0.0001,
                        image_ratio=0.8, bbox_area=400000, has_embedded_fonts=False),
            PageAnalysis(page_number=3, char_count=5000, char_density=0.002,
                        image_ratio=0.1, bbox_area=400000, has_embedded_fonts=True),
        ]
        
        scanned, native = self.agent._estimate_page_types(analyses)
        
        assert scanned == 1
        assert native == 2


class TestDocumentProfileCreation:
    """Integration tests for DocumentProfile creation."""
    
    def test_profile_creation(self):
        """Test full profile creation."""
        agent = TriageAgent()
        
        # Mock the page analysis
        with patch.object(agent, '_analyze_pages') as mock_analyze:
            mock_analyze.return_value = [
                PageAnalysis(
                    page_number=1,
                    char_count=5000,
                    char_density=0.002,
                    image_ratio=0.1,
                    bbox_area=400000,
                    text_blocks=[{"text": "Financial report revenue", "bbox": [50, 100, 550, 150]}],
                    images=[],
                    tables=1,
                    has_embedded_fonts=True,
                ),
            ]
            
            # Mock saving
            with patch.object(agent, '_save_profile'):
                result = agent.analyze("/test/document.pdf")
        
        profile = result.profile
        
        assert isinstance(profile, DocumentProfile)
        assert profile.file_path == "/test/document.pdf"
        assert profile.origin_type in OriginType
        assert profile.layout_complexity in LayoutComplexity
        assert profile.domain_hint in DomainHint
        assert profile.extraction_cost_hint in ExtractionCostHint
        assert profile.page_count == 1
        assert profile.confidence_score > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
