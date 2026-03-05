"""Validator plugin interface.

Provides the base interface for implementing custom validators.
Validators check extracted content for quality, security, and completeness.
"""

from abc import ABC, abstractmethod
from enum import Enum
from pydantic import BaseModel, Field
from typing import Any, Dict, List, Optional

from src.utils.plugin_system import Plugin, PluginMetadata, PluginType


class ValidationLevel(str, Enum):
    """Validation severity levels."""
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


class ValidationIssue(BaseModel):
    """A single validation issue."""
    level: ValidationLevel = Field(..., description="Issue severity level")
    code: str = Field(..., description="Issue code")
    message: str = Field(..., description="Human-readable message")
    field_path: Optional[str] = Field(default=None, description="Path to the field with issue")
    suggestion: Optional[str] = Field(default=None, description="Suggested fix")


class ValidationResult(BaseModel):
    """Result of validation."""
    is_valid: bool = Field(..., description="Whether validation passed")
    issues: List[ValidationIssue] = Field(default_factory=list, description="Validation issues")
    score: float = Field(
        default=1.0,
        ge=0.0,
        le=1.0,
        description="Overall validation score"
    )
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional validation metadata"
    )


class Validator(Plugin, ABC):
    """Base class for validator plugins.
    
    Validators check extracted content for:
    - Quality (completeness, accuracy)
    - Security (no malicious content)
    - Format compliance
    - Business rules
    """
    
    @property
    def plugin_type(self) -> PluginType:
        return PluginType.VALIDATOR
    
    @property
    @abstractmethod
    def validation_type(self) -> str:
        """Return the type of validation this validator performs."""
        pass
    
    @abstractmethod
    async def validate(self, content: Any) -> ValidationResult:
        """Validate content.
        
        Args:
            content: Content to validate (can be text, dict, or model)
            
        Returns:
            ValidationResult with issues found
        """
        pass
    
    def validate_sync(self, content: Any) -> ValidationResult:
        """Synchronous validation wrapper.
        
        Override this if async is not needed.
        """
        import asyncio
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # If we're in an async context, we need to create a new task
                future = asyncio.coroutine(self.validate)(content)
                return asyncio.run_until_complete(future)
        except RuntimeError:
            pass
        return asyncio.run(self.validate(content))


class ContentQualityValidator(Validator):
    """Validator for content quality checks."""
    
    @property
    def metadata(self) -> PluginMetadata:
        return PluginMetadata(
            name="content-quality-validator",
            version="1.0.0",
            description="Validates content quality and completeness",
            author="Document Intelligence Team",
            plugin_type=PluginType.VALIDATOR
        )
    
    @property
    def validation_type(self) -> str:
        return "quality"
    
    def initialize(self) -> None:
        pass
    
    def shutdown(self) -> None:
        pass
    
    async def validate(self, content: Any) -> ValidationResult:
        """Validate content quality."""
        issues = []
        
        if isinstance(content, str):
            # Check for empty content
            if not content.strip():
                issues.append(ValidationIssue(
                    level=ValidationLevel.ERROR,
                    code="EMPTY_CONTENT",
                    message="Content is empty"
                ))
            
            # Check for minimum length
            if len(content) < 10:
                issues.append(ValidationIssue(
                    level=ValidationLevel.WARNING,
                    code="SHORT_CONTENT",
                    message=f"Content is very short ({len(content)} chars)",
                    suggestion="Consider if this is expected"
                ))
            
            # Check for OCR indicators
            ocr_indicators = ["�", "\x00", "\ufffd"]
            if any(indicator in content for indicator in ocr_indicators):
                issues.append(ValidationIssue(
                    level=ValidationLevel.WARNING,
                    code="OCR_ERROR_CHARS",
                    message="Content contains potential OCR error characters"
                ))
        
        elif isinstance(content, dict):
            if not content:
                issues.append(ValidationIssue(
                    level=ValidationLevel.ERROR,
                    code="EMPTY_DICT",
                    message="Content dictionary is empty"
                ))
        
        is_valid = not any(i.level == ValidationLevel.ERROR for i in issues)
        score = 1.0 - (len(issues) * 0.1)
        
        return ValidationResult(
            is_valid=is_valid,
            issues=issues,
            score=max(0.0, score)
        )


