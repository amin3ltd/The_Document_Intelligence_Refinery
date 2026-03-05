"""Token reduction module for semantic text processing.

This module provides token reduction capabilities for reducing text length while
preserving semantic meaning. Useful for:
- Reducing token counts for LLM inputs
- Creating concise summaries
- CJK text processing
- Semantic deduplication
"""

import re
from dataclasses import dataclass
from typing import Dict, List, Optional, Set, Tuple


@dataclass
class ReductionResult:
    """Result of token reduction."""
    original_text: str
    reduced_text: str
    original_token_count: int
    reduced_token_count: int
    reduction_ratio: float
    method: str


class TokenReducer:
    """
    Token reducer for semantic text processing.
    
    Provides multiple reduction strategies:
    - Simple word removal
    - Stopword-based reduction
    - Semantic deduplication
    - Sentence compression
    """
    
    def __init__(self):
        """Initialize the token reducer."""
        self.default_max_tokens = 512
        self.default_ratio = 0.5
    
    def reduce(
        self,
        text: str,
        max_tokens: Optional[int] = None,
        ratio: Optional[float] = None,
        method: str = "hybrid"
    ) -> ReductionResult:
        """
        Reduce text token count.
        
        Args:
            text: Input text
            max_tokens: Maximum tokens in output (optional)
            ratio: Target reduction ratio (0.0-1.0) (optional)
            method: Reduction method ("simple", "stopwords", "semantic", "hybrid")
            
        Returns:
            ReductionResult with reduced text
        """
        max_tokens = max_tokens or self.default_max_tokens
        ratio = ratio or self.default_ratio
        
        if method == "simple":
            reduced = self._reduce_simple(text, ratio)
        elif method == "stopwords":
            reduced = self._reduce_by_stopwords(text, ratio)
        elif method == "semantic":
            reduced = self._reduce_semantic(text, ratio)
        elif method == "hybrid":
            reduced = self._reduce_hybrid(text, ratio)
        else:
            reduced = text
        
        # Estimate token counts (rough approximation: 1 token ≈ 4 chars)
        original_tokens = len(text) // 4
        reduced_tokens = len(reduced) // 4
        
        return ReductionResult(
            original_text=text,
            reduced_text=reduced,
            original_token_count=original_tokens,
            reduced_token_count=reduced_tokens,
            reduction_ratio=1.0 - (reduced_tokens / max(1, original_tokens)),
            method=method
        )
    
    def _reduce_simple(self, text: str, ratio: float) -> str:
        """Simple reduction by removing every nth word."""
        words = text.split()
        if len(words) <= 10:
            return text
        
        # Keep every nth word based on ratio
        keep_interval = int(1 / ratio) if ratio > 0 else 1
        reduced_words = [w for i, w in enumerate(words) if i % keep_interval == 0]
        
        return " ".join(reduced_words)
    
    def _reduce_by_stopwords(self, text: str, ratio: float) -> str:
        """Reduce by removing stopwords."""
        from src.utils.stopwords import Stopwords
        
        words = text.split()
        if len(words) <= 10:
            return text
        
        # Try to detect language or use English
        lang = "en"
        
        # Remove stopwords
        stopwords = Stopwords.get_stopwords(lang)
        if stopwords:
            reduced_words = [w for w in words if w.lower() not in stopwords]
        else:
            reduced_words = words
        
        # If still too long, apply simple reduction
        if len(reduced_words) > len(words) * ratio:
            return self._reduce_simple(" ".join(reduced_words), ratio)
        
        return " ".join(reduced_words)
    
    def _reduce_semantic(self, text: str, ratio: float) -> str:
        """Semantic reduction by removing near-duplicate sentences."""
        sentences = self._split_sentences(text)
        
        if len(sentences) <= 2:
            return text
        
        # Remove similar sentences (simple similarity based on word overlap)
        unique_sentences = []
        for sent in sentences:
            is_duplicate = False
            for unique in unique_sentences:
                if self._sentence_similarity(sent, unique) > 0.5:
                    is_duplicate = True
                    break
            if not is_duplicate:
                unique_sentences.append(sent)
        
        reduced = " ".join(unique_sentences)
        
        # If still too long, use simple reduction
        if len(reduced) > len(text) * ratio:
            return self._reduce_simple(text, ratio)
        
        return reduced
    
    def _reduce_hybrid(self, text: str, ratio: float) -> str:
        """Hybrid approach combining all methods."""
        # First, remove stopwords
        text = self._reduce_by_stopwords(text, 0.3)
        
        # Then remove duplicate sentences
        text = self._reduce_semantic(text, ratio)
        
        # Finally, if still too long, use simple reduction
        if len(text.split()) > self.default_max_tokens:
            text = self._reduce_simple(text, ratio)
        
        return text
    
    def _split_sentences(self, text: str) -> List[str]:
        """Split text into sentences."""
        # Simple sentence splitting
        sentences = re.split(r"[.!?]\s+", text)
        return [s.strip() for s in sentences if s.strip()]
    
    def _sentence_similarity(self, sent1: str, sent2: str) -> float:
        """Calculate simple word overlap similarity between sentences."""
        words1 = set(sent1.lower().split())
        words2 = set(sent2.lower().split())
        
        if not words1 or not words2:
            return 0.0
        
        intersection = words1 & words2
        union = words1 | words2
        
        return len(intersection) / len(union)


