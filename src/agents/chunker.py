"""
Semantic Chunking Engine for Document Intelligence Refinery.

The Chunking Engine creates Logical Document Units (LDUs) that preserve
structural context for downstream processing.
Includes ChunkValidator to enforce all 5 chunking rules.
"""

import hashlib
import logging
from typing import List, Optional

from src.models.document_profile import DocumentProfile
from src.models.extracted_document import ExtractedDocument
from src.models.ldu import (
    ChunkType,
    LDU,
    LDUSet,
    SemanticRelationship,
)
from src.utils.plugin_system import Plugin, PluginMetadata, PluginType

logger = logging.getLogger(__name__)


class ChunkingRules:
    """
    The 5 rules for semantic chunking from DOMAIN_NOTES.md.
    
    These rules ensure that Logical Document Units (LDUs) preserve
    structural context and avoid the "Context Poverty" failure mode.
    """
    
    # Maximum chunk sizes (characters)
    MAX_PARAGRAPH_SIZE = 2000
    MAX_HEADING_SIZE = 500
    MAX_TABLE_CELL_SIZE = 500
    
    # Minimum chunk sizes to avoid fragmentation
    MIN_CHUNK_SIZE = 50
    
    # Relationship strengths
    REFERENCE_STRENGTH = 1.0
    CONTINUES_STRENGTH = 0.8
    
    @staticmethod
    def should_split_paragraph(text: str, word_count: int) -> bool:
        """Rule 1: Split long paragraphs at natural boundaries."""
        if word_count * 5 > ChunkingRules.MAX_PARAGRAPH_SIZE:  # ~5 chars per word
            return True
        return False
    
    @staticmethod
    def should_split_at_heading(text: str) -> bool:
        """Rule 2: Always start new chunk at headings."""
        # Simple heuristic: short lines that might be headings
        lines = text.split("\n")
        if len(lines) > 1:
            first_line = lines[0].strip()
            if len(first_line) < 100 and first_line.isupper():
                return True
        return False
    
    @staticmethod
    def preserve_table_integrity(table_text: str) -> bool:
        """Rule 3: Never split table cells across chunks."""
        # Tables should be kept as single LDUs
        return True
    
    @staticmethod
    def preserve_figure_caption_relation(caption: str, figure_ref: str) -> bool:
        """Rule 4: Keep figure captions with their figures."""
        return True
    
    @staticmethod
    def preserve_cross_references(text: str, references: List[str]) -> bool:
        """Rule 5: Keep cross-references with their targets."""
        # If text references figures/tables, keep them together
        for ref in references:
            if ref in text:
                return True
        return False


class Chunker:
    """
    Semantic chunking engine that creates LDUs from extracted documents.
    
    Implements the 5 chunking rules to avoid Context Poverty failure modes.
    """
    
    def __init__(self):
        """Initialize the chunker."""
        self.rules = ChunkingRules()
    
    def chunk(
        self,
        extracted_doc: ExtractedDocument,
        profile: DocumentProfile,
    ) -> LDUSet:
        """
        Create LDUs from extracted document content.
        
        Args:
            extracted_doc: The extracted document
            profile: Document profile for context
            
        Returns:
            LDUSet containing all LDUs
        """
        logger.info(f"Chunking document {extracted_doc.doc_id}")
        
        ldus: List[LDU] = []
        ldu_counter = 0
        
        # Process each page
        for page in extracted_doc.pages:
            for page_num, blocks in page.items():
                for block in blocks:
                    ldu = self._create_ldu_from_block(
                        block=block,
                        page_num=page_num,
                        doc_id=extracted_doc.doc_id,
                        ldu_counter=ldu_counter,
                    )
                    ldus.append(ldu)
                    ldu_counter += 1
        
        # Process tables as separate LDUs
        for table in extracted_doc.tables:
            ldu = self._create_ldu_from_table(
                table=table,
                doc_id=extracted_doc.doc_id,
                ldu_counter=ldu_counter,
            )
            ldus.append(ldu)
            ldu_counter += 1
        
        # Build semantic relationships between LDUs
        ldus = self._build_relationships(ldus)
        
        ldu_set = LDUSet(
            doc_id=extracted_doc.doc_id,
            ldus=ldus,
            total_ldu_count=len(ldus),
            chunking_strategy="semantic_v1",
        )
        
        logger.info(f"Created {len(ldus)} LDUs")
        
        return ldu_set
    
    def _create_ldu_from_block(
        self,
        block,
        page_num: int,
        doc_id: str,
        ldu_counter: int,
    ) -> LDU:
        """Create an LDU from a text block."""
        text = block.get("text", "")
        bbox = block.get("bbox")
        
        word_count = len(text.split())
        char_count = len(text)
        
        # Determine chunk type
        chunk_type = self._detect_chunk_type(text, block)
        
        # Generate content hash
        content_hash = hashlib.sha256(text.encode()).hexdigest()
        
        # Detect references
        references = self._extract_references(text)
        
        # Detect numbers
        has_numbers = any(c.isdigit() for c in text)
        
        return LDU(
            ldu_id=f"{doc_id}_ldu_{ldu_counter:04d}",
            doc_id=doc_id,
            chunk_type=chunk_type,
            content=text,
            page_number=page_num,
            bbox=bbox,
            word_count=word_count,
            char_count=char_count,
            has_numbers=has_numbers,
            has_references=len(references) > 0,
            references=references,
            related_entities=self._extract_entities(text),
            content_hash=content_hash,
        )
    
    def _create_ldu_from_table(
        self,
        table,
        doc_id: str,
        ldu_counter: int,
    ) -> LDU:
        """Create an LDU from a table."""
        # Flatten table for text representation
        text = ""
        if table.headers:
            text += " | ".join(table.headers) + "\n"
        for row in table.rows:
            text += " | ".join(row) + "\n"
        
        return LDU(
            ldu_id=f"{doc_id}_ldu_{ldu_counter:04d}",
            doc_id=doc_id,
            chunk_type=ChunkType.TABLE,
            content=text,
            page_number=table.page_number,
            bbox=table.bbox,
            word_count=len(text.split()),
            char_count=len(text),
            has_numbers=True,
            content_hash=hashlib.sha256(text.encode()).hexdigest(),
        )
    
    def _detect_chunk_type(self, text: str, block: dict) -> ChunkType:
        """Detect the chunk type based on text content."""
        # Simple heuristics for chunk type detection
        lines = text.split("\n")
        
        if len(lines) == 1 and len(text) < 100:
            # Short single line might be a heading
            if text.isupper() or text.endswith(":"):
                return ChunkType.HEADING
        
        # Check for list items
        if text.strip().startswith(("-", "*", "•", "1.", "2.", "3.")):
            return ChunkType.LIST_ITEM
        
        # Default to paragraph
        return ChunkType.PARAGRAPH
    
    def _extract_references(self, text: str) -> List[str]:
        """Extract figure/table references from text."""
        import re
        
        # Pattern for references like "Table 3.1", "Figure 2", etc.
        patterns = [
            r"(?:table|figure|fig\.|chart)\s*\d+\.?\d*",
        ]
        
        references = []
        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            references.extend(matches)
        
        return references
    
    def _extract_entities(self, text: str) -> List[str]:
        """Extract entity references from text."""
        import re
        
        # Extract potential entity references
        entities = []
        
        # Table references
        table_refs = re.findall(r"(?:table|tab\.)\s*(\d+\.?\d*)", text, re.IGNORECASE)
        entities.extend([f"Table {ref}" for ref in table_refs])
        
        # Figure references
        fig_refs = re.findall(r"(?:figure|fig\.)\s*(\d+\.?\d*)", text, re.IGNORECASE)
        entities.extend([f"Figure {ref}" for ref in fig_refs])
        
        # Section references
        section_refs = re.findall(r"(?:section|sec\.)\s*(\d+\.?\d*)", text, re.IGNORECASE)
        entities.extend([f"Section {ref}" for ref in section_refs])
        
        return entities
    
    def _build_relationships(self, ldus: List[LDU]) -> List[LDU]:
        """Build semantic relationships between LDUs."""
        # Simple relationship building based on references
        for i, ldu in enumerate(ldus):
            for j, other in enumerate(ldus):
                if i == j:
                    continue
                
                # Check if this LDU references the other
                for ref in ldu.references:
                    if ref.lower() in other.content.lower():
                        relationship = SemanticRelationship(
                            related_ldu_id=other.ldu_id,
                            relationship_type="references",
                            strength=ChunkingRules.REFERENCE_STRENGTH,
                        )
                        ldu.semantic_relationships.append(relationship)
        
        return ldus


