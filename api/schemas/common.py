"""Common Pydantic schema models for AI Meeting Action-Item Extractor."""

from typing import Generic, TypeVar, Optional, List, Any
from pydantic import BaseModel, Field

T = TypeVar("T")


class APIResponse(BaseModel, Generic[T]):
    """Standard unified response wrapper."""
    success: bool = True
    message: str = "Operation completed successfully"
    data: Optional[T] = None
    errors: Optional[List[str]] = None


class ValidationIssue(BaseModel):
    """Represents a rule validation warning or error."""
    rule_name: str
    severity: str = "warning"  # info | warning | error | critical
    message: str
    affected_field: Optional[str] = None


class HealthCheckResponse(BaseModel):
    """System health check payload."""
    status: str = "healthy"
    app_name: str
    version: str
    provider: str
    database: str
