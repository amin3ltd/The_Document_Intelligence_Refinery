"""Unit tests for language detection module."""

import pytest
from src.utils.language_detection import (
    LanguageDetector,
    MultiLanguageDetector,
    detect_language,
    detect_document_languages
)


class TestLanguageDetector:
    """Test cases for LanguageDetector class."""
    
    def test_detect_english(self):
        """Test detecting English text."""
        detector = LanguageDetector()
        text = "This is a sample English text for testing purposes."
        lang, confidence = detector.detect(text)
        
        assert lang == "en"
        assert confidence > 0.0
    
    def test_detect_german(self):
        """Test detecting German text."""
        detector = LanguageDetector()
        text = "Dies ist ein deutscher Text zum Testen"
        lang, confidence = detector.detect(text)
        
        assert lang == "de"
        assert confidence > 0.0
    
    def test_detect_short_text(self):
        """Test that short text returns None."""
        detector = LanguageDetector(min_text_length=20)
        text = "Short"
        lang, confidence = detector.detect(text)
        
        assert lang is None
        assert confidence == 0.0
    
    def test_get_language_name(self):
        """Test getting full language name."""
        detector = LanguageDetector()
        
        assert detector.get_language_name("en") == "English"
        assert detector.get_language_name("de") == "German"
        assert detector.get_language_name("am") == "Amharic"
    
    def test_detect_batch(self):
        """Test batch detection."""
        detector = LanguageDetector()
        texts = [
            "This is English",
            "Dies ist Deutsch",
            "Ceci est français"
        ]
        
        results = detector.detect_batch(texts)
        
        assert len(results) == 3
        assert results[0][0] == "en"
        assert results[1][0] == "de"
        assert results[2][0] == "fr"


class TestMultiLanguageDetector:
    """Test cases for MultiLanguageDetector class."""
    
    def test_detect_page_languages(self):
        """Test detecting languages for multiple pages."""
        detector = MultiLanguageDetector()
        pages = [
            "This is English text on page one",
            "This is still English on page two",
            "Deutsch text auf Seite drei"
        ]
        
        results = detector.detect_page_languages(pages)
        
        assert len(results) == 3
        assert results[0]["page_number"] == 1
        assert results[0]["language"] == "en"
        assert results[2]["language"] == "de"
    
    def test_detect_document_language_first(self):
        """Test document language detection using first page."""
        detector = MultiLanguageDetector()
        pages = [
            "This is English text",
            "More English text",
            "Even more English"
        ]
        
        result = detector.detect_document_language(pages, method="first")
        
        assert result["language"] == "en"
        assert result["method"] == "first_page"
    
    def test_detect_document_language_majority(self):
        """Test document language detection using majority voting."""
        detector = MultiLanguageDetector()
        pages = [
            "This is English text",
            "More English text",
            "Deutsch Text",  # German
            "Noch mehr Englisch"  # German
        ]
        
        result = detector.detect_document_language(pages, method="majority")
        
        # English appears 2 times, German 2 times - depends on confidence
        assert result["method"] == "majority_vote"
    
    def test_empty_pages(self):
        """Test with empty pages list."""
        detector = MultiLanguageDetector()
        
        result = detector.detect_document_language([])
        
        assert result["language"] is None


class TestConvenienceFunctions:
    """Test convenience functions."""
    
    def test_detect_language_function(self):
        """Test detect_language convenience function."""
        lang, confidence = detect_language("This is English")
        
        assert lang == "en"
        assert confidence > 0.0
    
    def test_detect_document_languages_function(self):
        """Test detect_document_languages convenience function."""
        pages = ["English text", "More English"]
        
        result = detect_document_languages(pages)
        
        assert "language" in result
        assert "confidence" in result
