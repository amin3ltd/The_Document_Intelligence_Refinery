"""Unit tests for token reduction module."""

import pytest
from src.utils.token_reduction import (
    TokenReducer,
    CJKTokenizer,
    SemanticDeduplicator,
    reduce_tokens,
    extract_cjk_keywords,
    deduplicate_texts,
    deduplicate_sentences,
    ReductionResult
)


class TestTokenReducer:
    """Test cases for TokenReducer class."""
    
    def test_simple_reduction(self):
        """Test simple token reduction."""
        reducer = TokenReducer()
        text = "This is a test text with many words to reduce"
        
        result = reducer.reduce(text, ratio=0.5, method="simple")
        
        assert isinstance(result, ReductionResult)
        assert result.reduced_token_count < result.original_token_count
    
    def test_hybrid_reduction(self):
        """Test hybrid token reduction."""
        reducer = TokenReducer()
        text = "This is a sample text for testing the hybrid reduction method"
        
        result = reducer.reduce(text, ratio=0.5, method="hybrid")
        
        assert isinstance(result, ReductionResult)
        assert result.method == "hybrid"
    
    def test_empty_text(self):
        """Test with empty text."""
        reducer = TokenReducer()
        
        result = reducer.reduce("", ratio=0.5)
        
        assert result.reduced_text == ""
    
    def test_short_text(self):
        """Test with short text."""
        reducer = TokenReducer()
        text = "Short text"
        
        result = reducer.reduce(text, ratio=0.5)
        
        assert isinstance(result, ReductionResult)


class TestCJKTokenizer:
    """Test cases for CJKTokenizer class."""
    
    def test_is_cjk_char_chinese(self):
        """Test Chinese character detection."""
        tokenizer = CJKTokenizer()
        
        assert tokenizer.is_cjk_char("中") is True
        assert tokenizer.is_cjk_char("文") is True
    
    def test_is_cjk_char_japanese(self):
        """Test Japanese character detection."""
        tokenizer = CJKTokenizer()
        
        assert tokenizer.is_cjk_char("日") is True
        assert tokenizer.is_cjk_char("本") is True
    
    def test_is_cjk_char_korean(self):
        """Test Korean character detection."""
        tokenizer = CJKTokenizer()
        
        assert tokenizer.is_cjk_char("한") is True
        assert tokenizer.is_cjk_char("글") is True
    
    def test_is_cjk_char_english(self):
        """Test English character detection."""
        tokenizer = CJKTokenizer()
        
        assert tokenizer.is_cjk_char("a") is False
        assert tokenizer.is_cjk_char("b") is False
    
    def test_tokenize_mixed(self):
        """Test tokenizing mixed CJK and English text."""
        tokenizer = CJKTokenizer()
        text = "Hello 世界 this is テスト"
        
        tokens = tokenizer.tokenize(text)
        
        assert isinstance(tokens, list)
        assert len(tokens) > 0
    
    def test_extract_keywords_chinese(self):
        """Test extracting Chinese keywords."""
        tokenizer = CJKTokenizer()
        text = "中文文本处理中文分析中文提取"
        
        keywords = tokenizer.extract_keywords(text, top_n=3)
        
        assert isinstance(keywords, list)
        assert len(keywords) <= 3


class TestSemanticDeduplicator:
    """Test cases for SemanticDeduplicator class."""
    
    def test_deduplicate_texts(self):
        """Test text deduplication."""
        dedup = SemanticDeduplicator(similarity_threshold=0.8)
        texts = [
            "This is a sample text",
            "This is a sample text",  # Duplicate
            "This is a different text"
        ]
        
        unique = dedup.deduplicate(texts)
        
        assert len(unique) == 2
    
    def test_deduplicate_sentences(self):
        """Test sentence deduplication."""
        dedup = SemanticDeduplicator()
        text = "First sentence. Second sentence. First sentence."
        
        unique = dedup.deduplicate_sentences(text)
        
        assert "First sentence." in unique
        assert unique.count("First sentence.") == 1
    
    def test_similarity_calculation(self):
        """Test similarity calculation."""
        dedup = SemanticDeduplicator()
        
        sim = dedup._calculate_similarity("hello world", "hello world")
        assert sim == 1.0
        
        sim = dedup._calculate_similarity("hello world", "goodbye world")
        assert 0.0 <= sim < 1.0


class TestConvenienceFunctions:
    """Test convenience functions."""
    
    def test_reduce_tokens_function(self):
        """Test reduce_tokens convenience function."""
        text = "This is a sample text for token reduction testing"
        
        result = reduce_tokens(text, ratio=0.5)
        
        assert isinstance(result, ReductionResult)
    
    def test_extract_cjk_keywords_function(self):
        """Test extract_cjk_keywords convenience function."""
        text = "中文关键词提取测试"
        
        keywords = extract_cjk_keywords(text, top_n=3)
        
        assert isinstance(keywords, list)
    
    def test_deduplicate_texts_function(self):
        """Test deduplicate_texts convenience function."""
        texts = ["text one", "text one", "text two"]
        
        unique = deduplicate_texts(texts)
        
        assert len(unique) == 2
    
    def test_deduplicate_sentences_function(self):
        """Test deduplicate_sentences convenience function."""
        text = "First. Second. First."
        
        unique = deduplicate_sentences(text)
        
        assert unique.count("First.") == 1
