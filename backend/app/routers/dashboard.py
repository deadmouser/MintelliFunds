"""
API router for dashboard-related endpoints
"""
from fastapi import APIRouter, HTTPException, Depends, Query
from typing import Dict, Any, List, Optional
import logging
from datetime import datetime, timedelta

from ..models.requests import Permissions
from ..services.data_service import DataService
from ..services.privacy_service import PrivacyService

logger = logging.getLogger(__name__)

# Create router instance
router = APIRouter(prefix="/api", tags=["dashboard"])

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


@router.get("/dashboard")
async def get_dashboard_data(
    permissions: Permissions = Depends(get_default_permissions)
) -> Dict[str, Any]:
    """
    Get comprehensive dashboard data
    
    Args:
        permissions: User's data access permissions
        
    Returns:
        Dictionary containing all dashboard metrics
    """
    try:
        logger.info("Fetching dashboard data")
        
        # Load all data
        all_data = data_service.load_all_data()
        filtered_data = privacy_service.filter_data_by_permissions(all_data, permissions)
        
        # Calculate key metrics
        accounts = filtered_data.get("accounts", [])
        transactions = filtered_data.get("transactions", [])
        investments = filtered_data.get("investments", [])
        liabilities = filtered_data.get("liabilities", [])
        
        # Total balance
        total_balance = sum(acc.get("balance", 0) for acc in accounts)
        
        # Monthly spending (last 30 days)
        monthly_spending = _calculate_monthly_spending(transactions)
        
        # Savings progress
        savings_progress = _calculate_savings_progress(accounts, transactions)
        
        # Investment value
        investment_value = sum(inv.get("total_value", 0) for inv in investments)
        
        # Net worth
        total_assets = total_balance + investment_value
        total_debt = sum(liab.get("balance", 0) for liab in liabilities)
        net_worth = total_assets - total_debt
        
        # Calculate changes (mock data for now)
        balance_change = 8.5  # Mock percentage change
        spending_change = -12.3  # Mock percentage change
        investment_change = 15.2  # Mock percentage change
        
        return {
            "total_balance": round(total_balance, 2),
            "monthly_spending": round(monthly_spending, 2),
            "savings_progress": round(savings_progress, 2),
            "savings_goal": 100000,  # Mock savings goal
            "investment_value": round(investment_value, 2),
            "net_worth": round(net_worth, 2),
            "balance_change": balance_change,
            "spending_change": spending_change,
            "investment_change": investment_change,
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }
        
    except Exception as e:
        logger.error(f"Error fetching dashboard data: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )


@router.get("/spending-trend")
async def get_spending_trend(
    period: str = Query("1m", description="Time period for spending trend"),
    permissions: Permissions = Depends(get_default_permissions)
) -> Dict[str, Any]:
    """
    Get spending trend data for charts
    
    Args:
        period: Time period (1m, 3m, 6m, 1y)
        permissions: User's data access permissions
        
    Returns:
        Dictionary containing spending trend data
    """
    try:
        logger.info(f"Fetching spending trend for period: {period}")
        
        # Check permissions
        if not permissions.transactions:
            raise HTTPException(
                status_code=403,
                detail="Access denied: Transaction data permission required"
            )
        
        # Load data
        all_data = data_service.load_all_data()
        transactions = all_data.get("transactions", [])
        
        # Calculate spending by week
        spending_data = _calculate_weekly_spending(transactions, period)
        
        return {
            "labels": spending_data["labels"],
            "spending": spending_data["amounts"],
            "period": period,
            "total_spending": sum(spending_data["amounts"]),
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching spending trend: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )


@router.get("/category-breakdown")
async def get_category_breakdown(
    permissions: Permissions = Depends(get_default_permissions)
) -> Dict[str, Any]:
    """
    Get spending breakdown by category
    
    Args:
        permissions: User's data access permissions
        
    Returns:
        Dictionary containing category breakdown data
    """
    try:
        logger.info("Fetching category breakdown")
        
        # Check permissions
        if not permissions.transactions:
            raise HTTPException(
                status_code=403,
                detail="Access denied: Transaction data permission required"
            )
        
        # Load data
        all_data = data_service.load_all_data()
        transactions = all_data.get("transactions", [])
        
        # Calculate category breakdown
        category_data = _calculate_category_breakdown(transactions)
        
        return {
            "categories": category_data["categories"],
            "amounts": category_data["amounts"],
            "total_spending": sum(category_data["amounts"]),
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching category breakdown: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )


@router.get("/insights/dashboard")
async def get_dashboard_insights(
    permissions: Permissions = Depends(get_default_permissions)
) -> Dict[str, Any]:
    """
    Get AI-generated dashboard insights
    
    Args:
        permissions: User's data access permissions
        
    Returns:
        Dictionary containing dashboard insights
    """
    try:
        logger.info("Fetching dashboard insights")
        
        # Check permissions
        if not permissions.dashboard_insights:
            raise HTTPException(
                status_code=403,
                detail="Access denied: Dashboard insights permission required"
            )
        
        # Load data
        all_data = data_service.load_all_data()
        filtered_data = privacy_service.filter_data_by_permissions(all_data, permissions)
        
        # Generate insights based on available data
        insights = _generate_dashboard_insights(filtered_data)
        
        return {
            "insights": insights,
            "count": len(insights),
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching dashboard insights: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )


def _calculate_monthly_spending(transactions: List[Dict[str, Any]]) -> float:
    """Calculate monthly spending from transactions"""
    # Get transactions from last 30 days
    cutoff_date = datetime.now() - timedelta(days=30)
    
    monthly_transactions = []
    for t in transactions:
        try:
            transaction_date = datetime.fromisoformat(t["date"].replace('Z', '+00:00'))
            if transaction_date >= cutoff_date and t.get("amount", 0) < 0:
                monthly_transactions.append(abs(t.get("amount", 0)))
        except (ValueError, KeyError):
            continue
    
    return sum(monthly_transactions)


def _calculate_savings_progress(accounts: List[Dict[str, Any]], transactions: List[Dict[str, Any]]) -> float:
    """Calculate savings progress"""
    # Simple calculation: total balance as savings progress
    return sum(acc.get("balance", 0) for acc in accounts)


def _calculate_weekly_spending(transactions: List[Dict[str, Any]], period: str) -> Dict[str, Any]:
    """Calculate weekly spending data"""
    # Mock data for now - in real app, this would calculate actual weekly spending
    if period == "1m":
        labels = ["Week 1", "Week 2", "Week 3", "Week 4"]
        amounts = [12000, 15000, 13500, 18000]
    elif period == "3m":
        labels = ["Month 1", "Month 2", "Month 3"]
        amounts = [45000, 52000, 48000]
    elif period == "6m":
        labels = ["Month 1", "Month 2", "Month 3", "Month 4", "Month 5", "Month 6"]
        amounts = [45000, 52000, 48000, 55000, 49000, 51000]
    else:  # 1y
        labels = ["Q1", "Q2", "Q3", "Q4"]
        amounts = [150000, 165000, 158000, 172000]
    
    return {
        "labels": labels,
        "amounts": amounts
    }


def _calculate_category_breakdown(transactions: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Calculate spending breakdown by category"""
    category_totals = {}
    
    for t in transactions:
        if t.get("amount", 0) < 0:  # Only expenses
            category = t.get("category", "Uncategorized")
            amount = abs(t.get("amount", 0))
            category_totals[category] = category_totals.get(category, 0) + amount
    
    # Sort by amount and get top categories
    sorted_categories = sorted(category_totals.items(), key=lambda x: x[1], reverse=True)
    
    categories = [cat[0] for cat in sorted_categories[:5]]  # Top 5
    amounts = [cat[1] for cat in sorted_categories[:5]]
    
    return {
        "categories": categories,
        "amounts": amounts
    }


def _generate_dashboard_insights(filtered_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Generate AI insights for dashboard"""
    insights = []
    
    # Check if we have transaction data
    if filtered_data.get("transactions"):
        insights.append({
            "id": "1",
            "type": "Spending Alert",
            "text": "Your food expenses have increased by 25% this month."
        })
    
    # Check if we have investment data
    if filtered_data.get("investments"):
        insights.append({
            "id": "2",
            "type": "Investment Opportunity",
            "text": "Consider diversifying your portfolio with index funds."
        })
    
    # Check if we have savings data
    if filtered_data.get("accounts"):
        insights.append({
            "id": "3",
            "type": "Savings Opportunity",
            "text": "You could save ₹3,000 monthly by optimizing subscriptions."
        })
    
    return insights
