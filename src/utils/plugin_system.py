"""Plugin system for extensible document processing.

This module provides a plugin architecture for:
- Custom OCR backends
- Document validators
- Post-processors
- Document extractors

Based on a modular architecture that allows runtime extension.
"""

from abc import ABC, abstractmethod
from enum import Enum
from pydantic import BaseModel, Field
from typing import Any, Dict, List, Optional, Type
import importlib
import logging

logger = logging.getLogger(__name__)


class PluginType(str, Enum):
    """Types of plugins available in the system."""
    OCR_BACKEND = "ocr_backend"
    VALIDATOR = "validator"
    POST_PROCESSOR = "post_processor"
    DOCUMENT_EXTRACTOR = "document_extractor"


class PluginMetadata(BaseModel):
    """Metadata for a plugin."""
    name: str = Field(..., description="Plugin unique name")
    version: str = Field(..., description="Plugin semantic version")
    description: str = Field(default="", description="Plugin description")
    author: str = Field(default="", description="Plugin author")
    plugin_type: PluginType = Field(..., description="Type of plugin")
    dependencies: List[str] = Field(default_factory=list, description="Required dependencies")


class Plugin(ABC):
    """Base plugin interface.
    
    All plugins must implement this interface for lifecycle management.
    """
    
    @property
    @abstractmethod
    def metadata(self) -> PluginMetadata:
        """Return plugin metadata."""
        pass
    
    @abstractmethod
    def initialize(self) -> None:
        """Initialize the plugin.
        
        Called once when the plugin is registered.
        Use to load configuration, validate dependencies, etc.
        """
        pass
    
    @abstractmethod
    def shutdown(self) -> None:
        """Shutdown the plugin.
        
        Called when the plugin is being unregistered.
        Use to close connections, flush caches, etc.
        """
        pass
    
    def validate(self) -> bool:
        """Validate plugin configuration.
        
        Returns True if valid, False otherwise.
        Override to add validation logic.
        """
        return True


class PluginRegistry:
    """Central registry for all plugins.
    
    Manages plugin registration, lookup, and lifecycle.
    """
    
    def __init__(self):
        self._plugins: Dict[str, Plugin] = {}
        self._plugin_metadata: Dict[str, PluginMetadata] = {}
        self._initialized: bool = False
    
    def register(self, plugin: Plugin) -> None:
        """Register a plugin.
        
        Args:
            plugin: Plugin instance to register
            
        Raises:
            ValueError: If plugin with same name already exists
        """
        metadata = plugin.metadata
        if metadata.name in self._plugins:
            raise ValueError(f"Plugin '{metadata.name}' already registered")
        
        self._plugins[metadata.name] = plugin
        self._plugin_metadata[metadata.name] = metadata
        logger.info(f"Registered plugin: {metadata.name} v{metadata.version}")
    
    def unregister(self, name: str) -> None:
        """Unregister a plugin.
        
        Args:
            name: Plugin name to unregister
        """
        if name in self._plugins:
            plugin = self._plugins[name]
            plugin.shutdown()
            del self._plugins[name]
            del self._plugin_metadata[name]
            logger.info(f"Unregistered plugin: {name}")
    
    def get(self, name: str) -> Optional[Plugin]:
        """Get a plugin by name.
        
        Args:
            name: Plugin name
            
        Returns:
            Plugin instance or None if not found
        """
        return self._plugins.get(name)
    
    def get_by_type(self, plugin_type: PluginType) -> List[Plugin]:
        """Get all plugins of a specific type.
        
        Args:
            plugin_type: Type of plugin to retrieve
            
        Returns:
            List of plugins matching the type
        """
        return [
            plugin for plugin in self._plugins.values()
            if plugin.metadata.plugin_type == plugin_type
        ]
    
    def list_plugins(self) -> List[PluginMetadata]:
        """List all registered plugins.
        
        Returns:
            List of plugin metadata
        """
        return list(self._plugin_metadata.values())
    
    def initialize_all(self) -> None:
        """Initialize all registered plugins."""
        for plugin in self._plugins.values():
            try:
                plugin.initialize()
            except Exception as e:
                logger.error(f"Failed to initialize plugin {plugin.metadata.name}: {e}")
                raise
        self._initialized = True
        logger.info(f"Initialized {len(self._plugins)} plugins")
    
    def shutdown_all(self) -> None:
        """Shutdown all registered plugins."""
        for name, plugin in self._plugins.items():
            try:
                plugin.shutdown()
            except Exception as e:
                logger.error(f"Error shutting down plugin {name}: {e}")
        self._initialized = False
        logger.info("Shutdown all plugins")
    
    @property
    def is_initialized(self) -> bool:
        """Check if all plugins are initialized."""
        return self._initialized


# Global registry instance
_global_registry: Optional[PluginRegistry] = None


def get_registry() -> PluginRegistry:
    """Get the global plugin registry.
    
    Returns:
        Global PluginRegistry instance
    """
    global _global_registry
    if _global_registry is None:
        _global_registry = PluginRegistry()
    return _global_registry


def register_plugin(plugin: Plugin) -> None:
    """Register a plugin in the global registry.
    
    Args:
        plugin: Plugin instance to register
    """
    get_registry().register(plugin)


def load_plugins_from_module(module_name: str) -> List[Plugin]:
    """Load all Plugin subclasses from a module.
    
    Args:
        module_name: Python module to load plugins from
        
    Returns:
        List of discovered plugin instances
    """
    plugins = []
    try:
        module = importlib.import_module(module_name)
        
        for attr_name in dir(module):
            attr = getattr(module, attr_name)
            if (isinstance(attr, type) and 
                issubclass(attr, Plugin) and 
                attr is not Plugin):
                plugins.append(attr())
        
        logger.info(f"Loaded {len(plugins)} plugins from {module_name}")
    except ImportError as e:
        logger.warning(f"Failed to load module {module_name}: {e}")
    
    return plugins