class CJKTokenizer:
    """
    Tokenizer for CJK (Chinese, Japanese, Korean) text.
    
    Handles character-level and word-level tokenization for CJK languages.
    """
    
    def __init__(self):
        """Initialize CJK tokenizer."""
        # Common CJK Unicode ranges
        self.cjk_ranges = [
            (0x4E00, 0x9FFF),   # CJK Unified Ideographs
            (0x3400, 0x4DBF),   # CJK Unified Ideographs Extension A
            (0x20000, 0x2A6DF), # CJK Unified Ideographs Extension B
            (0x2A700, 0x2B73F), # CJK Unified Ideographs Extension C
            (0x2B740, 0x2B81F), # CJK Unified Ideographs Extension D
            (0x3040, 0x309F),   # Hiragana
            (0x30A0, 0x30FF),   # Katakana
            (0xAC00, 0xD7AF),   # Hangul Syllables
        ]
    
    def is_cjk_char(self, char: str) -> bool:
        """Check if character is CJK."""
        code = ord(char)
        return any(start <= code <= end for start, end in self.cjk_ranges)
    
    def tokenize(self, text: str) -> List[str]:
        """
        Tokenize CJK text.
        
        Args:
            text: Input text
            
        Returns:
            List of tokens
        """
        tokens = []
        current_token = ""
        
        for char in text:
            if self.is_cjk_char(char):
                # CJK character - handle as individual or as part of bigram
                if current_token:
                    tokens.append(current_token)
                    current_token = ""
                
                # Add character
                tokens.append(char)
                
                # Could also add bigram here for better coverage
            else:
                # Non-CJK - accumulate
                current_token += char
                
                # Add token when hitting whitespace or punctuation
                if char.isspace() or char in ".,;:!?()[]{}":
                    if current_token.strip():
                        tokens.append(current_token.strip())
                    current_token = ""
        
        # Add remaining token
        if current_token.strip():
            tokens.append(current_token.strip())
        
        return tokens
    
    def extract_keywords(self, text: str, top_n: int = 10) -> List[Tuple[str, int]]:
        """
        Extract keywords from CJK text using character frequency.
        
        Args:
            text: Input text
            top_n: Number of top keywords to return
            
        Returns:
            List of (keyword, frequency) tuples
        """
        tokens = self.tokenize(text)
        
        # Filter to CJK characters only
        cjk_chars = [t for t in tokens if t and self.is_cjk_char(t)]
        
        # Count frequencies
        freq: Dict[str, int] = {}
        for char in cjk_chars:
            freq[char] = freq.get(char, 0) + 1
        
        # Sort by frequency
        sorted_chars = sorted(freq.items(), key=lambda x: x[1], reverse=True)
        
        return sorted_chars[:top_n]


class SemanticDeduplicator:
    """
    Semantic deduplicator for removing near-duplicate content.
    """
    
    def __init__(self, similarity_threshold: float = 0.8):
        """
        Initialize deduplicator.
        
        Args:
            similarity_threshold: Threshold for considering content duplicate
        """
        self.similarity_threshold = similarity_threshold
    
    def deduplicate(self, texts: List[str]) -> List[str]:
        """
        Remove duplicate or near-duplicate texts.
        
        Args:
            texts: List of text strings
            
        Returns:
            Deduplicated list
        """
        unique_texts = []
        
        for text in texts:
            is_duplicate = False
            
            for unique in unique_texts:
                if self._calculate_similarity(text, unique) >= self.similarity_threshold:
                    is_duplicate = True
                    break
            
            if not is_duplicate:
                unique_texts.append(text)
        
        return unique_texts
    
    def deduplicate_sentences(self, text: str) -> str:
        """
        Remove duplicate sentences from text.
        
        Args:
            text: Input text
            
        Returns:
            Text with duplicate sentences removed
        """
        # Split into sentences
        sentences = re.split(r"(?<=[.!?])\s+", text)
        
        # Deduplicate
        unique_sentences = self.deduplicate(sentences)
        
        return " ".join(unique_sentences)
    
    def _calculate_similarity(self, text1: str, text2: str) -> float:
        """Calculate similarity between two texts."""
        # Simple Jaccard similarity on words
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())
        
        if not words1 or not words2:
            return 0.0
        
        intersection = words1 & words2
        union = words1 | words2
        
        return len(intersection) / len(union)


# Convenience functions
def reduce_tokens(
    text: str,
    max_tokens: Optional[int] = None,
    ratio: Optional[float] = None,
    method: str = "hybrid"
) -> ReductionResult:
    """Reduce text token count."""
    reducer = TokenReducer()
    return reducer.reduce(text, max_tokens, ratio, method)


def extract_cjk_keywords(text: str, top_n: int = 10) -> List[Tuple[str, int]]:
    """Extract keywords from CJK text."""
    tokenizer = CJKTokenizer()
    return tokenizer.extract_keywords(text, top_n)


def deduplicate_texts(texts: List[str], threshold: float = 0.8) -> List[str]:
    """Remove duplicate texts."""
    dedup = SemanticDeduplicator(similarity_threshold=threshold)
    return dedup.deduplicate(texts)


def deduplicate_sentences(text: str) -> str:
    """Remove duplicate sentences from text."""
    dedup = SemanticDeduplicator()
    return dedup.deduplicate_sentences(text)
