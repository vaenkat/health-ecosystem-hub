"""
Logging middleware for Health Ecosystem Hub Backend
"""

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
import time
import logging
import json
from typing import Dict, Any

logger = logging.getLogger(__name__)


class LoggingMiddleware(BaseHTTPMiddleware):
    """Request/response logging middleware"""
    
    def __init__(self, app, log_level: str = "INFO"):
        super().__init__(app)
        self.log_level = getattr(logging, log_level.upper(), logging.INFO)
        self.logger = logging.getLogger("request_logger")
        
        # Configure request logger
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        self.logger.setLevel(self.log_level)
    
    async def dispatch(self, request, call_next):
        """Log request and response"""
        start_time = time.time()
        
        # Get request details
        request_id = self._generate_request_id()
        method = request.method
        url = str(request.url)
        client_ip = self._get_client_ip(request)
        user_agent = request.headers.get("user-agent", "Unknown")
        
        # Log request
        self.logger.info(
            f"Request {request_id}: {method} {url} - IP: {client_ip} - UA: {user_agent}"
        )
        
        # Process request
        try:
            response = await call_next(request)
            process_time = time.time() - start_time
            
            # Log successful response
            self.logger.info(
                f"Response {request_id}: {response.status_code} - "
                f"Duration: {process_time:.3f}s - Size: {len(response.body) if hasattr(response, 'body') else 'N/A'} bytes"
            )
            
            # Add request ID to response headers
            response.headers["X-Request-ID"] = request_id
            response.headers["X-Process-Time"] = f"{process_time:.3f}"
            
            return response
            
        except Exception as e:
            process_time = time.time() - start_time
            
            # Log error
            self.logger.error(
                f"Error {request_id}: {str(e)} - "
                f"Duration: {process_time:.3f}s"
            )
            
            # Return error response
            return JSONResponse(
                status_code=500,
                content={
                    "success": False,
                    "message": "Internal server error",
                    "error_code": "INTERNAL_ERROR",
                    "request_id": request_id,
                    "timestamp": time.time()
                }
            )
    
    def _generate_request_id(self) -> str:
        """Generate unique request ID"""
        import uuid
        return str(uuid.uuid4())[:8]
    
    def _get_client_ip(self, request) -> str:
        """Get client IP address"""
        # Check for forwarded headers
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip
        
        # Fall back to client host
        return request.client.host if request.client else "Unknown"


class SecurityLoggingMiddleware(BaseHTTPMiddleware):
    """Security-focused logging middleware"""
    
    def __init__(self, app):
        super().__init__(app)
        self.logger = logging.getLogger("security_logger")
        
        # Configure security logger
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            '%(asctime)s - SECURITY - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        self.logger.setLevel(logging.INFO)
    
    async def dispatch(self, request, call_next):
        """Log security-related events"""
        client_ip = self._get_client_ip(request)
        user_agent = request.headers.get("user-agent", "Unknown")
        path = request.url.path
        
        # Log suspicious activities
        if self._is_suspicious_request(request):
            self.logger.warning(
                f"Suspicious request from {client_ip}: {request.method} {path} - UA: {user_agent}"
            )
        
        # Log authentication attempts
        if "/auth/" in path:
            self.logger.info(
                f"Auth attempt from {client_ip}: {request.method} {path}"
            )
        
        # Log admin access
        if path.startswith("/admin") or "/admin" in path:
            self.logger.info(
                f"Admin access attempt from {client_ip}: {request.method} {path}"
            )
        
        response = await call_next(request)
        return response
    
    def _is_suspicious_request(self, request) -> bool:
        """Detect potentially suspicious requests"""
        suspicious_patterns = [
            "..",  # Directory traversal
            "<script",  # XSS attempt
            "select ",  # SQL injection
            "union ",  # SQL injection
            "drop ",  # SQL injection
            "exec(",  # Code injection
            "eval(",  # Code injection
            "system(",  # Command injection
        ]
        
        url_str = str(request.url).lower()
        return any(pattern in url_str for pattern in suspicious_patterns)
    
    def _get_client_ip(self, request) -> str:
        """Get client IP address"""
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip
        
        return request.client.host if request.client else "Unknown"


class PerformanceLoggingMiddleware(BaseHTTPMiddleware):
    """Performance monitoring middleware"""
    
    def __init__(self, app):
        super().__init__(app)
        self.logger = logging.getLogger("performance_logger")
        self.request_times = {}
        
        # Configure performance logger
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            '%(asctime)s - PERFORMANCE - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        self.logger.setLevel(logging.INFO)
    
    async def dispatch(self, request, call_next):
        """Monitor request performance"""
        start_time = time.time()
        path = request.url.path
        
        try:
            response = await call_next(request)
            process_time = time.time() - start_time
            
            # Log slow requests (> 2 seconds)
            if process_time > 2.0:
                self.logger.warning(
                    f"Slow request: {request.method} {path} - "
                    f"Duration: {process_time:.3f}s - Status: {response.status_code}"
                )
            
            # Track performance metrics
            self._track_performance(path, process_time)
            
            return response
            
        except Exception as e:
            process_time = time.time() - start_time
            self.logger.error(
                f"Request failed: {request.method} {path} - "
                f"Duration: {process_time:.3f}s - Error: {str(e)}"
            )
            raise
    
    def _track_performance(self, path: str, duration: float):
        """Track performance metrics"""
        if path not in self.request_times:
            self.request_times[path] = []
        
        self.request_times[path].append(duration)
        
        # Keep only last 100 requests per path
        if len(self.request_times[path]) > 100:
            self.request_times[path] = self.request_times[path][-100:]
        
        # Log performance summary every 100 requests
        if len(self.request_times[path]) % 100 == 0:
            avg_time = sum(self.request_times[path]) / len(self.request_times[path])
            max_time = max(self.request_times[path])
            min_time = min(self.request_times[path])
            
            self.logger.info(
                f"Performance summary for {path}: "
                f"Avg: {avg_time:.3f}s, Max: {max_time:.3f}s, "
                f"Min: {min_time:.3f}s, Count: {len(self.request_times[path])}"
            )
