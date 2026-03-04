"""Logical Document Unit (LDU) schema for semantic chunking."""

from pydantic import BaseModel, Field, field_validator, model_validator
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


class LDURelationship(BaseModel):
    """Parent-child relationship between LDUs."""
    parent_ldu_id: Optional[str] = Field(default=None, description="Parent LDU ID")
    child_ldu_ids: List[str] = Field(
        default_factory=list, 
        description="Child LDU IDs"
    )
    sibling_ldu_ids: List[str] = Field(
        default_factory=list,
        description="Sibling LDU IDs (same parent)"
    )
    
    def add_child(self, child_id: str) -> None:
        """Add a child LDU ID."""
        if child_id not in self.child_ldu_ids:
            self.child_ldu_ids.append(child_id)
    
    def remove_child(self, child_id: str) -> None:
        """Remove a child LDU ID."""
        if child_id in self.child_ldu_ids:
            self.child_ldu_ids.remove(child_id)


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
    
    # Spatial metadata using BBox
    bbox: Optional[List[float]] = Field(
        default=None,
        description="Bounding box [x0, y0, x1, y1]",
        min_length=4,
        max_length=4
    )
    page_number: int = Field(..., ge=1, description="Page number where this LDU appears")
    
    # Parent-child relationships
    relationships: LDURelationship = Field(
        default_factory=LDURelationship,
        description="Parent-child and sibling relationships"
    )
    
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
    
    @field_validator('bbox')
    @classmethod
    def validate_bbox_coordinates(cls, v: Optional[List[float]]) -> Optional[List[float]]:
        """Validate bbox coordinates if provided."""
        if v is None:
            return v
        if len(v) != 4:
            raise ValueError(f"BBox must have exactly 4 coordinates, got {len(v)}")
        x0, y0, x1, y1 = v
        if x1 <= x0:
            raise ValueError(f"x1 ({x1}) must be greater than x0 ({x0})")
        if y1 <= y0:
            raise ValueError(f"y1 ({y1}) must be greater than y0 ({y0})")
        return v
    
    def set_parent(self, parent_id: Optional[str]) -> None:
        """Set the parent LDU ID and update relationships."""
        self.relationships.parent_ldu_id = parent_id
    
    def add_child(self, child_id: str) -> None:
        """Add a child LDU ID."""
        self.relationships.add_child(child_id)
    
    def get_parent_id(self) -> Optional[str]:
        """Get the parent LDU ID."""
        return self.relationships.parent_ldu_id
    
    def get_child_ids(self) -> List[str]:
        """Get all child LDU IDs."""
        return self.relationships.child_ldu_ids.copy()
    
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
                "bbox": [50.0, 100.0, 500.0, 280.0],
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
    
    # Surface content_hash at the set level for easy verification
    content_hash: Optional[str] = Field(
        default=None,
        description="Combined SHA256 hash of all LDU content for verification"
    )
    
    @model_validator(mode='after')
    def update_count(self):
        """Update total_ldu_count based on actual LDUs."""
        self.total_ldu_count = len(self.ldus)
        return self
    
    def get_by_type(self, chunk_type: ChunkType) -> List[LDU]:
        """Get all LDUs of a specific type."""
        return [ldu for ldu in self.ldus if ldu.chunk_type == chunk_type]
    
    def get_by_page(self, page_number: int) -> List[LDU]:
        """Get all LDUs on a specific page."""
        return [ldu for ldu in self.ldus if ldu.page_number == page_number]
    
    def get_by_section(self, section_path: List[str]) -> List[LDU]:
        """Get all LDUs in a specific section."""
        return [ldu for ldu in self.ldus if ldu.section_path == section_path]
    
    def get_by_id(self, ldu_id: str) -> Optional[LDU]:
        """Get a specific LDU by ID."""
        for ldu in self.ldus:
            if ldu.ldu_id == ldu_id:
                return ldu
        return None
    
    def get_children(self, parent_id: str) -> List[LDU]:
        """Get all children of a specific LDU."""
        parent = self.get_by_id(parent_id)
        if parent is None:
            return []
        return [ldu for ldu in self.ldus if parent_id in ldu.relationships.child_ldu_ids]
    
    def get_siblings(self, ldu_id: str) -> List[LDU]:
        """Get all siblings of a specific LDU."""
        ldu = self.get_by_id(ldu_id)
        if ldu is None or ldu.relationships.parent_ldu_id is None:
            return []
        return [
            sibling for sibling in self.ldus 
            if sibling.ldu_id != ldu_id 
            and sibling.relationships.parent_ldu_id == ldu.relationships.parent_ldu_id
        ]
    
    def build_hierarchy(self) -> None:
        """Build parent-child relationships from section paths."""
        # Group LDUs by parent section
        section_ldus: Dict[str, List[LDU]] = {}
        for ldu in self.ldus:
            parent = ldu.parent_section or "root"
            if parent not in section_ldus:
                section_ldus[parent] = []
            section_ldus[parent].append(ldu)
        
        # Set up parent-child relationships based on section hierarchy
        for ldu in self.ldus:
            if ldu.section_path and len(ldu.section_path) > 1:
                # Parent is the previous level in the path
                parent_section = ldu.section_path[-2]
                # Find parent LDU
                for other_ldu in self.ldus:
                    if other_ldu.chunk_type == ChunkType.HEADING and other_ldu.content == parent_section:
                        ldu.set_parent(other_ldu.ldu_id)
                        other_ldu.add_child(ldu.ldu_id)
                        break
