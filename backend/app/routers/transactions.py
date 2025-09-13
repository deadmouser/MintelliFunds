"""
API router for transaction-related endpoints
"""
from fastapi import APIRouter, HTTPException, Query, Depends
from typing import Dict, Any, List, Optional
import logging
from datetime import datetime

from ..models.requests import Permissions
from ..services.data_service import DataService
from ..services.privacy_service import PrivacyService

logger = logging.getLogger(__name__)

# Create router instance
router = APIRouter(prefix="/api", tags=["transactions"])

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


@router.get("/transactions")
async def get_transactions(
    limit: Optional[int] = Query(10, description="Number of transactions to return"),
    offset: Optional[int] = Query(0, description="Number of transactions to skip"),
    category: Optional[str] = Query(None, description="Filter by category"),
    start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD)"),
    permissions: Permissions = Depends(get_default_permissions)
) -> Dict[str, Any]:
    """
    Get transactions with optional filtering
    
    Args:
        limit: Maximum number of transactions to return
        offset: Number of transactions to skip
        category: Filter by transaction category
        start_date: Filter transactions from this date
        end_date: Filter transactions until this date
        permissions: User's data access permissions
        
    Returns:
        Dictionary containing filtered transactions and metadata
    """
    try:
        logger.info(f"Fetching transactions with filters: limit={limit}, category={category}")
        
        # Check if user has permission to access transactions
        if not permissions.transactions:
            raise HTTPException(
                status_code=403,
                detail="Access denied: Transaction data permission required"
            )
        
        # Load all data
        all_data = data_service.load_all_data()
        
        # Get transactions
        transactions = all_data.get("transactions", [])
        
        # Apply filters
        filtered_transactions = transactions
        
        if category:
            filtered_transactions = [t for t in filtered_transactions if t.get("category", "").lower() == category.lower()]
        
        if start_date:
            filtered_transactions = [t for t in filtered_transactions if t.get("date", "") >= start_date]
        
        if end_date:
            filtered_transactions = [t for t in filtered_transactions if t.get("date", "") <= end_date]
        
        # Apply pagination
        total_count = len(filtered_transactions)
        paginated_transactions = filtered_transactions[offset:offset + limit]
        
        # Calculate summary statistics
        total_amount = sum(t.get("amount", 0) for t in paginated_transactions)
        income_amount = sum(t.get("amount", 0) for t in paginated_transactions if t.get("amount", 0) > 0)
        expense_amount = abs(sum(t.get("amount", 0) for t in paginated_transactions if t.get("amount", 0) < 0))
        
        return {
            "transactions": paginated_transactions,
            "pagination": {
                "limit": limit,
                "offset": offset,
                "total": total_count,
                "has_more": offset + limit < total_count
            },
            "summary": {
                "total_amount": round(total_amount, 2),
                "income_amount": round(income_amount, 2),
                "expense_amount": round(expense_amount, 2),
                "transaction_count": len(paginated_transactions)
            },
            "filters": {
                "category": category,
                "start_date": start_date,
                "end_date": end_date
            },
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching transactions: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )


@router.get("/transactions/recent")
async def get_recent_transactions(
    limit: int = Query(10, description="Number of recent transactions to return"),
    permissions: Permissions = Depends(get_default_permissions)
) -> Dict[str, Any]:
    """
    Get recent transactions (last N transactions)
    
    Args:
        limit: Number of recent transactions to return
        permissions: User's data access permissions
        
    Returns:
        Dictionary containing recent transactions
    """
    try:
        logger.info(f"Fetching {limit} recent transactions")
        
        # Check permissions
        if not permissions.transactions:
            raise HTTPException(
                status_code=403,
                detail="Access denied: Transaction data permission required"
            )
        
        # Load data
        all_data = data_service.load_all_data()
        transactions = all_data.get("transactions", [])
        
        # Sort by date (most recent first) and take limit
        sorted_transactions = sorted(transactions, key=lambda x: x.get("date", ""), reverse=True)
        recent_transactions = sorted_transactions[:limit]
        
        return {
            "transactions": recent_transactions,
            "count": len(recent_transactions),
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching recent transactions: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )


