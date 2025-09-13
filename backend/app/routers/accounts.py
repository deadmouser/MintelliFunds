"""
API router for account-related endpoints
"""
from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any, List, Optional
import logging
from datetime import datetime

from ..models.requests import Permissions
from ..services.data_service import DataService
from ..services.privacy_service import PrivacyService

logger = logging.getLogger(__name__)

# Create router instance
router = APIRouter(prefix="/api", tags=["accounts"])

# Initialize services
data_service = DataService()
privacy_service = PrivacyService()


def get_default_permissions() -> Permissions:
    """Get default permissions for testing (all enabled)"""
    return Permissions(
        transactions=True,
        accounts=True,
        assets=True,
        liabilities=True,
        epf_balance=True,
        credit_score=True,
        investments=True,
        spending_trends=True,
        category_breakdown=True,
        dashboard_insights=True
    )


@router.get("/accounts")
async def get_accounts(
    permissions: Permissions = Depends(get_default_permissions)
) -> Dict[str, Any]:
    """
    Get all user accounts
    
    Args:
        permissions: User's data access permissions
        
    Returns:
        Dictionary containing accounts and summary information
    """
    try:
        logger.info("Fetching user accounts")
        
        # Check if user has permission to access accounts
        if not permissions.accounts:
            raise HTTPException(
                status_code=403,
                detail="Access denied: Account data permission required"
            )
        
        # Load all data
        all_data = data_service.load_all_data()
        
        # Get accounts
        accounts = all_data.get("accounts", [])
        
        # Calculate summary statistics
        total_balance = sum(acc.get("balance", 0) for acc in accounts)
        account_count = len(accounts)
        
        # Group by account type
        account_types = {}
        for acc in accounts:
            acc_type = acc.get("type", "Unknown")
            if acc_type not in account_types:
                account_types[acc_type] = {"count": 0, "total_balance": 0}
            account_types[acc_type]["count"] += 1
            account_types[acc_type]["total_balance"] += acc.get("balance", 0)
        
        return {
            "accounts": accounts,
            "summary": {
                "total_balance": round(total_balance, 2),
                "account_count": account_count,
                "account_types": account_types
            },
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching accounts: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )


@router.get("/accounts/{account_id}/balance")
async def get_account_balance(
    account_id: str,
    permissions: Permissions = Depends(get_default_permissions)
) -> Dict[str, Any]:
    """
    Get balance for a specific account
    
    Args:
        account_id: ID of the account
        permissions: User's data access permissions
        
    Returns:
        Dictionary containing account balance information
    """
    try:
        logger.info(f"Fetching balance for account: {account_id}")
        
        # Check permissions
        if not permissions.accounts:
            raise HTTPException(
                status_code=403,
                detail="Access denied: Account data permission required"
            )
        
        # Load data
        all_data = data_service.load_all_data()
        accounts = all_data.get("accounts", [])
        
        # Find account by ID
        account = next((acc for acc in accounts if acc.get("id") == account_id), None)
        
        if not account:
            raise HTTPException(
                status_code=404,
                detail=f"Account with ID {account_id} not found"
            )
        
        return {
            "account_id": account_id,
            "account_name": account.get("name", "Unknown Account"),
            "balance": account.get("balance", 0),
            "currency": account.get("currency", "USD"),
            "last_updated": account.get("last_updated", datetime.utcnow().isoformat() + "Z"),
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching account balance for {account_id}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )


@router.get("/net-worth")
async def get_net_worth(
    permissions: Permissions = Depends(get_default_permissions)
) -> Dict[str, Any]:
    """
    Calculate and return net worth
    
    Args:
        permissions: User's data access permissions
        
    Returns:
        Dictionary containing net worth calculation
    """
    try:
        logger.info("Calculating net worth")
        
        # Check permissions
        if not permissions.accounts or not permissions.assets or not permissions.liabilities:
            raise HTTPException(
                status_code=403,
                detail="Access denied: Account, asset, and liability data permissions required"
            )
        
        # Load data
        all_data = data_service.load_all_data()
        accounts = all_data.get("accounts", [])
        assets = all_data.get("assets", [])
        liabilities = all_data.get("liabilities", [])
        
        # Calculate totals
        total_assets = sum(acc.get("balance", 0) for acc in accounts)
        total_assets += sum(asset.get("value", 0) for asset in assets)
        total_liabilities = sum(liab.get("balance", 0) for liab in liabilities)
        net_worth = total_assets - total_liabilities
        
        return {
            "net_worth": round(net_worth, 2),
            "total_assets": round(total_assets, 2),
            "total_liabilities": round(total_liabilities, 2),
            "breakdown": {
                "liquid_assets": round(sum(acc.get("balance", 0) for acc in accounts), 2),
                "other_assets": round(sum(asset.get("value", 0) for asset in assets), 2),
                "total_debt": round(total_liabilities, 2)
            },
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error calculating net worth: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )
