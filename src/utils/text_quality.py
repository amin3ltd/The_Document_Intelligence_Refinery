"""Text quality processing module for document extraction.

This module provides text quality assessment and cleaning capabilities including:
- OCR artifact detection (scattered characters, repeated punctuation, malformed words)
- Quality scoring with weights for OCR, navigation content, structure
- Pattern-based cleanup (whitespace, newlines, UTF-8 validation)
"""

import re
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple


@dataclass
class QualityScore:
    """Quality score result."""
    overall: float
    ocr_penalty: float
    script_penalty: float
    nav_penalty: float
    structure_bonus: float
    metadata_bonus: float
    issues: List[str]


class TextQualityProcessor:
    """
    Text quality processor for detecting and cleaning OCR artifacts.
    
    Provides comprehensive quality assessment and cleanup based on patterns
    commonly found in OCR output.
    """
    
    # Weight constants
    OCR_PENALTY_WEIGHT = 0.3
    SCRIPT_PENALTY_WEIGHT = 0.2
    NAV_PENALTY_WEIGHT = 0.1
    STRUCTURE_BONUS_WEIGHT = 0.2
    METADATA_BONUS_WEIGHT = 0.1
    
    # Thresholds
    MIN_TEXT_LENGTH = 10
    LARGE_TEXT_LENGTH = 1000
    MIN_SENTENCE_WORDS = 10.0
    MAX_SENTENCE_WORDS = 30.0
    MIN_PARAGRAPH_WORDS = 50.0
    MAX_PARAGRAPH_WORDS = 300.0
    
    def __init__(self):
        """Initialize the text quality processor."""
        # OCR artifact patterns
        self.scattered_chars_pattern = re.compile(
            r"\b[a-zA-Z]\s{2,}[a-zA-Z]\s{2,}[a-zA-Z]\b"
        )
        self.repeated_punct_pattern = re.compile(r"[.]{3,}|[_]{3,}")
        self.dash_pattern = re.compile(r"[-]{3,}")
        self.isolated_punct_pattern = re.compile(r"\s[.,;:!?]\s")
        self.malformed_words_pattern = re.compile(
            r"\b[a-zA-Z]+[0-9]+[a-zA-Z]+[a-zA-Z0-9]*\b"
        )
        self.excessive_whitespace_pattern = re.compile(r"\s{3,}")
        
        # Script patterns
        self.js_function_pattern = re.compile(
            r"(?i)function\s+\w+\s*\([^)]*\)\s*\{[^}]*\}"
        )
        self.css_rules_pattern = re.compile(
            r"(?i)\.[a-zA-Z][\w-]*\s*\{[^}]*\}"
        )
        self.script_tag_pattern = re.compile(r"(?is)<script[^>]*>.*?</script>")
        self.style_tag_pattern = re.compile(r"(?is)<style[^>]*>.*?</style>")
        
        # Navigation patterns
        self.nav_words_pattern = re.compile(
            r"(?i)\b(?:Skip to main content|Back to top|Main navigation|Site navigation)\b"
        )
        self.breadcrumb_pattern = re.compile(r"Home\s*[>»]\s*|[>»]\s*")
        self.pagination_pattern = re.compile(
            r"(?i)\b(?:Page \d+ of \d+|First page|Last page|Previous page|Next page|^\d+ of \d+$)\b"
        )
        
        # Text structure patterns
        self.sentence_detect = re.compile(r"[.!?]\s+[A-Z]")
        self.punctuation_detect = re.compile(r"[.!?]")
        
        # Whitespace normalization
        self.whitespace_normalize = re.compile(
            r"[ \t\f\v\r\xa0\u2000-\u200b\u2028\u2029\u3000]+"
        )
        self.newline_normalize = re.compile(r"\n\s*\n\s*\n+")
        self.newline_cleanup = re.compile(r"\n+")
    
    def calculate_quality_score(self, text: str) -> QualityScore:
        """
        Calculate quality score for text.
        
        Args:
            text: Input text
            
        Returns:
            QualityScore with detailed breakdown
        """
        if len(text) < self.MIN_TEXT_LENGTH:
            return QualityScore(
                overall=0.0,
                ocr_penalty=0.0,
                script_penalty=0.0,
                nav_penalty=0.0,
                structure_bonus=0.0,
                metadata_bonus=0.0,
                issues=["Text too short to assess"]
            )
        
        issues = []
        
        # Calculate OCR penalty
        ocr_penalty = self._calculate_ocr_penalty(text)
        
        # Calculate script penalty
        script_penalty = self._calculate_script_penalty(text)
        
        # Calculate navigation penalty
        nav_penalty = self._calculate_nav_penalty(text)
        
        # Calculate structure bonus
        structure_bonus = self._calculate_structure_bonus(text)
        
        # Calculate metadata bonus
        metadata_bonus = self._calculate_metadata_bonus(text)
        
        # Calculate overall score
        overall = 1.0 - (
            ocr_penalty * self.OCR_PENALTY_WEIGHT +
            script_penalty * self.SCRIPT_PENALTY_WEIGHT +
            nav_penalty * self.NAV_PENALTY_WEIGHT
        ) + (
            structure_bonus * self.STRUCTURE_BONUS_WEIGHT +
            metadata_bonus * self.METADATA_BONUS_WEIGHT
        )
        
        # Clamp overall to [0, 1]
        overall = max(0.0, min(1.0, overall))
        
        # Add issue descriptions
        if ocr_penalty > 0:
            issues.append(f"OCR artifacts detected (penalty: {ocr_penalty:.2f})")
        if script_penalty > 0:
            issues.append(f"Script/CSS content detected (penalty: {script_penalty:.2f})")
        if nav_penalty > 0:
            issues.append(f"Navigation content detected (penalty: {nav_penalty:.2f})")
        if structure_bonus == 0:
            issues.append("Poor text structure")
        if metadata_bonus == 0:
            issues.append("No metadata indicators")
        
        return QualityScore(
            overall=overall,
            ocr_penalty=ocr_penalty,
            script_penalty=script_penalty,
            nav_penalty=nav_penalty,
            structure_bonus=structure_bonus,
            metadata_bonus=metadata_bonus,
            issues=issues
        )
    
    def _calculate_ocr_penalty(self, text: str) -> float:
        """Calculate OCR artifact penalty."""
        penalty = 0.0
        length = len(text)
        
        # Check scattered characters
        scattered_count = len(self.scattered_chars_pattern.findall(text))
        if scattered_count > 0:
            penalty += scattered_count / max(1, length / 100)
        
        # Check repeated punctuation
        repeated_count = len(self.repeated_punct_pattern.findall(text))
        if repeated_count > 0:
            penalty += repeated_count / max(1, length / 100)
        
        # Check malformed words
        malformed_count = len(self.malformed_words_pattern.findall(text))
        if malformed_count > 0:
            penalty += malformed_count / max(1, length / 100)
        
        # Check excessive whitespace
        excessive_count = len(self.excessive_whitespace_pattern.findall(text))
        if excessive_count > 0:
            penalty += excessive_count / max(1, length / 100)
        
        # Check isolated punctuation
        isolated_count = len(self.isolated_punct_pattern.findall(text))
        if isolated_count > 0:
            penalty += isolated_count / max(1, length / 100)
        
        return min(1.0, penalty)
    
    def _calculate_script_penalty(self, text: str) -> float:
        """Calculate script/CSS content penalty."""
        penalty = 0.0
        
        # Check JavaScript
        if self.js_function_pattern.search(text):
            penalty += 0.3
        
        # Check CSS
        if self.css_rules_pattern.search(text):
            penalty += 0.2
        
        # Check script tags
        if self.script_tag_pattern.search(text):
            penalty += 0.3
        
        # Check style tags
        if self.style_tag_pattern.search(text):
            penalty += 0.2
        
        return min(1.0, penalty)
    
    def _calculate_nav_penalty(self, text: str) -> float:
        """Calculate navigation content penalty."""
        penalty = 0.0
        
        # Check navigation words
        if self.nav_words_pattern.search(text):
            penalty += 0.3
        
        # Check breadcrumbs
        if self.breadcrumb_pattern.search(text):
            penalty += 0.3
        
        # Check pagination
        if self.pagination_pattern.search(text):
            penalty += 0.4
        
        return min(1.0, penalty)
    
    def _calculate_structure_bonus(self, text: str) -> float:
        """Calculate text structure bonus."""
        bonus = 0.0
        
        # Check sentence structure
        sentences = self.sentence_detect.findall(text)
        if sentences:
            # Good sentence count
            bonus += 0.3
        
        # Check paragraph structure (double newlines)
        paragraphs = self.newline_normalize.split(text)
        if len(paragraphs) > 1:
            bonus += 0.3
        
        # Check punctuation variety
        punct_count = len(self.punctuation_detect.findall(text))
        if punct_count > 10:
            bonus += 0.2
        
        # Check reasonable word counts per sentence
        words = text.split()
        if sentences:
            avg_words_per_sent = len(words) / len(sentences)
            if self.MIN_SENTENCE_WORDS <= avg_words_per_sent <= self.MAX_SENTENCE_WORDS:
                bonus += 0.2
        
        return min(1.0, bonus)
    
    def _calculate_metadata_bonus(self, text: str) -> float:
        """Calculate metadata indicator bonus."""
        bonus = 0.0
        
        # Check for title-like content (short line at start)
        lines = text.split('\n')
        if lines and len(lines[0].strip()) < 50:
            bonus += 0.3
        
        # Check for date patterns
        date_pattern = re.compile(r"\d{4}[-/]\d{2}[-/]\d{2}")
        if date_pattern.search(text):
            bonus += 0.2
        
        # Check for email patterns
        email_pattern = re.compile(r"[\w.-]+@[\w.-]+\.\w+")
        if email_pattern.search(text):
            bonus += 0.2
        
        # Check for URL patterns
        url_pattern = re.compile(r"https?://[\w./-]+")
        if url_pattern.search(text):
            bonus += 0.3
        
        return min(1.0, bonus)
    
    def clean_text(self, text: str) -> str:
        """
        Clean text by removing common OCR artifacts.
        
        Args:
            text: Input text
            
        Returns:
            Cleaned text
        """
        cleaned = text
        
        # Remove excessive whitespace
        cleaned = self.whitespace_normalize.sub(" ", cleaned)
        
        # Normalize newlines
        cleaned = self.newline_normalize.sub("\n\n", cleaned)
        cleaned = self.newline_cleanup.sub(" ", cleaned)
        
        # Remove repeated punctuation (more than 2)
        cleaned = re.sub(r"[.]{3,}", "...", cleaned)
        cleaned = re.sub(r"[-]{3,}", "---", cleaned)
        cleaned = re.sub(r"[_]{3,}", "___", cleaned)
        
        # Remove script and style content
        cleaned = self.script_tag_pattern.sub("", cleaned)
        cleaned = self.style_tag_pattern.sub("", cleaned)
        
        # Remove navigation content
        cleaned = self.nav_words_pattern.sub("", cleaned)
        cleaned = self.breadcrumb_pattern.sub("", cleaned)
        cleaned = self.pagination_pattern.sub("", cleaned)
        
        return cleaned.strip()
    
    def extract_quality_report(self, text: str) -> Dict[str, any]:
        """
        Generate a comprehensive quality report.
        
        Args:
            text: Input text
            
        Returns:
            Dictionary with detailed quality report
        """
        score = self.calculate_quality_score(text)
        
        # Get specific artifact counts
        artifacts = {
            "scattered_chars": len(self.scattered_chars_pattern.findall(text)),
            "repeated_punct": len(self.repeated_punct_pattern.findall(text)),
            "malformed_words": len(self.malformed_words_pattern.findall(text)),
            "excessive_whitespace": len(self.excessive_whitespace_pattern.findall(text)),
            "script_tags": len(self.script_tag_pattern.findall(text)),
            "style_tags": len(self.style_tag_pattern.findall(text)),
            "nav_content": len(self.nav_words_pattern.findall(text)),
        }
        
        # Text statistics
        words = text.split()
        sentences = self.sentence_detect.findall(text)
        
        stats = {
            "char_count": len(text),
            "word_count": len(words),
            "sentence_count": len(sentences),
            "avg_words_per_sentence": len(words) / max(1, len(sentences)),
            "line_count": len(text.split('\n')),
        }
        
        return {
            "score": score,
            "artifacts": artifacts,
            "statistics": stats,
            "cleaned_text": self.clean_text(text) if score.overall < 0.8 else text
        }


