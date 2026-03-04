"""ProvenanceChain schema for source tracking and verification."""

from pydantic import BaseModel, Field, field_validator
from typing import List, Optional, Dict, Any
from enum import Enum
from datetime import datetime


class VerificationStatus(str, Enum):
    """Status of verification for extracted content."""
    VERIFIED = "verified"
    UNVERIFIED = "unverified"
    DISPUTED = "disputed"
    FLAGGED = "flagged"


class SourceLocation(BaseModel):
    """Location of extracted content within the source document."""
    document_name: str = Field(..., description="Source document filename")
    document_path: str = Field(..., description="Full path to source document")
    page_number: int = Field(..., ge=1, description="Page number in source")
    bbox: Optional[List[float]] = Field(
        default=None,
        description="Bounding box [x0, y0, x1, y1]",
        min_length=4,
        max_length=4
    )
    block_index: Optional[int] = Field(default=None, description="Text block index on page")
    line_numbers: Optional[List[int]] = Field(
        default=None,
        description="Line numbers within the block"
    )
    
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


class SourceContent(BaseModel):
    """Original content extracted from the source."""
    text: str = Field(..., description="Original extracted text")
    text_hash: str = Field(..., description="SHA256 hash of original text")
    language: Optional[str] = Field(default=None, description="Detected language")
    confidence: float = Field(
        default=1.0,
        ge=0.0,
        le=1.0,
        description="Confidence in extraction accuracy"
    )
    extraction_method: str = Field(
        ...,
        description="Method used: fast_text, layout_aware, vision"
    )


class ProvenanceSource(BaseModel):
    """A single source for a piece of extracted content."""
    location: SourceLocation = Field(..., description="Source location information")
    content: SourceContent = Field(..., description="Original content from source")
    
    # Additional metadata
    document_id: str = Field(..., description="Document ID in the system")
    page_id: str = Field(..., description="Page identifier")
    block_id: Optional[str] = Field(default=None, description="Text block identifier")


class Claim(BaseModel):
    """A claim or assertion derived from source content."""
    claim_id: str = Field(..., description="Unique identifier for this claim")
    content: str = Field(..., description="The claim/assertion made")
    sources: List[ProvenanceSource] = Field(
        default_factory=list,
        description="All sources supporting this claim"
    )
    
    # Verification
    verification_status: VerificationStatus = Field(
        default=VerificationStatus.UNVERIFIED,
        description="Current verification status"
    )
    verification_method: Optional[str] = Field(
        default=None,
        description="Method used for verification"
    )
    verified_at: Optional[datetime] = Field(
        default=None,
        description="Timestamp of verification"
    )
    
    # Metadata
    confidence: float = Field(
        default=1.0,
        ge=0.0,
        le=1.0,
        description="Confidence in claim accuracy"
    )
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Timestamp of claim creation"
    )


class ProvenanceChain(BaseModel):
    """
    ProvenanceChain tracks the origin of all extracted content,
    enabling verification and answering "Where does this come from?".
    """
    chain_id: str = Field(..., description="Unique identifier for this provenance chain")
    doc_id: str = Field(..., description="Parent document ID")
    
    # Claims and sources
    claims: List[Claim] = Field(
        default_factory=list,
        description="All claims made from this document"
    )
    
    # Statistics
    total_sources: int = Field(
        default=0,
        description="Total number of source references"
    )
    verified_claims: int = Field(
        default=0,
        description="Number of verified claims"
    )
    
    # Surface bbox and content_hash at chain level for easy access
    primary_bbox: Optional[List[float]] = Field(
        default=None,
        description="Primary bounding box for the entire extraction",
        min_length=4,
        max_length=4
    )
    content_hash: Optional[str] = Field(
        default=None,
        description="Combined SHA256 hash of all content for verification"
    )
    
    # Chain metadata
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Chain creation timestamp"
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Last update timestamp"
    )
    
    @field_validator('primary_bbox')
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
    
    def add_claim(
        self,
        claim_id: str,
        content: str,
        sources: List[ProvenanceSource],
        confidence: float = 1.0
    ) -> Claim:
        """Add a new claim with sources to the chain."""
        claim = Claim(
            claim_id=claim_id,
            content=content,
            sources=sources,
            confidence=confidence
        )
        self.claims.append(claim)
        self.total_sources += len(sources)
        self.updated_at = datetime.utcnow()
        return claim
    
    def verify_claim(
        self,
        claim_id: str,
        status: VerificationStatus,
        method: str
    ) -> bool:
        """Update the verification status of a claim."""
        for claim in self.claims:
            if claim.claim_id == claim_id:
                claim.verification_status = status
                claim.verification_method = method
                claim.verified_at = datetime.utcnow()
                if status == VerificationStatus.VERIFIED:
                    self.verified_claims += 1
                self.updated_at = datetime.utcnow()
                return True
        return False
    
    def get_sources_for_claim(self, claim_id: str) -> List[ProvenanceSource]:
        """Get all sources for a specific claim."""
        for claim in self.claims:
            if claim.claim_id == claim_id:
                return claim.sources
        return []
    
    def get_claims_for_page(self, page_number: int) -> List[Claim]:
        """Get all claims originating from a specific page."""
        return [
            claim for claim in self.claims
            if any(source.location.page_number == page_number for source in claim.sources)
        ]
    
    def get_verification_summary(self) -> Dict[str, int]:
        """Get a summary of verification statuses."""
        summary = {status.value: 0 for status in VerificationStatus}
        for claim in self.claims:
            summary[claim.verification_status.value] += 1
        return summary
    
    def compute_content_hash(self) -> str:
        """Compute combined hash of all claim content."""
        import hashlib
        hasher = hashlib.sha256()
        for claim in sorted(self.claims, key=lambda c: c.claim_id):
            hasher.update(claim.content.encode('utf-8'))
        self.content_hash = f"sha256:{hasher.hexdigest()}"
        return self.content_hash
    
    def compute_primary_bbox(self) -> Optional[List[float]]:
        """Compute primary bounding box from all claims."""
        all_bboxes = []
        for claim in self.claims:
            for source in claim.sources:
                if source.location.bbox:
                    all_bboxes.append(source.location.bbox)
        
        if not all_bboxes:
            return None
        
        # Compute union of all bboxes
        x0 = min(b[0] for b in all_bboxes)
        y0 = min(b[1] for b in all_bboxes)
        x1 = max(b[2] for b in all_bboxes)
        y1 = max(b[3] for b in all_bboxes)
        
        self.primary_bbox = [x0, y0, x1, y1]
        return self.primary_bbox
    
    class Config:
        """Pydantic model configuration."""
        use_enum_values = True
        json_schema_extra = {
            "example": {
                "chain_id": "prov_doc_001",
                "doc_id": "doc_001",
                "claims": [
                    {
                        "claim_id": "claim_001",
                        "content": "Revenue was $4.2B in Q3",
                        "sources": [
                            {
                                "location": {
                                    "document_name": "annual_report.pdf",
                                    "page_number": 42,
                                    "bbox": [50, 200, 500, 280]
                                },
                                "content": {
                                    "text": "Q3 Revenue: $4.2B",
                                    "text_hash": "sha256:abc123"
                                }
                            }
                        ],
                        "verification_status": "verified",
                        "confidence": 0.95
                    }
                ],
                "total_sources": 1,
                "verified_claims": 1,
                "primary_bbox": [50, 200, 500, 280],
                "content_hash": "sha256:def456"
            }
        }
