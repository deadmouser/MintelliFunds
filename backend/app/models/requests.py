"""
Pydantic models for request validation
"""
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any


class Permissions(BaseModel):
    """Permissions model for data access control"""
    transactions: bool = Field(default=False, description="Access to transaction data")
    assets: bool = Field(default=False, description="Access to assets data")
    liabilities: bool = Field(default=False, description="Access to liabilities data")
    epf_balance: bool = Field(default=False, description="Access to EPF balance data")
    credit_score: bool = Field(default=False, description="Access to credit score data")
    investments: bool = Field(default=False, description="Access to investments data")
    accounts: bool = Field(default=False, description="Access to accounts data")
    spending_trends: bool = Field(default=False, description="Access to spending trends data")
    category_breakdown: bool = Field(default=False, description="Access to category breakdown data")
    dashboard_insights: bool = Field(default=False, description="Access to dashboard insights data")


class InsightsRequest(BaseModel):
    """Request model for the /api/insights endpoint"""
    query: str = Field(..., min_length=1, max_length=1000, description="Natural language query from user")
    permissions: Permissions = Field(..., description="Data access permissions")
    
    class Config:
        json_schema_extra = {
            "example": {
                "query": "What are my spending patterns this month?",
                "permissions": {
                    "transactions": True,
                    "assets": False,
                    "liabilities": False,
                    "epf_balance": False,
                    "credit_score": False,
                    "investments": True,
                    "accounts": True,
                    "spending_trends": True,
                    "category_breakdown": True,
                    "dashboard_insights": True
                }
            }
        }


class InsightsResponse(BaseModel):
    """Response model for the /api/insights endpoint"""
    query: str = Field(..., description="Original user query")
    filtered_data: Dict[str, Any] = Field(..., description="Data filtered based on permissions")
    timestamp: str = Field(..., description="Response timestamp")
    status: str = Field(default="success", description="Response status")
    
    class Config:
        json_schema_extra = {
            "example": {
                "query": "What are my spending patterns this month?",
                "filtered_data": {
                    "transactions": [...],
                    "spending_trends": [...],
                    "category_breakdown": [...]
                },
                "timestamp": "2024-01-15T10:30:00Z",
                "status": "success"
            }
        }
