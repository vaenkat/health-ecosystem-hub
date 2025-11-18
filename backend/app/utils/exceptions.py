"""
Custom exceptions for Health Ecosystem Hub Backend
"""

from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
import logging
import time
from typing import Dict, Any

logger = logging.getLogger(__name__)


class HealthHubException(Exception):
    """Base exception for Health Hub application"""
    
    def __init__(
        self,
        message: str,
        error_code: str = "UNKNOWN_ERROR",
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        details: Dict[str, Any] = None
    ):
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.status_code = status_code
        self.details = details or {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert exception to dictionary"""
        return {
            "success": False,
            "message": self.message,
            "error_code": self.error_code,
            "details": self.details,
            "timestamp": time.time()
        }


class AuthenticationError(HealthHubException):
    """Authentication related errors"""
    
    def __init__(self, message: str, details: Dict[str, Any] = None):
        super().__init__(
            message=message,
            error_code="AUTH_ERROR",
            status_code=status.HTTP_401_UNAUTHORIZED,
            details=details
        )


class AuthorizationError(HealthHubException):
    """Authorization related errors"""
    
    def __init__(self, message: str, details: Dict[str, Any] = None):
        super().__init__(
            message=message,
            error_code="AUTHORIZATION_ERROR",
            status_code=status.HTTP_403_FORBIDDEN,
            details=details
        )


class ValidationError(HealthHubException):
    """Validation related errors"""
    
    def __init__(self, message: str, details: Dict[str, Any] = None):
        super().__init__(
            message=message,
            error_code="VALIDATION_ERROR",
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            details=details
        )


class NotFoundError(HealthHubException):
    """Resource not found errors"""
    
    def __init__(self, message: str, resource_type: str = None, details: Dict[str, Any] = None):
        super().__init__(
            message=message,
            error_code="NOT_FOUND",
            status_code=status.HTTP_404_NOT_FOUND,
            details={**(details or {}), "resource_type": resource_type}
        )


class ConflictError(HealthHubException):
    """Conflict errors"""
    
    def __init__(self, message: str, details: Dict[str, Any] = None):
        super().__init__(
            message=message,
            error_code="CONFLICT",
            status_code=status.HTTP_409_CONFLICT,
            details=details
        )


class BusinessLogicError(HealthHubException):
    """Business logic errors"""
    
    def __init__(self, message: str, details: Dict[str, Any] = None):
        super().__init__(
            message=message,
            error_code="BUSINESS_LOGIC_ERROR",
            status_code=status.HTTP_400_BAD_REQUEST,
            details=details
        )


class DatabaseError(HealthHubException):
    """Database related errors"""
    
    def __init__(self, message: str, details: Dict[str, Any] = None):
        super().__init__(
            message=message,
            error_code="DATABASE_ERROR",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            details=details
        )


class ExternalServiceError(HealthHubException):
    """External service errors"""
    
    def __init__(self, message: str, service_name: str = None, details: Dict[str, Any] = None):
        super().__init__(
            message=message,
            error_code="EXTERNAL_SERVICE_ERROR",
            status_code=status.HTTP_502_BAD_GATEWAY,
            details={**(details or {}), "service_name": service_name}
        )


class RateLimitError(HealthHubException):
    """Rate limiting errors"""
    
    def __init__(self, message: str, retry_after: int = None, details: Dict[str, Any] = None):
        super().__init__(
            message=message,
            error_code="RATE_LIMIT_EXCEEDED",
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            details={**(details or {}), "retry_after": retry_after}
        )


class ConfigurationError(HealthHubException):
    """Configuration related errors"""
    
    def __init__(self, message: str, details: Dict[str, Any] = None):
        super().__init__(
            message=message,
            error_code="CONFIGURATION_ERROR",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            details=details
        )


def setup_exception_handlers(app):
    """Setup custom exception handlers for FastAPI app"""
    
    @app.exception_handler(HealthHubException)
    async def health_hub_exception_handler(request: Request, exc: HealthHubException):
        """Handle Health Hub exceptions"""
        logger.error(f"HealthHub Exception: {exc.error_code} - {exc.message}")
        return JSONResponse(
            status_code=exc.status_code,
            content=exc.to_dict()
        )
    
    @app.exception_handler(ValueError)
    async def value_error_handler(request: Request, exc: ValueError):
        """Handle ValueError exceptions"""
        logger.error(f"ValueError: {str(exc)}")
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "success": False,
                "message": "Invalid input value",
                "error_code": "INVALID_VALUE",
                "details": {"error": str(exc)},
                "timestamp": time.time()
            }
        )
    
    @app.exception_handler(KeyError)
    async def key_error_handler(request: Request, exc: KeyError):
        """Handle KeyError exceptions"""
        logger.error(f"KeyError: {str(exc)}")
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "success": False,
                "message": "Missing required field",
                "error_code": "MISSING_FIELD",
                "details": {"missing_key": str(exc)},
                "timestamp": time.time()
            }
        )
    
    @app.exception_handler(TypeError)
    async def type_error_handler(request: Request, exc: TypeError):
        """Handle TypeError exceptions"""
        logger.error(f"TypeError: {str(exc)}")
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "success": False,
                "message": "Invalid data type",
                "error_code": "INVALID_TYPE",
                "details": {"error": str(exc)},
                "timestamp": time.time()
            }
        )
    
    @app.exception_handler(PermissionError)
    async def permission_error_handler(request: Request, exc: PermissionError):
        """Handle PermissionError exceptions"""
        logger.error(f"PermissionError: {str(exc)}")
        return JSONResponse(
            status_code=status.HTTP_403_FORBIDDEN,
            content={
                "success": False,
                "message": "Permission denied",
                "error_code": "PERMISSION_DENIED",
                "details": {"error": str(exc)},
                "timestamp": time.time()
            }
        )


def handle_database_error(error: Exception, operation: str = "database operation") -> HealthHubException:
    """Convert database errors to HealthHubException"""
    error_str = str(error).lower()
    
    if "connection" in error_str or "timeout" in error_str:
        return DatabaseError(
            f"Database connection error during {operation}",
            details={"original_error": str(error)}
        )
    elif "duplicate" in error_str or "unique" in error_str:
        return ConflictError(
            f"Duplicate record during {operation}",
            details={"original_error": str(error)}
        )
    elif "not found" in error_str or "no rows" in error_str:
        return NotFoundError(
            f"Record not found during {operation}",
            details={"original_error": str(error)}
        )
    elif "permission" in error_str or "access" in error_str:
        return AuthorizationError(
            f"Access denied during {operation}",
            details={"original_error": str(error)}
        )
    else:
        return DatabaseError(
            f"Database error during {operation}",
            details={"original_error": str(error)}
        )


def log_exception(exc: Exception, context: str = "application"):
    """Log exception with context"""
    if isinstance(exc, HealthHubException):
        logger.error(
            f"{context}: {exc.error_code} - {exc.message}",
            extra={"details": exc.details}
        )
    else:
        logger.error(f"{context}: {type(exc).__name__} - {str(exc)}", exc_info=True)


def create_error_response(
    message: str,
    error_code: str = "UNKNOWN_ERROR",
    status_code: int = 500,
    details: Dict[str, Any] = None
) -> Dict[str, Any]:
    """Create standardized error response"""
    return {
        "success": False,
        "message": message,
        "error_code": error_code,
        "details": details or {},
        "timestamp": time.time()
    }
