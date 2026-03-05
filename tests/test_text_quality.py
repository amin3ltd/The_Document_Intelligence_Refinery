"""Unit tests for text quality processing module."""

import pytest
from src.utils.text_quality import (
    TextQualityProcessor,
    TextCleaner,
    calculate_quality_score,
    clean_text,
    get_quality_report,
    QualityScore
)


class TestTextQualityProcessor:
    """Test cases for TextQualityProcessor class."""
    
    def test_calculate_quality_score_good_text(self):
        """Test quality score for good text."""
        processor = TextQualityProcessor()
        text = "This is a sample text with proper sentence structure. It contains multiple sentences with good punctuation. The text is well-formed."
        
        score = processor.calculate_quality_score(text)
        
        assert isinstance(score, QualityScore)
        assert score.overall >= 0.0
        assert score.overall <= 1.0
    
    def test_calculate_quality_score_short_text(self):
        """Test quality score for short text."""
        processor = TextQualityProcessor()
        text = "Short"
        
        score = processor.calculate_quality_score(text)
        
        assert score.overall == 0.0
        assert "Text too short" in score.issues[0]
    
    def test_ocr_artifact_detection(self):
        """Test OCR artifact detection."""
        processor = TextQualityProcessor()
        text = "This is a test... with extra   whitespace and t3st w0rds"
        
        score = processor.calculate_quality_score(text)
        
        # Should detect OCR artifacts
        assert any("OCR" in issue for issue in score.issues)
    
    def test_clean_text(self):
        """Test text cleaning."""
        processor = TextQualityProcessor()
        text = "Text with    multiple   spaces  and\n\n\nextra newlines"
        
        cleaned = processor.clean_text(text)
        
        assert "  " not in cleaned
        assert "\n\n\n" not in cleaned
    
    def test_extract_quality_report(self):
        """Test quality report extraction."""
        processor = TextQualityProcessor()
        text = "This is a sample text for testing quality."
        
        report = processor.get_quality_report(text)
        
        assert "score" in report
        assert "artifacts" in report
        assert "statistics" in report
        assert "cleaned_text" in report


class TestTextCleaner:
    """Test cases for TextCleaner class."""
    
    def test_normalize_whitespace(self):
        """Test whitespace normalization."""
        text = "Multiple    spaces   here"
        cleaned = TextCleaner.normalize_whitespace(text)
        
        assert "    " not in cleaned
        assert cleaned == "Multiple spaces here"
    
    def test_remove_extra_newlines(self):
        """Test extra newline removal."""
        text = "Line1\n\n\n\nLine2"
        cleaned = TextCleaner.remove_extra_newlines(text)
        
        assert "\n\n\n" not in cleaned
    
    def test_remove_control_chars(self):
        """Test control character removal."""
        text = "Text\x00with\x07control\x1fchars"
        cleaned = TextCleaner.remove_control_chars(text)
        
        assert "\x00" not in cleaned
        assert "\x07" not in cleaned
    
    def test_fix_unicode_issues(self):
        """Test Unicode fix."""
        text = "Test\u2019s text with\u2018quotes\u201d"
        cleaned = TextCleaner.fix_unicode_issues(text)
        
        assert "\u2019" not in cleaned
        assert "'" in cleaned
    
    def test_clean(self):
        """Test full cleaning."""
        text = "Text\x00 with  multiple   spaces\n\n\nand\u00a0unicode"
        cleaned = TextCleaner.clean(text)
        
        assert isinstance(cleaned, str)
        assert len(cleaned) > 0


class TestConvenienceFunctions:
    """Test convenience functions."""
    
    def test_calculate_quality_score_function(self):
        """Test calculate_quality_score convenience function."""
        text = "This is a sample text for quality assessment."
        
        score = calculate_quality_score(text)
        
        assert isinstance(score, QualityScore)
    
    def test_clean_text_function(self):
        """Test clean_text convenience function."""
        text = "Text with    extra   spaces"
        
        cleaned = clean_text(text)
        
        assert "  " not in cleaned
    
    def test_get_quality_report_function(self):
        """Test get_quality_report convenience function."""
        text = "Sample text for quality report"
        
        report = get_quality_report(text)
        
        assert "score" in report
        assert "artifacts" in report
