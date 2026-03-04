"""
Strategy C: Vision-Augmented Extraction using VLM with Budget Accounting.

This strategy uses Vision Language Models (GPT-4o, Gemini, local VLMs via Ollama/LM Studio)
for scanned images, handwriting, and complex visual documents.
Highest cost but best quality for difficult documents.

Features:
- Per-document budget accounting
- Hard caps that halt or degrade processing
- Confidence metadata attachment
- Table/figure preservation

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
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from enum import Enum

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
from src.utils.config import get_config

logger = logging.getLogger(__name__)


class BudgetStatus(str, Enum):
    """Status of budget accounting."""
    WITHIN_BUDGET = "within_budget"
    COST_EXCEEDED = "cost_exceeded"
    PAGES_EXCEEDED = "pages_exceeded"
    DEGRADED = "degraded"


@dataclass
class BudgetState:
    """Tracks budget consumption for a document extraction."""
    max_cost: float = 10.0  # Maximum cost in USD
    max_pages: int = 100    # Maximum pages to process
    current_cost: float = 0.0
    pages_processed: int = 0
    degrade_on_overrun: bool = True
    status: BudgetStatus = BudgetStatus.WITHIN_BUDGET
    warnings: List[str] = field(default_factory=list)
    
    def can_process_page(self, estimated_cost_per_page: float = 0.10) -> Tuple[bool, Optional[str]]:
        """Check if we can process another page within budget."""
        if self.pages_processed >= self.max_pages:
            self.status = BudgetStatus.PAGES_EXCEEDED
            return False, f"Page limit exceeded ({self.max_pages})"
        
        projected_cost = self.current_cost + estimated_cost_per_page
        if projected_cost > self.max_cost:
            if self.degrade_on_overrun:
                self.status = BudgetStatus.DEGRADED
                return True, "Budget exceeded, degrading to lower-cost strategy"
            else:
                self.status = BudgetStatus.COST_EXCEEDED
                return False, f"Cost limit exceeded (${self.max_cost})"
        
        return True, None
    
    def record_page_cost(self, cost: float) -> None:
        """Record the cost of processing a page."""
        self.current_cost += cost
        self.pages_processed += 1
    
    def get_remaining_budget(self) -> Dict[str, float]:
        """Get remaining budget information."""
        return {
            "remaining_cost": max(0, self.max_cost - self.current_cost),
            "remaining_pages": max(0, self.max_pages - self.pages_processed),
            "cost_percentage": (self.current_cost / self.max_cost) * 100 if self.max_cost > 0 else 0,
            "pages_percentage": (self.pages_processed / self.max_pages) * 100 if self.max_pages > 0 else 0,
        }


class VisionStrategy:
    """
    Vision-augmented extraction using VLM with budget accounting.
    
    Best for: Scanned images, handwriting, complex visuals
    Cost: High (~$0.10-0.50/page) for API, Free for local
    Quality: Highest for difficult documents
    
    Supported providers:
    - "ollama": Local VLM via Ollama (free)
    - "lmstudio": Local VLM via LM Studio (free)
    - "openai": OpenAI GPT-4o (paid)
    - "google": Google Gemini (paid)
    
    Budget Features:
    - Tracks per-document cost
    - Enforces hard caps on cost and pages
    - Degrades to lower-cost strategy when budget exceeded
    """
    
    # Cost estimates per page (USD)
    COST_ESTIMATES = {
        "openai": 0.15,      # GPT-4o ~$0.15 per page
        "google": 0.10,      # Gemini ~$0.10 per page
        "ollama": 0.0,       # Local - free
        "lmstudio": 0.0,     # Local - free
    }
    
    @property
    def name(self) -> str:
        return "strategy_c"
    
    def __init__(
        self,
        provider: str = "ollama",
        model: str = "llava",
        api_key: Optional[str] = None,
        base_url: str = "http://localhost:11434",
        config_path: Optional[str] = None,
    ):
        """
        Initialize the strategy.
        
        Args:
            provider: VLM provider (ollama, lmstudio, openai, google)
            model: Model name
            api_key: API key for the provider (optional for local)
            base_url: Base URL for local providers
            config_path: Path to configuration file
        """
        self.provider = provider
        self.model = model
        self.api_key = api_key
        self.base_url = base_url
        self.config = get_config(config_path)
        self._client = None
        self._budget: Optional[BudgetState] = None
    
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
    
    def _init_budget(self, profile: DocumentProfile) -> BudgetState:
        """Initialize budget tracking from config."""
        budget_config = self.config.budget_config
        
        return BudgetState(
            max_cost=budget_config.get("max_cost_per_document", 10.0),
            max_pages=min(
                budget_config.get("max_pages_per_document", 100),
                profile.page_count  # Can't exceed actual page count
            ),
            degrade_on_overrun=budget_config.get("degrade_on_overrun", True),
        )
    
    def extract(self, file_path: str, profile: DocumentProfile) -> ExtractedDocument:
        """
        Extract text using VLM with budget accounting.
        
        Args:
            file_path: Path to the document (PDF or image)
            profile: Document profile for context
            
        Returns:
            ExtractedDocument with extracted content and budget metadata
        """
        start_time = time.time()
        
        # Initialize budget tracking
        self._budget = self._init_budget(profile)
        
        logger.info(
            f"Starting VLM extraction for {file_path} using {self.provider}/{self.model} "
            f"(budget: ${self._budget.max_cost}, {self._budget.max_pages} pages)"
        )
        
        # Try VLM extraction with budget checks
        try:
            if self._get_client():
                return self._extract_with_vlm(file_path, profile, start_time)
        except Exception as e:
            logger.warning(f"VLM extraction failed: {e}")
        
        # Fallback to layout-aware strategy
        logger.info("Falling back to layout-aware extraction")
        return self._fallback_extract(file_path, profile, start_time)
    
    def get_confidence(self, result: ExtractedDocument) -> float:
        """Get confidence score from extraction result."""
        return result.metadata.confidence_score
    
    def _extract_with_vlm(
        self,
        file_path: str,
        profile: DocumentProfile,
        start_time: float,
    ) -> ExtractedDocument:
        """Extract using VLM API (local or cloud) with budget accounting."""
        
        # Convert PDF to images if needed
        images = self._convert_to_images(file_path)
        
        if not images:
            logger.warning("No images generated, using fallback")
            return self._fallback_extract(file_path, profile, start_time)
        
        # Check if we can process all pages within budget
        cost_per_page = self.COST_ESTIMATES.get(self.provider, 0.10)
        can_process_all = True
        
        for i in range(len(images)):
            can_process, warning = self._budget.can_process_page(cost_per_page)
            if not can_process:
                logger.warning(f"Budget check failed for page {i+1}: {warning}")
                can_process_all = False
                break
        
        # If we can't process all pages and degradation is enabled
        if not can_process_all and self._budget.degrade_on_overrun:
            logger.warning("Budget exceeded, degrading to layout-aware strategy")
            return self._fallback_extract(file_path, profile, start_time)
        
        # Extract from each page image
        all_text_blocks = []
        all_tables = []
        all_figures = []
        pages_processed = 0
        
        extraction_prompt = """Analyze this document page and extract:
1. All text blocks with their content and bounding boxes
2. Any tables (with headers and rows)
3. Any figures/images with captions
4. Preserve reading order

Return as JSON:
{
    "text_blocks": [{"text": "...", "bbox": [x0, y0, x1, y1], "reading_order": 1}],
    "tables": [{"headers": [...], "rows": [...], "bbox": [x0, y0, x1, y1]}],
    "figures": [{"caption": "...", "bbox": [x0, y0, x1, y1]}],
    "confidence": 0.95
}

If no table is found, use "tables": [].
Respond ONLY with valid JSON."""

        for page_num, image in enumerate(images, 1):
            # Check budget before processing
            can_process, warning = self._budget.can_process_page(cost_per_page)
            if not can_process:
                if self._budget.degrade_on_overrun:
                    logger.warning(f"Budget exceeded at page {page_num}, degrading")
                    # Process remaining pages with fallback
                    break
                else:
                    logger.error(f"Budget exceeded, halting at page {page_num}")
                    break
            
            logger.info(f"Processing page {page_num}/{len(images)} (budget: ${self._budget.current_cost:.2f})")
            
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
                
                # Convert to our format with reading order preservation
                reading_order = 1
                for block in sorted(parsed.get("text_blocks", []), 
                                   key=lambda x: x.get("reading_order", 0) or x.get("bbox", [0,0,0,0])[1]):
                    bbox = block.get("bbox", [0, 0, 100, 100])
                    all_text_blocks.append(TextBlock(
                        text=block.get("text", ""),
                        page=page_num,
                        bbox={"x0": bbox[0], "top": bbox[1], "x1": bbox[2], "bottom": bbox[3]},
                        reading_order=reading_order
                    ))
                    reading_order += 1
                
                for table in parsed.get("tables", []):
                    bbox = table.get("bbox", [0, 0, 100, 100])
                    all_tables.append(TableData(
                        headers=table.get("headers", []),
                        rows=table.get("rows", []),
                        page=page_num,
                        bbox={"x0": bbox[0], "top": bbox[1], "x1": bbox[2], "bottom": bbox[3]}
                    ))
                
                for fig in parsed.get("figures", []):
                    bbox = fig.get("bbox", [0, 0, 100, 100])
                    all_figures.append(FigureData(
                        caption=fig.get("caption", ""),
                        page=page_num,
                        bbox={"x0": bbox[0], "top": bbox[1], "x1": bbox[2], "bottom": bbox[3]}
                    ))
                
                # Record cost and increment counter
                self._budget.record_page_cost(cost_per_page)
                pages_processed += 1
                
                # Clean up temp file
                Path(temp_img_path).unlink(missing_ok=True)
                
            except Exception as e:
                logger.warning(f"Failed to process page {page_num}: {e}")
        
        # Create ExtractedDocument with budget metadata
        processing_time = time.time() - start_time
        
        # Calculate average confidence
        avg_confidence = 0.85  # Default VLM confidence
        if pages_processed > 0:
            budget_remaining = self._budget.get_remaining_budget()
            # Adjust confidence based on budget status
            if self._budget.status == BudgetStatus.DEGRADED:
                avg_confidence = 0.70  # Lower confidence when degraded
            elif budget_remaining["cost_percentage"] > 80:
                avg_confidence = 0.80  # Lower confidence when budget nearly exhausted
        
        metadata = ExtractionMetadata(
            strategy_used=self.name,
            tool_version=f"{self.provider}/{self.model}",
            pages_processed=pages_processed,
            total_pages=len(images),
            processing_time_seconds=processing_time,
            confidence_score=avg_confidence,
            budget_consumed=self._budget.current_cost,
            budget_status=self._budget.status.value,
            budget_warnings=self._budget.warnings,
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
        result.metadata.strategy_used = self.name + "_degraded"
        result.metadata.tool_version = "layout_aware_fallback"
        result.metadata.budget_status = "degraded_due_to_budget"
        
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
    
    def get_budget_summary(self) -> Optional[Dict[str, any]]:
        """Get budget summary if extraction has occurred."""
        if self._budget is None:
            return None
        
        return {
            "status": self._budget.status.value,
            "current_cost": self._budget.current_cost,
            "pages_processed": self._budget.pages_processed,
            "remaining": self._budget.get_remaining_budget(),
            "warnings": self._budget.warnings,
        }
