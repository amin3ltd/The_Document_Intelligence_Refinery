"""
Strategy A: Fast Text Extraction using pdfplumber.

This strategy is optimized for native digital PDFs with simple layouts.
Low cost, fast processing for single-column documents.
"""

import hashlib
import logging
import time
from datetime import datetime
from typing import Dict, List

import pdfplumber

from src.models.document_profile import DocumentProfile
from src.models.extracted_document import (
    ExtractedDocument,
    ExtractionMetadata,
    TextBlock,
)

logger = logging.getLogger(__name__)


class FastTextStrategy:
    """
    Fast text extraction strategy using pdfplumber.
    
    Best for: Native digital PDFs with simple layouts
    Cost: Low (~$0.001/page)
    Speed: Fast
    """
    
    @property
    def name(self) -> str:
        return "strategy_a"
    
    def extract(self, file_path: str, profile: DocumentProfile) -> ExtractedDocument:
        """
        Extract text using pdfplumber.
        
        Args:
            file_path: Path to the PDF file
            profile: Document profile for context
            
        Returns:
            ExtractedDocument with extracted content
        """
        start_time = time.time()
        
        logger.info(f"Starting fast text extraction for {file_path}")
        
        pages: List[Dict[int, List[TextBlock]]] = []
        full_text_parts = []
        pages_processed = 0
        pages_failed = 0
        
        try:
            with pdfplumber.open(file_path) as pdf:
                page_count = len(pdf.pages)
                
                for page_num, page in enumerate(pdf.pages, start=1):
                    try:
                        # Extract text
                        text = page.extract_text() or ""
                        full_text_parts.append(text)
                        
                        # Extract words with positions for text blocks
                        words = page.extract_words() or []
                        
                        # Group words into blocks
                        blocks = self._extract_blocks(words, page_num)
                        pages.append(blocks)
                        
                        pages_processed += 1
                        
                    except Exception as e:
                        logger.warning(f"Failed to extract page {page_num}: {e}")
                        pages_failed += 1
                
                full_text = "\n\n".join(full_text_parts)
                
                # Calculate confidence
                confidence = self._calculate_confidence(
                    pages_processed, 
                    pages_failed, 
                    page_count,
                    full_text
                )
        
        except Exception as e:
            logger.error(f"Failed to open PDF: {e}")
            raise
        
        extraction_time_ms = int((time.time() - start_time) * 1000)
        
        metadata = ExtractionMetadata(
            strategy_used=self.name,
            extraction_time_ms=extraction_time_ms,
            tool_version=pdfplumber.__version__,
            confidence_score=confidence,
            pages_processed=pages_processed,
            pages_failed=pages_failed,
            timestamp=datetime.utcnow(),
        )
        
        result = ExtractedDocument(
            doc_id=profile.doc_id,
            file_path=file_path,
            page_count=len(pages),
            pages=pages,
            full_text=full_text,
            metadata=metadata,
            language=profile.language,
            domain_hint=profile.domain_hint.value if profile.domain_hint else None,
        )
        
        logger.info(
            f"Fast text extraction complete: {pages_processed} pages, "
            f"confidence: {confidence:.2f}, time: {extraction_time_ms}ms"
        )
        
        return result
    
    def _extract_blocks(self, words: List[Dict], page_num: int) -> Dict[int, List[TextBlock]]:
        """Extract text blocks from words."""
        blocks = {}
        
        if not words:
            return blocks
        
        # Group words by their vertical position (line)
        line_map: Dict[int, List[Dict]] = {}
        for word in words:
            top = int(word.get("top", 0))
            if top not in line_map:
                line_map[top] = []
            line_map[top].append(word)
        
        # Create blocks from lines
        block_id = 0
        for top in sorted(line_map.keys()):
            line_words = line_map[top]
            text = " ".join(w.get("text", "") for w in line_words)
            
            x0 = min(w.get("x0", 0) for w in line_words)
            x1 = max(w.get("x1", 0) for w in line_words)
            y0 = min(w.get("top", 0) for w in line_words)
            y1 = max(w.get("bottom", 0) for w in line_words)
            
            block = TextBlock(
                text=text,
                bbox=[x0, y0, x1, y1],
                page_number=page_num,
                block_type="text",
                confidence=0.9,
            )
            
            blocks[block_id] = [block]
            block_id += 1
        
        return blocks
    
    def _calculate_confidence(
        self,
        processed: int,
        failed: int,
        total: int,
        full_text: str,
    ) -> float:
        """Calculate confidence score for the extraction."""
        if total == 0:
            return 0.0
        
        # Base confidence from page success rate
        page_confidence = processed / total if total > 0 else 0.0
        
        # Text density confidence
        avg_chars_per_page = len(full_text) / total if total > 0 else 0
        
        if avg_chars_per_page > 500:
            density_confidence = 1.0
        elif avg_chars_per_page > 100:
            density_confidence = 0.7
        else:
            density_confidence = 0.3
        
        # Text quality confidence (presence of meaningful text)
        text_quality = 1.0 if full_text.strip() else 0.0
        
        # Weighted combination
        confidence = (
            0.4 * page_confidence +
            0.3 * density_confidence +
            0.3 * text_quality
        )
        
        return round(confidence, 2)
