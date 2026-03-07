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
- CPU/Memory protection
- Request timeout and retry logic
- Circuit breaker pattern

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
from threading import Lock

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
from src.utils.system_check import get_health_checker

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


class CircuitBreakerState(str, Enum):
    """Circuit breaker states."""
    CLOSED = "closed"      # Normal operation
    OPEN = "open"         # Failing, reject requests
    HALF_OPEN = "half_open"  # Testing if service recovered


@dataclass
class CircuitBreaker:
    """Circuit breaker for failing services."""
    failure_threshold: int = 5      # Failures before opening
    success_threshold: int = 2      # Successes to close from half-open
    timeout_seconds: float = 30.0   # Time before trying half-open
    _failures: int = 0
    _successes: int = 0
    state: CircuitBreakerState = CircuitBreakerState.CLOSED
    _last_failure_time: float = 0
    _lock: Lock = field(default_factory=Lock)
    
    def record_success(self) -> None:
        """Record a successful call."""
        with self._lock:
            if self.state == CircuitBreakerState.HALF_OPEN:
                self._successes += 1
                if self._successes >= self.success_threshold:
                    self.state = CircuitBreakerState.CLOSED
                    self._failures = 0
                    self._successes = 0
                    logger.info("Circuit breaker closed")
            else:
                self._failures = 0
    
    def record_failure(self) -> None:
        """Record a failed call."""
        with self._lock:
            self._failures += 1
            self._last_failure_time = time.time()
            
            if self.state == CircuitBreakerState.HALF_OPEN:
                self.state = CircuitBreakerState.OPEN
                self._successes = 0
                logger.warning("Circuit breaker opened after half-open failure")
            elif self._failures >= self.failure_threshold:
                self.state = CircuitBreakerState.OPEN
                logger.warning(f"Circuit breaker opened after {self._failures} failures")
    
    def can_execute(self) -> bool:
        """Check if a request can be executed."""
        with self._lock:
            if self.state == CircuitBreakerState.CLOSED:
                return True
            
            if self.state == CircuitBreakerState.OPEN:
                # Check if timeout has passed
                if time.time() - self._last_failure_time >= self.timeout_seconds:
                    self.state = CircuitBreakerState.HALF_OPEN
                    self._successes = 0
                    logger.info("Circuit breaker half-open, testing...")
                    return True
                return False
            
            # Half-open - allow one request
            return True


@dataclass
class SafetyLimits:
    """Safety limits for VLM extraction."""
    max_context_tokens: int = 4096          # Maximum context window
    temperature_min: float = 0.0             # Minimum temperature
    temperature_max: float = 0.3             # Maximum temperature for extraction
    temperature_default: float = 0.1        # Default temperature
    
    # Resource protection
    max_memory_mb: int = 2048                # Max memory per document (MB)
    max_image_size_mb: int = 50              # Max image file size (MB)
    max_pages_per_batch: int = 5             # Pages to process per batch
    
    # Timeouts (seconds)
    request_timeout: float = 120.0           # VLM request timeout
    page_process_timeout: float = 60.0       # Per-page timeout
    total_timeout: float = 600.0             # Total extraction timeout
    
    # Retry configuration
    max_retries: int = 3                    # Max retry attempts
    base_retry_delay: float = 1.0            # Base delay between retries
    max_retry_delay: float = 30.0           # Max delay between retries
    exponential_base: float = 2.0           # Exponential backoff base
    
    # CPU protection
    cpu_throttle_threshold: float = 80.0    # CPU % to start throttling
    cpu_pause_threshold: float = 95.0      # CPU % to pause processing
    health_check_interval: int = 5          # Check health every N pages
    
    # Memory limits for documents
    max_pages_total: int = 500              # Absolute max pages
    max_document_size_mb: int = 100         # Max document size


def get_safe_temperature(temperature: Optional[float], limits: SafetyLimits) -> float:
    """Get a safe temperature value within bounds."""
    if temperature is None:
        return limits.temperature_default
    
    return max(limits.temperature_min, min(limits.temperature_max, temperature))


def calculate_retry_delay(attempt: int, limits: SafetyLimits) -> float:
    """Calculate exponential backoff delay."""
    delay = limits.base_retry_delay * (limits.exponential_base ** attempt)
    return min(delay, limits.max_retry_delay)


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
        safety_limits: Optional[SafetyLimits] = None,
    ):
        """
        Initialize the strategy.
        
        Args:
            provider: VLM provider (ollama, lmstudio, openai, google)
            model: Model name
            api_key: API key for the provider (optional for local)
            base_url: Base URL for local providers
            config_path: Path to configuration file
            safety_limits: Optional safety limits configuration
        """
        self.provider = provider
        self.model = model
        self.api_key = api_key
        self.base_url = base_url
        self.config = get_config(config_path)
        
        # Initialize safety limits - load from config if not provided
        if safety_limits is not None:
            self.safety_limits = safety_limits
        else:
            # Load from config - all configurable from UI
            limits_config = self.config.safety_limits_config
            self.safety_limits = SafetyLimits(
                max_context_tokens=limits_config.get("max_context_tokens", 4096),
                temperature_min=limits_config.get("temperature_min", 0.0),
                temperature_max=limits_config.get("temperature_max", 0.3),
                temperature_default=limits_config.get("temperature_default", 0.1),
                max_memory_mb=limits_config.get("max_memory_mb", 2048),
                max_image_size_mb=limits_config.get("max_image_size_mb", 50),
                max_pages_per_batch=limits_config.get("max_pages_per_batch", 5),
                request_timeout=limits_config.get("request_timeout", 120.0),
                page_process_timeout=limits_config.get("page_process_timeout", 60.0),
                total_timeout=limits_config.get("total_timeout", 600.0),
                max_retries=limits_config.get("max_retries", 3),
                base_retry_delay=limits_config.get("base_retry_delay", 1.0),
                max_retry_delay=limits_config.get("max_retry_delay", 30.0),
                exponential_base=limits_config.get("exponential_base", 2.0),
                cpu_throttle_threshold=limits_config.get("cpu_throttle_threshold", 80.0),
                cpu_pause_threshold=limits_config.get("cpu_pause_threshold", 95.0),
                health_check_interval=limits_config.get("health_check_interval", 5),
                max_pages_total=limits_config.get("max_pages_total", 500),
                max_document_size_mb=limits_config.get("max_document_size_mb", 100),
            )
        
        # Initialize circuit breaker for this provider
        self.circuit_breaker = CircuitBreaker(
            failure_threshold=5,
            success_threshold=2,
            timeout_seconds=30.0,
        )
        
        # Get health checker
        self._health_checker = get_health_checker()
        
        self._client = None
        self._budget: Optional[BudgetState] = None
        self._throttle_until: float = 0  # Timestamp to wait until
    
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
    
    def _check_system_health(self) -> Tuple[bool, Optional[str]]:
        """
        Check system health and return (ok, warning_message).
        
        Returns:
            Tuple of (system_ok, warning_message)
        """
        try:
            health = self._health_checker.check_system()
            
            # Check for critical resources
            for resource in health.resources:
                if resource.status == "critical":
                    return False, f"Critical {resource.name}: {resource.value:.1f}{resource.unit}"
                elif resource.status == "warning":
                    logger.warning(f"High {resource.name}: {resource.value:.1f}{resource.unit}")
            
            # Check for missing required packages
            missing = [p.name for p in health.required_packages if not p.installed]
            if missing:
                return False, f"Missing required packages: {missing}"
            
            return True, None
            
        except Exception as e:
            logger.warning(f"Health check failed: {e}")
            # Don't block on health check failures
            return True, None
    
    def _apply_cpu_throttle(self) -> None:
        """
        Apply CPU throttling if system is overloaded.
        Sleeps if CPU is above threshold.
        """
        if time.time() < self._throttle_until:
            # Currently throttling
            sleep_time = self._throttle_until - time.time()
            logger.info(f"Throttling for {sleep_time:.1f}s due to high CPU")
            time.sleep(min(sleep_time, 5.0))  # Cap sleep at 5 seconds
            return
        
        try:
            health = self._health_checker.check_system()
            
            for resource in health.resources:
                if resource.name == "cpu_percent" and resource.status != "ok":
                    if resource.value >= self.safety_limits.cpu_pause_threshold:
                        # High CPU - pause for longer
                        self._throttle_until = time.time() + 10.0
                        logger.warning(f"High CPU ({resource.value:.1f}%), pausing extraction")
                    elif resource.value >= self.safety_limits.cpu_throttle_threshold:
                        # Moderate CPU - throttle
                        self._throttle_until = time.time() + 2.0
                        logger.info(f"Elevated CPU ({resource.value:.1f}%), throttling")
        except Exception as e:
            logger.debug(f"CPU throttle check failed: {e}")
    
    def _wait_for_resources(self, timeout: float = 30.0) -> bool:
        """
        Wait for system resources to become available.
        
        Args:
            timeout: Maximum time to wait in seconds
            
        Returns:
            True if resources available, False if timeout
        """
        start = time.time()
        while time.time() - start < timeout:
            self._apply_cpu_throttle()
            
            ok, warning = self._check_system_health()
            if ok:
                return True
            
            time.sleep(1.0)
        
        logger.warning("Resource wait timeout")
        return False
    
    def extract(self, file_path: str, profile: DocumentProfile) -> ExtractedDocument:
        """
        Extract text using VLM with budget accounting and safety checks.
        
        Args:
            file_path: Path to the document (PDF or image)
            profile: Document profile for context
            
        Returns:
            ExtractedDocument with extracted content and budget metadata
        """
        start_time = time.time()
        
        # Safety check: Check total timeout
        if time.time() - start_time > self.safety_limits.total_timeout:
            logger.warning("Total extraction timeout exceeded, using fallback")
            return self._fallback_extract(file_path, profile, start_time)
        
        # Safety check: Check circuit breaker
        if not self.circuit_breaker.can_execute():
            logger.warning(f"Circuit breaker is {self.circuit_breaker.state.value}, falling back")
            return self._fallback_extract(file_path, profile, start_time)
        
        # Initialize budget tracking
        self._budget = self._init_budget(profile)
        
        # Apply safety limits to budget
        self._budget.max_pages = min(
            self._budget.max_pages,
            self.safety_limits.max_pages_total
        )
        
        logger.info(
            f"Starting VLM extraction for {file_path} using {self.provider}/{self.model} "
            f"(budget: ${self._budget.max_cost}, {self._budget.max_pages} pages)"
        )
        
        # Try VLM extraction with budget checks and safety
        try:
            if self._get_client():
                return self._extract_with_vlm(file_path, profile, start_time)
        except Exception as e:
            logger.warning(f"VLM extraction failed: {e}")
            self.circuit_breaker.record_failure()
        
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
            
            # Periodic health check
            if page_num % self.safety_limits.health_check_interval == 0:
                self._apply_cpu_throttle()
                ok, health_warning = self._check_system_health()
                if not ok:
                    logger.warning(f"Health check failed: {health_warning}")
                    # Try waiting for resources
                    if not self._wait_for_resources(timeout=30.0):
                        logger.warning("Resources not available, degrading")
                        break
            
            # Check total timeout
            if time.time() - start_time > self.safety_limits.total_timeout:
                logger.warning("Total timeout reached, stopping processing")
                break
            
            logger.info(f"Processing page {page_num}/{len(images)} (budget: ${self._budget.current_cost:.2f})")
            
            try:
                # Save temp image for VLM
                temp_img_path = f".refinery/temp_page_{page_num}.png"
                image.save(temp_img_path)
                
                # Extract with retry logic
                result = None
                last_error = None
                
                for attempt in range(self.safety_limits.max_retries):
                    try:
                        if self.provider in ("ollama", "lmstudio"):
                            result = self._extract_with_ollama(temp_img_path, extraction_prompt)
                        elif self.provider == "openai":
                            result = self._extract_with_openai(temp_img_path, extraction_prompt)
                        elif self.provider == "google":
                            result = self._extract_with_google(temp_img_path, extraction_prompt)
                        else:
                            result = {}
                        
                        # Success
                        if result:
                            break
                            
                    except Exception as e:
                        last_error = e
                        if attempt < self.safety_limits.max_retries - 1:
                            delay = calculate_retry_delay(attempt, self.safety_limits)
                            logger.warning(f"Page {page_num} attempt {attempt + 1} failed: {e}. Retrying in {delay:.1f}s")
                            time.sleep(delay)
                        else:
                            logger.error(f"Page {page_num} failed after {self.safety_limits.max_retries} attempts: {e}")
                
                if result is None:
                    # All retries failed
                    logger.warning(f"Failed to extract page {page_num} after retries")
                    self.circuit_breaker.record_failure()
                    # Continue to next page
                    Path(temp_img_path).unlink(missing_ok=True)
                    continue
                
                self.circuit_breaker.record_success()
                
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
        """Extract using Ollama or LM Studio with timeout and safety."""
        client = self._get_client()
        
        if hasattr(client, 'extract_from_image'):
            return client.extract_from_image(image_path, prompt)
        else:
            # Direct API call with timeout
            import httpx
            
            # Encode image
            with open(image_path, "rb") as f:
                img_b64 = base64.b64encode(f.read()).decode("utf-8")
            
            # Use safety limits for timeout
            timeout = self.safety_limits.request_timeout
            client = httpx.Client(base_url=self.base_url, timeout=timeout)
            
            # Get safe temperature
            temperature = get_safe_temperature(0.1, self.safety_limits)
            
            # Prepare message with image
            content = [
                {"type": "text", "text": prompt},
                {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{img_b64}"}}
            ]
            
            response = client.post("/api/chat", json={
                "model": self.model,
                "messages": [{"role": "user", "content": content}],
                "stream": False,
                "options": {
                    "temperature": temperature,
                }
            })
            
            return response.json().get("message", {}).get("content", "{}")
    
    def _extract_with_openai(self, image_path: str, prompt: str) -> str:
        """Extract using OpenAI GPT-4o with safety bounds."""
        import httpx
        
        # Check file size
        file_size = Path(image_path).stat().st_size / (1024 * 1024)  # MB
        if file_size > self.safety_limits.max_image_size_mb:
            raise ValueError(f"Image too large: {file_size:.1f}MB > {self.safety_limits.max_image_size_mb}MB")
        
        # Encode image
        with open(image_path, "rb") as f:
            img_b64 = base64.b64encode(f.read()).decode("utf-8")
        
        # Use safe temperature within bounds
        temperature = get_safe_temperature(0.1, self.safety_limits)
        
        # Use context limit
        max_tokens = min(self.safety_limits.max_context_tokens, 4096)
        
        client = self._get_client()
        
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
            max_tokens=max_tokens,
            temperature=temperature,
            timeout=self.safety_limits.request_timeout,
        )
        
        return response.choices[0].message.content
    
    def _extract_with_google(self, image_path: str, prompt: str) -> str:
        """Extract using Google Gemini with safety bounds."""
        client = self._get_client()
        
        # Check file size
        file_size = Path(image_path).stat().st_size / (1024 * 1024)  # MB
        if file_size > self.safety_limits.max_image_size_mb:
            raise ValueError(f"Image too large: {file_size:.1f}MB > {self.safety_limits.max_image_size_mb}MB")
        
        # Load image
        img = Image.open(image_path)
        
        # Use safe temperature
        temperature = get_safe_temperature(0.1, self.safety_limits)
        
        model = client.GenerativeModel(self.model)
        
        # Configure generation with safety settings
        generation_config = {
            "temperature": temperature,
            "max_output_tokens": min(self.safety_limits.max_context_tokens, 4096),
        }
        
        response = model.generate_content([prompt, img], generation_config=generation_config)
        
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
        Convert PDF or image file to list of PIL Images with memory protection.
        
        Args:
            file_path: Path to PDF or image file
            
        Returns:
            List of PIL Images, one per page
        """
        path = Path(file_path)
        images = []
        
        # Check file size
        file_size_mb = path.stat().st_size / (1024 * 1024)
        if file_size_mb > self.safety_limits.max_document_size_mb:
            logger.warning(f"Document too large: {file_size_mb:.1f}MB > {self.safety_limits.max_document_size_mb}MB")
            return []
        
        try:
            if path.suffix.lower() == ".pdf":
                # Convert PDF to images
                doc = fitz.open(file_path)
                total_pages = len(doc)
                
                # Check page count limit
                if total_pages > self.safety_limits.max_pages_total:
                    logger.warning(f"Too many pages: {total_pages} > {self.safety_limits.max_pages_total}")
                    doc.close()
                    return []
                
                for page_num in range(total_pages):
                    # Check memory before processing each page
                    if len(images) * 10 > self.safety_limits.max_memory_mb:  # Estimate ~10MB per image
                        logger.warning("Memory limit reached, truncating document")
                        break
                    
                    page = doc[page_num]
                    # Render page to image at 2x for quality, but check memory
                    pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))
                    img_data = pix.tobytes("png")
                    img = Image.open(io.BytesIO(img_data))
                    images.append(img)
                doc.close()
                
            else:
                # Single image file
                # Check image size
                img = Image.open(file_path)
                
                # Convert to RGB if needed
                if img.mode != "RGB":
                    img = img.convert("RGB")
                
                # Check dimensions
                width, height = img.size
                max_dim = 4096  # Max dimension to prevent huge images
                if width > max_dim or height > max_dim:
                    # Resize if too large
                    ratio = min(max_dim / width, max_dim / height)
                    new_size = (int(width * ratio), int(height * ratio))
                    img = img.resize(new_size, Image.LANCZOS)
                    logger.info(f"Resized image from {width}x{height} to {new_size[0]}x{new_size[1]}")
                
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
    
    def get_safety_status(self) -> Dict[str, any]:
        """Get current safety status including circuit breaker and health."""
        health = self._health_checker.check_system()
        
        return {
            "circuit_breaker": {
                "state": self.circuit_breaker.state.value,
                "failures": self.circuit_breaker._failures,
            },
            "safety_limits": {
                "max_context_tokens": self.safety_limits.max_context_tokens,
                "temperature_range": [
                    self.safety_limits.temperature_min,
                    self.safety_limits.temperature_max,
                ],
                "request_timeout": self.safety_limits.request_timeout,
                "max_retries": self.safety_limits.max_retries,
            },
            "system_health": health.get_summary(),
            "throttle_active": time.time() < self._throttle_until,
        }
    
    def reset_circuit_breaker(self) -> None:
        """Manually reset the circuit breaker."""
        self.circuit_breaker = CircuitBreaker()
        logger.info("Circuit breaker manually reset")
