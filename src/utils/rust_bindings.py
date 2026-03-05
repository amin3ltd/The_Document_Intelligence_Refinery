"""Python bindings for high-performance Rust text processing.

This module provides Python wrappers around the Rust extensions
for performance-critical operations.
"""

from typing import List, Tuple, Optional
import logging

logger = logging.getLogger(__name__)

# Try to import from Rust extension, fall back to pure Python
RUST_AVAILABLE = False

try:
    from rust_ext import document_intelligence_refinery as rust_lib
    RUST_AVAILABLE = True
    logger.info("Rust extensions loaded successfully")
except ImportError:
    logger.warning("Rust extensions not available, using pure Python fallback")
    rust_lib = None


class FastTextProcessor:
    """
    High-performance text processor using Rust for parallel processing.
    
    Falls back to pure Python if Rust extension is not available.
    """
    
    def __init__(self, max_chunk_size: int = 1000, min_chunk_size: int = 50):
        """
        Initialize the text processor.
        
        Args:
            max_chunk_size: Maximum chunk size in characters
            min_chunk_size: Minimum chunk size in characters
        """
        self.max_chunk_size = max_chunk_size
        self.min_chunk_size = min_chunk_size
        
        if RUST_AVAILABLE:
            self._processor = rust_lib.TextProcessor(max_chunk_size, min_chunk_size)
        else:
            self._processor = None
    
    def split_into_chunks(self, text: str) -> List[dict]:
        """
        Split text into chunks using parallel processing.
        
        Args:
            text: Input text to split
            
        Returns:
            List of chunks with metadata
        """
        if RUST_AVAILABLE and self._processor:
            chunks = self._processor.split_into_chunks(text)
            return [
                {
                    "text": c.text,
                    "start_idx": c.start_idx,
                    "end_idx": c.end_idx,
                    "chunk_type": c.chunk_type,
                    "word_count": c.word_count,
                }
                for c in chunks
            ]
        
        # Fallback to pure Python
        return self._python_split_chunks(text)
    
    def _python_split_chunks(self, text: str) -> List[dict]:
        """Pure Python fallback for chunk splitting."""
        paragraphs = text.split("\n\n")
        chunks = []
        
        for para in paragraphs:
            para = para.strip()
            if not para:
                continue
            
            words = para.split()
            word_count = len(words)
            
            if word_count * 5 <= self.max_chunk_size:
                chunks.append({
                    "text": para,
                    "start_idx": 0,
                    "end_idx": len(para),
                    "chunk_type": "paragraph",
                    "word_count": word_count,
                })
            else:
                # Split into smaller chunks
                current = []
                current_words = 0
                for word in words:
                    if current_words > 0 and current_words * 5 >= self.max_chunk_size:
                        chunks.append({
                            "text": " ".join(current),
                            "start_idx": 0,
                            "end_idx": len(" ".join(current)),
                            "chunk_type": "paragraph",
                            "word_count": current_words,
                        })
                        current = []
                        current_words = 0
                    current.append(word)
                    current_words += 1
                
                if current:
                    chunks.append({
                        "text": " ".join(current),
                        "start_idx": 0,
                        "end_idx": len(" ".join(current)),
                        "chunk_type": "paragraph",
                        "word_count": current_words,
                    })
        
        return chunks
    
    def extract_keywords(self, texts: List[str], top_k: int = 20) -> List[Tuple[str, int]]:
        """
        Extract keywords using parallel processing.
        
        Args:
            texts: List of texts to analyze
            top_k: Number of top keywords to return
            
        Returns:
            List of (keyword, count) tuples
        """
        if RUST_AVAILABLE and self._processor:
            keywords = self._processor.extract_keywords(texts, top_k)
            return [(k, c) for k, c in keywords]
        
        # Fallback to pure Python
        from collections import Counter
        import re
        
        all_words = []
        for text in texts:
            words = re.findall(r'\b\w+\b', text.lower())
            all_words.extend([w for w in words if len(w) > 3])
        
        counter = Counter(all_words)
        return counter.most_common(top_k)
    
    @staticmethod
    def count_words(text: str) -> int:
        """Count words in text."""
        if RUST_AVAILABLE and rust_lib:
            return rust_lib.TextProcessor.count_words_static(text)
        return len(text.split())
    
    @staticmethod
    def jaccard_similarity(text1: str, text2: str) -> float:
        """Calculate Jaccard similarity between two texts."""
        if RUST_AVAILABLE and rust_lib:
            return rust_lib.TextProcessor.jaccard_similarity_static(text1, text2)
        
        # Pure Python fallback
        set1 = set(text1.lower().split())
        set2 = set(text2.lower().split())
        intersection = len(set1 & set2)
        union = len(set1 | set2)
        return intersection / union if union > 0 else 0.0


class FastBoundingBox:
    """
    High-performance bounding box operations using Rust.
    """
    
    def __init__(self, x0: float, y0: float, x1: float, y1: float):
        """
        Initialize bounding box.
        
        Args:
            x0: Left coordinate
            y0: Top coordinate  
            x1: Right coordinate
            y1: Bottom coordinate
        """
        self.x0 = x0
        self.y0 = y0
        self.x1 = x1
        self.y1 = y1
        
        if RUST_AVAILABLE:
            self._bbox = rust_lib.BoundingBox(x0, y0, x1, y1)
        else:
            self._bbox = None
    
    def iou(self, other: "FastBoundingBox") -> float:
        """
        Calculate Intersection over Union with another bounding box.
        
        Args:
            other: Another FastBoundingBox
            
        Returns:
            IOU value between 0 and 1
        """
        if RUST_AVAILABLE and self._bbox:
            return self._bbox.iou(other._bbox)
        
        # Pure Python fallback
        left = max(self.x0, other.x0)
        top = max(self.y0, other.y0)
        right = min(self.x1, other.x1)
        bottom = min(self.y1, other.y1)
        
        if left >= right or top >= bottom:
            return 0.0
        
        intersection = (right - left) * (bottom - top)
        union = self.area() + other.area() - intersection
        
        return intersection / union if union > 0 else 0.0
    
    def area(self) -> float:
        """Calculate area of bounding box."""
        return (self.x1 - self.x0) * (self.y1 - self.y0)
    
    def overlaps(self, other: "FastBoundingBox") -> bool:
        """Check if this box overlaps with another."""
        return (self.x0 < other.x1 and other.x0 < self.x1 and
                self.y0 < other.y1 and other.y0 < self.y1)


# Convenience functions
def create_processor(
    max_chunk_size: int = 1000,
    min_chunk_size: int = 50
) -> FastTextProcessor:
    """
    Create a FastTextProcessor instance.
    
    Args:
        max_chunk_size: Maximum chunk size
        min_chunk_size: Minimum chunk size
        
    Returns:
        FastTextProcessor instance
    """
    return FastTextProcessor(max_chunk_size, min_chunk_size)


def create_bounding_box(
    x0: float,
    y0: float,
    x1: float,
    y1: float
) -> FastBoundingBox:
    """
    Create a FastBoundingBox instance.
    
    Args:
        x0: Left coordinate
        y0: Top coordinate
        x1: Right coordinate
        y1: Bottom coordinate
        
    Returns:
        FastBoundingBox instance
    """
    return FastBoundingBox(x0, y0, x1, y1)
