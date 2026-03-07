"""
System Health Checker for Document Intelligence Refinery.

Checks for:
- Required Python packages
- Optional tools (Ollama, LM Studio, Rust toolchain)
- System resources (RAM, CPU, disk space)

Provides installation instructions for missing dependencies.
"""

import logging
import shutil
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


@dataclass
class SystemResource:
    """System resource information."""
    name: str
    value: float
    unit: str
    status: str  # "ok", "warning", "critical"
    threshold: float


@dataclass
class ToolCheck:
    """Result of checking a tool/package."""
    name: str
    installed: bool
    version: Optional[str] = None
    error: Optional[str] = None
    install_instructions: Optional[str] = None


@dataclass
class SystemHealthReport:
    """Complete system health report."""
    healthy: bool
    python_version: str
    required_packages: List[ToolCheck] = field(default_factory=list)
    optional_tools: List[ToolCheck] = field(default_factory=list)
    resources: List[SystemResource] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    
    def get_summary(self) -> Dict:
        """Get a summary dictionary for API responses."""
        return {
            "healthy": self.healthy,
            "python_version": self.python_version,
            "required_packages": {
                p.name: {
                    "installed": p.installed,
                    "version": p.version,
                    "error": p.error,
                }
                for p in self.required_packages
            },
            "optional_tools": {
                t.name: {
                    "installed": t.installed,
                    "version": t.version,
                    "error": t.error,
                }
                for t in self.optional_tools
            },
            "resources": {
                r.name: {
                    "value": r.value,
                    "unit": r.unit,
                    "status": r.status,
                }
                for r in self.resources
            },
            "warnings": self.warnings,
            "errors": self.errors,
            "missing_tools": [
                p.name for p in self.required_packages if not p.installed
            ],
            "install_instructions": self._get_install_instructions(),
        }
    
    def _get_install_instructions(self) -> Dict[str, str]:
        """Generate installation instructions for missing tools."""
        instructions = {}
        
        for pkg in self.required_packages:
            if not pkg.installed and pkg.install_instructions:
                instructions[pkg.name] = pkg.install_instructions
        
        for tool in self.optional_tools:
            if not tool.installed and tool.install_instructions:
                instructions[tool.name] = tool.install_instructions
        
        return instructions


class SystemHealthChecker:
    """
    System health checker for Document Intelligence Refinery.
    
    Checks:
    - Required Python packages
    - Optional tools (Ollama, LM Studio, Rust)
    - System resources (CPU, RAM, disk)
    """
    
    # Required Python packages with their import names and install instructions
    REQUIRED_PACKAGES = {
        "pdfplumber": {
            "import_name": "pdfplumber",
            "install": "pip install pdfplumber",
            "description": "PDF text extraction",
        },
        "fitz": {
            "import_name": "fitz",
            "install": "pip install PyMuPDF",
            "description": "PDF processing (PyMuPDF)",
        },
        "PIL": {
            "import_name": "PIL",
            "install": "pip install Pillow",
            "description": "Image processing",
        },
        "numpy": {
            "import_name": "numpy",
            "install": "pip install numpy",
            "description": "Numerical computing",
        },
        "yaml": {
            "import_name": "yaml",
            "install": "pip install PyYAML",
            "description": "YAML configuration",
        },
    }
    
    # Optional tools with their check commands
    OPTIONAL_TOOLS = {
        "ollama": {
            "check": "ollama --version",
            "install": "Visit https://ollama.ai to download and install",
            "description": "Local VLM provider",
        },
        "lm_studio": {
            "check": None,  # Check via port
            "check_port": 1234,
            "install": "Visit https://lmstudio.ai to download and install",
            "description": "Local VLM provider (run app and load a model)",
        },
        "rust": {
            "check": "rustc --version",
            "install": "curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh",
            "description": "Rust toolchain for fast text extraction",
        },
        "tesseract": {
            "check": "tesseract --version",
            "install": "Install Tesseract OCR from https://github.com/UB-Mannheim/tesseract/wiki",
            "description": "OCR for scanned documents",
        },
    }
    
    # Resource thresholds
    RESOURCE_THRESHOLDS = {
        "cpu_percent_warning": 80.0,
        "cpu_percent_critical": 95.0,
        "memory_percent_warning": 80.0,
        "memory_percent_critical": 95.0,
        "disk_percent_warning": 85.0,
        "disk_percent_critical": 95.0,
        "memory_min_gb": 2.0,  # Minimum required memory in GB
    }
    
    def __init__(self):
        """Initialize the system health checker."""
        self._psutil_available = False
        self._try_import_psutil()
    
    def _try_import_psutil(self) -> None:
        """Try to import psutil for system monitoring."""
        try:
            import psutil
            self._psutil = psutil
            self._psutil_available = True
            logger.debug("psutil is available for system monitoring")
        except ImportError:
            logger.warning("psutil not available - system resource monitoring will be limited")
            self._psutil = None
    
    def check_system(self) -> SystemHealthReport:
        """
        Perform complete system health check.
        
        Returns:
            SystemHealthReport with all check results
        """
        # Check Python version
        python_version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
        
        report = SystemHealthReport(healthy=True, python_version=python_version)
        
        # Check required packages
        report.required_packages = self._check_required_packages()
        
        # Check optional tools
        report.optional_tools = self._check_optional_tools()
        
        # Check system resources
        report.resources = self._check_system_resources()
        
        # Determine overall health
        missing_required = [p for p in report.required_packages if not p.installed]
        critical_resources = [r for r in report.resources if r.status == "critical"]
        
        if missing_required:
            report.healthy = False
            report.errors.append(f"Missing required packages: {[p.name for p in missing_required]}")
        
        if critical_resources:
            report.healthy = False
            report.errors.append(f"Critical resource levels: {[r.name for r in critical_resources]}")
        
        # Add warnings
        warning_resources = [r for r in report.resources if r.status == "warning"]
        for r in warning_resources:
            report.warnings.append(f"High {r.name}: {r.value:.1f}{r.unit}")
        
        return report
    
    def _check_required_packages(self) -> List[ToolCheck]:
        """Check if required Python packages are installed."""
        results = []
        
        for pkg_name, pkg_info in self.REQUIRED_PACKAGES.items():
            check = ToolCheck(name=pkg_name, installed=False)
            
            try:
                # Try to import the package
                module = __import__(pkg_info["import_name"])
                check.installed = True
                
                # Try to get version
                if hasattr(module, "__version__"):
                    check.version = module.__version__
                elif hasattr(module, "VERSION"):
                    check.version = str(module.VERSION)
                elif hasattr(module, "version"):
                    check.version = str(module.version)
                
            except ImportError as e:
                check.installed = False
                check.error = str(e)
                check.install_instructions = f"{pkg_info['install']}  # {pkg_info['description']}"
            
            results.append(check)
        
        return results
    
    def _check_optional_tools(self) -> List[ToolCheck]:
        """Check if optional tools are available."""
        results = []
        
        # Get configured VLM provider from config
        try:
            from src.utils.config import get_config
            config = get_config()
            vlm_provider = config.get("vlm.provider", "lmstudio")  # Default to lmstudio
        except Exception:
            vlm_provider = "lmstudio"  # Default if config fails
        
        for tool_name, tool_info in self.OPTIONAL_TOOLS.items():
            # Skip VLM providers that aren't the configured one
            if tool_name in ("ollama", "lm_studio") and tool_name.replace("_", "") != vlm_provider:
                # Skip checking other VLM providers
                continue
            
            check = ToolCheck(name=tool_name, installed=False)
            
            # Check via command if specified
            if tool_info.get("check"):
                try:
                    result = subprocess.run(
                        tool_info["check"],
                        shell=True,
                        capture_output=True,
                        text=True,
                        timeout=5,
                    )
                    
                    if result.returncode == 0:
                        check.installed = True
                        # Extract version from output
                        output = result.stdout.strip()
                        if output:
                            check.version = output.split('\n')[0]
                    else:
                        check.installed = False
                        check.error = "Command failed"
                        check.install_instructions = f"{tool_info['install']}  # {tool_info['description']}"
                
                except subprocess.TimeoutExpired:
                    check.installed = False
                    check.error = "Command timed out"
                    check.install_instructions = f"{tool_info['install']}  # {tool_info['description']}"
                except FileNotFoundError:
                    check.installed = False
                    check.error = "Command not found"
                    check.install_instructions = f"{tool_info['install']}  # {tool_info['description']}"
                except Exception as e:
                    check.installed = False
                    check.error = str(e)
                    check.install_instructions = f"{tool_info['install']}  # {tool_info['description']}"
            
            # Check via port if specified
            elif tool_info.get("check_port"):
                check.installed = self._check_port(tool_info["check_port"])
                if not check.installed:
                    check.error = f"Port {tool_info['check_port']} not reachable"
                    check.install_instructions = f"{tool_info['install']}  # {tool_info['description']}"
            
            results.append(check)
        
        return results
    
    def _check_port(self, port: int) -> bool:
        """Check if a port is listening."""
        import socket
        
        try:
            with socket.create_connection(("localhost", port), timeout=2):
                return True
        except (socket.timeout, ConnectionRefusedError, OSError):
            return False
    
    def _check_system_resources(self) -> List[SystemResource]:
        """Check system resources (CPU, memory, disk)."""
        resources = []
        
        if not self._psutil_available:
            # Add placeholder when psutil not available
            resources.append(SystemResource(
                name="psutil",
                value=0,
                unit="",
                status="warning",
                threshold=1,
            ))
            return resources
        
        # CPU usage
        try:
            cpu_percent = self._psutil.cpu_percent(interval=1)
            cpu_status = "ok"
            if cpu_percent >= self.RESOURCE_THRESHOLDS["cpu_percent_critical"]:
                cpu_status = "critical"
            elif cpu_percent >= self.RESOURCE_THRESHOLDS["cpu_percent_warning"]:
                cpu_status = "warning"
            
            resources.append(SystemResource(
                name="cpu_percent",
                value=cpu_percent,
                unit="%",
                status=cpu_status,
                threshold=self.RESOURCE_THRESHOLDS["cpu_percent_warning"],
            ))
        except Exception as e:
            logger.warning(f"Failed to check CPU: {e}")
        
        # Memory usage
        try:
            mem = self._psutil.virtual_memory()
            mem_percent = mem.percent
            
            mem_status = "ok"
            if mem_percent >= self.RESOURCE_THRESHOLDS["memory_percent_critical"]:
                mem_status = "critical"
            elif mem_percent >= self.RESOURCE_THRESHOLDS["memory_percent_warning"]:
                mem_status = "warning"
            
            resources.append(SystemResource(
                name="memory_percent",
                value=mem_percent,
                unit="%",
                status=mem_status,
                threshold=self.RESOURCE_THRESHOLDS["memory_percent_warning"],
            ))
            
            # Also add available memory in GB
            available_gb = mem.available / (1024 ** 3)
            mem_available_status = "ok"
            if available_gb < self.RESOURCE_THRESHOLDS["memory_min_gb"]:
                mem_available_status = "critical"
            
            resources.append(SystemResource(
                name="memory_available_gb",
                value=available_gb,
                unit="GB",
                status=mem_available_status,
                threshold=self.RESOURCE_THRESHOLDS["memory_min_gb"],
            ))
        except Exception as e:
            logger.warning(f"Failed to check memory: {e}")
        
        # Disk usage
        try:
            disk = self._psutil.disk_usage("/")
            disk_percent = disk.percent
            
            disk_status = "ok"
            if disk_percent >= self.RESOURCE_THRESHOLDS["disk_percent_critical"]:
                disk_status = "critical"
            elif disk_percent >= self.RESOURCE_THRESHOLDS["disk_percent_warning"]:
                disk_status = "warning"
            
            resources.append(SystemResource(
                name="disk_percent",
                value=disk_percent,
                unit="%",
                status=disk_status,
                threshold=self.RESOURCE_THRESHOLDS["disk_percent_warning"],
            ))
        except Exception as e:
            logger.warning(f"Failed to check disk: {e}")
        
        return resources
    
    def check_vlm_provider(self, provider: str) -> Tuple[bool, Optional[str]]:
        """
        Check if a specific VLM provider is available.
        
        Args:
            provider: Provider name (ollama, lmstudio, openai, google)
            
        Returns:
            Tuple of (available, error_message)
        """
        if provider == "ollama":
            return self._check_port(11434), "Ollama not running on port 11434"
        
        elif provider == "lmstudio":
            return self._check_port(1234), "LM Studio not running on port 1234"
        
        elif provider == "openai":
            # Check if openai package is available and API key is set
            try:
                import openai
                import os
                if os.getenv("OPENAI_API_KEY"):
                    return True, None
                else:
                    return False, "OPENAI_API_KEY not set"
            except ImportError:
                return False, "openai package not installed"
        
        elif provider == "google":
            # Check if google-generativeai is available
            try:
                import google.generativeai as genai
                import os
                if os.getenv("GOOGLE_API_KEY"):
                    return True, None
                else:
                    return False, "GOOGLE_API_KEY not set"
            except ImportError:
                return False, "google-generativeai package not installed"
        
        return False, f"Unknown provider: {provider}"


# Global instance
_checker: Optional[SystemHealthChecker] = None


def get_health_checker() -> SystemHealthChecker:
    """Get the global health checker instance."""
    global _checker
    if _checker is None:
        _checker = SystemHealthChecker()
    return _checker


def check_system_health() -> SystemHealthReport:
    """Check system health and return report."""
    return get_health_checker().check_system()


def get_install_instructions() -> Dict[str, str]:
    """Get installation instructions for missing dependencies."""
    report = check_system_health()
    return report.get_summary().get("install_instructions", {})
