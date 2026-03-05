"""OCR backend plugin interface.

Provides the base interface for implementing custom OCR backends.
Supported backends include Tesseract, EasyOCR, PaddleOCR, and cloud services.
"""

from abc import ABC, abstractmethod
from enum import Enum
from pydantic import BaseModel, Field
from typing import Any, Dict, List, Optional

from src.utils.plugin_system import Plugin, PluginMetadata, PluginType


class OcrBackendType(str, Enum):
    """OCR backend types."""
    TESSERACT = "tesseract"
    EASYOCR = "easyocr"
    PADDLEOCR = "paddleocr"
    GOOGLE_VISION = "google_vision"
    AWS_TEXTTRACT = "aws_textract"
    AZURE_FORM_RECOGNIZER = "azure_form_recognizer"
    CUSTOM = "custom"


class OcrConfig(BaseModel):
    """Configuration for OCR processing."""
    languages: List[str] = Field(
        default=["eng"],
        description="Languages for OCR (ISO 639-2 codes)"
    )
    dpi: int = Field(default=300, ge=72, le=600, description="Image DPI")
    rotate_and_deskew: bool = Field(default=True, description="Auto-rotate and deskew")
    enhance_image: bool = Field(default=True, description="Enhance image before OCR")
    ocr_timeout: int = Field(default=300, ge=1, description="OCR timeout in seconds")
    min_confidence: float = Field(
        default=0.5,
        ge=0.0,
        le=1.0,
        description="Minimum confidence threshold"
    )
    include_bounding_boxes: bool = Field(
        default=True,
        description="Include bounding box coordinates"
    )
    include_words: bool = Field(default=True, description="Include word-level results")
    custom_config: Dict[str, Any] = Field(
        default_factory=dict,
        description="Backend-specific configuration"
    )


class OcrResult(BaseModel):
    """Result from OCR processing."""
    text: str = Field(..., description="Extracted text")
    confidence: float = Field(
        default=1.0,
        ge=0.0,
        le=1.0,
        description="Overall OCR confidence"
    )
    words: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Word-level results with bounding boxes"
    )
    languages_detected: List[str] = Field(
        default_factory=list,
        description="Detected languages"
    )
    processing_time_ms: int = Field(default=0, description="Processing time in milliseconds")


class OcrBackend(Plugin, ABC):
    """Base class for OCR backend plugins.
    
    Implement this class to add custom OCR capabilities.
    """
    
    @property
    def plugin_type(self) -> PluginType:
        return PluginType.OCR_BACKEND
    
    @abstractmethod
    def backend_type(self) -> OcrBackendType:
        """Return the type of OCR backend."""
        pass
    
    @abstractmethod
    async def process_image(
        self,
        image_bytes: bytes,
        config: OcrConfig
    ) -> OcrResult:
        """Process an image and extract text.
        
        Args:
            image_bytes: Raw image bytes
            config: OCR configuration
            
        Returns:
            OcrResult with extracted text and metadata
        """
        pass
    
    @abstractmethod
    async def process_file(
        self,
        file_path: str,
        config: OcrConfig
    ) -> OcrResult:
        """Process an image file and extract text.
        
        Args:
            file_path: Path to image file
            config: OCR configuration
            
        Returns:
            OcrResult with extracted text and metadata
        """
        pass
    
    @abstractmethod
    def supports_language(self, lang: str) -> bool:
        """Check if backend supports a language.
        
        Args:
            lang: Language code (ISO 639-2)
            
        Returns:
            True if language is supported
        """
        pass
    
    def get_supported_languages(self) -> List[str]:
        """Get list of supported languages.
        
        Returns:
            List of supported language codes
        """
        return ["eng"]  # Default implementation


