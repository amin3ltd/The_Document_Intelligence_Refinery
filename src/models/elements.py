"""Element-based result format for Unstructured-compatible processing.

This module provides semantic element extraction with:
- Element type classification
- Unique identifiers for tracking
- Hierarchical relationships
- Spatial metadata


"""

from enum import Enum
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime


class ElementType(str, Enum):
    """Semantic element types for document content.
    
    Compatible with Unstructured's element types.
    """
    # Text elements
    PARAGRAPH = "Paragraph"
    TITLE = "Title"
    HEADING_1 = "Heading-1"
    HEADING_2 = "Heading-2"
    HEADING_3 = "Heading-3"
    FORMULA = "Formula"
    EQUATION = "Equation"
    
    # Lists
    LIST_ITEM = "ListItem"
    BULLETED_LIST = "BulletedList"
    NUMBERED_LIST = "NumberedList"
    
    # Tables
    TABLE = "Table"
    TABLE_FOOTER = "TableFooter"
    
    # Media
    FIGURE = "Figure"
    IMAGE = "Image"
    CHART = "Chart"
    
    # Document structure
    PAGE_BREAK = "PageBreak"
    SECTION_HEADER = "SectionHeader"
    
    # OCR-specific
    OCR_ERROR = "OCRError"
    
    # Forms
    FORM_TEXT = "FormText"
    FORM_FIELD = "FormField"
    
    # Headers/Footers
    HEADER = "Header"
    FOOTER = "Footer"
    
    # Footnotes
    FOOTNOTE = "Footnote"
    CITATION = "Citation"
    
    # Catch-all
    UNCLASSIFIED = "Unclassified"


class ContentLayer(str, Enum):
    """Content layer classification - which part of the page the element belongs to."""
    BODY = "body"
    HEADER = "header"
    FOOTER = "footer"
    FOOTNOTE = "footnote"
    MARGINALIA = "marginalia"


class ElementMetadata(BaseModel):
    """Metadata for an element."""
    # File/source info
    filename: Optional[str] = Field(default=None, description="Source filename")
    file_directory: Optional[str] = Field(default=None, description="Source directory")
    file_type: Optional[str] = Field(default=None, description="MIME type")
    
    # Page info
    page_number: Optional[int] = Field(default=None, ge=1, description="Page number")
    page_index: Optional[int] = Field(default=None, ge=0, description="Zero-based page index")
    
    # Coordinates
    coordinates: Optional[List[float]] = Field(
        default=None,
        description="Bounding box [x0, y0, x1, y1]",
        min_length=4,
        max_length=4
    )
    
    # Text metadata
    text_as_html: Optional[str] = Field(default=None, description="HTML representation")
    is_continuation: bool = Field(default=False, description="Is this a continuation of previous element")
    
    # Detection metadata
    detection_origin: Optional[str] = Field(default=None, description="Where this element was detected")
    layout_origin: Optional[str] = Field(default=None, description="Layout analysis source")
    
    # Links and references
    url: Optional[str] = Field(default=None, description="Associated URL if any")
    link_urls: List[str] = Field(default_factory=list, description="All URLs in this element")
    
    # Table-specific
    table_row_count: Optional[int] = Field(default=None, description="Number of rows")
    table_column_count: Optional[int] = Field(default=None, description="Number of columns")
    table_header_rows: Optional[int] = Field(default=None, description="Header row count")
    
    # Font metadata
    font_family: Optional[str] = Field(default=None, description="Font family")
    font_size: Optional[float] = Field(default=None, description="Font size in points")
    font_color: Optional[str] = Field(default=None, description="Font color")
    is_bold: bool = Field(default=False, description="Is bold text")
    is_italic: bool = Field(default=False, description="Is italic text")
    
    # Classification
    category_depth: Optional[int] = Field(default=None, description="Heading hierarchy depth")
    is_list_item: bool = Field(default=False, description="Is part of a list")
    list_marker: Optional[str] = Field(default=None, description="List marker (bullet, number, etc.)")
    
    # Custom metadata
    custom_metadata: Dict[str, Any] = Field(default_factory=dict, description="Custom key-value metadata")
    
    # Timestamps
    detected_at: datetime = Field(default_factory=datetime.utcnow, description="Detection timestamp")


class Element(BaseModel):
    """
    A semantic element with type classification and unique identification.
    
    This is the Unstructured-compatible element format that can be used
    for downstream processing, RAG pipelines, and knowledge graph construction.
    """
    # Element identification
    element_id: str = Field(
        ...,
        description="Unique identifier for this element (deterministic hash-based)"
    )
    
    # Type classification
    type: ElementType = Field(default=ElementType.UNCLASSIFIED, description="Element type")
    
    # Content
    text: str = Field(default="", description="Element text content")
    embed_text: Optional[str] = Field(
        default=None,
        description="Embedded/representative text for embeddings"
    )
    
    # Hierarchy
    layout_layer: ContentLayer = Field(default=ContentLayer.BODY, description="Content layer")
    parent_id: Optional[str] = Field(default=None, description="Parent element ID")
    child_ids: List[str] = Field(default_factory=list, description="Child element IDs")
    
    # Section/semantic hierarchy
    section_path: List[str] = Field(
        default_factory=list,
        description="Section hierarchy path (e.g., ['Chapter 1', 'Section 1.1'])"
    )
    heading_level: Optional[int] = Field(default=None, ge=1, description="Heading level (1-6)")
    
    # Position in sequence
    position_index: int = Field(default=0, ge=0, description="Position in reading order")
    
    # Metadata
    metadata: ElementMetadata = Field(
        default_factory=ElementMetadata,
        description="Element metadata"
    )
    
    # Confidence scores
    detection_confidence: float = Field(
        default=1.0,
        ge=0.0,
        le=1.0,
        description="Detection confidence score"
    )
    classification_confidence: float = Field(
        default=1.0,
        ge=0.0,
        le=1.0,
        description="Classification confidence score"
    )
    
    def __repr__(self) -> str:
        return f"<Element {self.element_id[:8]}... type={self.type.value} text={self.text[:30]}...>"
    
    class Config:
        """Pydantic model configuration."""
        use_enum_values = False


