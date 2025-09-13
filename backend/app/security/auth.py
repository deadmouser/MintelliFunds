"""
Authentication and security module for Financial AI Assistant
"""
import os
import jwt
import hashlib
import secrets
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from fastapi import HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from passlib.context import CryptContext
import logging

logger = logging.getLogger(__name__)

# Security configuration
SECRET_KEY = os.getenv("SECRET_KEY", secrets.token_hex(32))
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT Bearer token authentication
security = HTTPBearer()

class SecurityManager:
    """Central security management class"""
    
    def __init__(self):
        self.secret_key = SECRET_KEY
        self.algorithm = ALGORITHM
        self.pwd_context = pwd_context
        
    def hash_password(self, password: str) -> str:
        """Hash a password using bcrypt"""
        return self.pwd_context.hash(password)
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash"""
        return self.pwd_context.verify(plain_password, hashed_password)
    
    def create_access_token(self, data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
        """Create a JWT access token"""
        to_encode = data.copy()
        
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        
        to_encode.update({"exp": expire, "type": "access"})
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt
    
    def create_refresh_token(self, data: Dict[str, Any]) -> str:
        """Create a JWT refresh token"""
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
        to_encode.update({"exp": expire, "type": "refresh"})
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt
    
    def decode_token(self, token: str) -> Dict[str, Any]:
        """Decode and validate a JWT token"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has expired",
                headers={"WWW-Authenticate": "Bearer"},
            )
        except jwt.JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
    
    def get_current_user(self, token: HTTPAuthorizationCredentials = Depends(security)) -> Dict[str, Any]:
        """Get current user from JWT token"""
        payload = self.decode_token(token.credentials)
        
        if payload.get("type") != "access":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token missing user ID",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        return {
            "user_id": user_id,
            "username": payload.get("username"),
            "permissions": payload.get("permissions", []),
            "exp": payload.get("exp")
        }
    
    def generate_api_key(self, user_id: str) -> str:
        """Generate a secure API key for a user"""
        raw_key = f"{user_id}:{secrets.token_hex(32)}:{datetime.utcnow().isoformat()}"
        api_key = hashlib.sha256(raw_key.encode()).hexdigest()
        return f"fa_{api_key[:32]}"  # fa_ prefix for Financial Assistant
    
    def validate_api_key(self, api_key: str) -> bool:
        """Validate an API key format"""
        if not api_key.startswith("fa_"):
            return False
        if len(api_key) != 35:  # fa_ + 32 chars
            return False
        return True
    
    def rate_limit_check(self, user_id: str, endpoint: str, limit_per_minute: int = 60) -> bool:
        """Basic rate limiting check (in production, use Redis or similar)"""
        # This is a basic implementation - in production use Redis
        # For now, we'll just log the request
        logger.info(f"Rate limit check: {user_id} accessing {endpoint}")
        return True  # Allow all requests for now
    
    def audit_log(self, user_id: str, action: str, details: Dict[str, Any] = None):
        """Log security-relevant actions"""
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "user_id": user_id,
            "action": action,
            "details": details or {},
            "ip_address": "unknown"  # Would get from request in real implementation
        }
        
        logger.info(f"AUDIT: {log_entry}")
        
        # In production, store in secure audit database
        # For now, just log to file
        try:
            with open("security_audit.log", "a") as f:
                f.write(f"{log_entry}\n")
        except Exception as e:
            logger.error(f"Failed to write audit log: {e}")

# Global security manager instance
security_manager = SecurityManager()

# Dependency functions for FastAPI
def get_current_user(token: HTTPAuthorizationCredentials = Depends(security)) -> Dict[str, Any]:
    """FastAPI dependency to get current authenticated user"""
    return security_manager.get_current_user(token)

def require_permission(permission: str):
    """FastAPI dependency factory to require specific permissions"""
    def permission_checker(current_user: Dict[str, Any] = Depends(get_current_user)):
        user_permissions = current_user.get("permissions", [])
        if permission not in user_permissions and "admin" not in user_permissions:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Missing required permission: {permission}"
            )
        return current_user
    return permission_checker

