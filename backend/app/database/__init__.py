"""
Database module for Financial AI Assistant
"""

from .models import (
    Base,
    BaseModel, 
    User,
    Account,
    Transaction,
    Investment,
    Asset,
    Liability,
    ChatMessage,
    PrivacySetting,
    AuditLog,
    AICache,
    get_all_models
)

from .connection import (
    DatabaseManager,
    db_manager,
    get_db,
    run_migrations,
    create_initial_admin_user,
    migrate_json_data
)

__all__ = [
    # Models
    "Base",
    "BaseModel",
    "User", 
    "Account",
    "Transaction",
    "Investment",
    "Asset",
    "Liability", 
    "ChatMessage",
    "PrivacySetting",
    "AuditLog",
    "AICache",
    "get_all_models",
    
    # Connection and management
    "DatabaseManager",
    "db_manager",
    "get_db",
    "run_migrations", 
    "create_initial_admin_user",
    "migrate_json_data"
]