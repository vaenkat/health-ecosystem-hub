"""
Common schemas used across the application
"""

from pydantic import BaseModel, Field
from typing import Optional, Any, List, Generic, TypeVar
from datetime import datetime
from enum import Enum

T = TypeVar('T')


class UserRole(str, Enum):
    """User roles enumeration"""
    PATIENT = "patient"
    HOSPITAL_STAFF = "hospital_staff"
    PHARMACY_STAFF = "pharmacy_staff"
    ADMIN = "admin"


class BaseResponse(BaseModel, Generic[T]):
    """Base response schema"""
    success: bool = True
    message: str = "Operation completed successfully"
    data: Optional[T] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class ErrorResponse(BaseModel):
    """Error response schema"""
    success: bool = False
    message: str
    error_code: Optional[str] = None
    details: Optional[dict[str, Any]] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class PaginatedResponse(BaseModel, Generic[T]):
    """Paginated response schema"""
    success: bool = True
    data: List[T]
    total: int
    page: int
    page_size: int
    total_pages: int
    has_next: bool
    has_prev: bool
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class PaginationParams(BaseModel):
    """Pagination parameters"""
    page: int = Field(default=1, ge=1, description="Page number (1-based)")
    page_size: int = Field(default=20, ge=1, le=100, description="Items per page")
    
    @property
    def offset(self) -> int:
        """Calculate offset for database queries"""
        return (self.page - 1) * self.page_size
    
    @property
    def limit(self) -> int:
        """Get limit for database queries"""
        return self.page_size


class SortParams(BaseModel):
    """Sorting parameters"""
    sort_by: Optional[str] = Field(default=None, description="Field to sort by")
    sort_order: Optional[str] = Field(default="asc", pattern="^(asc|desc)$", description="Sort order")


class FilterParams(BaseModel):
    """Base filter parameters"""
    search: Optional[str] = Field(default=None, description="Search term")
    created_after: Optional[datetime] = Field(default=None, description="Filter by creation date (after)")
    created_before: Optional[datetime] = Field(default=None, description="Filter by creation date (before)")
    updated_after: Optional[datetime] = Field(default=None, description="Filter by update date (after)")
    updated_before: Optional[datetime] = Field(default=None, description="Filter by update date (before)")


class HealthCheck(BaseModel):
    """Health check response"""
    status: str = "healthy"
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    version: str
    database: str
    services: dict[str, str]


class FileUpload(BaseModel):
    """File upload response"""
    filename: str
    file_path: str
    file_size: int
    content_type: str
    upload_timestamp: datetime = Field(default_factory=datetime.utcnow)


class NotificationMessage(BaseModel):
    """WebSocket notification message"""
    type: str
    title: str
    message: str
    data: Optional[dict[str, Any]] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    user_id: Optional[str] = None
    role: Optional[UserRole] = None


class AuditLog(BaseModel):
    """Audit log entry"""
    id: str
    user_id: str
    action: str
    resource_type: str
    resource_id: str
    old_values: Optional[dict[str, Any]] = None
    new_values: Optional[dict[str, Any]] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    timestamp: datetime


class APIKey(BaseModel):
    """API key information"""
    key_id: str
    name: str
    permissions: List[str]
    created_at: datetime
    last_used: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    is_active: bool = True


class SystemMetrics(BaseModel):
    """System metrics for monitoring"""
    cpu_usage: float
    memory_usage: float
    disk_usage: float
    active_connections: int
    requests_per_minute: int
    error_rate: float
    uptime: int
    timestamp: datetime = Field(default_factory=datetime.utcnow)
