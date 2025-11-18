"""
Rate limiting middleware for Health Ecosystem Hub Backend
"""

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
from fastapi import Request, HTTPException, status
import time
import logging
from typing import Dict, Optional
from collections import defaultdict, deque

logger = logging.getLogger(__name__)


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Rate limiting middleware"""
    
    def __init__(self, app, requests_per_minute: int = 60, burst_size: int = 10):
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
        self.burst_size = burst_size
        self.clients = defaultdict(lambda: {
            'requests': deque(),
            'blocked_until': None,
            'warning_sent': False
        })
        self.logger = logging.getLogger("rate_limit_logger")
        
        # Configure rate limit logger
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            '%(asctime)s - RATE_LIMIT - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        self.logger.setLevel(logging.INFO)
    
    async def dispatch(self, request: Request, call_next):
        """Apply rate limiting to requests"""
        client_id = self._get_client_id(request)
        current_time = time.time()
        
        # Check if client is blocked
        if self._is_client_blocked(client_id, current_time):
            self.logger.warning(f"Blocked request from {client_id}")
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={
                    "success": False,
                    "message": "Rate limit exceeded. Please try again later.",
                    "error_code": "RATE_LIMIT_EXCEEDED",
                    "retry_after": int(self.clients[client_id]['blocked_until'] - current_time),
                    "timestamp": current_time
                }
            )
        
        # Clean old requests
        self._clean_old_requests(client_id, current_time)
        
        # Check rate limit
        if self._is_rate_limited(client_id, current_time):
            # Send warning on first violation
            if not self.clients[client_id]['warning_sent']:
                self.clients[client_id]['warning_sent'] = True
                self.logger.info(f"Rate limit warning for {client_id}")
            
            # Apply rate limit
            block_duration = self._calculate_block_duration(client_id)
            self.clients[client_id]['blocked_until'] = current_time + block_duration
            
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={
                    "success": False,
                    "message": "Rate limit exceeded. Please try again later.",
                    "error_code": "RATE_LIMIT_EXCEEDED",
                    "retry_after": int(block_duration),
                    "timestamp": current_time
                }
            )
        
        # Record request
        self.clients[client_id]['requests'].append(current_time)
        
        # Reset warning flag if under limit
        if len(self.clients[client_id]['requests']) < self.requests_per_minute:
            self.clients[client_id]['warning_sent'] = False
        
        # Add rate limit headers
        response = await call_next(request)
        remaining = max(0, self.requests_per_minute - len(self.clients[client_id]['requests']))
        response.headers["X-RateLimit-Limit"] = str(self.requests_per_minute)
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        response.headers["X-RateLimit-Reset"] = str(int(current_time + 60))
        
        return response
    
    def _get_client_id(self, request: Request) -> str:
        """Get unique client identifier"""
        # Try to get user ID from authentication
        try:
            from app.middleware.auth import get_current_user_id
            return f"user:{get_current_user_id(request)}"
        except:
            # Fall back to IP address
            client_ip = self._get_client_ip(request)
            return f"ip:{client_ip}"
    
    def _get_client_ip(self, request: Request) -> str:
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
    
    def _is_client_blocked(self, client_id: str, current_time: float) -> bool:
        """Check if client is currently blocked"""
        blocked_until = self.clients[client_id]['blocked_until']
        return blocked_until is not None and current_time < blocked_until
    
    def _clean_old_requests(self, client_id: str, current_time: float):
        """Remove requests older than 1 minute"""
        cutoff_time = current_time - 60
        requests = self.clients[client_id]['requests']
        
        # Remove old requests
        while requests and requests[0] < cutoff_time:
            requests.popleft()
    
    def _is_rate_limited(self, client_id: str, current_time: float) -> bool:
        """Check if client has exceeded rate limit"""
        request_count = len(self.clients[client_id]['requests'])
        
        # Check burst limit (very short window)
        recent_requests = [
            req_time for req_time in self.clients[client_id]['requests']
            if current_time - req_time < 10  # Last 10 seconds
        ]
        
        return request_count >= self.requests_per_minute or len(recent_requests) > self.burst_size
    
    def _calculate_block_duration(self, client_id: str) -> float:
        """Calculate block duration based on violation count"""
        request_count = len(self.clients[client_id]['requests'])
        
        if request_count > self.requests_per_minute * 2:
            return 300  # 5 minutes for severe violations
        elif request_count > self.requests_per_minute * 1.5:
            return 120  # 2 minutes for moderate violations
        else:
            return 60   # 1 minute for minor violations


class AdvancedRateLimitMiddleware(BaseHTTPMiddleware):
    """Advanced rate limiting with multiple strategies"""
    
    def __init__(self, app):
        super().__init__(app)
        self.limits = {
            'per_minute': 60,
            'per_hour': 1000,
            'per_day': 10000
        }
        self.clients = defaultdict(lambda: {
            'minute_window': deque(),
            'hour_window': deque(),
            'day_window': deque(),
            'blocked_until': None,
            'violations': 0
        })
        self.logger = logging.getLogger("advanced_rate_limit_logger")
    
    async def dispatch(self, request: Request, call_next):
        """Apply advanced rate limiting"""
        client_id = self._get_client_id(request)
        current_time = time.time()
        
        # Check if blocked
        if self._is_client_blocked(client_id, current_time):
            return self._create_rate_limit_response(client_id, current_time)
        
        # Clean old requests
        self._clean_windows(client_id, current_time)
        
        # Check all limits
        if self._check_limits(client_id, current_time):
            return self._create_rate_limit_response(client_id, current_time)
        
        # Record request
        self._record_request(client_id, current_time)
        
        # Add headers
        response = await call_next(request)
        self._add_rate_limit_headers(response, client_id, current_time)
        
        return response
    
    def _get_client_id(self, request: Request) -> str:
        """Get unique client identifier"""
        try:
            from app.middleware.auth import get_current_user_id
            return f"user:{get_current_user_id(request)}"
        except:
            client_ip = self._get_client_ip(request)
            return f"ip:{client_ip}"
    
    def _get_client_ip(self, request: Request) -> str:
        """Get client IP address"""
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip
        
        return request.client.host if request.client else "Unknown"
    
    def _is_client_blocked(self, client_id: str, current_time: float) -> bool:
        """Check if client is blocked"""
        blocked_until = self.clients[client_id]['blocked_until']
        if blocked_until and current_time < blocked_until:
            return True
        return False
    
    def _clean_windows(self, client_id: str, current_time: float):
        """Clean old requests from all time windows"""
        client_data = self.clients[client_id]
        
        # Clean minute window (last 60 seconds)
        minute_cutoff = current_time - 60
        while client_data['minute_window'] and client_data['minute_window'][0] < minute_cutoff:
            client_data['minute_window'].popleft()
        
        # Clean hour window (last 3600 seconds)
        hour_cutoff = current_time - 3600
        while client_data['hour_window'] and client_data['hour_window'][0] < hour_cutoff:
            client_data['hour_window'].popleft()
        
        # Clean day window (last 86400 seconds)
        day_cutoff = current_time - 86400
        while client_data['day_window'] and client_data['day_window'][0] < day_cutoff:
            client_data['day_window'].popleft()
    
    def _check_limits(self, client_id: str, current_time: float) -> bool:
        """Check all rate limits"""
        client_data = self.clients[client_id]
        
        # Check minute limit
        if len(client_data['minute_window']) >= self.limits['per_minute']:
            return True
        
        # Check hour limit
        if len(client_data['hour_window']) >= self.limits['per_hour']:
            return True
        
        # Check day limit
        if len(client_data['day_window']) >= self.limits['per_day']:
            return True
        
        return False
    
    def _record_request(self, client_id: str, current_time: float):
        """Record request in all time windows"""
        client_data = self.clients[client_id]
        client_data['minute_window'].append(current_time)
        client_data['hour_window'].append(current_time)
        client_data['day_window'].append(current_time)
    
    def _create_rate_limit_response(self, client_id: str, current_time: float) -> JSONResponse:
        """Create rate limit response"""
        client_data = self.clients[client_id]
        blocked_until = current_time + 60  # 1 minute block
        client_data['blocked_until'] = blocked_until
        client_data['violations'] += 1
        
        return JSONResponse(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            content={
                "success": False,
                "message": "Rate limit exceeded. Please try again later.",
                "error_code": "RATE_LIMIT_EXCEEDED",
                "retry_after": 60,
                "violations": client_data['violations'],
                "timestamp": current_time
            }
        )
    
    def _add_rate_limit_headers(self, response, client_id: str, current_time: float):
        """Add rate limit headers to response"""
        client_data = self.clients[client_id]
        
        response.headers["X-RateLimit-Limit-Minute"] = str(self.limits['per_minute'])
        response.headers["X-RateLimit-Remaining-Minute"] = str(
            max(0, self.limits['per_minute'] - len(client_data['minute_window']))
        )
        
        response.headers["X-RateLimit-Limit-Hour"] = str(self.limits['per_hour'])
        response.headers["X-RateLimit-Remaining-Hour"] = str(
            max(0, self.limits['per_hour'] - len(client_data['hour_window']))
        )
        
        response.headers["X-RateLimit-Limit-Day"] = str(self.limits['per_day'])
        response.headers["X-RateLimit-Remaining-Day"] = str(
            max(0, self.limits['per_day'] - len(client_data['day_window']))
        )
        
        response.headers["X-RateLimit-Reset"] = str(int(current_time + 60))
