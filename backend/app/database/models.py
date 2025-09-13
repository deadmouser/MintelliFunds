"""
Database models for Financial AI Assistant
"""
from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Text, ForeignKey, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
from typing import Dict, Any, Optional

Base = declarative_base()

class BaseModel(Base):
    """Base model with common fields"""
    __abstract__ = True
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    is_active = Column(Boolean, default=True)

class User(BaseModel):
    """User model for authentication"""
    __tablename__ = "users"
    
    username = Column(String(100), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(200))
    is_verified = Column(Boolean, default=False)
    is_admin = Column(Boolean, default=False)
    last_login = Column(DateTime)
    login_count = Column(Integer, default=0)
    
    # Relationships
    accounts = relationship("Account", back_populates="user")
    transactions = relationship("Transaction", back_populates="user")
    investments = relationship("Investment", back_populates="user")
    assets = relationship("Asset", back_populates="user")
    liabilities = relationship("Liability", back_populates="user")
    chat_messages = relationship("ChatMessage", back_populates="user")
    privacy_settings = relationship("PrivacySetting", back_populates="user")
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "full_name": self.full_name,
            "is_verified": self.is_verified,
            "is_admin": self.is_admin,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "last_login": self.last_login.isoformat() if self.last_login else None,
            "login_count": self.login_count
        }

class Account(BaseModel):
    """Financial accounts model"""
    __tablename__ = "accounts"
    
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    account_name = Column(String(200), nullable=False)
    account_type = Column(String(50), nullable=False)  # savings, checking, credit_card, etc.
    account_number = Column(String(100))  # Encrypted
    institution_name = Column(String(200))
    balance = Column(Float, default=0.0)
    currency = Column(String(10), default="INR")
    is_primary = Column(Boolean, default=False)
    
    # Relationships
    user = relationship("User", back_populates="accounts")
    transactions = relationship("Transaction", back_populates="account")
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "account_name": self.account_name,
            "account_type": self.account_type,
            "institution_name": self.institution_name,
            "balance": self.balance,
            "currency": self.currency,
            "is_primary": self.is_primary,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }

class Transaction(BaseModel):
    """Financial transactions model"""
    __tablename__ = "transactions"
    
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    account_id = Column(String(36), ForeignKey("accounts.id"), nullable=False)
    description = Column(String(500), nullable=False)
    amount = Column(Float, nullable=False)
    category = Column(String(100), nullable=False)
    subcategory = Column(String(100))
    transaction_type = Column(String(50), nullable=False)  # debit, credit
    transaction_date = Column(DateTime, nullable=False)
    merchant_name = Column(String(200))
    reference_id = Column(String(100))
    notes = Column(Text)
    tags = Column(JSON)  # For flexible tagging
    
    # Relationships
    user = relationship("User", back_populates="transactions")
    account = relationship("Account", back_populates="transactions")
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "description": self.description,
            "amount": self.amount,
            "category": self.category,
            "subcategory": self.subcategory,
            "transaction_type": self.transaction_type,
            "transaction_date": self.transaction_date.isoformat() if self.transaction_date else None,
            "merchant_name": self.merchant_name,
            "account_id": self.account_id,
            "notes": self.notes,
            "tags": self.tags
        }

class Investment(BaseModel):
    """Investment holdings model"""
    __tablename__ = "investments"
    
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    investment_name = Column(String(200), nullable=False)
    investment_type = Column(String(100), nullable=False)  # stocks, mutual_funds, bonds, etc.
    symbol = Column(String(50))  # Stock symbol or fund code
    quantity = Column(Float, default=0.0)
    purchase_price = Column(Float, default=0.0)
    current_price = Column(Float, default=0.0)
    total_value = Column(Float, default=0.0)
    currency = Column(String(10), default="INR")
    purchase_date = Column(DateTime)
    platform = Column(String(100))  # Zerodha, Groww, etc.
    
    # Relationships
    user = relationship("User", back_populates="investments")
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "investment_name": self.investment_name,
            "investment_type": self.investment_type,
            "symbol": self.symbol,
            "quantity": self.quantity,
            "purchase_price": self.purchase_price,
            "current_price": self.current_price,
            "total_value": self.total_value,
            "currency": self.currency,
            "purchase_date": self.purchase_date.isoformat() if self.purchase_date else None,
            "platform": self.platform
        }

class Asset(BaseModel):
    """Assets model"""
    __tablename__ = "assets"
    
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    asset_name = Column(String(200), nullable=False)
    asset_type = Column(String(100), nullable=False)  # property, vehicle, jewelry, etc.
    estimated_value = Column(Float, default=0.0)
    purchase_value = Column(Float, default=0.0)
    purchase_date = Column(DateTime)
    description = Column(Text)
    location = Column(String(200))
    documents = Column(JSON)  # Store document references
    
    # Relationships
    user = relationship("User", back_populates="assets")
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "asset_name": self.asset_name,
            "asset_type": self.asset_type,
            "estimated_value": self.estimated_value,
            "purchase_value": self.purchase_value,
            "purchase_date": self.purchase_date.isoformat() if self.purchase_date else None,
            "description": self.description,
            "location": self.location
        }