class Chunk(BaseModel):
    """
    A text chunk with optional embeddings for vector search.
    
    Created when chunking is enabled in extraction configuration.
    """
    chunk_id: str = Field(..., description="Unique chunk identifier")
    text: str = Field(..., description="Chunk text content")
    
    # Position info
    chunk_index: int = Field(default=0, ge=0, description="Zero-based chunk index")
    total_chunks: int = Field(default=1, ge=1, description="Total number of chunks")
    
    # Source tracking
    source_element_ids: List[str] = Field(
        default_factory=list,
        description="IDs of source elements this chunk came from"
    )
    
    # Page tracking
    page_numbers: List[int] = Field(
        default_factory=list,
        description="Page numbers this chunk spans"
    )
    
    # Embeddings
    embedding: Optional[List[float]] = Field(
        default=None,
        description="Vector embedding (if enabled)"
    )
    embedding_model: Optional[str] = Field(
        default=None,
        description="Model used to generate embedding"
    )
    
    # Context
    preceding_context: Optional[str] = Field(
        default=None,
        description="Text before this chunk (for context)"
    )
    following_context: Optional[str] = Field(
        default=None,
        description="Text after this chunk (for context)"
    )
    
    # Metadata
    token_count: Optional[int] = Field(default=None, ge=0, description="Estimated token count")
    char_count: int = Field(default=0, ge=0, description="Character count")
    
    def __repr__(self) -> str:
        return f"<Chunk {self.chunk_id[:8]}... index={self.chunk_index}/{self.total_chunks}>"
    
    class Config:
        """Pydantic model configuration."""
        json_schema_extra = {
            "example": {
                "chunk_id": "chunk_001",
                "text": "The quick brown fox...",
                "chunk_index": 0,
                "total_chunks": 10,
                "source_element_ids": ["el_001", "el_002"],
                "page_numbers": [1, 2],
                "char_count": 150
            }
        }


class ExtractedImage(BaseModel):
    """An image extracted from the document."""
    image_id: str = Field(..., description="Unique image identifier")
    
    # Image data
    image_bytes: Optional[bytes] = Field(
        default=None,
        description="Raw image bytes (if embedded)"
    )
    image_path: Optional[str] = Field(
        default=None,
        description="Path to saved image file"
    )
    
    # Image metadata
    mime_type: str = Field(default="image/png", description="Image MIME type")
    width: int = Field(..., ge=0, description="Image width in pixels")
    height: int = Field(..., ge=0, description="Image height in pixels")
    
    # Position
    page_number: int = Field(default=1, ge=1, description="Page number")
    bbox: Optional[List[float]] = Field(
        default=None,
        description="Bounding box on page [x0, y0, x1, y1]"
    )
    
    # Caption and context
    caption: Optional[str] = Field(default=None, description="Image caption if detected")
    alt_text: Optional[str] = Field(default=None, description="Alternative text")
    
    # OCR result if applicable
    ocr_result: Optional[str] = Field(
        default=None,
        description="OCR text if image was processed"
    )
    
    # Confidence
    extraction_confidence: float = Field(
        default=1.0,
        ge=0.0,
        le=1.0,
        description="Extraction confidence"
    )


class PageContent(BaseModel):
    """Per-page content when page extraction is enabled."""
    page_number: int = Field(..., ge=1, description="Page number")
    page_index: int = Field(default=0, ge=0, description="Zero-based page index")
    
    # Page text
    text: str = Field(default="", description="Full page text")
    
    # Elements on this page
    elements: List[Element] = Field(
        default_factory=list,
        description="All elements on this page"
    )
    
    # Tables on this page
    tables: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Tables on this page"
    )
    
    # Images on this page
    images: List[ExtractedImage] = Field(
        default_factory=list,
        description="Images on this page"
    )
    
    # Page metadata
    width: Optional[float] = Field(default=None, description="Page width in points")
    height: Optional[float] = Field(default=None, description="Page height in points")
    rotation: int = Field(default=0, description="Page rotation in degrees")
    
    # OCR-specific
    languages: List[str] = Field(
        default_factory=list,
        description="Detected languages on this page"
    )
    is_scanned: bool = Field(default=False, description="Whether page required OCR")
    
    class Config:
        """Pydantic model configuration."""
        json_schema_extra = {
            "example": {
                "page_number": 1,
                "page_index": 0,
                "text": "Page text content...",
                "elements": [],
                "tables": [],
                "images": [],
                "width": 612.0,
                "height": 792.0
            }
        }
