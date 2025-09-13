"""
Authentication endpoints for Financial AI Assistant API
"""
from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import HTTPAuthorizationCredentials
from pydantic import BaseModel
from typing import Dict, Any
import logging
from datetime import datetime

from ..security import (
    authenticate_user,
    create_user_tokens,
    security_manager,
    get_current_user,
    get_optional_user,
    sanitize_input,
    add_security_headers,
    require_permission
)

logger = logging.getLogger(__name__)

# Create router instance
router = APIRouter(prefix="/api/auth", tags=["authentication"])

# Request/Response models
class LoginRequest(BaseModel):
    username: str
    password: str

class LoginResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str
    expires_in: int
    user_info: Dict[str, Any]

class RefreshTokenRequest(BaseModel):
    refresh_token: str

class UserInfoResponse(BaseModel):
    user_id: str
    username: str
    permissions: list
    is_active: bool

@router.post("/login", response_model=LoginResponse)
async def login(login_data: LoginRequest):
    """
    Authenticate user and return access tokens
    
    Args:
        login_data: Login credentials
        
    Returns:
        Access token, refresh token, and user information
        
    Raises:
        HTTPException: If authentication fails
    """
    try:
        # Sanitize input
        username = sanitize_input(login_data.username)
        password = login_data.password  # Don't sanitize password
        
        logger.info(f"Login attempt for user: {username}")
        
        # Authenticate user
        user = authenticate_user(username, password)
        if not user:
            # Log failed attempt
            security_manager.audit_log(username, "login_failed", {"reason": "invalid_credentials"})
            
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Create tokens
        tokens = create_user_tokens(user)
        
        # Log successful login
        security_manager.audit_log(user["user_id"], "login_success")
        
        # Prepare response
        response_data = {
            "access_token": tokens["access_token"],
            "refresh_token": tokens["refresh_token"], 
            "token_type": tokens["token_type"],
            "expires_in": 1800,  # 30 minutes in seconds
            "user_info": {
                "user_id": user["user_id"],
                "username": user["username"],
                "permissions": user["permissions"],
                "is_active": user["is_active"]
            }
        }
        
        logger.info(f"Login successful for user: {username}")
        return response_data
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Authentication service error"
        )

@router.post("/refresh", response_model=Dict[str, Any])
async def refresh_access_token(refresh_data: RefreshTokenRequest):
    """
    Refresh access token using refresh token
    
    Args:
        refresh_data: Refresh token request
        
    Returns:
        New access token
    """
    try:
        # Decode and validate refresh token
        payload = security_manager.decode_token(refresh_data.refresh_token)
        
        if payload.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )
        
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )
        
        # Create new access token
        # In production, verify user still exists and is active
        token_data = {
            "sub": user_id,
            "username": user_id,  # Simplified for demo
            "permissions": ["read_transactions", "read_accounts", "ai_chat"]
        }
        
        new_access_token = security_manager.create_access_token(token_data)
        
        # Log token refresh
        security_manager.audit_log(user_id, "token_refresh")
        
        return {
            "access_token": new_access_token,
            "token_type": "bearer",
            "expires_in": 1800
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Token refresh error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )

@router.post("/logout")
async def logout(current_user: Dict[str, Any] = Depends(get_current_user)):
    """
    Logout user (invalidate tokens)
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        Success message
    """
    try:
        user_id = current_user["user_id"]
        
        # Log logout
        security_manager.audit_log(user_id, "logout")
        
        # In production, add token to blacklist
        logger.info(f"User logged out: {user_id}")
        
        return {
            "message": "Successfully logged out",
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }
        
    except Exception as e:
        logger.error(f"Logout error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Logout service error"
        )

@router.get("/me", response_model=UserInfoResponse)
async def get_current_user_info(current_user: Dict[str, Any] = Depends(get_current_user)):
    """
    Get current user information
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        User information
    """
    return {
        "user_id": current_user["user_id"],
        "username": current_user["username"],
        "permissions": current_user["permissions"],
        "is_active": True
    }

@router.get("/verify")
async def verify_token(current_user: Dict[str, Any] = Depends(get_optional_user)):
    """
    Verify if token is valid
    
    Args:
        current_user: Current user if authenticated, None otherwise
        
    Returns:
        Token validity status
    """
    if current_user:
        return {
            "valid": True,
            "user_id": current_user["user_id"],
            "expires_at": current_user.get("exp"),
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }
    else:
        return {
            "valid": False,
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }

@router.get("/permissions")
async def get_user_permissions(current_user: Dict[str, Any] = Depends(get_current_user)):
    """
    Get current user's permissions
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        User permissions and capabilities
    """
    permissions = current_user.get("permissions", [])
    
    # Map permissions to capabilities
    capabilities = {
        "can_read_transactions": "read_transactions" in permissions or "admin" in permissions,
        "can_read_accounts": "read_accounts" in permissions or "admin" in permissions,
        "can_read_investments": "read_investments" in permissions or "admin" in permissions,
        "can_use_ai_chat": "ai_chat" in permissions or "admin" in permissions,
        "can_export_data": "export_data" in permissions or "admin" in permissions,
        "is_admin": "admin" in permissions
    }
    
    return {
        "user_id": current_user["user_id"],
        "permissions": permissions,
        "capabilities": capabilities,
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }

@router.post("/change-password")
async def change_password(
    current_password: str,
    new_password: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Change user password
    
    Args:
        current_password: Current password
        new_password: New password
        current_user: Current authenticated user
        
    Returns:
        Success message
    """
    try:
        # In production, verify current password and update in database
        user_id = current_user["user_id"]
        
        # Basic validation
        if len(new_password) < 8:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Password must be at least 8 characters long"
            )
        
        # Log password change
        security_manager.audit_log(user_id, "password_change")
        
        logger.info(f"Password changed for user: {user_id}")
        
        return {
            "message": "Password changed successfully",
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Password change error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Password change service error"
        )

@router.get("/audit-log")
async def get_audit_log(
    limit: int = 50,
    current_user: Dict[str, Any] = Depends(require_permission("admin"))
):
    """
    Get security audit log (admin only)
    
    Args:
        limit: Number of log entries to return
        current_user: Current authenticated admin user
        
    Returns:
        Audit log entries
    """
    try:
        # In production, read from secure audit database
        # For now, return mock data
        mock_audit_entries = [
            {
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "user_id": "demo_user",
                "action": "login_success",
                "details": {"ip_address": "127.0.0.1"},
                "id": "audit_001"
            },
            {
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "user_id": "demo_user", 
                "action": "api_access",
                "details": {"endpoint": "/api/dashboard", "method": "GET"},
                "id": "audit_002"
            }
        ]
        
        return {
            "audit_entries": mock_audit_entries[:limit],
            "total_entries": len(mock_audit_entries),
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }
        
    except Exception as e:
        logger.error(f"Audit log retrieval error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Audit log service error"
        )

