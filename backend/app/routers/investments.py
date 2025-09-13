"""
API router for investment-related endpoints
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
router = APIRouter(prefix="/api", tags=["investments"])

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


@router.get("/investments")
async def get_investments(
    permissions: Permissions = Depends(get_default_permissions)
) -> Dict[str, Any]:
    """
    Get all user investments
    
    Args:
        permissions: User's data access permissions
        
    Returns:
        Dictionary containing investments and portfolio summary
    """
    try:
        logger.info("Fetching user investments")
        
        # Check if user has permission to access investments
        if not permissions.investments:
            raise HTTPException(
                status_code=403,
                detail="Access denied: Investment data permission required"
            )
        
        # Load all data
        all_data = data_service.load_all_data()
        
        # Get investments
        investments = all_data.get("investments", [])
        
        # Calculate portfolio summary
        total_value = sum(inv.get("total_value", 0) for inv in investments)
        total_invested = sum(inv.get("invested_amount", 0) for inv in investments)
        total_gain_loss = total_value - total_invested
        total_gain_loss_percent = (total_gain_loss / total_invested * 100) if total_invested > 0 else 0
        
        # Group by investment type
        investment_types = {}
        for inv in investments:
            inv_type = inv.get("type", "Unknown")
            if inv_type not in investment_types:
                investment_types[inv_type] = {
                    "count": 0,
                    "total_value": 0,
                    "total_invested": 0
                }
            investment_types[inv_type]["count"] += 1
            investment_types[inv_type]["total_value"] += inv.get("total_value", 0)
            investment_types[inv_type]["total_invested"] += inv.get("invested_amount", 0)
        
        return {
            "investments": investments,
            "portfolio_summary": {
                "total_value": round(total_value, 2),
                "total_invested": round(total_invested, 2),
                "total_gain_loss": round(total_gain_loss, 2),
                "total_gain_loss_percent": round(total_gain_loss_percent, 2),
                "investment_count": len(investments)
            },
            "investment_types": investment_types,
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching investments: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )


@router.get("/investments/{investment_id}/performance")
async def get_investment_performance(
    investment_id: str,
    permissions: Permissions = Depends(get_default_permissions)
) -> Dict[str, Any]:
    """
    Get performance data for a specific investment
    
    Args:
        investment_id: ID of the investment
        permissions: User's data access permissions
        
    Returns:
        Dictionary containing investment performance data
    """
    try:
        logger.info(f"Fetching performance for investment: {investment_id}")
        
        # Check permissions
        if not permissions.investments:
            raise HTTPException(
                status_code=403,
                detail="Access denied: Investment data permission required"
            )
        
        # Load data
        all_data = data_service.load_all_data()
        investments = all_data.get("investments", [])
        
        # Find investment by ID
        investment = next((inv for inv in investments if inv.get("id") == investment_id), None)
        
        if not investment:
            raise HTTPException(
                status_code=404,
                detail=f"Investment with ID {investment_id} not found"
            )
        
        # Calculate performance metrics
        current_value = investment.get("total_value", 0)
        invested_amount = investment.get("invested_amount", 0)
        gain_loss = current_value - invested_amount
        gain_loss_percent = (gain_loss / invested_amount * 100) if invested_amount > 0 else 0
        
        return {
            "investment_id": investment_id,
            "investment_name": investment.get("name", "Unknown Investment"),
            "performance": {
                "current_value": round(current_value, 2),
                "invested_amount": round(invested_amount, 2),
                "gain_loss": round(gain_loss, 2),
                "gain_loss_percent": round(gain_loss_percent, 2)
            },
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching investment performance for {investment_id}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )


@router.get("/assets")
async def get_assets(
    permissions: Permissions = Depends(get_default_permissions)
) -> Dict[str, Any]:
    """
    Get all user assets
    
    Args:
        permissions: User's data access permissions
        
    Returns:
        Dictionary containing assets and summary information
    """
    try:
        logger.info("Fetching user assets")
        
        # Check if user has permission to access assets
        if not permissions.assets:
            raise HTTPException(
                status_code=403,
                detail="Access denied: Asset data permission required"
            )
        
        # Load all data
        all_data = data_service.load_all_data()
        
        # Get assets
        assets = all_data.get("assets", [])
        
        # Calculate summary statistics
        total_value = sum(asset.get("value", 0) for asset in assets)
        asset_count = len(assets)
        
        # Group by asset type
        asset_types = {}
        for asset in assets:
            asset_type = asset.get("type", "Unknown")
            if asset_type not in asset_types:
                asset_types[asset_type] = {"count": 0, "total_value": 0}
            asset_types[asset_type]["count"] += 1
            asset_types[asset_type]["total_value"] += asset.get("value", 0)
        
        return {
            "assets": assets,
            "summary": {
                "total_value": round(total_value, 2),
                "asset_count": asset_count,
                "asset_types": asset_types
            },
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching assets: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )


@router.get("/liabilities")
async def get_liabilities(
    permissions: Permissions = Depends(get_default_permissions)
) -> Dict[str, Any]:
    """
    Get all user liabilities
    
    Args:
        permissions: User's data access permissions
        
    Returns:
        Dictionary containing liabilities and summary information
    """
    try:
        logger.info("Fetching user liabilities")
        
        # Check if user has permission to access liabilities
        if not permissions.liabilities:
            raise HTTPException(
                status_code=403,
                detail="Access denied: Liability data permission required"
            )
        
        # Load all data
        all_data = data_service.load_all_data()
        
        # Get liabilities
        liabilities = all_data.get("liabilities", [])
        
        # Calculate summary statistics
        total_balance = sum(liab.get("balance", 0) for liab in liabilities)
        total_monthly_payment = sum(liab.get("monthly_payment", 0) for liab in liabilities)
        liability_count = len(liabilities)
        
        # Group by liability type
        liability_types = {}
        for liab in liabilities:
            liab_type = liab.get("type", "Unknown")
            if liab_type not in liability_types:
                liability_types[liab_type] = {
                    "count": 0,
                    "total_balance": 0,
                    "total_monthly_payment": 0
                }
            liability_types[liab_type]["count"] += 1
            liability_types[liab_type]["total_balance"] += liab.get("balance", 0)
            liability_types[liab_type]["total_monthly_payment"] += liab.get("monthly_payment", 0)
        
        return {
            "liabilities": liabilities,
            "summary": {
                "total_balance": round(total_balance, 2),
                "total_monthly_payment": round(total_monthly_payment, 2),
                "liability_count": liability_count,
                "liability_types": liability_types
            },
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching liabilities: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )
