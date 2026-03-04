"""Logical Document Unit (LDU) schema for semantic chunking."""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from enum import Enum


class ChunkType(str, Enum):
    """Types of logical document units for semantic chunking."""
    PARAGRAPH = "paragraph"
    HEADING = "heading"
    TABLE = "table"
    TABLE_CELL = "table_cell"
    FIGURE_CAPTION = "figure_caption"
    LIST_ITEM = "list_item"
    CODE_BLOCK = "code_block"
    QUOTE = "quote"
    FOOTNOTE = "footnote"
    HEADER = "header"
    FOOTER = "footer"


class SemanticRelationship(BaseModel):
    """Represents semantic relationships between LDUs."""
    related_ldu_id: str = Field(..., description="ID of the related LDU")
    relationship_type: str = Field(
        ..., 
        description="Type: 'continues', 'references', 'describes', 'contains', 'precedes'"
    )
    strength: float = Field(default=1.0, ge=0.0, le=1.0, description="Relationship strength")


class LDU(BaseModel):
    """
    Logical Document Unit represents a semantically meaningful chunk
    of document content that preserves structural context.
    
    This is the output of the Semantic Chunking Engine and serves
    as the primary unit for downstream processing.
    """
    ldu_id: str = Field(..., description="Unique identifier for this LDU")
    doc_id: str = Field(..., description="Parent document ID")
    chunk_type: ChunkType = Field(..., description="Type of content in this LDU")
    content: str = Field(..., description="Text content of this chunk")
    
    # Structural metadata
    parent_section: Optional[str] = Field(default=None, description="Parent section title/ID")
    section_path: List[str] = Field(
        default_factory=list,
        description="Full path from root to current section"
    )
    level: int = Field(default=1, ge=0, description="Hierarchical level in document structure")
    
    # Spatial metadata for provenance
    bbox: Optional[List[float]] = Field(
        default=None,
        description="Bounding box [x0, y0, x1, y1]",
        min_length=4,
        max_length=4
    )
    page_number: int = Field(..., ge=1, description="Page number where this LDU appears")
    
    # Content analysis
    word_count: int = Field(default=0, ge=0, description="Number of words in this chunk")
    char_count: int = Field(default=0, ge=0, description="Number of characters in this chunk")
    has_numbers: bool = Field(default=False, description="Whether content contains numerical data")
    has_references: bool = Field(default=False, description="Whether content has cross-references")
    
    # Semantic relationships
    related_entities: List[str] = Field(
        default_factory=list,
        description="Entities mentioned in this chunk (tables, figures, sections)"
    )
    references: List[str] = Field(
        default_factory=list,
        description="Other LDUs or objects referenced by this chunk"
    )
    semantic_relationships: List[SemanticRelationship] = Field(
        default_factory=list,
        description="Structured relationships to other LDUs"
    )
    
    # Provenance
    source_block_ids: List[str] = Field(
        default_factory=list,
        description="IDs of source text blocks this LDU was derived from"
    )
    content_hash: str = Field(..., description="SHA256 hash of content for verification")
    
    # Confidence and quality
    confidence: float = Field(default=1.0, ge=0.0, le=1.0, description="Extraction confidence")
    is_complete: bool = Field(default=True, description="Whether this is a complete thought/unit")
    
    class Config:
        """Pydantic model configuration."""
        use_enum_values = True
        json_schema_extra = {
            "example": {
                "ldu_id": "doc_001_ldu_001",
                "doc_id": "doc_001",
                "chunk_type": "paragraph",
                "content": "The financial performance of the company is summarized in Table 3.1 below.",
                "parent_section": "Section 3.2: Financial Summary",
                "section_path": ["Annual Report 2023", "Financial Summary", "Section 3.2"],
                "level": 3,
                "page_number": 12,
                "word_count": 15,
                "has_numbers": False,
                "has_references": True,
                "related_entities": ["Table 3.1"],
                "references": ["table_3_1"],
                "semantic_relationships": [
                    {
                        "related_ldu_id": "doc_001_ldu_042",
                        "relationship_type": "references",
                        "strength": 1.0
                    }
                ],
                "content_hash": "sha256:abc123...",
                "confidence": 0.95,
                "is_complete": True
            }
        }


class LDUSet(BaseModel):
    """A collection of LDUs representing a processed document."""
    doc_id: str = Field(..., description="Document ID")
    ldus: List[LDU] = Field(default_factory=list, description="List of LDUs")
    total_ldu_count: int = Field(default=0, description="Total number of LDUs")
    chunking_strategy: str = Field(..., description="Strategy used for chunking")
    processing_time_ms: int = Field(default=0, description="Processing time in milliseconds")
    
    def get_by_type(self, chunk_type: ChunkType) -> List[LDU]:
        """Get all LDUs of a specific type."""
        return [ldu for ldu in self.ldus if ldu.chunk_type == chunk_type]
    
    def get_by_page(self, page_number: int) -> List[LDU]:
        """Get all LDUs on a specific page."""
        return [ldu for ldu in self.ldus if ldu.page_number == page_number]
    
    def get_by_section(self, section_path: List[str]) -> List[LDU]:
        """Get all LDUs in a specific section."""
        return [ldu for ldu in self.ldus if ldu.section_path == section_path]
