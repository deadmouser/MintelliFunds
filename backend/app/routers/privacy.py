"""
API router for privacy and data access management endpoints
"""
from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any, List, Optional
import logging
from datetime import datetime

from ..models.requests import Permissions
from ..services.privacy_service import PrivacyService

logger = logging.getLogger(__name__)

# Create router instance
router = APIRouter(prefix="/api", tags=["privacy"])

# Initialize services
privacy_service = PrivacyService()


@router.get("/privacy/settings")
async def get_privacy_settings() -> Dict[str, Any]:
    """
    Get current privacy settings
    
    Returns:
        Dictionary containing current privacy settings and available categories
    """
    try:
        logger.info("Fetching privacy settings")
        
        # Get default settings (in real app, this would come from user's stored preferences)
        default_settings = {
            "transactions": True,
            "accounts": True,
            "assets": True,
            "liabilities": True,
            "epf_balance": True,
            "credit_score": True,
            "investments": True,
            "spending_trends": True,
            "category_breakdown": True,
            "dashboard_insights": True
        }
        
        # Get available data categories
        categories = privacy_service.get_data_categories()
        
        return {
            "settings": default_settings,
            "available_categories": categories,
            "data_access_level": privacy_service.get_data_access_level(Permissions(**default_settings)),
            "permission_summary": privacy_service.get_permission_summary(Permissions(**default_settings)),
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }
        
    except Exception as e:
        logger.error(f"Error fetching privacy settings: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )


@router.put("/privacy/settings")
async def update_privacy_settings(
    settings: Dict[str, bool]
) -> Dict[str, Any]:
    """
    Update privacy settings
    
    Args:
        settings: Dictionary of category names to boolean values
        
    Returns:
        Dictionary containing updated privacy settings
    """
    try:
        logger.info(f"Updating privacy settings: {settings}")
        
        # Validate settings structure
        valid_categories = [
            "transactions", "accounts", "assets", "liabilities", 
            "epf_balance", "credit_score", "investments",
            "spending_trends", "category_breakdown", "dashboard_insights"
        ]
        
        # Filter out invalid categories
        filtered_settings = {k: v for k, v in settings.items() if k in valid_categories}
        
        # Create permissions object
        permissions = Permissions(**filtered_settings)
        
        # Validate permissions
        if not privacy_service.validate_permissions(permissions):
            raise HTTPException(
                status_code=400,
                detail="Invalid permissions structure"
            )
        
        # Get updated summary
        permission_summary = privacy_service.get_permission_summary(permissions)
        access_level = privacy_service.get_data_access_level(permissions)
        
        logger.info(f"Privacy settings updated. Access level: {access_level}")
        logger.info(f"Granted access to {permission_summary['granted_count']} categories")
        
        return {
            "settings": filtered_settings,
            "data_access_level": access_level,
            "permission_summary": permission_summary,
            "message": "Privacy settings updated successfully",
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating privacy settings: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )


@router.get("/privacy/categories")
async def get_data_categories() -> Dict[str, Any]:
    """
    Get available data categories and their descriptions
    
    Returns:
        Dictionary containing data categories with descriptions
    """
    try:
        logger.info("Fetching data categories")
        
        categories = privacy_service.get_data_categories()
        
        # Add detailed descriptions for each category
        category_details = []
        for category in categories:
            category_details.append({
                "category": category,
                "display_name": privacy_service.get_category_display_name(category),
                "description": privacy_service.get_category_description(category),
                "data_types": privacy_service.get_data_types_for_category(category)
            })
        
        return {
            "categories": category_details,
            "total_categories": len(category_details),
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }
        
    except Exception as e:
        logger.error(f"Error fetching data categories: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )


@router.post("/privacy/delete")
async def request_data_deletion(
    request_data: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Request data deletion for specific categories
    
    Args:
        request_data: Dictionary containing categories to delete
        
    Returns:
        Dictionary containing deletion request confirmation
    """
    try:
        categories = request_data.get("categories", [])
        logger.info(f"Data deletion requested for categories: {categories}")
        
        # Validate categories
        valid_categories = [
            "transactions", "accounts", "assets", "liabilities", 
            "epf_balance", "credit_score", "investments",
            "spending_trends", "category_breakdown", "dashboard_insights"
        ]
        
        filtered_categories = [cat for cat in categories if cat in valid_categories]
        
        if not filtered_categories:
            raise HTTPException(
                status_code=400,
                detail="No valid categories specified for deletion"
            )
        
        # Generate request ID
        request_id = f"del_req_{datetime.utcnow().timestamp()}"
        
        # In a real application, this would:
        # 1. Log the deletion request
        # 2. Schedule the actual deletion
        # 3. Send confirmation to user
        # 4. Update user's privacy settings
        
        return {
            "request_id": request_id,
            "categories": filtered_categories,
            "status": "pending",
            "message": f"Data deletion request submitted for {len(filtered_categories)} categories",
            "estimated_completion": (datetime.utcnow().timestamp() + 86400),  # 24 hours
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing data deletion request: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )


@router.get("/privacy/audit")
async def get_privacy_audit() -> Dict[str, Any]:
    """
    Get privacy audit information
    
    Returns:
        Dictionary containing privacy audit data
    """
    try:
        logger.info("Fetching privacy audit information")
        
        # In a real application, this would fetch actual audit data
        audit_data = {
            "last_updated": datetime.utcnow().isoformat() + "Z",
            "settings_changes": [],
            "data_access_log": {
                "api_calls": 0,
                "data_queries": 0,
                "ai_interactions": 0,
                "last_access": datetime.utcnow().isoformat() + "Z"
            },
            "compliance_status": {
                "gdpr_compliant": True,
                "data_retention_policy": "7 years",
                "encryption_status": "enabled"
            }
        }
        
        return audit_data
        
    except Exception as e:
        logger.error(f"Error fetching privacy audit: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )
