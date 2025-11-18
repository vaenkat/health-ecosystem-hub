"""
Authentication and authorization schemas
"""

from pydantic import BaseModel, Field, EmailStr, validator
from typing import Optional, List
from datetime import datetime
from .common import UserRole


class LoginRequest(BaseModel):
    """Login request schema"""
    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., min_length=6, max_length=100, description="User password")
    remember_me: bool = Field(default=False, description="Remember me option")


class LoginResponse(BaseModel):
    """Login response schema"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    user: "UserResponse"
    permissions: List[str]


class UserCreate(BaseModel):
    """User creation schema"""
    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., min_length=8, max_length=100, description="User password")
    full_name: str = Field(..., min_length=2, max_length=100, description="User full name")
    phone: Optional[str] = Field(None, max_length=20, description="User phone number")
    role: UserRole = Field(..., description="User role")
    
    @validator('password')
    def validate_password(cls, v):
        """Validate password strength"""
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(c.islower() for c in v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain at least one digit')
        return v


class UserUpdate(BaseModel):
    """User update schema"""
    full_name: Optional[str] = Field(None, min_length=2, max_length=100)
    phone: Optional[str] = Field(None, max_length=20)
    email: Optional[EmailStr] = None


class UserResponse(BaseModel):
    """User response schema"""
    id: str
    email: str
    full_name: str
    phone: Optional[str]
    role: UserRole
    created_at: datetime
    updated_at: Optional[datetime]
    last_sign_in_at: Optional[datetime]
    is_active: bool = True
    
    class Config:
        from_attributes = True


class PasswordChange(BaseModel):
    """Password change schema"""
    current_password: str = Field(..., description="Current password")
    new_password: str = Field(..., min_length=8, max_length=100, description="New password")
    confirm_password: str = Field(..., description="Confirm new password")
    
    @validator('confirm_password')
    def passwords_match(cls, v, values):
        """Validate that new password and confirmation match"""
        if 'new_password' in values and v != values['new_password']:
            raise ValueError('Passwords do not match')
        return v
    
    @validator('new_password')
    def validate_new_password(cls, v):
        """Validate new password strength"""
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(c.islower() for c in v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain at least one digit')
        return v


class PasswordReset(BaseModel):
    """Password reset request schema"""
    email: EmailStr = Field(..., description="User email address")


class PasswordResetConfirm(BaseModel):
    """Password reset confirmation schema"""
    token: str = Field(..., description="Reset token")
    new_password: str = Field(..., min_length=8, max_length=100, description="New password")
    confirm_password: str = Field(..., description="Confirm new password")
    
    @validator('confirm_password')
    def passwords_match(cls, v, values):
        """Validate that passwords match"""
        if 'new_password' in values and v != values['new_password']:
            raise ValueError('Passwords do not match')
        return v


class RefreshTokenRequest(BaseModel):
    """Refresh token request schema"""
    refresh_token: str = Field(..., description="Refresh token")


class RefreshTokenResponse(BaseModel):
    """Refresh token response schema"""
    access_token: str
    token_type: str = "bearer"
    expires_in: int


class UserProfile(BaseModel):
    """User profile schema"""
    id: str
    full_name: str
    email: str
    phone: Optional[str]
    role: UserRole
    avatar_url: Optional[str] = None
    preferences: Optional[dict] = {}
    created_at: datetime
    last_login: Optional[datetime]
    
    class Config:
        from_attributes = True


class RoleAssignment(BaseModel):
    """Role assignment schema"""
    user_id: str
    role: UserRole
    assigned_by: str
    assigned_at: datetime = Field(default_factory=datetime.utcnow)
    expires_at: Optional[datetime] = None


class Permission(BaseModel):
    """Permission schema"""
    id: str
    name: str
    description: str
    resource: str
    action: str
    
    class Config:
        from_attributes = True


class UserPermission(BaseModel):
    """User permission schema"""
    user_id: str
    permission_id: str
    granted_at: datetime = Field(default_factory=datetime.utcnow)
    granted_by: str
    expires_at: Optional[datetime] = None


class SessionInfo(BaseModel):
    """Session information schema"""
    session_id: str
    user_id: str
    ip_address: str
    user_agent: str
    created_at: datetime
    last_activity: datetime
    is_active: bool = True
    expires_at: datetime


class APIKeyCreate(BaseModel):
    """API key creation schema"""
    name: str = Field(..., min_length=2, max_length=100, description="API key name")
    permissions: List[str] = Field(..., description="List of permissions")
    expires_at: Optional[datetime] = Field(None, description="Expiration date")


class APIKeyResponse(BaseModel):
    """API key response schema"""
    key_id: str
    key: str  # Only returned on creation
    name: str
    permissions: List[str]
    created_at: datetime
    expires_at: Optional[datetime]
    last_used: Optional[datetime]
    is_active: bool = True


class AuthToken(BaseModel):
    """Authentication token schema"""
    token: str
    token_type: str = "bearer"
    expires_in: int
    scope: Optional[str] = None


class TokenValidation(BaseModel):
    """Token validation response"""
    valid: bool
    user_id: Optional[str] = None
    role: Optional[UserRole] = None
    expires_at: Optional[datetime] = None
    error: Optional[str] = None
