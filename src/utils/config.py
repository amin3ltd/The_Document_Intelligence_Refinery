"""Configuration management for the Document Intelligence Refinery."""

import os
from pathlib import Path
from typing import Any, Dict, Optional

import yaml


class Config:
    """
    Configuration manager for the Document Intelligence Refinery.
    
    Loads settings from environment variables and YAML configuration files.
    All tunable parameters are externalized - no hardcoded thresholds.
    """
    
    # Default configuration - all values can be overridden
    DEFAULT_CONFIG = {
        # Project paths
        "profiles_dir": ".refinery/profiles",
        "extraction_ledger_path": ".refinery/extraction_ledger/extraction_ledger.jsonl",
        "pageindex_dir": ".refinery/pageindex",
        
        # Triage thresholds - configurable for different document types
        "triage": {
            # Character density threshold for native digital detection
            # Higher values indicate native digital (extracted text is dense)
            "char_density_native_threshold": 0.001,
            
            # Minimum character count to consider a page has meaningful text
            "char_count_min": 100,
            
            # Image ratio threshold for scanned detection
            # Higher values indicate scanned documents (more image content)
            "image_ratio_scanned_threshold": 0.50,
            
            # Threshold for embedded fonts detection
            "embedded_fonts_threshold": 0.8,
            
            # Column detection - x-coordinate gap to detect multiple columns
            "column_gap_threshold": 50,
            
            # Table detection - minimum tables to consider table-heavy
            "table_count_threshold": 2,
            
            # Special document flags
            "flags": {
                "zero_text_threshold": 10,  # Max chars for zero-text document
                "form_fillable_detection": True,  # Enable form-fillable PDF detection
            }
        },
        
        # Extraction strategy thresholds
        "extraction": {
            "default_strategy": "strategy_a",
            
            # Confidence thresholds for escalation
            # Strategy A (Fast Text)
            "strategy_a": {
                "high_confidence": 0.85,      # No escalation needed
                "medium_confidence": 0.50,    # Consider escalation to B
                "escalate_to_b": True,        # Enable A->B escalation
            },
            
            # Strategy B (Layout-Aware)
            "strategy_b": {
                "high_confidence": 0.80,      # No escalation needed
                "escalate_to_c": True,        # Enable B->C escalation
            },
            
            # Strategy C (Vision)
            "strategy_c": {
                "high_confidence": 0.75,
            },
            
            # Budget accounting for Vision strategy
            "budget": {
                "enabled": True,
                "max_cost_per_document": 10.0,  # Maximum cost in USD
                "max_pages_per_document": 100,   # Maximum pages to process
                "degrade_on_overrun": True,      # Degrade to lower cost strategy if exceeded
            }
        },
        
        # Chunking settings
        "chunking": {
            "max_paragraph_size": 2000,
            "max_heading_size": 500,
            "min_chunk_size": 50,
        },
        
        # VLM settings
        "vlm": {
            "provider": "openai",
            "model": "gpt-4o",
            "temperature": 0.0,
        },
        
        # Safety limits for VLM extraction - all configurable from UI
        "safety_limits": {
            # Context and tokens
            "max_context_tokens": 4096,
            
            # Temperature bounds
            "temperature_min": 0.0,
            "temperature_max": 0.3,
            "temperature_default": 0.1,
            
            # Resource protection
            "max_memory_mb": 2048,
            "max_image_size_mb": 50,
            "max_pages_per_batch": 5,
            
            # Timeouts (seconds)
            "request_timeout": 120.0,
            "page_process_timeout": 60.0,
            "total_timeout": 600.0,
            
            # Retry configuration
            "max_retries": 3,
            "base_retry_delay": 1.0,
            "max_retry_delay": 30.0,
            "exponential_base": 2.0,
            
            # CPU protection
            "cpu_throttle_threshold": 80.0,
            "cpu_pause_threshold": 95.0,
            "health_check_interval": 5,
            
            # Document limits
            "max_pages_total": 500,
            "max_document_size_mb": 100,
        },
        
        # Domain keywords for classification - easily extendable
        "domains": {
            "financial": {
                "keywords": [
                    "revenue", "profit", "loss", "balance sheet", "income statement",
                    "cash flow", "assets", "liabilities", "equity", "ebitda", "eps"
                ],
                "weight": 1.0
            },
            "legal": {
                "keywords": [
                    "plaintiff", "defendant", "court", "judge", "contract",
                    "agreement", "whereas", "hereby", "pursuant", "clause"
                ],
                "weight": 1.0
            },
            "technical": {
                "keywords": [
                    "api", "architecture", "implementation", "algorithm",
                    "database", "server", "endpoint", "microservice"
                ],
                "weight": 1.0
            },
            "medical": {
                "keywords": [
                    "patient", "diagnosis", "treatment", "symptoms",
                    "medication", "clinical", "prescription"
                ],
                "weight": 1.0
            }
        },
        
        # Logging
        "logging": {
            "level": "INFO",
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        },
    }
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize the configuration."""
        self._config = self._deep_copy(self.DEFAULT_CONFIG)
        
        if config_path:
            self._load_from_file(config_path)
        
        self._load_from_environment()
    
    def _deep_copy(self, obj: Any) -> Any:
        """Deep copy a nested dictionary."""
        if isinstance(obj, dict):
            return {k: self._deep_copy(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self._deep_copy(item) for item in obj]
        return obj
    
    def _load_from_file(self, config_path: str) -> None:
        """Load configuration from YAML file."""
        path = Path(config_path)
        if path.exists():
            with open(path) as f:
                user_config = yaml.safe_load(f)
                if user_config:
                    self._merge_config(user_config)
    
    def _load_from_environment(self) -> None:
        """Load configuration from environment variables."""
        # Project paths
        if profiles_dir := os.getenv("REFINERY_PROFILES_DIR"):
            self._config["profiles_dir"] = profiles_dir
        
        if ledger_path := os.getenv("REFINERY_LEDGER_PATH"):
            self._config["extraction_ledger_path"] = ledger_path
        
        if pageindex_dir := os.getenv("REFINERY_PAGEINDEX_DIR"):
            self._config["pageindex_dir"] = pageindex_dir
        
        # Triage thresholds
        if char_density := os.getenv("REFINERY_CHAR_DENSITY_THRESHOLD"):
            self._config["triage"]["char_density_native_threshold"] = float(char_density)
        
        if image_ratio := os.getenv("REFINERY_IMAGE_RATIO_THRESHOLD"):
            self._config["triage"]["image_ratio_scanned_threshold"] = float(image_ratio)
        
        if char_count_min := os.getenv("REFINERY_CHAR_COUNT_MIN"):
            self._config["triage"]["char_count_min"] = int(char_count_min)
        
        # Extraction strategy
        if default_strategy := os.getenv("REFINERY_DEFAULT_STRATEGY"):
            self._config["extraction"]["default_strategy"] = default_strategy
        
        # Budget settings
        if max_cost := os.getenv("REFINERY_MAX_COST_PER_DOC"):
            self._config["extraction"]["budget"]["max_cost_per_document"] = float(max_cost)
        
        if max_pages := os.getenv("REFINERY_MAX_PAGES_PER_DOC"):
            self._config["extraction"]["budget"]["max_pages_per_document"] = int(max_pages)
        
        # VLM settings
        if vlm_provider := os.getenv("REFINERY_VLM_PROVIDER"):
            self._config["vlm"]["provider"] = vlm_provider
        
        if vlm_model := os.getenv("REFINERY_VLM_MODEL"):
            self._config["vlm"]["model"] = vlm_model
        
        if api_key := os.getenv("REFINERY_API_KEY"):
            self._config["vlm"]["api_key"] = api_key
        
        # Logging
        if log_level := os.getenv("REFINERY_LOG_LEVEL"):
            self._config["logging"]["level"] = log_level
    
    def _merge_config(self, user_config: Dict[str, Any]) -> None:
        """Merge user configuration with defaults."""
        for key, value in user_config.items():
            if isinstance(value, dict) and key in self._config and isinstance(self._config[key], dict):
                self._merge_nested(self._config[key], value)
            else:
                self._config[key] = value
    
    def _merge_nested(self, base: Dict[str, Any], override: Dict[str, Any]) -> None:
        """Recursively merge nested dictionaries."""
        for key, value in override.items():
            if isinstance(value, dict) and key in base and isinstance(base[key], dict):
                self._merge_nested(base[key], value)
            else:
                base[key] = value
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get a configuration value using dot notation."""
        keys = key.split(".")
        value = self._config
        
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
                if value is None:
                    return default
            else:
                return default
        
        return value
    
    def set(self, key: str, value: Any) -> None:
        """Set a configuration value using dot notation."""
        keys = key.split(".")
        config = self._config
        
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        config[keys[-1]] = value
    
    @property
    def profiles_dir(self) -> Path:
        """Get profiles directory path."""
        return Path(self.get("profiles_dir", ".refinery/profiles"))
    
    @property
    def extraction_ledger_path(self) -> Path:
        """Get extraction ledger path."""
        return Path(self.get("extraction_ledger_path", ".refinery/extraction_ledger/extraction_ledger.jsonl"))
    
    @property
    def pageindex_dir(self) -> Path:
        """Get pageindex directory path."""
        return Path(self.get("pageindex_dir", ".refinery/pageindex"))
    
    @property
    def triage_thresholds(self) -> Dict[str, Any]:
        """Get triage thresholds."""
        return self.get("triage", {})
    
    @property
    def extraction_config(self) -> Dict[str, Any]:
        """Get extraction configuration."""
        return self.get("extraction", {})
    
    @property
    def budget_config(self) -> Dict[str, Any]:
        """Get budget configuration for Vision strategy."""
        return self.get("extraction.budget", {})
    
    @property
    def safety_limits_config(self) -> Dict[str, Any]:
        """Get safety limits configuration - all configurable from UI."""
        return self.get("safety_limits", {})
    
    def get_safety_limit(self, key: str, default: Any = None) -> Any:
        """Get a specific safety limit value."""
        return self.get(f"safety_limits.{key}", default)
    
    def set_safety_limit(self, key: str, value: Any) -> None:
        """Set a specific safety limit value."""
        self.set(f"safety_limits.{key}", value)
    
    def update_safety_limits(self, limits: Dict[str, Any]) -> None:
        """Update multiple safety limits at once."""
        for key, value in limits.items():
            self.set(f"safety_limits.{key}", value)
    
    def get_strategy_thresholds(self, strategy: str) -> Dict[str, Any]:
        """Get thresholds for a specific extraction strategy."""
        return self.get(f"extraction.{strategy}", {})
    
    def get_domain_keywords(self, domain: str) -> Dict[str, Any]:
        """Get keywords for a specific domain."""
        return self.get(f"domains.{domain}", {})
    
    def add_domain(self, name: str, keywords: list, weight: float = 1.0) -> None:
        """Add a new domain for classification."""
        self.set(f"domains.{name}", {
            "keywords": keywords,
            "weight": weight
        })
    
    def ensure_directories(self) -> None:
        """Ensure all required directories exist."""
        self.profiles_dir.mkdir(parents=True, exist_ok=True)
        self.extraction_ledger_path.parent.mkdir(parents=True, exist_ok=True)
        self.pageindex_dir.mkdir(parents=True, exist_ok=True)
    
    def to_dict(self) -> Dict[str, Any]:
        """Export configuration as dictionary."""
        return self._deep_copy(self._config)
    
    def save(self, path: str) -> None:
        """Save configuration to YAML file."""
        with open(path, 'w') as f:
            yaml.dump(self._config, f, default_flow_style=False, sort_keys=True)


# Global configuration instance
_config: Optional[Config] = None


def get_config(config_path: Optional[str] = None) -> Config:
    """Get the global configuration instance."""
    global _config
    
    if _config is None:
        _config = Config(config_path)
    
    return _config


def load_rules() -> Dict[str, Any]:
    """Load extraction rules from the rules file."""
    rules_path = Path("rubric/extraction_rules.yaml")
    
    if rules_path.exists():
        with open(rules_path) as f:
            return yaml.safe_load(f)
    
    return {}


def reset_config() -> None:
    """Reset the global configuration instance."""
    global _config
    _config = None