class TextCleaner:
    """
    Simple text cleaner with common cleanup operations.
    """
    
    @staticmethod
    def normalize_whitespace(text: str) -> str:
        """Normalize all whitespace to single spaces."""
        return re.sub(r"\s+", " ", text).strip()
    
    @staticmethod
    def remove_extra_newlines(text: str) -> str:
        """Remove extra newlines."""
        return re.sub(r"\n{3,}", "\n\n", text)
    
    @staticmethod
    def remove_control_chars(text: str) -> str:
        """Remove control characters except newlines and tabs."""
        return re.sub(r"[\x00-\x08\x0b-\x0c\x0e-\x1f\x7f]", "", text)
    
    @staticmethod
    def fix_unicode_issues(text: str) -> str:
        """Fix common Unicode issues."""
        # Replace common OCR Unicode errors
        replacements = {
            "\u2018": "'",  # Left single quote
            "\u2019": "'",  # Right single quote
            "\u201c": '"',  # Left double quote
            "\u201d": '"',  # Right double quote
            "\u2013": "-",  # En dash
            "\u2014": "-",  # Em dash
            "\u2026": "...",  # Ellipsis
            "\u00a0": " ",  # Non-breaking space
        }
        
        for old, new in replacements.items():
            text = text.replace(old, new)
        
        return text
    
    @staticmethod
    def clean(text: str) -> str:
        """Apply all cleaning operations."""
        text = TextCleaner.remove_control_chars(text)
        text = TextCleaner.fix_unicode_issues(text)
        text = TextCleaner.normalize_whitespace(text)
        text = TextCleaner.remove_extra_newlines(text)
        
        return text


def calculate_quality_score(text: str) -> QualityScore:
    """Convenience function to calculate quality score."""
    processor = TextQualityProcessor()
    return processor.calculate_quality_score(text)


def clean_text(text: str) -> str:
    """Convenience function to clean text."""
    processor = TextQualityProcessor()
    return processor.clean_text(text)


def get_quality_report(text: str) -> Dict[str, any]:
    """Convenience function to get quality report."""
    processor = TextQualityProcessor()
    return processor.extract_quality_report(text)
