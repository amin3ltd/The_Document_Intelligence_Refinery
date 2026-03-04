"""
Ollama/LM Studio Client for Local VLM Inference

Supports connecting to:
- Ollama (http://localhost:11434)
- LM Studio (http://localhost:1234)

This enables free, local vision-language model inference
without requiring OpenAI API keys.
"""

import base64
import json
from pathlib import Path
from typing import Optional, Dict, Any, List
from enum import Enum

import httpx
from PIL import Image
from loguru import logger
from pydantic import BaseModel


class LocalVLMProvider(str, Enum):
    OLLAMA = "ollama"
    LM_STUDIO = "lmstudio"


class OllamaConfig(BaseModel):
    """Configuration for Ollama/LM Studio connection"""
    provider: LocalVLMProvider = LocalVLMProvider.OLLAMA
    base_url: str = "http://localhost:11434"
    model: str = "llava"  # Default vision model for Ollama
    timeout: int = 120
    temperature: float = 0.1


class ExtractionPrompt:
    """Prompt templates for document extraction"""
    
    TABLE_EXTRACTION = """Extract the table from this document image.
Return the table data as JSON with headers and rows.
If no table is found, return {{"error": "No table found"}}.

Output format:
{{
    "headers": ["col1", "col2", ...],
    "rows": [["val1", "val2", ...], ...]
}}
"""
    
    FULL_EXTRACTION = """Analyze this document and extract all structured information.
Extract:
- Text blocks with their positions
- Tables with headers and data
- Figures with captions
- Section headers

Return as JSON:
{{
    "text_blocks": [{{"text": "...", "bbox": [x0, y0, x1, y1]}}],
    "tables": [{{"headers": [...], "rows": [...]}}],
    "figures": [{{"caption": "...", "bbox": [...]}}],
    "sections": [{{"title": "...", "level": 1, "bbox": [...]}}]
}}
"""
    
    OCR_EXTRACTION = """Perform OCR on this document image.
Extract all readable text while preserving reading order.
Include layout information (columns, paragraphs).
Return as JSON:
{{
    "text": "full extracted text...",
    "blocks": [{{"text": "...", "bbox": [x0, y0, x1, y1], "type": "paragraph"}}]
}}
"""


