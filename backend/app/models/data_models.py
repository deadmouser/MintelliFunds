"""
Pydantic models for financial data structures
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from decimal import Decimal


class Transaction(BaseModel):
    """Transaction data model"""
    id: str = Field(..., description="Unique transaction ID")
    date: str = Field(..., description="Transaction date in ISO format")
    amount: float = Field(..., description="Transaction amount")
    description: str = Field(..., description="Transaction description")
    category: str = Field(..., description="Transaction category")
    account: str = Field(..., description="Account name")
    type: str = Field(..., description="Transaction type (income/expense)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "txn_001",
                "date": "2024-01-15T10:30:00Z",
                "amount": -150.50,
                "description": "Grocery shopping at SuperMart",
                "category": "Food & Dining",
                "account": "Checking Account",
                "type": "expense"
            }
        }


class Asset(BaseModel):
    """Asset data model"""
    id: str = Field(..., description="Unique asset ID")
    name: str = Field(..., description="Asset name")
    type: str = Field(..., description="Asset type")
    value: float = Field(..., description="Current asset value")
    currency: str = Field(default="USD", description="Currency code")
    last_updated: str = Field(..., description="Last update timestamp")
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "asset_001",
                "name": "Primary Residence",
                "type": "real_estate",
                "value": 450000.00,
                "currency": "USD",
                "last_updated": "2024-01-15T10:30:00Z"
            }
        }


class Liability(BaseModel):
    """Liability data model"""
    id: str = Field(..., description="Unique liability ID")
    name: str = Field(..., description="Liability name")
    type: str = Field(..., description="Liability type")
    balance: float = Field(..., description="Current balance")
    interest_rate: float = Field(..., description="Interest rate percentage")
    monthly_payment: float = Field(..., description="Monthly payment amount")
    currency: str = Field(default="USD", description="Currency code")
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "liab_001",
                "name": "Home Mortgage",
                "type": "mortgage",
                "balance": 320000.00,
                "interest_rate": 3.5,
                "monthly_payment": 1800.00,
                "currency": "USD"
            }
        }


class Investment(BaseModel):
    """Investment data model"""
    id: str = Field(..., description="Unique investment ID")
    symbol: str = Field(..., description="Investment symbol")
    name: str = Field(..., description="Investment name")
    type: str = Field(..., description="Investment type")
    quantity: float = Field(..., description="Number of shares/units")
    current_price: float = Field(..., description="Current price per unit")
    total_value: float = Field(..., description="Total current value")
    currency: str = Field(default="USD", description="Currency code")
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "inv_001",
                "symbol": "AAPL",
                "name": "Apple Inc.",
                "type": "stock",
                "quantity": 100.0,
                "current_price": 150.25,
                "total_value": 15025.00,
                "currency": "USD"
            }
        }


class Account(BaseModel):
    """Account data model"""
    id: str = Field(..., description="Unique account ID")
    name: str = Field(..., description="Account name")
    type: str = Field(..., description="Account type")
    balance: float = Field(..., description="Current balance")
    currency: str = Field(default="USD", description="Currency code")
    last_updated: str = Field(..., description="Last update timestamp")
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "acc_001",
                "name": "Primary Checking",
                "type": "checking",
                "balance": 2500.75,
                "currency": "USD",
                "last_updated": "2024-01-15T10:30:00Z"
            }
        }


class SpendingTrend(BaseModel):
    """Spending trend data model"""
    period: str = Field(..., description="Time period")
    total_spending: float = Field(..., description="Total spending for period")
    average_daily: float = Field(..., description="Average daily spending")
    trend_direction: str = Field(..., description="Trend direction (up/down/stable)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "period": "2024-01",
                "total_spending": 3200.50,
                "average_daily": 103.24,
                "trend_direction": "up"
            }
        }


class CategoryBreakdown(BaseModel):
    """Category breakdown data model"""
    category: str = Field(..., description="Spending category")
    amount: float = Field(..., description="Amount spent in category")
    percentage: float = Field(..., description="Percentage of total spending")
    transaction_count: int = Field(..., description="Number of transactions")
    
    class Config:
        json_schema_extra = {
            "example": {
                "category": "Food & Dining",
                "amount": 850.25,
                "percentage": 26.5,
                "transaction_count": 45
            }
        }


class DashboardInsight(BaseModel):
    """Dashboard insight data model"""
    id: str = Field(..., description="Unique insight ID")
    title: str = Field(..., description="Insight title")
    description: str = Field(..., description="Insight description")
    type: str = Field(..., description="Insight type")
    priority: str = Field(..., description="Priority level")
    actionable: bool = Field(..., description="Whether insight is actionable")
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "insight_001",
                "title": "High Dining Expenses",
                "description": "Your dining expenses are 30% higher than last month",
                "type": "spending_alert",
                "priority": "medium",
                "actionable": True
            }
        }