class SecurityValidator(Validator):
    """Validator for security checks."""
    
    @property
    def metadata(self) -> PluginMetadata:
        return PluginMetadata(
            name="security-validator",
            version="1.0.0",
            description="Validates content for security issues",
            author="Document Intelligence Team",
            plugin_type=PluginType.VALIDATOR
        )
    
    @property
    def validation_type(self) -> str:
        return "security"
    
    def initialize(self) -> None:
        pass
    
    def shutdown(self) -> None:
        pass
    
    async def validate(self, content: Any) -> ValidationResult:
        """Validate content security."""
        issues = []
        
        if isinstance(content, str):
            # Check for script tags (XSS)
            if "<script" in content.lower():
                issues.append(ValidationIssue(
                    level=ValidationLevel.ERROR,
                    code="SCRIPT_TAG",
                    message="Content contains script tags",
                    suggestion="Sanitize HTML before processing"
                ))
            
            # Check for SQL injection patterns
            sql_patterns = ["' OR '1'='1", "DROP TABLE", "INSERT INTO"]
            for pattern in sql_patterns:
                if pattern.lower() in content.lower():
                    issues.append(ValidationIssue(
                        level=ValidationLevel.ERROR,
                        code="SQL_INJECTION",
                        message=f"Content contains potential SQL injection pattern: {pattern}"
                    ))
            
            # Check for paths traversal
            if "../" in content or "..\\" in content:
                issues.append(ValidationIssue(
                    level=ValidationLevel.WARNING,
                    code="PATH_TRAVERSAL",
                    message="Content contains path traversal patterns"
                ))
        
        is_valid = not any(i.level == ValidationLevel.ERROR for i in issues)
        
        return ValidationResult(
            is_valid=is_valid,
            issues=issues,
            score=1.0 if is_valid else 0.5
        )


class FormatValidator(Validator):
    """Validator for format compliance."""
    
    def __init__(self, required_fields: List[str] = None):
        self.required_fields = required_fields or []
    
    @property
    def metadata(self) -> PluginMetadata:
        return PluginMetadata(
            name="format-validator",
            version="1.0.0",
            description="Validates format and required fields",
            author="Document Intelligence Team",
            plugin_type=PluginType.VALIDATOR
        )
    
    @property
    def validation_type(self) -> str:
        return "format"
    
    def initialize(self) -> None:
        pass
    
    def shutdown(self) -> None:
        pass
    
    async def validate(self, content: Any) -> ValidationResult:
        """Validate format and required fields."""
        issues = []
        
        if isinstance(content, dict):
            for field in self.required_fields:
                if field not in content:
                    issues.append(ValidationIssue(
                        level=ValidationLevel.ERROR,
                        code="MISSING_FIELD",
                        message=f"Required field '{field}' is missing",
                        field_path=field
                    ))
                elif content[field] is None or content[field] == "":
                    issues.append(ValidationIssue(
                        level=ValidationLevel.WARNING,
                        code="EMPTY_FIELD",
                        message=f"Required field '{field}' is empty",
                        field_path=field
                    ))
        
        is_valid = not any(i.level == ValidationLevel.ERROR for i in issues)
        
        return ValidationResult(
            is_valid=is_valid,
            issues=issues,
            score=1.0 if is_valid else 0.0
        )


# Registry for validators
_validators: Dict[str, type[Validator]] = {
    "quality": ContentQualityValidator,
    "security": SecurityValidator,
}


def get_validator(validation_type: str) -> Validator:
    """Get a validator by type.
    
    Args:
        validation_type: Type of validation
        
    Returns:
        Validator instance
    """
    validator_class = _validators.get(validation_type)
    if validator_class is None:
        raise ValueError(f"Unknown validator type: {validation_type}")
    return validator_class()


def register_validator(validation_type: str, validator_class: type[Validator]) -> None:
    """Register a custom validator.
    
    Args:
        validation_type: Type identifier for the validator
        validator_class: Validator class to register
    """
    _validators[validation_type] = validator_class
