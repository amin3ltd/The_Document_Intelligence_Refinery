"""Keyword extraction using YAKE (Yet Another Keyword Extractor).

This module provides keyword extraction for document processing,
similar to kreuzberg's keyword module.
"""

import re
from typing import Dict, List, Set, Tuple
from collections import Counter
import math


class KeywordExtractor:
    """
    YAKE-based keyword extractor.
    
    Extracts keywords from text using a unsupervised approach
    that doesn't require training data.
    """
    
    def __init__(
        self,
        language: str = "en",
        n_grams: int = 3,
        top_k: int = 20,
        min_keyword_length: int = 3,
        window_size: int = 1
    ):
        """
        Initialize the keyword extractor.
        
        Args:
            language: Language code (en, de, fr, etc.)
            n_grams: Maximum n-gram size
            top_k: Number of top keywords to return
            min_keyword_length: Minimum keyword length
            window_size: Window size for co-occurrence
        """
        self.language = language
        self.n_grams = n_grams
        self.top_k = top_k
        self.min_keyword_length = min_keyword_length
        self.window_size = window_size
        
        # Language-specific stop words
        self._load_stop_words()
    
    def _load_stop_words(self) -> None:
        """Load language-specific stop words."""
        # Common English stop words
        self.stop_words: Set[str] = {
            "a", "an", "and", "are", "as", "at", "be", "by", "for",
            "from", "has", "he", "in", "is", "it", "its", "of", "on",
            "that", "the", "to", "was", "were", "will", "with", "this",
            "but", "they", "have", "had", "what", "when", "where", "who",
            "which", "why", "how", "all", "each", "every", "both", "few",
            "more", "most", "other", "some", "such", "no", "nor", "not",
            "only", "own", "same", "so", "than", "too", "very", "can",
            "just", "should", "now", "the", "also", "into", "our", "you",
            "your", "we", "them", "their", "these", "those", "about",
            "after", "again", "before", "being", "between", "during",
            "under", "above", "over", "through", "while", "here", "there"
        }
        
        # Add language-specific stop words if needed
        if self.language == "de":
            self.stop_words.update({"der", "die", "das", "und", "ist", "in", "zu", "den", "mit", "von"})
        elif self.language == "fr":
            self.stop_words.update({"le", "la", "les", "et", "est", "un", "une", "du", "des", "en", "que"})
    
    def extract_keywords(self, text: str) -> List[Tuple[str, float]]:
        """
        Extract keywords from text.
        
        Args:
            text: Input text
            
        Returns:
            List of (keyword, score) tuples sorted by score (lower is better)
        """
        # Preprocess text
        text_lower = text.lower()
        words = self._tokenize(text_lower)
        
        # Extract n-grams
        ngrams = self._extract_ngrams(words)
        
        # Calculate scores
        scores = self._calculate_scores(ngrams, text_lower, words)
        
        # Sort and return top k
        sorted_keywords = sorted(scores.items(), key=lambda x: x[1])
        
        return sorted_keywords[:self.top_k]
    
    def _tokenize(self, text: str) -> List[str]:
        """Tokenize text into words."""
        # Remove special characters and split
        text = re.sub(r'[^\w\s]', ' ', text)
        words = text.split()
        
        # Filter by length
        words = [w for w in words if len(w) >= self.min_keyword_length]
        
        # Remove stop words
        words = [w for w in words if w not in self.stop_words]
        
        return words
    
    def _extract_ngrams(self, words: List[str]) -> Dict[Tuple[str, ...], int]:
        """Extract n-grams from words."""
        ngrams: Dict[Tuple[str, ...], int] = Counter()
        
        for n in range(1, self.n_grams + 1):
            for i in range(len(words) - n + 1):
                ngram = tuple(words[i:i + n])
                ngrams[ngram] += 1
        
        return dict(ngrams)
    
    def _calculate_scores(
        self,
        ngrams: Dict[Tuple[str, ...], int],
        text: str,
        words: List[str]
    ) -> Dict[str, float]:
        """Calculate YAKE scores for n-grams."""
        scores: Dict[str, float] = {}
        
        word_count = len(words)
        
        for ngram, freq in ngrams.items():
            keyword = " ".join(ngram)
            
            # Skip if too short
            if len(keyword) < self.min_keyword_length:
                continue
            
            # Calculate term frequency
            tf = freq / word_count
            
            # Calculate term context score (co-occurrence)
            context_score = self._calculate_context_score(ngram, words)
            
            # Calculate position score (earlier is better)
            first_pos = text.find(keyword)
            pos_score = 1 - (first_pos / max(len(text), 1)) if first_pos >= 0 else 0
            
            # Calculate length score (shorter is better)
            length_score = 1 / math.log1p(len(keyword))
            
            # Combined score (lower is better)
            score = (tf * 0.5 + context_score * 0.3 + pos_score * 0.1 + length_score * 0.1)
            
            scores[keyword] = score
        
        return scores
    
    def _calculate_context_score(self, ngram: Tuple[str, ...], words: List[str]) -> float:
        """Calculate context score based on co-occurrence."""
        keyword_set = set(ngram)
        
        # Find neighboring words
        context_words = set()
        
        for i, word in enumerate(words):
            if word in keyword_set:
                # Get words in window
                start = max(0, i - self.window_size)
                end = min(len(words), i + self.window_size + 1)
                
                for j in range(start, end):
                    if j != i and words[j] not in keyword_set:
                        context_words.add(words[j])
        
        # Calculate score (more context words = lower score)
        if not context_words:
            return 0.5
        
        return 1.0 / math.log1p(len(context_words))
    
    def extract_keyphrases(self, text: str) -> List[str]:
        """
        Extract key phrases (multi-word keywords).
        
        Args:
            text: Input text
            
        Returns:
            List of key phrases
        """
        keywords = self.extract_keywords(text)
        
        # Filter for multi-word phrases
        keyphrases = [
            kw for kw, score in keywords
            if " " in kw
        ]
        
        return keyphrases
    
    def extract_with_weights(self, text: str) -> Dict[str, float]:
        """
        Extract keywords with normalized weights.
        
        Args:
            text: Input text
            
        Returns:
            Dictionary of keyword -> normalized weight
        """
        keywords = self.extract_keywords(text)
        
        if not keywords:
            return {}
        
        # Normalize scores (0-1 range, higher is better)
        min_score = min(score for _, score in keywords)
        max_score = max(score for _, score in keywords)
        
        if max_score == min_score:
            return {kw: 1.0 for kw, _ in keywords}
        
        weights = {}
        for kw, score in keywords:
            # Invert score (lower YAKE score = better = higher weight)
            weights[kw] = 1 - (score - min_score) / (max_score - min_score)
        
        return weights


class RakeExtractor:
    """
    RAKE (Rapid Automatic Keyword Extraction) implementation.
    
    Extracts keywords using a graph-based approach.
    """
    
    def __init__(
        self,
        min_phrase_length: int = 2,
        max_phrase_length: int = 5,
        top_k: int = 20
    ):
        """
        Initialize RAKE extractor.
        
        Args:
            min_phrase_length: Minimum phrase length
            max_phrase_length: Maximum phrase length
            top_k: Number of keywords to return
        """
        self.min_phrase_length = min_phrase_length
        self.max_phrase_length = max_phrase_length
        self.top_k = top_k
        
        # Load stop words
        self._load_stop_words()
    
    def _load_stop_words(self) -> None:
        """Load stop words for phrase detection."""
        self.stop_words: Set[str] = {
            "a", "an", "and", "are", "as", "at", "be", "by", "for",
            "from", "has", "he", "in", "is", "it", "its", "of", "on",
            "that", "the", "to", "was", "were", "will", "with",
            "this", "but", "they", "have", "had"
        }
    
    def extract_keywords(self, text: str) -> List[Tuple[str, float]]:
        """
        Extract keywords using RAKE algorithm.
        
        Args:
            text: Input text
            
        Returns:
            List of (keyword, score) tuples
        """
        # Split into sentences
        sentences = re.split(r'[.!?,\n]+', text.lower())
        
        # Extract candidate phrases
        phrases = []
        for sentence in sentences:
            if sentence.strip():
                phrases.extend(self._extract_phrases(sentence))
        
        # Calculate word scores
        word_scores = self._calculate_word_scores(phrases)
        
        # Calculate phrase scores
        phrase_scores = {}
        for phrase in phrases:
            words = phrase.split()
            if words:
                score = sum(word_scores.get(w, 0) for w in words) / len(words)
                phrase_scores[phrase] = score
        
        # Sort and return top k
        sorted_phrases = sorted(phrase_scores.items(), key=lambda x: x[1], reverse=True)
        
        return sorted_phrases[:self.top_k]
    
    def _extract_phrases(self, sentence: str) -> List[str]:
        """Extract candidate phrases from sentence."""
        # Split into words
        words = sentence.split()
        
        # Identify stop word positions
        phrase_boundaries = [0]
        for i, word in enumerate(words):
            if word in self.stop_words:
                phrase_boundaries.append(i)
        phrase_boundaries.append(len(words))
        
        # Extract phrases between stop words
        phrases = []
        for i in range(len(phrase_boundaries) - 1):
            start = phrase_boundaries[i]
            end = phrase_boundaries[i + 1]
            
            phrase_words = words[start:end]
            
            if len(phrase_words) >= self.min_phrase_length:
                phrase = " ".join(phrase_words)
                if len(phrase) >= self.min_phrase_length:
                    phrases.append(phrase)
        
        return phrases
    
    def _calculate_word_scores(self, phrases: List[str]) -> Dict[str, float]:
        """Calculate word scores based on frequency and co-occurrence."""
        word_freq: Dict[str, int] = Counter()
        word_degree: Dict[str, int] = Counter()
        
        for phrase in phrases:
            words = phrase.split()
            
            for word in words:
                word_freq[word] += 1
                word_degree[word] += len(words) - 1
        
        # Calculate scores
        scores = {}
        for word in word_freq:
            if word not in self.stop_words:
                scores[word] = word_degree[word] / word_freq[word]
        
        return scores


def extract_keywords(
    text: str,
    method: str = "yake",
    top_k: int = 20,
    language: str = "en"
) -> List[Tuple[str, float]]:
    """
    Convenience function to extract keywords.
    
    Args:
        text: Input text
        method: Extraction method ("yake" or "rake")
        top_k: Number of keywords to return
        language: Language code (for YAKE)
        
    Returns:
        List of (keyword, score) tuples
    """
    if method.lower() == "yake":
        extractor = KeywordExtractor(language=language, top_k=top_k)
    else:
        extractor = RakeExtractor(top_k=top_k)
    
    return extractor.extract_keywords(text)
