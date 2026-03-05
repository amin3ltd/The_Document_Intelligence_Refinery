"""Unit tests for keyword extraction module."""

import pytest
from src.utils.keyword_extraction import (
    YAKEKeywordExtractor,
    RAKEKeywordExtractor,
    extract_keywords_yake,
    extract_keywords_rake
)


class TestYAKEKeywordExtractor:
    """Test cases for YAKE keyword extractor."""
    
    def test_yake_extraction(self):
        """Test YAKE keyword extraction."""
        extractor = YAKEKeywordExtractor()
        text = "Natural language processing is a subfield of linguistics, computer science, and artificial intelligence concerned with the understanding of human language."
        
        keywords = extractor.extract(text, top_n=5)
        
        assert len(keywords) <= 5
        assert isinstance(keywords, list)
    
    def test_yake_with_custom_parameters(self):
        """Test YAKE with custom parameters."""
        extractor = YAKEKeywordExtractor(
            n=2,  # bigrams
            top=10
        )
        text = "Machine learning and deep learning are related fields"
        
        keywords = extractor.extract(text, top_n=5)
        
        assert isinstance(keywords, list)
    
    def test_yake_empty_text(self):
        """Test YAKE with empty text."""
        extractor = YAKEKeywordExtractor()
        
        keywords = extractor.extract("", top_n=5)
        
        assert keywords == []


class TestRAKEKeywordExtractor:
    """Test cases for RAKE keyword extractor."""
    
    def test_rake_extraction(self):
        """Test RAKE keyword extraction."""
        extractor = RAKEKeywordExtractor()
        text = "Natural language processing is a subfield of linguistics, computer science, and artificial intelligence concerned with the understanding of human language."
        
        keywords = extractor.extract(text, top_n=5)
        
        assert isinstance(keywords, list)
    
    def test_rake_with_stopwords(self):
        """Test RAKE with custom stopwords."""
        from src.utils.stopwords import get_stopwords
        
        stopwords = get_stopwords("en") or set()
        extractor = RAKEKeywordExtractor(stopwords=stopwords)
        text = "The quick brown fox jumps over the lazy dog"
        
        keywords = extractor.extract(text, top_n=3)
        
        assert isinstance(keywords, list)
    
    def test_rake_empty_text(self):
        """Test RAKE with empty text."""
        extractor = RAKEKeywordExtractor()
        
        keywords = extractor.extract("", top_n=5)
        
        assert keywords == []


class TestConvenienceFunctions:
    """Test convenience functions."""
    
    def test_extract_keywords_yake(self):
        """Test YAKE convenience function."""
        keywords = extract_keywords_yake("Sample text for keyword extraction", top_n=5)
        
        assert isinstance(keywords, list)
    
    def test_extract_keywords_rake(self):
        """Test RAKE convenience function."""
        keywords = extract_keywords_rake("Sample text for keyword extraction", top_n=5)
        
        assert isinstance(keywords, list)
    
    def test_top_n_parameter(self):
        """Test top_n parameter."""
        text = "This is a test text with multiple keywords for testing purposes"
        
        keywords_yake = extract_keywords_yake(text, top_n=3)
        keywords_rake = extract_keywords_rake(text, top_n=3)
        
        assert len(keywords_yake) <= 3
        assert len(keywords_rake) <= 3