class OllamaClient:
    """
    Client for local VLM inference using Ollama or LM Studio.
    
    Usage:
        client = OllamaClient(provider=LocalVLMProvider.OLLAMA, model="llava")
        result = client.extract_from_image(image_path, ExtractionPrompt.TABLE_EXTRACTION)
    """
    
    def __init__(self, config: Optional[OllamaConfig] = None):
        self.config = config or OllamaConfig()
        self.client = httpx.Client(
            base_url=self.config.base_url,
            timeout=self.config.timeout
        )
        self._available_models: Optional[List[str]] = None
        
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.client.close()
    
    @property
    def available_models(self) -> List[str]:
        """Get list of available models"""
        if self._available_models is None:
            self._available_models = self._list_models()
        return self._available_models
    
    def _list_models(self) -> List[str]:
        """Query available models from the server"""
        try:
            if self.config.provider == LocalVLMProvider.OLLAMA:
                response = self.client.get("/api/tags")
                if response.status_code == 200:
                    data = response.json()
                    return [m["name"] for m in data.get("models", [])]
            elif self.config.provider == LocalVLMProvider.LM_STUDIO:
                response = self.client.get("/v1/models")
                if response.status_code == 200:
                    data = response.json()
                    return [m["id"] for m in data.get("data", [])]
        except Exception as e:
            logger.warning(f"Failed to list models: {e}")
        return []
    
    def is_model_available(self, model: Optional[str] = None) -> bool:
        """Check if the specified model is available"""
        model = model or self.config.model
        return model in self.available_models
    
    def _encode_image(self, image_path: str) -> str:
        """Encode image to base64"""
        with open(image_path, "rb") as f:
            return base64.b64encode(f.read()).decode("utf-8")
    
    def _encode_pil_image(self, image: Image.Image) -> str:
        """Encode PIL Image to base64"""
        import io
        buffer = io.BytesIO()
        image.save(buffer, format="PNG")
        return base64.b64encode(buffer.getvalue()).decode("utf-8")
    
    def chat(
        self,
        message: str,
        images: Optional[List[str]] = None,
        system: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Send a chat request with optional images
        
        Args:
            message: Text message
            images: List of image paths or base64 encoded images
            system: Optional system prompt
            **kwargs: Additional parameters (temperature, etc.)
        
        Returns:
            Response dict with "content" field
        """
        # Prepare messages
        messages = []
        
        if system:
            messages.append({"role": "system", "content": system})
        
        # Prepare content
        content = []
        if images:
            for img in images:
                if Path(img).exists():
                    # It's a file path
                    b64_img = self._encode_image(img)
                    content.append({
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/png;base64,{b64_img}"
                        }
                    })
                elif img.startswith("data:"):
                    # Already base64
                    content.append({
                        "type": "image_url",
                        "image_url": {"url": img}
                    })
        
        content.append({"type": "text", "text": message})
        messages.append({"role": "user", "content": content})
        
        try:
            if self.config.provider == LocalVLMProvider.OLLAMA:
                return self._ollama_chat(messages, **kwargs)
            elif self.config.provider == LocalVLMProvider.LM_STUDIO:
                return self._lmstudio_chat(messages, **kwargs)
        except Exception as e:
            logger.error(f"Chat request failed: {e}")
            raise
    
    def _ollama_chat(self, messages: List[Dict], **kwargs) -> Dict[str, Any]:
        """Send chat request to Ollama"""
        payload = {
            "model": self.config.model,
            "messages": messages,
            "stream": False,
            "options": {
                "temperature": kwargs.get("temperature", self.config.temperature)
            }
        }
        
        response = self.client.post("/api/chat", json=payload)
        response.raise_for_status()
        return response.json()
    
    def _lmstudio_chat(self, messages: List[Dict], **kwargs) -> Dict[str, Any]:
        """Send chat request to LM Studio"""
        # LM Studio uses OpenAI-compatible API
        payload = {
            "model": self.config.model,
            "messages": messages,
            "temperature": kwargs.get("temperature", self.config.temperature)
        }
        
        response = self.client.post("/v1/chat/completions", json=payload)
        response.raise_for_status()
        data = response.json()
        
        # Convert to Ollama-like format
        return {
            "message": {
                "role": data["choices"][0]["message"]["role"],
                "content": data["choices"][0]["message"]["content"]
            },
            "done": True
        }
    
    def extract_from_image(
        self,
        image_path: str,
        prompt: str,
        response_format: str = "json"
    ) -> str:
        """
        Extract structured data from an image using VLM
        
        Args:
            image_path: Path to the image file
            prompt: Extraction prompt (use ExtractionPrompt class)
            response_format: Expected response format ("json" or "text")
        
        Returns:
            Extracted text content
        """
        # Add format instruction to prompt
        if response_format == "json":
            prompt = prompt + "\n\nRespond ONLY with valid JSON, no other text."
        
        result = self.chat(message=prompt, images=[image_path])
        return result.get("message", {}).get("content", "")
    
    def extract_table(self, image_path: str) -> Dict[str, Any]:
        """Extract table from image"""
        result = self.extract_from_image(
            image_path,
            ExtractionPrompt.TABLE_EXTRACTION,
            response_format="json"
        )
        try:
            return json.loads(result)
        except json.JSONDecodeError:
            logger.warning(f"Failed to parse table JSON: {result}")
            return {"error": "Parse error", "raw": result}
    
    def ocr_image(self, image_path: str) -> Dict[str, Any]:
        """Perform OCR on image"""
        result = self.extract_from_image(
            image_path,
            ExtractionPrompt.OCR_EXTRACTION,
            response_format="json"
        )
        try:
            return json.loads(result)
        except json.JSONDecodeError:
            logger.warning(f"Failed to parse OCR JSON: {result}")
            return {"text": result, "error": "Parse error"}
    
    def full_extraction(self, image_path: str) -> Dict[str, Any]:
        """Full document extraction from image"""
        result = self.extract_from_image(
            image_path,
            ExtractionPrompt.FULL_EXTRACTION,
            response_format="json"
        )
        try:
            return json.loads(result)
        except json.JSONDecodeError:
            logger.warning(f"Failed to parse extraction JSON: {result}")
            return {"error": "Parse error", "raw": result}


def create_ollama_client(
    provider: str = "ollama",
    base_url: str = "http://localhost:11434",
    model: str = "llava"
) -> OllamaClient:
    """
    Factory function to create Ollama client
    
    Args:
        provider: "ollama" or "lmstudio"
        base_url: Base URL for the server
        model: Model name to use
    
    Returns:
        Configured OllamaClient instance
    """
    config = OllamaConfig(
        provider=LocalVLMProvider(provider),
        base_url=base_url,
        model=model
    )
    return OllamaClient(config)