@router.get("/transactions/{transaction_id}")
async def get_transaction_by_id(
    transaction_id: str,
    permissions: Permissions = Depends(get_default_permissions)
) -> Dict[str, Any]:
    """
    Get a specific transaction by ID
    
    Args:
        transaction_id: ID of the transaction to retrieve
        permissions: User's data access permissions
        
    Returns:
        Dictionary containing the transaction data
    """
    try:
        logger.info(f"Fetching transaction with ID: {transaction_id}")
        
        # Check permissions
        if not permissions.transactions:
            raise HTTPException(
                status_code=403,
                detail="Access denied: Transaction data permission required"
            )
        
        # Load data
        all_data = data_service.load_all_data()
        transactions = all_data.get("transactions", [])
        
        # Find transaction by ID
        transaction = next((t for t in transactions if t.get("id") == transaction_id), None)
        
        if not transaction:
            raise HTTPException(
                status_code=404,
                detail=f"Transaction with ID {transaction_id} not found"
            )
        
        return {
            "transaction": transaction,
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching transaction {transaction_id}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )


@router.post("/transactions")
async def create_transaction(
    transaction_data: Dict[str, Any],
    permissions: Permissions = Depends(get_default_permissions)
) -> Dict[str, Any]:
    """
    Create a new transaction (mock implementation)
    
    Args:
        transaction_data: Transaction data to create
        permissions: User's data access permissions
        
    Returns:
        Dictionary containing the created transaction
    """
    try:
        logger.info("Creating new transaction")
        
        # Check permissions
        if not permissions.transactions:
            raise HTTPException(
                status_code=403,
                detail="Access denied: Transaction data permission required"
            )
        
        # Mock implementation - in real app, this would save to database
        new_transaction = {
            "id": f"txn_{datetime.utcnow().timestamp()}",
            "description": transaction_data.get("description", "New Transaction"),
            "amount": transaction_data.get("amount", 0),
            "category": transaction_data.get("category", "Uncategorized"),
            "account": transaction_data.get("account", "Default Account"),
            "date": transaction_data.get("date", datetime.utcnow().isoformat() + "Z"),
            "created_at": datetime.utcnow().isoformat() + "Z"
        }
        
        return {
            "transaction": new_transaction,
            "message": "Transaction created successfully",
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating transaction: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )


@router.put("/transactions/{transaction_id}")
async def update_transaction(
    transaction_id: str,
    transaction_data: Dict[str, Any],
    permissions: Permissions = Depends(get_default_permissions)
) -> Dict[str, Any]:
    """
    Update an existing transaction (mock implementation)
    
    Args:
        transaction_id: ID of the transaction to update
        transaction_data: Updated transaction data
        permissions: User's data access permissions
        
    Returns:
        Dictionary containing the updated transaction
    """
    try:
        logger.info(f"Updating transaction with ID: {transaction_id}")
        
        # Check permissions
        if not permissions.transactions:
            raise HTTPException(
                status_code=403,
                detail="Access denied: Transaction data permission required"
            )
        
        # Mock implementation - in real app, this would update database
        updated_transaction = {
            "id": transaction_id,
            "description": transaction_data.get("description", "Updated Transaction"),
            "amount": transaction_data.get("amount", 0),
            "category": transaction_data.get("category", "Uncategorized"),
            "account": transaction_data.get("account", "Default Account"),
            "date": transaction_data.get("date", datetime.utcnow().isoformat() + "Z"),
            "updated_at": datetime.utcnow().isoformat() + "Z"
        }
        
        return {
            "transaction": updated_transaction,
            "message": "Transaction updated successfully",
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating transaction {transaction_id}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )


@router.delete("/transactions/{transaction_id}")
async def delete_transaction(
    transaction_id: str,
    permissions: Permissions = Depends(get_default_permissions)
) -> Dict[str, Any]:
    """
    Delete a transaction (mock implementation)
    
    Args:
        transaction_id: ID of the transaction to delete
        permissions: User's data access permissions
        
    Returns:
        Dictionary containing deletion confirmation
    """
    try:
        logger.info(f"Deleting transaction with ID: {transaction_id}")
        
        # Check permissions
        if not permissions.transactions:
            raise HTTPException(
                status_code=403,
                detail="Access denied: Transaction data permission required"
            )
        
        # Mock implementation - in real app, this would delete from database
        return {
            "message": f"Transaction {transaction_id} deleted successfully",
            "deleted_id": transaction_id,
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting transaction {transaction_id}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )
