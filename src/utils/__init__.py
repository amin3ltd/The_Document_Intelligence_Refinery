"""Utils package for the Document Intelligence Refinery."""

from src.utils.config import Config, get_config, load_rules
from src.utils.ledger import ExtractionLedger, get_ledger
from src.utils.plugins import (
    get_ocr_backend,
    get_post_processor,
    get_registry,
    get_validator,
    OcrBackend,
    OcrBackendType,
    OcrConfig,
    OcrResult,
    Plugin,
    PluginMetadata,
    PluginRegistry,
    PluginType,
    PostProcessResult,
    PostProcessor,
    PostProcessorType,
    register_plugin,
    ValidationIssue,
    ValidationLevel,
    ValidationResult,
    Validator,
)

__all__ = [
    # Config
    "Config",
    "get_config",
    "load_rules",
    # Ledger
    "ExtractionLedger",
    "get_ledger",
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
    # Validators
    "Validator",
    "ValidationResult",
    "ValidationIssue",
    "ValidationLevel",
    "get_validator",
    # Post-processors
    "PostProcessor",
    "PostProcessResult",
    "PostProcessorType",
    "get_post_processor",
]
