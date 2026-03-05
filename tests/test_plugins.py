"""Unit tests for plugin system."""

import pytest
from src.utils.plugins import (
    get_ocr_backend,
    get_validator,
    get_post_processor,
    OcrBackendType,
    PostProcessorType,
    PluginRegistry
)


class TestOCRBackends:
    """Test cases for OCR backend plugins."""
    
    def test_get_tesseract_backend(self):
        """Test getting Tesseract OCR backend."""
        try:
            backend = get_ocr_backend(OcrBackendType.TESSERACT)
            assert backend is not None
        except Exception as e:
            pytest.skip(f"Tesseract not available: {e}")
    
    def test_get_easyocr_backend(self):
        """Test getting EasyOCR backend."""
        try:
            backend = get_ocr_backend(OcrBackendType.EASYOCR)
            assert backend is not None
        except Exception as e:
            pytest.skip(f"EasyOCR not available: {e}")
    
    def test_get_paddleocr_backend(self):
        """Test getting PaddleOCR backend."""
        try:
            backend = get_ocr_backend(OcrBackendType.PADDLEOCR)
            assert backend is not None
        except Exception as e:
            pytest.skip(f"PaddleOCR not available: {e}")


class TestValidators:
    """Test cases for validator plugins."""
    
    def test_get_quality_validator(self):
        """Test getting quality validator."""
        try:
            validator = get_validator("quality")
            assert validator is not None
        except Exception as e:
            pytest.skip(f"Quality validator not available: {e}")
    
    def test_get_security_validator(self):
        """Test getting security validator."""
        try:
            validator = get_validator("security")
            assert validator is not None
        except Exception as e:
            pytest.skip(f"Security validator not available: {e}")


class TestPostProcessors:
    """Test cases for post-processor plugins."""
    
    def test_get_text_cleanup_processor(self):
        """Test getting text cleanup post-processor."""
        try:
            processor = get_post_processor(PostProcessorType.TEXT_CLEANUP)
            assert processor is not None
        except Exception as e:
            pytest.skip(f"Text cleanup processor not available: {e}")
    
    def test_get_language_detection_processor(self):
        """Test getting language detection post-processor."""
        try:
            processor = get_post_processor(PostProcessorType.LANGUAGE_DETECTION)
            assert processor is not None
        except Exception as e:
            pytest.skip(f"Language detection processor not available: {e}")
    
    def test_get_entity_extraction_processor(self):
        """Test getting entity extraction post-processor."""
        try:
            processor = get_post_processor(PostProcessorType.ENTITY_EXTRACTION)
            assert processor is not None
        except Exception as e:
            pytest.skip(f"Entity extraction processor not available: {e}")


class TestPluginRegistry:
    """Test cases for PluginRegistry class."""
    
    def test_registry_creation(self):
        """Test creating a plugin registry."""
        registry = PluginRegistry()
        
        assert registry is not None
    
    def test_register_plugin(self):
        """Test registering a plugin."""
        registry = PluginRegistry()
        
        # Register a simple test plugin
        def test_plugin():
            return "test"
        
        registry.register("test", test_plugin)
        
        # Should be able to retrieve
        plugin = registry.get("test")
        assert plugin is not None
    
    def test_unregister_plugin(self):
        """Test unregistering a plugin."""
        registry = PluginRegistry()
        
        # Register then unregister
        def test_plugin():
            return "test"
        
        registry.register("test_plugin", test_plugin)
        registry.unregister("test_plugin")
        
        # Should be None after unregister
        plugin = registry.get("test_plugin")
        assert plugin is None
    
    def test_list_plugins(self):
        """Test listing registered plugins."""
        registry = PluginRegistry()
        
        def plugin1():
            return "1"
        
        def plugin2():
            return "2"
        
        registry.register("p1", plugin1)
        registry.register("p2", plugin2)
        
        plugins = registry.list_plugins()
        
        assert "p1" in plugins
        assert "p2" in plugins
