"""Language detection module for document processing.

This module provides language detection capabilities similar to kreuzberg's
language detection functionality.
"""

import re
from collections import Counter
from typing import Dict, List, Optional, Tuple


class LanguageDetector:
    """
    Language detector based on character n-gram profiles.
    
    Supports multiple languages and provides confidence scores.
    """
    
    # Language profiles (common trigrams)
    LANGUAGE_PROFILES = {
        "am": {
            # Amharic character trigrams (Geez script)
            "እንደ", "ስለ", "ነው", "ያለ", "አለ", "ነበር", "ነዚ", "ሆነ", "ነሱ", "ማን",
            "ዓይ", "ምን", "አይ", "አን", "እየ", "አማ", "በር", "ለም", "እስ", "ስም"
        },
        "en": {
            "the", "and", "ing", "ent", "ion", "her", "tha", "int", "for", "you",
            "thi", "hat", "are", "was", "all", "wer", "hes", "his", "not", "but"
        },
        "de": {
            "der", "die", "und", "ein", "ich", "ist", "den", "das", "nicht", "mit",
            "sie", "auf", "für", "von", "auch", "es", "an", "wer", "dem", "dass"
        },
        "fr": {
            "ent", "les", "une", "des", "est", "pour", "vous", "dans", "que",
            "sur", "une", "plus", "par", "pas", "sont", "qui", "avec", "votre", "cette"
        },
        "es": {
            "los", "que", "del", "las", "por", "una", "con", "para", "como",
            "más", "sobre", "este", "pero", "tiene", "tiene", "sus", "ello", "entre"
        },
        "it": {
            "che", "gli", "non", "per", "del", "una", "sono", "della", "anche",
            "quest", "come", "più", "alla", "quando", "hanno", "dopo", "agli", "sua"
        },
        "pt": {
            "que", "de", "para", "uma", "com", "não", "os", "por", "mais",
            "como", "são", "sua", "dos", "suas", "essa", "seu", "está", "nem"
        },
        "ru": {
            "что", "и", "в", "не", "на", "я", "быть", "он", "с", "это",
            "а", "по", "к", "весь", "она", "как", "у", "мы", "ты"
        },
        "zh": {
            "的", "一", "是", "在", "不", "了", "有", "和", "人", "这",
            "中", "大", "为", "上", "个", "国", "我", "以", "要", "他"
        },
        "ja": {
            "の", "に", "は", "を", "た", "が", "で", "て", "と", "し",
            "れ", "さ", "ある", "いる", "も", "する", "から", "な", "こと", "として"
        },
        "ar": {
            "في", "من", "على", "إلى", "أن", "كان", "هذا", "التي", "الذي", "بين",
            "قد", "بعد", "ذلك", "له", "عند", "إذا", "كما", "ذلك", "هذه", "ذات"
        },
        "am": {
            # Amharic character trigrams (Geez script)
            "እንደ", "ስለ", "ነው", "ያለ", "አለ", "ነበር", "ነዚ", "ሆነ", "ነሱ", "ማን",
            "ዓይ", "ምን", "አይ", "አን", "እየ", "አማ", "በር", "ለም", "እስ", "ስም"
        }
    }
    
    def __init__(
        self,
        min_confidence: float = 0.5,
        min_text_length: int = 20
    ):
        """
        Initialize the language detector.
        
        Args:
            min_confidence: Minimum confidence threshold
            min_text_length: Minimum text length for detection
        """
        self.min_confidence = min_confidence
        self.min_text_length = min_text_length
    
    def detect(self, text: str) -> Tuple[Optional[str], float]:
        """
        Detect the language of the text.
        
        Args:
            text: Input text
            
        Returns:
            Tuple of (language_code, confidence)
        """
        if len(text) < self.min_text_length:
            return None, 0.0
        
        # Extract character trigrams
        trigrams = self._extract_trigrams(text.lower())
        
        if not trigrams:
            return None, 0.0
        
        # Calculate scores for each language
        scores = {}
        
        for lang, profile in self.LANGUAGE_PROFILES.items():
            score = 0
            for trigram in trigrams:
                if trigram in profile:
                    score += 1
            
            if score > 0:
                scores[lang] = score / len(trigrams)
        
        if not scores:
            return None, 0.0
        
        # Get the best match
        best_lang = max(scores, key=scores.get)
        confidence = scores[best_lang]
        
        if confidence < self.min_confidence:
            return None, confidence
        
        return best_lang, confidence
    
    def _extract_trigrams(self, text: str) -> List[str]:
        """Extract character trigrams from text."""
        # Remove non-alphabetic characters for European languages
        text = re.sub(r'[^a-zA-Z\u4e00-\u9fff\u0600-\u06ff]', '', text)
        
        if len(text) < 3:
            return []
        
        trigrams = []
        for i in range(len(text) - 2):
            trigrams.append(text[i:i+3])
        
        return trigrams
    
    def detect_batch(self, texts: List[str]) -> List[Tuple[Optional[str], float]]:
        """
        Detect languages for multiple texts.
        
        Args:
            texts: List of texts
            
        Returns:
            List of (language, confidence) tuples
        """
        return [self.detect(text) for text in texts]
    
    def get_language_name(self, code: str) -> str:
        """Get full language name from code."""
        names = {
            "en": "English",
            "de": "German",
            "fr": "French",
            "es": "Spanish",
            "it": "Italian",
            "pt": "Portuguese",
            "ru": "Russian",
            "zh": "Chinese",
            "ja": "Japanese",
            "ar": "Arabic",
            "am": "Amharic"
        }
        return names.get(code, code)