def get_optional_user(credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)):
    """Get user if authenticated, otherwise return None"""
    if not credentials:
        return None
    try:
        return security_manager.get_current_user(credentials)
    except HTTPException:
        return None

# Security middleware functions
def validate_request_size(max_size_mb: int = 10):
    """Validate request body size"""
    def size_validator(content_length: Optional[int] = None):
        if content_length and content_length > max_size_mb * 1024 * 1024:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"Request too large. Maximum size: {max_size_mb}MB"
            )
    return size_validator

def sanitize_input(text: str) -> str:
    """Basic input sanitization"""
    if not text:
        return ""
    
    # Remove potentially dangerous characters
    dangerous_chars = ["<", ">", "&", '"', "'", ";", "(", ")", "javascript:", "data:"]
    sanitized = text
    
    for char in dangerous_chars:
        sanitized = sanitized.replace(char, "")
    
    return sanitized.strip()

# Encryption utilities
class DataEncryption:
    """Simple data encryption utilities"""
    
    @staticmethod
    def encrypt_sensitive_data(data: str, key: Optional[str] = None) -> str:
        """Encrypt sensitive data (basic implementation)"""
        if not key:
            key = SECRET_KEY[:32]  # Use first 32 chars of secret key
        
        # In production, use proper encryption like Fernet
        # For now, just base64 encode with a simple transformation
        import base64
        encoded = base64.b64encode(data.encode()).decode()
        return f"enc_{encoded}"
    
    @staticmethod
    def decrypt_sensitive_data(encrypted_data: str, key: Optional[str] = None) -> str:
        """Decrypt sensitive data"""
        if not encrypted_data.startswith("enc_"):
            return encrypted_data  # Not encrypted
        
        import base64
        encoded = encrypted_data[4:]  # Remove "enc_" prefix
        decoded = base64.b64decode(encoded.encode()).decode()
        return decoded

# Security headers middleware
SECURITY_HEADERS = {
    "X-Content-Type-Options": "nosniff",
    "X-Frame-Options": "DENY",
    "X-XSS-Protection": "1; mode=block",
    "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
    "Content-Security-Policy": "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; img-src 'self' data: https:; connect-src 'self' http://localhost:*",
    "Referrer-Policy": "strict-origin-when-cross-origin",
    "Permissions-Policy": "geolocation=(), microphone=(), camera=()"
}

def add_security_headers(response):
    """Add security headers to response"""
    for header, value in SECURITY_HEADERS.items():
        response.headers[header] = value
    return response

# Mock user database (in production, use proper database)
MOCK_USERS = {
    "demo_user": {
        "user_id": "demo_user",
        "username": "demo_user",
        "hashed_password": security_manager.hash_password("demo_password"),
        "permissions": ["read_transactions", "read_accounts", "read_investments", "ai_chat"],
        "is_active": True,
        "created_at": datetime.utcnow().isoformat()
    },
    "admin_user": {
        "user_id": "admin_user", 
        "username": "admin_user",
        "hashed_password": security_manager.hash_password("admin_password"),
        "permissions": ["admin", "read_all", "write_all"],
        "is_active": True,
        "created_at": datetime.utcnow().isoformat()
    }
}

def authenticate_user(username: str, password: str) -> Optional[Dict[str, Any]]:
    """Authenticate a user with username and password"""
    user = MOCK_USERS.get(username)
    if not user or not user["is_active"]:
        return None
    
    if not security_manager.verify_password(password, user["hashed_password"]):
        return None
    
    # Log successful authentication
    security_manager.audit_log(user["user_id"], "login_success")
    return user

def create_user_tokens(user: Dict[str, Any]) -> Dict[str, str]:
    """Create access and refresh tokens for a user"""
    token_data = {
        "sub": user["user_id"],
        "username": user["username"],
        "permissions": user["permissions"]
    }
    
    access_token = security_manager.create_access_token(token_data)
    refresh_token = security_manager.create_refresh_token({"sub": user["user_id"]})
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }