"""Plugins package for the Document Intelligence Refinery.

This package provides a plugin architecture for extensible document processing:
- OCR backends (Tesseract, EasyOCR, PaddleOCR)
- Validators (quality, security, format)
- Post-processors (text cleanup, language detection, entity extraction)
"""

from src.utils.plugin_system import (
    Plugin,
    PluginMetadata,
    PluginRegistry,
    PluginType,
    get_registry,
    register_plugin,
)

from src.utils.plugins.ocr_backend import (
    OcrBackend,
    OcrBackendType,
    OcrConfig,
    OcrResult,
    get_ocr_backend,
    register_ocr_backend,
)

from src.utils.plugins.validator import (
    FormatValidator,
    SecurityValidator,
    ValidationIssue,
    ValidationLevel,
    ValidationResult,
    Validator,
    get_validator,
)

from src.utils.plugins.post_processor import (
    EntityExtractionPostProcessor,
    LanguageDetectionPostProcessor,
    PostProcessResult,
    PostProcessor,
    PostProcessorType,
    TextCleanupPostProcessor,
    get_post_processor,
)

__all__ = [
    # Plugin system
    "Plugin",
    "PluginMetadata",
    "PluginRegistry",
    "PluginType",
    "get_registry",
    "register_plugin",
    # OCR backends
    "OcrBackend",
    "OcrBackendType",
    "OcrConfig",
    "OcrResult",
    "get_ocr_backend",
    "register_ocr_backend",
    # Validators
    "FormatValidator",
    "SecurityValidator",
    "ValidationIssue",
    "ValidationLevel",
    "ValidationResult",
    "Validator",
    "get_validator",
    # Post-processors
    "EntityExtractionPostProcessor",
    "LanguageDetectionPostProcessor",
    "PostProcessResult",
    "PostProcessor",
    "PostProcessorType",
    "TextCleanupPostProcessor",
    "get_post_processor",
]
