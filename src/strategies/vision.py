"""
Strategy C: Vision-Augmented Extraction using VLM.

This strategy uses Vision Language Models (GPT-4o, Gemini, local VLMs via Ollama/LM Studio)
for scanned images, handwriting, and complex visual documents.
Highest cost but best quality for difficult documents.

Supports:
- OpenAI GPT-4o
- Google Gemini Vision
- Local VLMs via Ollama (llava, bakllava, etc.)
- Local VLMs via LM Studio
"""

import base64
import io
import json
import logging
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

import fitz  # PyMuPDF
from PIL import Image

from src.models.document_profile import DocumentProfile
from src.models.extracted_document import (
    ExtractedDocument,
    ExtractionMetadata,
    FigureData,
    TextBlock,
    TableData,
)

logger = logging.getLogger(__name__)


class VisionStrategy:
    """
    Vision-augmented extraction using VLM.
    
    Best for: Scanned images, handwriting, complex visuals
    Cost: High (~$0.10-0.50/page) for API, Free for local
    Quality: Highest for difficult documents
    
    Supported providers:
    - "ollama": Local VLM via Ollama (free)
    - "lmstudio": Local VLM via LM Studio (free)
    - "openai": OpenAI GPT-4o (paid)
    - "google": Google Gemini (paid)
    """
    
    @property
    def name(self) -> str:
        return "strategy_c"
    
    def __init__(
        self,
        provider: str = "ollama",
        model: str = "llava",
        api_key: Optional[str] = None,
        base_url: str = "http://localhost:11434",
    ):
        """
        Initialize the strategy.
        
        Args:
            provider: VLM provider (ollama, lmstudio, openai, google)
            model: Model name
            api_key: API key for the provider (optional for local)
            base_url: Base URL for local providers
        """
        self.provider = provider
        self.model = model
        self.api_key = api_key
        self.base_url = base_url
        self._client = None
    
    def _get_client(self):
        """Get or initialize the VLM client."""
        if self._client is not None:
            return self._client
        
        try:
            if self.provider in ("ollama", "lmstudio"):
                # Use local Ollama/LM Studio client
                from src.utils.ollama_client import OllamaClient, LocalVLMProvider
                
                provider_enum = (
                    LocalVLMProvider.OLLAMA 
                    if self.provider == "ollama" 
                    else LocalVLMProvider.LM_STUDIO
                )
                
                self._client = OllamaClient(
                    config=type('Config', (), {
                        'provider': provider_enum,
                        'base_url': self.base_url,
                        'model': self.model,
                        'timeout': 120,
                        'temperature': 0.1
                    })()
                )
                logger.info(f"Initialized {self.provider} client with model {self.model}")
                
            elif self.provider == "openai":
                from openai import OpenAI
                self._client = OpenAI(api_key=self.api_key)
                logger.info(f"Initialized OpenAI client with model {self.model}")
                
            elif self.provider == "google":
                import google.generativeai as genai
                genai.configure(api_key=self.api_key)
                self._client = genai
                logger.info(f"Initialized Google Gemini client")
                
        except ImportError as e:
            logger.warning(f"Provider client not available: {e}")
            self._client = None
            
        return self._client
    
    def extract(self, file_path: str, profile: DocumentProfile) -> ExtractedDocument:
        """
        Extract text using VLM.
        
        Args:
            file_path: Path to the document (PDF or image)
            profile: Document profile for context
            
        Returns:
            ExtractedDocument with extracted content
        """
        start_time = time.time()
        
        logger.info(f"Starting VLM extraction for {file_path} using {self.provider}/{self.model}")
        
        # Try VLM extraction first
        try:
            if self._get_client():
                return self._extract_with_vlm(file_path, profile, start_time)
        except Exception as e:
            logger.warning(f"VLM extraction failed: {e}")
        
        # Fallback to layout-aware strategy
        logger.info("Falling back to layout-aware extraction")
        return self._fallback_extract(file_path, profile, start_time)
    
    def _extract_with_vlm(
        self,
        file_path: str,
        profile: DocumentProfile,
        start_time: float,
    ) -> ExtractedDocument:
        """Extract using VLM API (local or cloud)."""
        
        # Convert PDF to images if needed
        images = self._convert_to_images(file_path)
        
        if not images:
            logger.warning("No images generated, using fallback")
            return self._fallback_extract(file_path, profile, start_time)
        
        # Extract from each page image
        all_text_blocks = []
        all_tables = []
        all_figures = []
        
        extraction_prompt = """Analyze this document page and extract:
1. All text blocks with their content
2. Any tables (with headers and rows)
3. Any figures/images with captions

Return as JSON:
{
    "text_blocks": [{"text": "...", "bbox": [x0, y0, x1, y1]}],
    "tables": [{"headers": [...], "rows": [...]}],
    "figures": [{"caption": "...", "bbox": [x0, y0, x1, y1]}]
}

If no table is found, use "tables": [].
Respond ONLY with valid JSON."""

        for page_num, image in enumerate(images, 1):
            logger.info(f"Processing page {page_num}/{len(images)}")
            
            try:
                # Save temp image for VLM
                temp_img_path = f".refinery/temp_page_{page_num}.png"
                image.save(temp_img_path)
                
                if self.provider in ("ollama", "lmstudio"):
                    result = self._extract_with_ollama(temp_img_path, extraction_prompt)
                elif self.provider == "openai":
                    result = self._extract_with_openai(temp_img_path, extraction_prompt)
                elif self.provider == "google":
                    result = self._extract_with_google(temp_img_path, extraction_prompt)
                else:
                    result = {}
                
                # Parse result
                parsed = json.loads(result) if isinstance(result, str) else result
                
                # Convert to our format
                for block in parsed.get("text_blocks", []):
                    bbox = block.get("bbox", [0, 0, 100, 100])
                    all_text_blocks.append(TextBlock(
                        text=block.get("text", ""),
                        page=page_num,
                        bbox={"x0": bbox[0], "top": bbox[1], "x1": bbox[2], "bottom": bbox[3]}
                    ))
                
                for table in parsed.get("tables", []):
                    all_tables.append(TableData(
                        headers=table.get("headers", []),
                        rows=table.get("rows", []),
                        page=page_num,
                        bbox={"x0": 0, "top": 0, "x1": 100, "bottom": 100}
                    ))
                
                for fig in parsed.get("figures", []):
                    bbox = fig.get("bbox", [0, 0, 100, 100])
                    all_figures.append(FigureData(
                        caption=fig.get("caption", ""),
                        page=page_num,
                        bbox={"x0": bbox[0], "top": bbox[1], "x1": bbox[2], "bottom": bbox[3]}
                    ))
                
                # Clean up temp file
                Path(temp_img_path).unlink(missing_ok=True)
                
            except Exception as e:
                logger.warning(f"Failed to process page {page_num}: {e}")
        
        # Create ExtractedDocument
        processing_time = time.time() - start_time
        
        metadata = ExtractionMetadata(
            strategy_used=self.name,
            tool_version=f"{self.provider}/{self.model}",
            pages_processed=len(images),
            processing_time_seconds=processing_time,
            confidence_score=0.85,  # VLM typically has high confidence
        )
        
        return ExtractedDocument(
            doc_id=profile.doc_id,
            file_path=file_path,
            text_blocks=all_text_blocks,
            tables=all_tables,
            figures=all_figures,
            metadata=metadata,
        )
    
    def _extract_with_ollama(self, image_path: str, prompt: str) -> str:
        """Extract using Ollama or LM Studio."""
        client = self._get_client()
        
        if hasattr(client, 'extract_from_image'):
            return client.extract_from_image(image_path, prompt)
        else:
            # Direct API call
            import httpx
            
            # Encode image
            with open(image_path, "rb") as f:
                img_b64 = base64.b64encode(f.read()).decode("utf-8")
            
            client = httpx.Client(base_url=self.base_url, timeout=120)
            
            # Prepare message with image
            content = [
                {"type": "text", "text": prompt},
                {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{img_b64}"}}
            ]
            
            response = client.post("/api/chat", json={
                "model": self.model,
                "messages": [{"role": "user", "content": content}],
                "stream": False
            })
            
            return response.json().get("message", {}).get("content", "{}")
    
    def _extract_with_openai(self, image_path: str, prompt: str) -> str:
        """Extract using OpenAI GPT-4o."""
        client = self._get_client()
        
        # Encode image
        with open(image_path, "rb") as f:
            img_b64 = base64.b64encode(f.read()).decode("utf-8")
        
        response = client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{img_b64}"}}
                    ]
                }
            ],
            max_tokens=4096
        )
        
        return response.choices[0].message.content
    
    def _extract_with_google(self, image_path: str, prompt: str) -> str:
        """Extract using Google Gemini."""
        client = self._get_client()
        
        # Load image
        img = Image.open(image_path)
        
        model = client.GenerativeModel(self.model)
        response = model.generate_content([prompt, img])
        
        return response.text
    
    def _fallback_extract(
        self,
        file_path: str,
        profile: DocumentProfile,
        start_time: float,
    ) -> ExtractedDocument:
        """Fallback extraction using layout-aware strategy."""
        from src.strategies.layout_aware import LayoutAwareStrategy
        
        strategy = LayoutAwareStrategy()
        result = strategy.extract(file_path, profile)
        
        # Update metadata to reflect fallback
        result.metadata.strategy_used = self.name + "_fallback"
        result.metadata.tool_version = "layout_aware_fallback"
        
        return result
    
    def _convert_to_images(self, file_path: str) -> List[Image.Image]:
        """
        Convert PDF or image file to list of PIL Images.
        
        Args:
            file_path: Path to PDF or image file
            
        Returns:
            List of PIL Images, one per page
        """
        path = Path(file_path)
        images = []
        
        try:
            if path.suffix.lower() == ".pdf":
                # Convert PDF to images
                doc = fitz.open(file_path)
                for page_num in range(len(doc)):
                    page = doc[page_num]
                    # Render page to image
                    pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))  # 2x for better quality
                    img_data = pix.tobytes("png")
                    img = Image.open(io.BytesIO(img_data))
                    images.append(img)
                doc.close()
                
            else:
                # Single image file
                img = Image.open(file_path)
                # Convert to RGB if needed
                if img.mode != "RGB":
                    img = img.convert("RGB")
                images.append(img)
                
        except Exception as e:
            logger.error(f"Failed to convert {file_path} to images: {e}")
            
        return images
    
    def _encode_image(self, image_path: str) -> str:
        """Encode image to base64 for VLM API."""
        with open(image_path, "rb") as f:
            return base64.b64encode(f.read()).decode("utf-8")
    
    def _call_vlm(
        self,
        image_base64: str,
        prompt: str,
    ) -> str:
        """
        Call VLM API with image and prompt.
        
        Args:
            image_base64: Base64-encoded image
            prompt: Prompt for the VLM
            
        Returns:
            VLM response text
        """
        client = self._get_client()
        
        if self.provider == "openai":
            response = client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{image_base64}"
                                }
                            }
                        ]
                    }
                ]
            )
            return response.choices[0].message.content
        
        elif self.provider == "google":
            import google.generativeai as genai
            from PIL import Image
            import io
            
            img = Image.open(io.BytesIO(base64.b64decode(image_base64)))
            model = client.GenerativeModel(self.model)
            response = model.generate_content([prompt, img])
            return response.text
        
        return ""
    
    def _parse_vlm_response(self, response: str) -> ExtractedDocument:
        """Parse VLM response into ExtractedDocument."""
        try:
            data = json.loads(response)
            # Convert parsed JSON to ExtractedDocument
            # ... (implementation would parse and create objects)
            return None
        except json.JSONDecodeError:
            logger.error(f"Failed to parse VLM response: {response[:200]}")
            return None
