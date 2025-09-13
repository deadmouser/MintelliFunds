"""
Configuration settings for Financial AI Assistant
"""
import os
from typing import List, Optional
from pydantic import BaseSettings, validator
import secrets
from enum import Enum

class Environment(str, Enum):
    """Application environment types"""
    DEVELOPMENT = "development"
    TESTING = "testing"
    STAGING = "staging" 
    PRODUCTION = "production"

class LogLevel(str, Enum):
    """Logging levels"""
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

class Settings(BaseSettings):
    """Application settings with environment variable support"""
    
    # Application settings
    APP_NAME: str = "Financial AI Assistant"
    APP_VERSION: str = "1.0.0"
    ENVIRONMENT: Environment = Environment.DEVELOPMENT
    DEBUG: bool = True
    
    # Server settings
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    WORKERS: int = 1
    RELOAD: bool = True
    
    # Security settings
    SECRET_KEY: str = secrets.token_hex(32)
    JWT_SECRET_KEY: str = secrets.token_hex(32)
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # API settings
    API_V1_STR: str = "/api"
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:8080", "http://127.0.0.1:3000"]
    ALLOWED_HOSTS: List[str] = ["*"]
    
    # Rate limiting
    RATE_LIMIT_REQUESTS: int = 100
    RATE_LIMIT_PERIOD: int = 60  # seconds
    
    # Database settings (for future use)
    DATABASE_URL: Optional[str] = None
    DATABASE_ECHO: bool = False
    DATABASE_POOL_SIZE: int = 10
    DATABASE_MAX_OVERFLOW: int = 20
    
    # Redis settings (for caching and rate limiting)
    REDIS_URL: Optional[str] = None
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_PASSWORD: Optional[str] = None
    
    # AI/ML service settings
    GOOGLE_AI_API_KEY: Optional[str] = None
    OPENAI_API_KEY: Optional[str] = None
    AI_SERVICE_TIMEOUT: int = 30
    AI_SERVICE_RETRIES: int = 3
    
    # File storage settings
    DATA_DIR: str = "data"
    UPLOAD_DIR: str = "uploads"
    MAX_UPLOAD_SIZE: int = 10 * 1024 * 1024  # 10MB
    ALLOWED_FILE_TYPES: List[str] = [".json", ".csv", ".xlsx"]
    
    # Logging settings
    LOG_LEVEL: LogLevel = LogLevel.INFO
    LOG_FILE: Optional[str] = None
    LOG_ROTATION: str = "1 day"
    LOG_RETENTION: str = "30 days"
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # Monitoring and observability
    ENABLE_METRICS: bool = False
    METRICS_PORT: int = 9090
    ENABLE_HEALTH_CHECKS: bool = True
    ENABLE_PROFILING: bool = False
    
    # Email settings (for notifications)
    SMTP_HOST: Optional[str] = None
    SMTP_PORT: int = 587
    SMTP_USERNAME: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    SMTP_USE_TLS: bool = True
    FROM_EMAIL: Optional[str] = None
    
    # Backup and disaster recovery
    BACKUP_ENABLED: bool = False
    BACKUP_SCHEDULE: str = "0 2 * * *"  # Daily at 2 AM
    BACKUP_RETENTION_DAYS: int = 30
    BACKUP_LOCATION: Optional[str] = None
    
    # Feature flags
    ENABLE_AUTHENTICATION: bool = False
    ENABLE_RATE_LIMITING: bool = False
    ENABLE_ANALYTICS: bool = False
    ENABLE_CACHING: bool = False
    ENABLE_BACKGROUND_TASKS: bool = False
    
    # Testing settings
    TESTING: bool = False
    TEST_DATABASE_URL: Optional[str] = None
    
    @validator("ENVIRONMENT", pre=True)
    def validate_environment(cls, v):
        if isinstance(v, str):
            return Environment(v.lower())
        return v
    
    @validator("LOG_LEVEL", pre=True) 
    def validate_log_level(cls, v):
        if isinstance(v, str):
            return LogLevel(v.lower())
        return v
    
    @validator("CORS_ORIGINS", pre=True)
    def validate_cors_origins(cls, v):
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v
    
    @validator("ALLOWED_HOSTS", pre=True)
    def validate_allowed_hosts(cls, v):
        if isinstance(v, str):
            return [host.strip() for host in v.split(",")]
        return v
    
    @property
    def is_development(self) -> bool:
        """Check if running in development environment"""
        return self.ENVIRONMENT == Environment.DEVELOPMENT
    
    @property
    def is_production(self) -> bool:
        """Check if running in production environment"""
        return self.ENVIRONMENT == Environment.PRODUCTION
    
    @property
    def is_testing(self) -> bool:
        """Check if running in testing environment"""
        return self.ENVIRONMENT == Environment.TESTING or self.TESTING
    
    def get_database_url(self) -> str:
        """Get database URL with fallback to SQLite for development"""
        if self.DATABASE_URL:
            return self.DATABASE_URL
        
        if self.is_production:
            raise ValueError("DATABASE_URL must be set in production environment")
        
        # Default SQLite for development
        return "sqlite:///./financial_ai.db"
    
    def get_redis_url(self) -> str:
        """Get Redis URL"""
        if self.REDIS_URL:
            return self.REDIS_URL
        
        auth_part = f":{self.REDIS_PASSWORD}@" if self.REDIS_PASSWORD else ""
        return f"redis://{auth_part}{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True