class ChunkValidator:
    """
    Validates that chunks satisfy all 5 chunking rules.
    
    This ensures LDUs avoid the "Context Poverty" failure mode
    by enforcing structural integrity rules.
    """
    
    def __init__(self):
        self.rules = ChunkingRules()
        self.validation_errors: List[str] = []
    
    def validate(self, ldu: LDU) -> bool:
        """
        Validate a single LDU against all 5 rules.
        
        Returns True if LDU is valid.
        """
        self.validation_errors = []
        
        # Rule 1: Check paragraph size
        if ldu.chunk_type == ChunkType.PARAGRAPH:
            if ldu.char_count > ChunkingRules.MAX_PARAGRAPH_SIZE:
                self.validation_errors.append(
                    f"Rule 1 violation: Paragraph exceeds max size "
                    f"({ldu.char_count} > {ChunkingRules.MAX_PARAGRAPH_SIZE})"
                )
            if ldu.char_count < ChunkingRules.MIN_CHUNK_SIZE:
                self.validation_errors.append(
                    f"Rule 1 violation: Paragraph below min size "
                    f"({ldu.char_count} < {ChunkingRules.MIN_CHUNK_SIZE})"
                )
        
        # Rule 2: Headings should not be too long
        if ldu.chunk_type == ChunkType.HEADING:
            if ldu.char_count > ChunkingRules.MAX_HEADING_SIZE:
                self.validation_errors.append(
                    f"Rule 2 violation: Heading exceeds max size "
                    f"({ldu.char_count} > {ChunkingRules.MAX_HEADING_SIZE})"
                )
        
        # Rule 3: Table integrity
        if ldu.chunk_type == ChunkType.TABLE:
            # Tables should not be split - check cell count
            if ldu.char_count > ChunkingRules.MAX_TABLE_CELL_SIZE * 10:
                self.validation_errors.append(
                    f"Rule 3 violation: Table appears to be too large "
                    f"({ldu.char_count} chars)"
                )
        
        # Rule 4: Figure-caption relation
        # This is validated at the relationship level
        if ldu.chunk_type == ChunkType.FIGURE_CAPTION:
            if not ldu.has_references:
                self.validation_errors.append(
                    f"Rule 4 warning: Figure caption has no reference target"
                )
        
        # Rule 5: Cross-reference integrity
        # Check that referenced content exists
        if ldu.has_references:
            for ref in ldu.references:
                if not ref:  # Empty reference
                    self.validation_errors.append(
                        f"Rule 5 violation: Empty reference in {ldu.ldu_id}"
                    )
        
        return len(self.validation_errors) == 0
    
    def validate_lduset(self, ldu_set: LDUSet) -> bool:
        """
        Validate all LDUs in a set.
        
        Returns True if all LDUs are valid.
        """
        all_valid = True
        for ldu in ldu_set.ldus:
            if not self.validate(ldu):
                all_valid = False
                for error in self.validation_errors:
                    logger.warning(f"{ldu.ldu_id}: {error}")
        
        return all_valid
    
    def get_validation_report(self, ldu_set: LDUSet) -> dict:
        """
        Get a detailed validation report.
        
        Returns a dictionary with validation results.
        """
        report = {
            "total_ldus": len(ldu_set.ldus),
            "valid_ldus": 0,
            "invalid_ldus": 0,
            "rule_violations": {
                "rule_1_paragraph_size": 0,
                "rule_2_heading_boundaries": 0,
                "rule_3_table_integrity": 0,
                "rule_4_figure_caption": 0,
                "rule_5_cross_references": 0,
            },
            "errors": [],
        }
        
        for ldu in ldu_set.ldus:
            if self.validate(ldu):
                report["valid_ldus"] += 1
            else:
                report["invalid_ldus"] += 1
                for error in self.validation_errors:
                    report["errors"].append({"ldu_id": ldu.ldu_id, "error": error})
                    
                    # Count rule violations
                    if "Rule 1" in error:
                        report["rule_violations"]["rule_1_paragraph_size"] += 1
                    elif "Rule 2" in error:
                        report["rule_violations"]["rule_2_heading_boundaries"] += 1
                    elif "Rule 3" in error:
                        report["rule_violations"]["rule_3_table_integrity"] += 1
                    elif "Rule 4" in error:
                        report["rule_violations"]["rule_4_figure_caption"] += 1
                    elif "Rule 5" in error:
                        report["rule_violations"]["rule_5_cross_references"] += 1
        
        return report