class Liability(BaseModel):
    """Liabilities model"""
    __tablename__ = "liabilities"
    
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    liability_name = Column(String(200), nullable=False)
    liability_type = Column(String(100), nullable=False)  # loan, credit_card, mortgage, etc.
    outstanding_balance = Column(Float, default=0.0)
    original_amount = Column(Float, default=0.0)
    interest_rate = Column(Float, default=0.0)
    monthly_payment = Column(Float, default=0.0)
    due_date = Column(DateTime)
    institution_name = Column(String(200))
    account_number = Column(String(100))  # Encrypted
    
    # Relationships
    user = relationship("User", back_populates="liabilities")
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "liability_name": self.liability_name,
            "liability_type": self.liability_type,
            "outstanding_balance": self.outstanding_balance,
            "original_amount": self.original_amount,
            "interest_rate": self.interest_rate,
            "monthly_payment": self.monthly_payment,
            "due_date": self.due_date.isoformat() if self.due_date else None,
            "institution_name": self.institution_name
        }

class ChatMessage(BaseModel):
    """AI chat messages model"""
    __tablename__ = "chat_messages"
    
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    message_type = Column(String(20), nullable=False)  # user, assistant
    content = Column(Text, nullable=False)
    intent = Column(String(100))
    confidence = Column(Float)
    context_data = Column(JSON)
    response_time = Column(Float)  # In milliseconds
    
    # Relationships
    user = relationship("User", back_populates="chat_messages")
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "message_type": self.message_type,
            "content": self.content,
            "intent": self.intent,
            "confidence": self.confidence,
            "context_data": self.context_data,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "response_time": self.response_time
        }

class PrivacySetting(BaseModel):
    """User privacy settings model"""
    __tablename__ = "privacy_settings"
    
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False, unique=True)
    transactions_enabled = Column(Boolean, default=True)
    accounts_enabled = Column(Boolean, default=True)
    assets_enabled = Column(Boolean, default=True)
    liabilities_enabled = Column(Boolean, default=True)
    epf_enabled = Column(Boolean, default=True)
    credit_score_enabled = Column(Boolean, default=False)  # Sensitive, default off
    investments_enabled = Column(Boolean, default=True)
    spending_trends_enabled = Column(Boolean, default=True)
    category_breakdown_enabled = Column(Boolean, default=True)
    dashboard_insights_enabled = Column(Boolean, default=True)
    
    # Relationships
    user = relationship("User", back_populates="privacy_settings")
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "user_id": self.user_id,
            "transactions": self.transactions_enabled,
            "accounts": self.accounts_enabled,
            "assets": self.assets_enabled,
            "liabilities": self.liabilities_enabled,
            "epf_balance": self.epf_enabled,
            "credit_score": self.credit_score_enabled,
            "investments": self.investments_enabled,
            "spending_trends": self.spending_trends_enabled,
            "category_breakdown": self.category_breakdown_enabled,
            "dashboard_insights": self.dashboard_insights_enabled
        }

class AuditLog(BaseModel):
    """Security and audit logging model"""
    __tablename__ = "audit_logs"
    
    user_id = Column(String(36), ForeignKey("users.id"), nullable=True)
    action = Column(String(100), nullable=False)
    resource = Column(String(100))
    resource_id = Column(String(36))
    ip_address = Column(String(45))
    user_agent = Column(Text)
    details = Column(JSON)
    success = Column(Boolean, default=True)
    error_message = Column(Text)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "user_id": self.user_id,
            "action": self.action,
            "resource": self.resource,
            "resource_id": self.resource_id,
            "ip_address": self.ip_address,
            "details": self.details,
            "success": self.success,
            "error_message": self.error_message,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }

class AICache(BaseModel):
    """AI response caching model"""
    __tablename__ = "ai_cache"
    
    query_hash = Column(String(64), unique=True, nullable=False, index=True)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    query_text = Column(Text, nullable=False)
    response_data = Column(JSON, nullable=False)
    intent = Column(String(100))
    confidence = Column(Float)
    cache_expires = Column(DateTime, nullable=False)
    hit_count = Column(Integer, default=1)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "query_hash": self.query_hash,
            "query_text": self.query_text,
            "response_data": self.response_data,
            "intent": self.intent,
            "confidence": self.confidence,
            "hit_count": self.hit_count,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "cache_expires": self.cache_expires.isoformat() if self.cache_expires else None
        }

# Utility function to get all model classes
def get_all_models():
    """Return all database model classes"""
    return [
        User, Account, Transaction, Investment, Asset, 
        Liability, ChatMessage, PrivacySetting, AuditLog, AICache
    ]