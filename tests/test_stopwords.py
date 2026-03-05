"""Unit tests for stopwords module."""

import pytest
from src.utils.stopwords import (
    Stopwords,
    get_stopwords,
    get_stopwords_with_fallback,
    is_stopword,
    filter_stopwords
)


class TestStopwords:
    """Test cases for Stopwords class."""
    
    def test_get_english_stopwords(self):
        """Test getting English stopwords."""
        stopwords = get_stopwords("en")
        assert stopwords is not None
        assert "the" in stopwords
        assert "is" in stopwords
        assert "and" in stopwords
    
    def test_get_amharic_stopwords(self):
        """Test getting Amharic stopwords."""
        stopwords = get_stopwords("am")
        assert stopwords is not None
        assert "እንደ" in stopwords
        assert "ስለ" in stopwords
        assert "ነው" in stopwords
    
    def test_get_german_stopwords(self):
        """Test getting German stopwords."""
        stopwords = get_stopwords("de")
        assert stopwords is not None
        assert "der" in stopwords
        assert "die" in stopwords
        assert "und" in stopwords
    
    def test_locale_normalization(self):
        """Test locale code normalization."""
        # en-US should normalize to en
        stopwords = get_stopwords("en-US")
        assert stopwords is not None
        
        # en_GB should normalize to en
        stopwords = get_stopwords("en_GB")
        assert stopwords is not None
    
    def test_case_insensitive(self):
        """Test case insensitive language codes."""
        assert get_stopwords("EN") is not None
        assert get_stopwords("En") is not None
        assert get_stopwords("AM") is not None
    
    def test_fallback_language(self):
        """Test fallback to another language."""
        # Unknown language should return None
        assert get_stopwords("xyz123") is None
        
        # With fallback, should return English
        stopwords = get_stopwords_with_fallback("xyz123", "en")
        assert stopwords is not None
        assert "the" in stopwords
    
    def test_is_stopword(self):
        """Test checking if word is a stopword."""
        assert is_stopword("the", "en") is True
        assert is_stopword("hello", "en") is False
        assert is_stopword("እንደ", "am") is True
        assert is_stopword("ነገር", "am") is False
    
    def test_filter_stopwords(self):
        """Test filtering stopwords from text."""
        text = "The quick brown fox jumps over the lazy dog"
        filtered = filter_stopwords(text, "en")
        
        assert "the" not in [w.lower() for w in filtered]
        assert "quick" in filtered
        assert "brown" in filtered
    
    def test_get_available_languages(self):
        """Test getting available languages."""
        languages = Stopwords.get_available_languages()
        assert "en" in languages
        assert "am" in languages
        assert "de" in languages
        assert "fr" in languages
    
    def test_empty_language_code(self):
        """Test empty language code."""
        assert get_stopwords("") is None
    
    def test_nonexistent_language(self):
        """Test non-existent language."""
        assert get_stopwords("xyz") is None
