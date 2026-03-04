"""Document Profile Pydantic Model for the Document Intelligence Refinery."""

from pydantic import BaseModel, Field
from typing import Literal, Optional
from enum import Enum


class OriginType(str, Enum):
    """Classification of document origin type based on how the content was created."""
    NATIVE_DIGITAL = "native_digital"
    SCANNED_IMAGE = "scanned_image"
    MIXED = "mixed"
    FORM_FILLABLE = "form_fillable"


class LayoutComplexity(str, Enum):
    """Classification of document layout complexity."""
    SINGLE_COLUMN = "single_column"
    MULTI_COLUMN = "multi_column"
    TABLE_HEAVY = "table_heavy"
    FIGURE_HEAVY = "figure_heavy"
    MIXED = "mixed"


class DomainHint(str, Enum):
    """Domain classification based on content analysis."""
    FINANCIAL = "financial"
    LEGAL = "legal"
    TECHNICAL = "technical"
    MEDICAL = "medical"
    GENERAL = "general"


class ExtractionCostHint(str, Enum):
    """Hint for the recommended extraction strategy based on document characteristics."""
    FAST_TEXT_SUFFICIENT = "fast_text_sufficient"
    NEEDS_LAYOUT_MODEL = "needs_layout_model"
    NEEDS_VISION_MODEL = "needs_vision_model"


class DocumentProfile(BaseModel):
    """
    DocumentProfile captures the essential characteristics of a document
    for routing decisions in the extraction pipeline.
    
    This is the output of the Triage Agent and is used by the Extraction Router
    to determine the optimal extraction strategy.
    """
    doc_id: str = Field(..., description="Unique identifier for the document")
    file_path: str = Field(..., description="Path to the source document file")
    origin_type: OriginType = Field(..., description="How the document content was created")
    layout_complexity: LayoutComplexity = Field(..., description="Complexity of the document layout")
    language: str = Field(default="en", description="Detected primary language")
    language_confidence: float = Field(default=1.0, ge=0.0, le=1.0, description="Confidence in language detection")
    domain_hint: DomainHint = Field(default=DomainHint.GENERAL, description="Domain classification hint")
    extraction_cost_hint: ExtractionCostHint = Field(..., description="Recommended extraction strategy")
    page_count: int = Field(..., ge=0, description="Total number of pages in the document")
    estimated_pages_scanned: int = Field(default=0, ge=0, description="Estimated number of scanned pages")
    estimated_pages_native: int = Field(default=0, ge=0, description="Estimated number of native digital pages")
    
    # Confidence metrics for audit and debugging
    char_density_avg: float = Field(default=0.0, ge=0.0, description="Average character density per page")
    image_ratio_avg: float = Field(default=0.0, ge=0.0, le=1.0, description="Average image area ratio per page")
    
    # Additional computed metrics for downstream use
    confidence_score: float = Field(
        default=0.0, 
        ge=0.0, 
        le=1.0,
        description="Overall confidence in document classification"
    )
    has_tables: bool = Field(default=False, description="Whether tables were detected")
    has_figures: bool = Field(default=False, description="Whether figures/images were detected")
    
    # Special document flags
    is_zero_text_document: bool = Field(
        default=False, 
        description="Whether the document has zero or minimal text content"
    )
    is_form_fillable: bool = Field(
        default=False, 
        description="Whether the document contains form fields"
    )
    zero_text_page_count: int = Field(
        default=0, 
        ge=0, 
        description="Number of pages with zero/minimal text"
    )
    form_fillable_page_count: int = Field(
        default=0, 
        ge=0, 
        description="Number of pages with form fields"
    )
    
    class Config:
        """Pydantic model configuration."""
        use_enum_values = True
        json_schema_extra = {
            "example": {
                "doc_id": "doc_001",
                "file_path": "/documents/annual_report.pdf",
                "origin_type": "native_digital",
                "layout_complexity": "multi_column",
                "language": "en",
                "language_confidence": 0.95,
                "domain_hint": "financial",
                "extraction_cost_hint": "needs_layout_model",
                "page_count": 42,
                "estimated_pages_scanned": 0,
                "estimated_pages_native": 42,
                "char_density_avg": 0.0025,
                "image_ratio_avg": 0.15,
                "confidence_score": 0.88,
                "has_tables": True,
                "has_figures": True,
                "is_zero_text_document": False,
                "is_form_fillable": False,
                "zero_text_page_count": 0,
                "form_fillable_page_count": 0
            }
        }