class TesseractOcrBackend(OcrBackend):
    """Tesseract OCR backend implementation."""
    
    @property
    def metadata(self) -> PluginMetadata:
        return PluginMetadata(
            name="tesseract-ocr",
            version="1.0.0",
            description="Tesseract OCR backend",
            author="Document Intelligence Team",
            plugin_type=PluginType.OCR_BACKEND,
            dependencies=["pytesseract"]
        )
    
    def backend_type(self) -> OcrBackendType:
        return OcrBackendType.TESSERACT
    
    def initialize(self) -> None:
        """Initialize Tesseract."""
        logger = __import__("logging").getLogger(__name__)
        logger.info("Initializing Tesseract OCR backend")
    
    def shutdown(self) -> None:
        """Shutdown Tesseract."""
        logger = __import__("logging").getLogger(__name__)
        logger.info("Shutting down Tesseract OCR backend")
    
    async def process_image(
        self,
        image_bytes: bytes,
        config: OcrConfig
    ) -> OcrResult:
        """Process image with Tesseract."""
        import pytesseract
        from PIL import Image
        import io
        
        image = Image.open(io.BytesIO(image_bytes))
        text = pytesseract.image_to_string(image, lang="+".join(config.languages))
        
        words = []
        if config.include_words:
            data = pytesseract.image_to_data(
                image,
                lang="+".join(config.languages),
                output_type=pytesseract.Output.DICT
            )
            for i, word in enumerate(data["text"]):
                if word.strip():
                    words.append({
                        "text": word,
                        "confidence": data["conf"][i] / 100.0,
                        "bbox": [
                            data["left"][i],
                            data["top"][i],
                            data["left"][i] + data["width"][i],
                            data["top"][i] + data["height"][i]
                        ]
                    })
        
        return OcrResult(
            text=text,
            confidence=0.85,
            words=words,
            languages_detected=config.languages
        )
    
    async def process_file(
        self,
        file_path: str,
        config: OcrConfig
    ) -> OcrResult:
        """Process image file with Tesseract."""
        with open(file_path, "rb") as f:
            return await self.process_image(f.read(), config)
    
    def supports_language(self, lang: str) -> bool:
        """Check if Tesseract supports language."""
        # Tesseract supports 100+ languages
        supported = ["eng", "deu", "fra", "spa", "ita", "por", "rus", "chi_sim", "chi_tra", "jpn", "kor"]
        return lang in supported
    
    def get_supported_languages(self) -> List[str]:
        return [
            "eng", "deu", "fra", "spa", "ita", "por", "rus",
            "chi_sim", "chi_tra", "jpn", "kor", "ara", "hin"
        ]


class EasyOcrBackend(OcrBackend):
    """EasyOCR backend implementation."""
    
    @property
    def metadata(self) -> PluginMetadata:
        return PluginMetadata(
            name="easyocr-backend",
            version="1.0.0",
            description="EasyOCR backend",
            author="Document Intelligence Team",
            plugin_type=PluginType.OCR_BACKEND,
            dependencies=["easyocr"]
        )
    
    def backend_type(self) -> OcrBackendType:
        return OcrBackendType.EASYOCR
    
    def initialize(self) -> None:
        """Initialize EasyOCR."""
        logger = __import__("logging").getLogger(__name__)
        logger.info("Initializing EasyOCR backend")
    
    def shutdown(self) -> None:
        """Shutdown EasyOCR."""
        pass
    
    async def process_image(
        self,
        image_bytes: bytes,
        config: OcrConfig
    ) -> OcrResult:
        """Process image with EasyOCR."""
        import easyocr
        import numpy as np
        from PIL import Image
        import io
        
        reader = easyocr.Reader(config.languages, gpu=False)
        
        image = Image.open(io.BytesIO(image_bytes))
        image_np = np.array(image)
        
        results = reader.readtext(image_np)
        
        words = []
        text_parts = []
        confidences = []
        
        for bbox, text, confidence in results:
            text_parts.append(text)
            confidences.append(confidence)
            words.append({
                "text": text,
                "confidence": confidence,
                "bbox": bbox
            })
        
        avg_confidence = sum(confidences) / len(confidences) if confidences else 0.0
        
        return OcrResult(
            text=" ".join(text_parts),
            confidence=avg_confidence,
            words=words,
            languages_detected=config.languages
        )
    
    async def process_file(
        self,
        file_path: str,
        config: OcrConfig
    ) -> OcrResult:
        """Process image file with EasyOCR."""
        with open(file_path, "rb") as f:
            return await self.process_image(f.read(), config)
    
    def supports_language(self, lang: str) -> bool:
        """Check if EasyOCR supports language."""
        # EasyOCR supports 80+ languages
        supported = ["en", "de", "fr", "es", "it", "pt", "ru", "zh", "ja", "ko", "ar"]
        return lang in supported or lang[:3] in supported


