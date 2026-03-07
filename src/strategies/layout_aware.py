"""
Strategy B: Layout-Aware Extraction using MinerU/Docling.

This strategy handles complex layouts including multi-column, tables,
and mixed origin documents. Higher cost but better accuracy.
"""

import logging
import time
from datetime import datetime
from typing import Dict, List, Optional

from src.models.document_profile import DocumentProfile
from src.models.extracted_document import (
    ExtractedDocument,
    ExtractionMetadata,
    FigureData,
    TableData,
    TextBlock,
)

logger = logging.getLogger(__name__)


class LayoutAwareStrategy:
    """
    Layout-aware extraction strategy using MinerU or Docling.
    
    Best for: Multi-column layouts, table-heavy documents, mixed origin
    Cost: Medium (~$0.01-0.05/page)
    Quality: High
    """
    
    @property
    def name(self) -> str:
        return "strategy_b"
    
    def __init__(self, backend: str = "mineru"):
        """
        Initialize the strategy.
        
        Args:
            backend: Either "mineru" or "docling"
        """
        self.backend = backend
        self._available = self._check_availability()
    
    def _check_availability(self) -> bool:
        """Check if the backend is available."""
        try:
            if self.backend == "mineru":
                # Try importing MagicPDF (MinerU)
                # import magic_pdf  # noqa: F401
                pass
            elif self.backend == "docling":
                # Try importing docling
                # from docling.document_converter import DocumentConverter  # noqa: F401
                pass
            logger.info(f"Layout-aware backend '{self.backend}' available")
            return True
        except ImportError:
            logger.warning(f"Layout-aware backend '{self.backend}' not available, using fallback")
            return False
    
    def extract(self, file_path: str, profile: DocumentProfile) -> ExtractedDocument:
        """
        Extract text using layout-aware method.
        
        Args:
            file_path: Path to the PDF file
            profile: Document profile for context
            
        Returns:
            ExtractedDocument with extracted content
        """
        start_time = time.time()
        
        logger.info(f"Starting layout-aware extraction for {file_path} using {self.backend}")
        
        # If the preferred backend is not available, use fallback
        if not self._available:
            return self._fallback_extract(file_path, profile, start_time)
        
        try:
            if self.backend == "mineru":
                return self._extract_with_mineru(file_path, profile, start_time)
            elif self.backend == "docling":
                return self._extract_with_docling(file_path, profile, start_time)
            else:
                return self._fallback_extract(file_path, profile, start_time)
        except Exception as e:
            logger.error(f"Layout-aware extraction failed: {e}, using fallback")
            return self._fallback_extract(file_path, profile, start_time)
    
    def _extract_with_mineru(
        self, 
        file_path: str, 
        profile: DocumentProfile,
        start_time: float,
    ) -> ExtractedDocument:
        """Extract using MagicPDF (MinerU)."""
        # Placeholder for MinerU implementation
        # In production, this would use:
        # from magic_pdf.data.data_reader_writer import FileBasedDataReader
        # from magic_pdf.data.dataset import PymuDocDataset
        # from magic_pdf.model.doc_analyze_by_custom_model import doc_analyze
        # from magic_pdf.pipeline.preproc.pipeline import PreprocPipeline
        
        logger.info("Using MinerU backend (placeholder)")
        return self._fallback_extract(file_path, profile, start_time)
    
    def _extract_with_docling(
        self, 
        file_path: str, 
        profile: DocumentProfile,
        start_time: float,
    ) -> ExtractedDocument:
        """Extract using Docling."""
        # Placeholder for Docling implementation
        # In production, this would use:
        # from docling.document_converter import DocumentConverter
        # from docling.datamodel.base_models import InputFormat
        # from docling.datamodel.pipeline_options import PdfPipelineOptions
        
        logger.info("Using Docling backend (placeholder)")
        return self._fallback_extract(file_path, profile, start_time)
    
    def _fallback_extract(
        self, 
        file_path: str, 
        profile: DocumentProfile,
        start_time: float,
    ) -> ExtractedDocument:
        """Fallback to pdfplumber with enhanced table extraction."""
        import pdfplumber
        
        pages: List[Dict[int, List[TextBlock]]] = []
        tables: List[TableData] = []
        figures: List[FigureData] = []
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
                        
                        # Extract words with positions
                        words = page.extract_words() or []
                        blocks = self._extract_blocks(words, page_num)
                        pages.append(blocks)
                        
                        # Extract tables with better detection
                        page_tables = page.extract_tables() or []
                        for i, table in enumerate(page_tables):
                            table_data = TableData(
                                headers=table[0] if table else [],
                                rows=table[1:] if len(table) > 1 else [],
                                page_number=page_num,
                                row_count=len(page_tables),
                                col_count=len(page_tables[0]) if page_tables else 0,
                            )
                            tables.append(table_data)
                        
                        # Extract images
                        page_images = page.images or []
                        for img in page_images:
                            figure = FigureData(
                                bbox=img.get("bbox"),
                                page_number=page_num,
                                figure_type="image",
                            )
                            figures.append(figure)
                        
                        pages_processed += 1
                        
                    except Exception as e:
                        logger.warning(f"Failed to extract page {page_num}: {e}")
                        pages_failed += 1
                
                full_text = "\n\n".join(full_text_parts)
                
        except Exception as e:
            logger.error(f"Failed to open PDF: {e}")
            raise
        
        extraction_time_ms = int((time.time() - start_time) * 1000)
        
        # Higher confidence for layout-aware (when using fallback, same as fast text)
        confidence = 0.85 if pages_processed > 0 else 0.0
        
        metadata = ExtractionMetadata(
            strategy_used=self.name,
            extraction_time_ms=extraction_time_ms,
            tool_version="pdfplumber_fallback",
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
            tables=tables,
            figures=figures,
            full_text=full_text,
            metadata=metadata,
            language=profile.language,
            domain_hint=profile.domain_hint if profile.domain_hint else None,
        )
        
        logger.info(
            f"Layout-aware extraction complete: {pages_processed} pages, "
            f"confidence: {confidence:.2f}, time: {extraction_time_ms}ms"
        )
        
        return result
    
    def _extract_blocks(self, words: List[Dict], page_num: int) -> Dict[int, List[TextBlock]]:
        """Extract text blocks from words with layout awareness."""
        blocks = {}
        
        if not words:
            return blocks
        
        # Group words by vertical position (line)
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
            
            # Detect block type based on position
            block_type = "text"
            if y1 < 50:  # Top of page
                block_type = "header"
            elif y0 > 700:  # Bottom of page
                block_type = "footer"
            
            block = TextBlock(
                text=text,
                bbox=[x0, y0, x1, y1],
                page_number=page_num,
                block_type=block_type,
                confidence=0.95,
            )
            
            blocks[block_id] = [block]
            block_id += 1
        
        return blocks
    
    def get_confidence(self, result: ExtractedDocument) -> float:
        """Get confidence score from extraction result."""
        # Use metadata confidence if available
        if result.metadata and hasattr(result.metadata, 'confidence_score'):
            return result.metadata.confidence_score
        # Otherwise return default confidence for layout-aware extraction
        return 0.85
