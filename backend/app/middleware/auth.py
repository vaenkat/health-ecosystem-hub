"""
Authentication middleware for Health Ecosystem Hub Backend
"""

from fastapi import Request, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
import jwt
import logging
from typing import Optional

from app.config import settings
from app.database import supabase_client
from app.schemas.common import ErrorResponse

logger = logging.getLogger(__name__)
security = HTTPBearer(auto_error=False)


class AuthMiddleware(BaseHTTPMiddleware):
    """Authentication middleware for API requests"""
    
    async def dispatch(self, request: Request, call_next):
        """Process request and add authentication"""
        # Skip authentication for certain paths
        if self._should_skip_auth(request.url.path):
            response = await call_next(request)
            return response
        
        try:
            # Get authorization header
            auth_header = request.headers.get("Authorization")
            if not auth_header:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Authorization header missing"
                )
            
            # Extract token
            if not auth_header.startswith("Bearer "):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid authorization header format"
                )
            
            token = auth_header.split(" ")[1]
            
            # Verify token
            payload = self._verify_token(token)
            if not payload:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid or expired token"
                )
            
            # Get user information
            user_info = await self._get_user_info(payload.get("sub"))
            if not user_info:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="User not found"
                )
            
            # Add user info to request state
            request.state.user = user_info
            request.state.user_id = payload.get("sub")
            request.state.user_role = user_info.get("role")
            
            response = await call_next(request)
            return response
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Authentication error: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication failed"
            )
    
    def _should_skip_auth(self, path: str) -> bool:
        """Check if path should skip authentication"""
        skip_paths = [
            "/",
            "/health",
            "/health/detailed",
            "/api/v1/info",
            "/docs",
            "/redoc",
            "/openapi.json",
            "/api/v1/auth/login",
            "/api/v1/auth/register",
            "/api/v1/auth/refresh",
            "/api/v1/auth/forgot-password",
            "/api/v1/auth/reset-password",
            "/ws/"
        ]
        
        return any(path.startswith(skip_path) for skip_path in skip_paths)
    
    def _verify_token(self, token: str) -> Optional[dict]:
        """Verify JWT token"""
        try:
            payload = jwt.decode(
                token,
                settings.secret_key,
                algorithms=[settings.algorithm]
            )
            return payload
        except jwt.ExpiredSignatureError:
            logger.warning("Token expired")
            return None
        except jwt.InvalidTokenError as e:
            logger.warning(f"Invalid token: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Token verification error: {str(e)}")
            return None
    
    async def _get_user_info(self, user_id: str) -> Optional[dict]:
        """Get user information from database"""
        try:
            # Get user profile
            profile_result = await supabase_client.get_client().table('profiles')\
                .select("*")\
                .eq('id', user_id)\
                .single()\
                .execute()
            
            if not profile_result.data:
                return None
            
            # Get user role
            role_result = await supabase_client.get_client().table('user_roles')\
                .select("role")\
                .eq('user_id', user_id)\
                .single()\
                .execute()
            
            user_info = profile_result.data
            user_info['role'] = role_result.data.get('role') if role_result.data else None
            
            return user_info
            
        except Exception as e:
            logger.error(f"Error getting user info: {str(e)}")
            return None


def get_current_user(request: Request) -> dict:
    """Get current user from request state"""
    if not hasattr(request.state, 'user'):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
        )
    return request.state.user


def get_current_user_id(request: Request) -> str:
    """Get current user ID from request state"""
    if not hasattr(request.state, 'user_id'):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
        )
    return request.state.user_id


def get_current_user_role(request: Request) -> str:
    """Get current user role from request state"""
    if not hasattr(request.state, 'user_role'):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
        )
    return request.state.user_role


def require_role(required_role: str):
    """Decorator to require specific role"""
    def role_checker(request: Request) -> bool:
        current_role = get_current_user_role(request)
        if current_role != required_role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Required role: {required_role}"
            )
        return True
    return role_checker


def require_any_role(allowed_roles: list):
    """Decorator to require any of the specified roles"""
    def role_checker(request: Request) -> bool:
        current_role = get_current_user_role(request)
        if current_role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Allowed roles: {', '.join(allowed_roles)}"
            )
        return True
    return role_checker


def require_admin(request: Request) -> bool:
    """Check if user has admin role"""
    return require_role("admin")(request)


def require_hospital_staff(request: Request) -> bool:
    """Check if user has hospital staff role"""
    return require_any_role(["hospital_staff", "admin"])(request)


def require_pharmacy_staff(request: Request) -> bool:
    """Check if user has pharmacy staff role"""
    return require_any_role(["pharmacy_staff", "admin"])(request)


def require_patient_or_staff(request: Request) -> bool:
    """Check if user is patient or staff"""
    return require_any_role(["patient", "hospital_staff", "pharmacy_staff", "admin"])(request)


async def get_optional_user(request: Request) -> Optional[dict]:
    """Get current user if authenticated, return None otherwise"""
    try:
        return get_current_user(request)
    except HTTPException:
        return None


# Rate limiting by user
def get_user_identifier(request: Request) -> str:
    """Get unique identifier for rate limiting"""
    # Try to get user ID first
    try:
        user_id = get_current_user_id(request)
        return f"user:{user_id}"
    except HTTPException:
        # Fall back to IP address
        client_ip = request.client.host
        return f"ip:{client_ip}"


# Token utilities
def create_access_token(data: dict) -> str:
    """Create JWT access token"""
    to_encode = data.copy()
    to_encode.update({
        "exp": time.time() + settings.access_token_expire_minutes * 60,
        "type": "access"
    })
    return jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)


def create_refresh_token(data: dict) -> str:
    """Create JWT refresh token"""
    to_encode = data.copy()
    to_encode.update({
        "exp": time.time() + 7 * 24 * 60 * 60,  # 7 days
        "type": "refresh"
    })
    return jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)


def verify_token(token: str) -> Optional[dict]:
    """Verify and decode JWT token"""
    try:
        payload = jwt.decode(
            token,
            settings.secret_key,
            algorithms=[settings.algorithm]
        )
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None