class PaddleOcrBackend(OcrBackend):
    """PaddleOCR backend implementation."""
    
    @property
    def metadata(self) -> PluginMetadata:
        return PluginMetadata(
            name="paddleocr-backend",
            version="1.0.0",
            description="PaddleOCR backend",
            author="Document Intelligence Team",
            plugin_type=PluginType.OCR_BACKEND,
            dependencies=["paddleocr"]
        )
    
    def backend_type(self) -> OcrBackendType:
        return OcrBackendType.PADDLEOCR
    
    def initialize(self) -> None:
        """Initialize PaddleOCR."""
        logger = __import__("logging").getLogger(__name__)
        logger.info("Initializing PaddleOCR backend")
    
    def shutdown(self) -> None:
        """Shutdown PaddleOCR."""
        pass
    
    async def process_image(
        self,
        image_bytes: bytes,
        config: OcrConfig
    ) -> OcrResult:
        """Process image with PaddleOCR."""
        from paddleocr import PaddleOCR
        import numpy as np
        from PIL import Image
        import io
        
        ocr = PaddleOCR(
            lang=config.languages[0] if config.languages else "en",
            use_angle_cls=True,
            show_log=False
        )
        
        image = Image.open(io.BytesIO(image_bytes))
        image_np = np.array(image)
        
        results = ocr.ocr(image_np, cls=True)
        
        words = []
        text_parts = []
        confidences = []
        
        if results and results[0]:
            for line in results[0]:
                bbox = line[0]
                text = line[1][0]
                confidence = line[1][1]
                
                text_parts.append(text)
                confidences.append(confidence)
                words.append({
                    "text": text,
                    "confidence": confidence,
                    "bbox": bbox
                })
        
        avg_confidence = sum(confidences) / len(confidences) if confidences else 0.0
        
        return OcrResult(
            text="\n".join(text_parts),
            confidence=avg_confidence,
            words=words,
            languages_detected=config.languages
        )
    
    async def process_file(
        self,
        file_path: str,
        config: OcrConfig
    ) -> OcrResult:
        """Process image file with PaddleOCR."""
        with open(file_path, "rb") as f:
            return await self.process_image(f.read(), config)
    
    def supports_language(self, lang: str) -> bool:
        """Check if PaddleOCR supports language."""
        supported = ["ch", "en", "fr", "de", "es", "ru", "ja", "ko"]
        return lang in supported


# Registry for OCR backends
_ocr_backends: Dict[OcrBackendType, type[OcrBackend]] = {
    OcrBackendType.TESSERACT: TesseractOcrBackend,
    OcrBackendType.EASYOCR: EasyOcrBackend,
    OcrBackendType.PADDLEOCR: PaddleOcrBackend,
}


def get_ocr_backend(backend_type: OcrBackendType) -> OcrBackend:
    """Get an OCR backend instance by type.
    
    Args:
        backend_type: Type of OCR backend
        
    Returns:
        OcrBackend instance
    """
    backend_class = _ocr_backends.get(backend_type)
    if backend_class is None:
        raise ValueError(f"Unknown OCR backend type: {backend_type}")
    return backend_class()


def register_ocr_backend(backend_type: OcrBackendType, backend_class: type[OcrBackend]) -> None:
    """Register a custom OCR backend.
    
    Args:
        backend_type: Type identifier for the backend
        backend_class: Backend class to register
    """
    _ocr_backends[backend_type] = backend_class