class MultiLanguageDetector:
    """
    Advanced multi-language detector with per-page detection.
    """
    
    def __init__(self):
        self.detector = LanguageDetector()
    
    def detect_page_languages(
        self,
        pages: List[str]
    ) -> List[Dict[str, any]]:
        """
        Detect language for each page.
        
        Args:
            pages: List of page texts
            
        Returns:
            List of detection results per page
        """
        results = []
        
        for i, page_text in enumerate(pages):
            lang, confidence = self.detector.detect(page_text)
            
            results.append({
                "page_number": i + 1,
                "language": lang,
                "confidence": confidence,
                "language_name": self.detector.get_language_name(lang) if lang else None,
                "text_length": len(page_text)
            })
        
        return results
    
    def detect_document_language(
        self,
        pages: List[str],
        method: str = "majority"
    ) -> Dict[str, any]:
        """
        Detect overall document language.
        
        Args:
            pages: List of page texts
            method: Detection method ("majority" or "first")
            
        Returns:
            Document language detection result
        """
        if method == "first":
            # Use first page's language
            if not pages:
                return {"language": None, "confidence": 0.0}
            
            lang, confidence = self.detector.detect(pages[0])
            return {
                "language": lang,
                "confidence": confidence,
                "language_name": self.detector.get_language_name(lang) if lang else None,
                "method": "first_page"
            }
        
        # Majority voting
        page_results = self.detect_page_languages(pages)
        
        lang_counts = Counter(
            r["language"] for r in page_results
            if r["language"] is not None
        )
        
        if not lang_counts:
            return {"language": None, "confidence": 0.0}
        
        # Get most common language
        majority_lang = lang_counts.most_common(1)[0][0]
        
        # Calculate average confidence for majority language
        confidences = [
            r["confidence"] for r in page_results
            if r["language"] == majority_lang
        ]
        avg_confidence = sum(confidences) / len(confidences) if confidences else 0.0
        
        return {
            "language": majority_lang,
            "confidence": avg_confidence,
            "language_name": self.detector.get_language_name(majority_lang),
            "method": "majority_vote",
            "language_distribution": dict(lang_counts),
            "page_count": len(pages)
        }


def detect_language(text: str) -> Tuple[Optional[str], float]:
    """
    Convenience function to detect language.
    
    Args:
        text: Input text
        
    Returns:
        Tuple of (language_code, confidence)
    """
    detector = LanguageDetector()
    return detector.detect(text)


def detect_document_languages(pages: List[str]) -> Dict[str, any]:
    """
    Convenience function to detect document languages.
    
    Args:
        pages: List of page texts
        
    Returns:
        Document language detection result
    """
    detector = MultiLanguageDetector()
    return detector.detect_document_language(pages)
