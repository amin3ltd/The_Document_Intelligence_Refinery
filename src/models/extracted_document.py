"""ExtractedDocument schema for the Document Intelligence Refinery."""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime


class TextBlock(BaseModel):
    """A single text block extracted from a page with spatial metadata."""
    text: str = Field(..., description="Extracted text content")
    bbox: List[float] = Field(
        ..., 
        description="Bounding box coordinates [x0, y0, x1, y1]",
        min_length=4,
        max_length=4
    )
    page_number: int = Field(..., ge=1, description="Page number where this block appears")
    block_type: str = Field(default="text", description="Type of block: text, table, figure, header, footer")
    confidence: float = Field(default=1.0, ge=0.0, le=1.0, description="Extraction confidence score")
    font_info: Optional[Dict[str, Any]] = Field(default=None, description="Font metadata if available")


class TableData(BaseModel):
    """Structured table data extracted from a document."""
    headers: List[str] = Field(default_factory=list, description="Table column headers")
    rows: List[List[str]] = Field(default_factory=list, description="Table rows data")
    bbox: Optional[List[float]] = Field(default=None, description="Bounding box if available")
    page_number: int = Field(..., ge=1, description="Page number")
    row_count: int = Field(default=0, description="Number of rows")
    col_count: int = Field(default=0, description="Number of columns")
    confidence: float = Field(default=1.0, ge=0.0, le=1.0, description="Table extraction confidence")


class FigureData(BaseModel):
    """Figure/image data extracted from a document."""
    image_path: Optional[str] = Field(default=None, description="Path to extracted image file")
    caption: Optional[str] = Field(default=None, description="Figure caption if detected")
    bbox: Optional[List[float]] = Field(default=None, description="Bounding box coordinates")
    page_number: int = Field(..., ge=1, description="Page number")
    figure_type: str = Field(default="image", description="Type: image, chart, diagram, etc.")


class ExtractionMetadata(BaseModel):
    """Metadata about the extraction process."""
    strategy_used: str = Field(..., description="Extraction strategy: fast_text, layout_aware, vision")
    extraction_time_ms: int = Field(default=0, ge=0, description="Total extraction time in milliseconds")
    tool_version: Optional[str] = Field(default=None, description="Version of extraction tool used")
    confidence_score: float = Field(default=0.0, ge=0.0, le=1.0, description="Overall extraction confidence")
    pages_processed: int = Field(default=0, ge=0, description="Number of pages successfully processed")
    pages_failed: int = Field(default=0, ge=0, description="Number of pages that failed extraction")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Extraction timestamp")


class ExtractedDocument(BaseModel):
    """
    ExtractedDocument is the output of the extraction strategies.
    It contains all extracted content with provenance information.
    """
    doc_id: str = Field(..., description="Document identifier matching DocumentProfile")
    file_path: str = Field(..., description="Original file path")
    page_count: int = Field(..., ge=0, description="Total number of pages")
    
    # Extracted content
    pages: List[Dict[int, List[TextBlock]]] = Field(
        default_factory=list,
        description="Pages with their text blocks, keyed by page number"
    )
    tables: List[TableData] = Field(default_factory=list, description="All tables extracted")
    figures: List[FigureData] = Field(default_factory=list, description="All figures/images extracted")
    
    # Full text representation
    full_text: str = Field(default="", description="Full text concatenation for easy access")
    
    # Metadata
    metadata: ExtractionMetadata = Field(
        default_factory=ExtractionMetadata,
        description="Extraction process metadata"
    )
    
    # Additional data
    language: Optional[str] = Field(default=None, description="Detected language")
    domain_hint: Optional[str] = Field(default=None, description="Domain classification")
    
    class Config:
        """Pydantic model configuration."""
        json_schema_extra = {
            "example": {
                "doc_id": "doc_001",
                "file_path": "/documents/annual_report.pdf",
                "page_count": 42,
                "pages": [],
                "tables": [],
                "figures": [],
                "full_text": "Sample text...",
                "metadata": {
                    "strategy_used": "layout_aware",
                    "extraction_time_ms": 15000,
                    "confidence_score": 0.92,
                    "pages_processed": 42,
                    "pages_failed": 0
                }
            }
        }
