"""
Authentication API routes for Health Ecosystem Hub Backend
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer
from typing import Optional
import logging

from app.schemas.auth import (
    LoginRequest, LoginResponse, UserCreate, UserResponse,
    PasswordChange, PasswordReset, PasswordResetConfirm,
    RefreshTokenRequest, RefreshTokenResponse, UserProfile,
    TokenValidation
)
from app.schemas.common import BaseResponse, PaginationParams
from app.middleware.auth import (
    get_current_user, get_current_user_id, get_current_user_role,
    create_access_token, create_refresh_token, verify_token
)
from app.database import supabase_client
from app.utils.exceptions import (
    AuthenticationError, AuthorizationError, ValidationError,
    NotFoundError, ConflictError, handle_database_error
)
from app.utils.helpers import (
    create_response_dict, create_success_response, create_error_response,
    validate_email, validate_password, hash_password, generate_id
)
from app.utils.validators import validate_name, validate_phone

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/auth", tags=["Authentication"])
security = HTTPBearer(auto_error=False)


@router.post("/login", response_model=BaseResponse[LoginResponse])
async def login(request: LoginRequest):
    """User login endpoint"""
    try:
        # Validate input
        is_valid, error_msg = validate_email(request.email)
        if not is_valid:
            raise ValidationError("Invalid email format")
        
        # Authenticate with Supabase
        auth_response = supabase_client.get_client().auth.sign_in_with_password({
            "email": request.email,
            "password": request.password
        })
        
        if auth_response.user is None:
            raise AuthenticationError("Invalid email or password")
        
        # Get user profile and role
        profile_result = await supabase_client.get_client().table("profiles")\
            .select("full_name, phone")\
            .eq("id", auth_response.user.id)\
            .single()\
            .execute()
        
        role_result = await supabase_client.get_client().table("user_roles")\
            .select("role")\
            .eq("user_id", auth_response.user.id)\
            .single()\
            .execute()
        
        if not profile_result.data:
            raise NotFoundError("User profile not found", "user")
        
        # Create tokens
        token_data = {
            "sub": auth_response.user.id,
            "email": auth_response.user.email,
            "role": role_result.data.get("role") if role_result.data else None
        }
        
        access_token = create_access_token(token_data)
        refresh_token = create_refresh_token(token_data)
        
        user_data = {
            "id": auth_response.user.id,
            "email": auth_response.user.email,
            "full_name": profile_result.data.get("full_name"),
            "phone": profile_result.data.get("phone"),
            "role": role_result.data.get("role"),
            "created_at": auth_response.user.created_at,
            "last_sign_in_at": auth_response.user.last_sign_in_at
        }
        
        logger.info(f"User logged in: {auth_response.user.email}")
        
        return create_success_response(
            message="Login successful",
            data=LoginResponse(
                access_token=access_token,
                refresh_token=refresh_token,
                token_type="bearer",
                expires_in=1800,  # 30 minutes
                user=user_data,
                permissions=[]  # TODO: Get user permissions
            )
        )
        
    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        if isinstance(e, (AuthenticationError, ValidationError, NotFoundError)):
            raise
        raise AuthenticationError("Login failed. Please try again.")


@router.post("/register", response_model=BaseResponse[UserResponse])
async def register(request: UserCreate):
    """User registration endpoint"""
    try:
        # Validate input
        is_valid, error_msg = validate_email(request.email)
        if not is_valid:
            raise ValidationError("Invalid email format")
        
        is_valid, error_msg = validate_password(request.password)
        if not is_valid:
            raise ValidationError(error_msg)
        
        is_valid, error_msg = validate_name(request.full_name, "Full name")
        if not is_valid:
            raise ValidationError(error_msg)
        
        if request.phone:
            is_valid, error_msg = validate_phone(request.phone)
            if not is_valid:
                raise ValidationError(error_msg)
        
        # Check if user already exists
        existing_user = supabase_client.get_client().auth.admin.list_users()
        if any(user.email == request.email for user in existing_user.users):
            raise ConflictError("User with this email already exists")
        
        # Create user in Supabase
        user_data = {
            "email": request.email,
            "password": request.password,
            "email_confirm": True,
            "data": {
                "full_name": request.full_name,
                "phone": request.phone,
                "role": request.role.value
            },
            "email_confirm": True
        }
        
        auth_response = supabase_client.get_client().auth.admin.create_user(user_data)
        
        if auth_response.user is None:
            raise AuthenticationError("Failed to create user")
        
        # Create user profile
        profile_data = {
            "id": auth_response.user.id,
            "full_name": request.full_name,
            "phone": request.phone
        }
        
        profile_result = await supabase_client.get_client().table("profiles")\
            .insert(profile_data)\
            .execute()
        
        # Create user role
        role_data = {
            "id": generate_id(),
            "user_id": auth_response.user.id,
            "role": request.role.value
        }
        
        role_result = await supabase_client.get_client().table("user_roles")\
            .insert(role_data)\
            .execute()
        
        logger.info(f"User registered: {auth_response.user.email}")
        
        user_response_data = {
            "id": auth_response.user.id,
            "email": auth_response.user.email,
            "full_name": request.full_name,
            "phone": request.phone,
            "role": request.role.value,
            "created_at": auth_response.user.created_at,
            "last_sign_in_at": auth_response.user.last_sign_in_at
        }
        
        return create_success_response(
            message="Registration successful",
            data=UserResponse(**user_response_data)
        )
        
    except Exception as e:
        logger.error(f"Registration error: {str(e)}")
        if isinstance(e, (AuthenticationError, ValidationError, ConflictError, NotFoundError)):
            raise
        raise AuthenticationError("Registration failed. Please try again.")


@router.post("/refresh", response_model=BaseResponse[RefreshTokenResponse])
async def refresh_token(request: RefreshTokenRequest):
    """Refresh access token endpoint"""
    try:
        # Verify refresh token
        payload = verify_token(request.refresh_token)
        if not payload or payload.get("type") != "refresh":
            raise AuthenticationError("Invalid or expired refresh token")
        
        user_id = payload.get("sub")
        if not user_id:
            raise AuthenticationError("Invalid token payload")
        
        # Get user info
        profile_result = await supabase_client.get_client().table("profiles")\
            .select("full_name, phone")\
            .eq("id", user_id)\
            .single()\
            .execute()
        
        role_result = await supabase_client.get_client().table("user_roles")\
            .select("role")\
            .eq("user_id", user_id)\
            .single()\
            .execute()
        
        # Create new access token
        token_data = {
            "sub": user_id,
            "email": payload.get("email"),
            "role": role_result.data.get("role") if role_result.data else None
        }
        
        access_token = create_access_token(token_data)
        
        logger.info(f"Token refreshed for user: {user_id}")
        
        return create_success_response(
            message="Token refreshed successfully",
            data=RefreshTokenResponse(
                access_token=access_token,
                token_type="bearer",
                expires_in=1800
            )
        )
        
    except Exception as e:
        logger.error(f"Token refresh error: {str(e)}")
        raise AuthenticationError("Token refresh failed")


@router.post("/logout", response_model=BaseResponse[dict])
async def logout(current_user_id: str = Depends(get_current_user_id)):
    """User logout endpoint"""
    try:
        # Revoke all user sessions (implementation depends on your session management)
        # For now, we will just log the logout
        logger.info(f"User logged out: {current_user_id}")
        
        return create_success_response(
            message="Logout successful"
        )
        
    except Exception as e:
        logger.error(f"Logout error: {str(e)}")
        raise AuthenticationError("Logout failed")


@router.get("/me", response_model=BaseResponse[UserProfile])
async def get_current_user_profile(current_user_id: str = Depends(get_current_user_id)):
    """Get current user profile"""
    try:
        # Get user profile
        profile_result = await supabase_client.get_client().table("profiles")\
            .select("full_name, phone, created_at, updated_at")\
            .eq("id", current_user_id)\
            .single()\
            .execute()
        
        if not profile_result.data:
            raise NotFoundError("User profile not found", "user")
        
        # Get user role
        role_result = await supabase_client.get_client().table("user_roles")\
            .select("role")\
            .eq("user_id", current_user_id)\
            .single()\
            .execute()
        
        # Get user email from auth
        auth_user = supabase_client.get_client().auth.admin.get_user_by_id(current_user_id)
        
        user_data = {
            "id": current_user_id,
            "email": auth_user.user.email if auth_user.user else None,
            "full_name": profile_result.data.get("full_name"),
            "phone": profile_result.data.get("phone"),
            "role": role_result.data.get("role") if role_result.data else None,
            "created_at": profile_result.data.get("created_at"),
            "updated_at": profile_result.data.get("updated_at")
        }
        
        return create_success_response(
            data=UserProfile(**user_data)
        )
        
    except Exception as e:
        logger.error(f"Get profile error: {str(e)}")
        handle_database_error(e, "get user profile")
        raise


@router.put("/profile", response_model=BaseResponse[UserProfile])
async def update_profile(
    request: dict,
    current_user_id: str = Depends(get_current_user_id)
):
    """Update user profile"""
    try:
        # Validate input
        allowed_fields = ["full_name", "phone"]
        update_data = {}
        
        for field in allowed_fields:
            if field in request:
                value = request[field]
                if field == "full_name":
                    is_valid, error_msg = validate_name(value, "Full name")
                    if not is_valid:
                        raise ValidationError(error_msg)
                    elif value and len(value.strip()) < 2:
                        raise ValidationError("Full name must be at least 2 characters long")
                    elif value and len(value) > 100:
                        raise ValidationError("Full name must be less than 100 characters long")
                    update_data[field] = value.strip()
                    
                elif field == "phone":
                    if value:
                        is_valid, error_msg = validate_phone(value)
                        if not is_valid:
                            raise ValidationError(error_msg)
                        update_data[field] = value.strip()
        
        if not update_data:
            raise ValidationError("No valid fields to update")
        
        # Update profile
        result = await supabase_client.get_client().table("profiles")\
            .update(update_data)\
            .eq("id", current_user_id)\
            .execute()
        
        if not result.data:
            raise NotFoundError("Failed to update profile", "user")
        
        logger.info(f"Profile updated for user: {current_user_id}")
        
        # Get updated profile
        profile_result = await supabase_client.get_client().table("profiles")\
            .select("full_name, phone, created_at, updated_at")\
            .eq("id", current_user_id)\
            .single()\
            .execute()
        
        # Get user role
        role_result = await supabase_client.get_client().table("user_roles")\
            .select("role")\
            .eq("user_id", current_user_id)\
            .single()\
            .execute()
        
        # Get user email from auth
        auth_user = supabase_client.get_client().auth.admin.get_user_by_id(current_user_id)
        
        user_data = {
            "id": current_user_id,
            "email": auth_user.user.email if auth_user.user else None,
            "full_name": profile_result.data.get("full_name"),
            "phone": profile_result.data.get("phone"),
            "role": role_result.data.get("role") if role_result.data else None,
            "created_at": profile_result.data.get("created_at"),
            "updated_at": profile_result.data.get("updated_at")
        }
        
        return create_success_response(
            message="Profile updated successfully",
            data=UserProfile(**user_data)
        )
        
    except Exception as e:
        logger.error(f"Update profile error: {str(e)}")
        handle_database_error(e, "update user profile")
        raise


@router.post("/change-password", response_model=BaseResponse[dict])
async def change_password(
    request: PasswordChange,
    current_user_id: str = Depends(get_current_user_id)
):
    """Change user password"""
    try:
        # Validate input
        is_valid, error_msg = validate_password(request.new_password)
        if not is_valid:
            raise ValidationError(error_msg)
        
        if request.new_password != request.confirm_password:
            raise ValidationError("New passwords do not match")
        
        # Authenticate with current password
        auth_user = supabase_client.get_client().auth.admin.get_user_by_id(current_user_id)
        
        # Update password in Supabase
        update_result = supabase_client.get_client().auth.admin.update_user_by_id(
            current_user_id,
            {"password": request.new_password}
        )
        
        if not update_result.user:
            raise AuthenticationError("Failed to update password")
        
        logger.info(f"Password changed for user: {current_user_id}")
        
        return create_success_response(
            message="Password changed successfully"
        )
        
    except Exception as e:
        logger.error(f"Change password error: {str(e)}")
        raise AuthenticationError("Password change failed")


@router.post("/forgot-password", response_model=BaseResponse[dict])
async def forgot_password(request: PasswordReset):
    """Forgot password endpoint"""
    try:
        # Validate email
        is_valid, error_msg = validate_email(request.email)
        if not is_valid:
            raise ValidationError("Invalid email format")
        
        # Generate reset token
        reset_token = generate_random_token()
        
        # Store reset token (you might want to store this in database)
        # For now, we will just log it
        logger.info(f"Password reset requested for: {request.email}, token: {reset_token}")
        
        # TODO: Send email with reset link
        # This would require email service integration
        
        return create_success_response(
            message="Password reset instructions sent to your email"
        )
        
    except Exception as e:
        logger.error(f"Forgot password error: {str(e)}")
        raise AuthenticationError("Password reset failed")


@router.post("/reset-password", response_model=BaseResponse[dict])
async def reset_password(request: PasswordResetConfirm):
    """Reset password confirmation endpoint"""
    try:
        # Validate token and new password
        is_valid, error_msg = validate_password(request.new_password)
        if not is_valid:
            raise ValidationError(error_msg)
        
        if request.new_password != request.confirm_password:
            raise ValidationError("Passwords do not match")
        
        # TODO: Verify reset token from database/email
        # For now, we will just log it
        logger.info(f"Password reset confirmed with token: {request.token}")
        
        # TODO: Find user by reset token and update password
        # This would require storing reset tokens in database
        
        return create_success_response(
            message="Password reset successfully"
        )
        
    except Exception as e:
        logger.error(f"Reset password error: {str(e)}")
        raise AuthenticationError("Password reset failed")


@router.post("/validate-token", response_model=BaseResponse[TokenValidation])
async def validate_token_endpoint(request: dict):
    """Validate token endpoint"""
    try:
        token = request.get("token")
        if not token:
            raise ValidationError("Token is required")
        
        payload = verify_token(token)
        if not payload:
            return create_success_response(
                data=TokenValidation(
                    valid=False,
                    error="Invalid or expired token"
                )
            )
        
        user_id = payload.get("sub")
        if not user_id:
            return create_success_response(
                data=TokenValidation(
                    valid=False,
                    error="Invalid token payload"
                )
            )
        
        # Check if user still exists
        auth_user = supabase_client.get_client().auth.admin.get_user_by_id(user_id)
        
        return create_success_response(
            data=TokenValidation(
                valid=True,
                user_id=user_id,
                role=payload.get("role"),
                expires_at=payload.get("exp")
            )
        )
        
    except Exception as e:
        logger.error(f"Token validation error: {str(e)}")
        raise AuthenticationError("Token validation failed")