class DevelopmentSettings(Settings):
    """Development environment settings"""
    ENVIRONMENT: Environment = Environment.DEVELOPMENT
    DEBUG: bool = True
    RELOAD: bool = True
    LOG_LEVEL: LogLevel = LogLevel.DEBUG
    
    # More permissive CORS for development
    CORS_ORIGINS: List[str] = ["*"]
    
    # Disable authentication for easier development
    ENABLE_AUTHENTICATION: bool = False

class ProductionSettings(Settings):
    """Production environment settings"""
    ENVIRONMENT: Environment = Environment.PRODUCTION
    DEBUG: bool = False
    RELOAD: bool = False
    LOG_LEVEL: LogLevel = LogLevel.INFO
    
    # Security hardening for production
    ENABLE_AUTHENTICATION: bool = True
    ENABLE_RATE_LIMITING: bool = True
    ENABLE_ANALYTICS: bool = True
    ENABLE_CACHING: bool = True
    
    # Stricter CORS in production
    CORS_ORIGINS: List[str] = []  # Must be explicitly set
    
    # Enable monitoring
    ENABLE_METRICS: bool = True
    ENABLE_HEALTH_CHECKS: bool = True
    
    # Backup enabled by default
    BACKUP_ENABLED: bool = True

class TestingSettings(Settings):
    """Testing environment settings"""
    ENVIRONMENT: Environment = Environment.TESTING
    TESTING: bool = True
    DEBUG: bool = True
    LOG_LEVEL: LogLevel = LogLevel.DEBUG
    
    # Use in-memory database for testing
    DATABASE_URL: str = "sqlite:///:memory:"
    
    # Disable external services in testing
    ENABLE_AUTHENTICATION: bool = False
    ENABLE_RATE_LIMITING: bool = False
    ENABLE_ANALYTICS: bool = False

def get_settings() -> Settings:
    """Get application settings based on environment"""
    environment = os.getenv("ENVIRONMENT", "development").lower()
    
    if environment == "production":
        return ProductionSettings()
    elif environment == "testing":
        return TestingSettings()
    else:
        return DevelopmentSettings()

# Global settings instance
settings = get_settings()

def create_directories():
    """Create necessary directories"""
    directories = [
        settings.DATA_DIR,
        settings.UPLOAD_DIR,
        "logs",
        "backups",
        "temp"
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)

def validate_production_settings():
    """Validate that all required production settings are set"""
    if not settings.is_production:
        return
    
    required_settings = [
        "SECRET_KEY",
        "JWT_SECRET_KEY", 
        "DATABASE_URL"
    ]
    
    missing = []
    for setting in required_settings:
        if not getattr(settings, setting, None):
            missing.append(setting)
    
    if missing:
        raise ValueError(f"Missing required production settings: {', '.join(missing)}")

def get_cors_settings():
    """Get CORS settings for FastAPI"""
    if settings.is_development:
        return {
            "allow_origins": ["*"],
            "allow_credentials": True,
            "allow_methods": ["*"],
            "allow_headers": ["*"],
        }
    else:
        return {
            "allow_origins": settings.CORS_ORIGINS,
            "allow_credentials": True,
            "allow_methods": ["GET", "POST", "PUT", "DELETE"],
            "allow_headers": ["*"],
        }

# Initialize on import
create_directories()
if settings.is_production:
    validate_production_settings()