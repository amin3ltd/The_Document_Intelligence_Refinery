"""
Configuration management for the Document Intelligence Refinery.
"""

import os
from pathlib import Path
from typing import Any, Dict, Optional

import yaml


class Config:
    """
    Configuration manager for the Document Intelligence Refinery.
    
    Loads settings from environment variables and YAML configuration files.
    """
    
    # Default configuration
    DEFAULT_CONFIG = {
        # Project paths
        "profiles_dir": ".refinery/profiles",
        "extraction_ledger_path": ".refinery/extraction_ledger/extraction_ledger.jsonl",
        "pageindex_dir": ".refinery/pageindex",
        
        # Extraction settings
        "extraction": {
            "default_strategy": "strategy_a",
            "confidence_thresholds": {
                "strategy_a": {"high": 0.85, "medium": 0.50},
                "strategy_b": {"high": 0.80},
                "strategy_c": {"high": 0.75},
            },
        },
        
        # Triage settings
        "triage": {
            "char_density_threshold": 0.001,
            "char_count_min": 100,
            "image_ratio_threshold": 0.50,
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
        
        # Logging
        "logging": {
            "level": "INFO",
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        },
    }
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize the configuration."""
        self._config = self.DEFAULT_CONFIG.copy()
        
        if config_path:
            self._load_from_file(config_path)
        
        self._load_from_environment()
    
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
        
        # Extraction settings
        if default_strategy := os.getenv("REFINERY_DEFAULT_STRATEGY"):
            self._config["extraction"]["default_strategy"] = default_strategy
        
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
            if isinstance(value, dict) and key in self._config:
                self._config[key].update(value)
            else:
                self._config[key] = value
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get a configuration value."""
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
        """Set a configuration value."""
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
    
    def ensure_directories(self) -> None:
        """Ensure all required directories exist."""
        self.profiles_dir.mkdir(parents=True, exist_ok=True)
        self.extraction_ledger_path.parent.mkdir(parents=True, exist_ok=True)
        self.pageindex_dir.mkdir(parents=True, exist_ok=True)


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
