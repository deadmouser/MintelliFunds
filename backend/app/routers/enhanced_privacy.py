"""
Enhanced API router for privacy and data access management
Provides comprehensive privacy controls, audit trails, and real-time enforcement
"""

from fastapi import APIRouter, HTTPException, Depends, Request, Query
from typing import Dict, Any, List, Optional
import logging
from datetime import datetime
from pydantic import BaseModel, Field

from ..services.enhanced_privacy_service import (
    EnhancedPrivacyService, PermissionLevel, AccessType, AuditAction
)

logger = logging.getLogger(__name__)

# Create router instance
router = APIRouter(prefix="/api/privacy", tags=["enhanced_privacy"])

# Initialize enhanced privacy service
privacy_service = EnhancedPrivacyService(audit_storage_path="logs/privacy_audit")


# Pydantic models for request/response
class PermissionUpdateRequest(BaseModel):
    """Request model for permission updates"""
    permissions: Dict[str, Any] = Field(..., description="Permission updates by category")
    session_context: Optional[Dict[str, Any]] = Field(None, description="Session context for audit")


class DataExportRequest(BaseModel):
    """Request model for data export"""
    categories: List[str] = Field(..., description="Categories to export")
    format: str = Field("json", description="Export format (json, csv)")


class DataDeletionRequest(BaseModel):
    """Request model for data deletion"""
    categories: List[str] = Field(..., description="Categories to delete")
    reason: Optional[str] = Field("", description="Reason for deletion")


class PrivacySettingsRequest(BaseModel):
    """Request model for privacy settings update"""
    privacy_level: Optional[str] = Field(None, description="Privacy level (basic, standard, strict)")
    data_minimization: Optional[bool] = Field(None, description="Enable data minimization")


# Helper function to extract session context
def get_session_context(request: Request) -> Dict[str, Any]:
    """Extract session context from request"""
    return {
        "ip_address": request.client.host if request.client else None,
        "user_agent": request.headers.get("user-agent"),
        "session_id": request.headers.get("session-id"),
        "timestamp": datetime.utcnow().isoformat()
    }


@router.post("/profile/create/{user_id}")
async def create_privacy_profile(
    user_id: str,
    initial_permissions: Optional[Dict[str, Any]] = None,
    request: Request = None
) -> Dict[str, Any]:
    """
    Create a new privacy profile for a user
    
    Args:
        user_id: User identifier
        initial_permissions: Optional initial permission settings
        
    Returns:
        Created privacy profile summary
    """
    try:
        logger.info(f"Creating privacy profile for user: {user_id}")
        
        profile = await privacy_service.create_privacy_profile(
            user_id=user_id,
            initial_permissions=initial_permissions
        )
        
        return {
            "user_id": user_id,
            "message": "Privacy profile created successfully",
            "profile": {
                "privacy_level": profile.privacy_level,
                "data_minimization": profile.data_minimization,
                "consent_timestamp": profile.consent_timestamp.isoformat(),
                "permissions_count": len(profile.permissions)
            }
        }
        
    except Exception as e:
        logger.error(f"Error creating privacy profile for {user_id}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create privacy profile: {str(e)}"
        )


@router.get("/dashboard/{user_id}")
async def get_privacy_dashboard(user_id: str) -> Dict[str, Any]:
    """
    Get comprehensive privacy dashboard for a user
    
    Args:
        user_id: User identifier
        
    Returns:
        Privacy dashboard data
    """
    try:
        logger.info(f"Fetching privacy dashboard for user: {user_id}")
        
        dashboard = await privacy_service.get_privacy_dashboard(user_id)
        
        return {
            "status": "success",
            "dashboard": dashboard,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error fetching privacy dashboard for {user_id}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch privacy dashboard: {str(e)}"
        )


@router.get("/permissions/{user_id}")
async def get_permissions_summary(user_id: str) -> Dict[str, Any]:
    """
    Get detailed permissions summary for a user
    
    Args:
        user_id: User identifier
        
    Returns:
        Comprehensive permissions summary
    """
    try:
        logger.info(f"Fetching permissions summary for user: {user_id}")
        
        summary = await privacy_service.get_permission_summary(user_id)
        
        return {
            "status": "success",
            "permissions": summary,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error fetching permissions for {user_id}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch permissions: {str(e)}"
        )


@router.put("/permissions/{user_id}")
async def update_permissions(
    user_id: str,
    update_request: PermissionUpdateRequest,
    request: Request
) -> Dict[str, Any]:
    """
    Update user permissions with audit trail
    
    Args:
        user_id: User identifier
        update_request: Permission update request
        
    Returns:
        Updated permissions summary
    """
    try:
        logger.info(f"Updating permissions for user: {user_id}")
        
        # Get session context
        session_context = get_session_context(request)
        if update_request.session_context:
            session_context.update(update_request.session_context)
        
        # Update permissions
        updated_summary = await privacy_service.update_permissions(
            user_id=user_id,
            permission_updates=update_request.permissions,
            session_context=session_context
        )
        
        return {
            "status": "success",
            "message": "Permissions updated successfully",
            "updated_permissions": updated_summary,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error updating permissions for {user_id}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to update permissions: {str(e)}"
        )


@router.post("/check-permission/{user_id}")
async def check_permission(
    user_id: str,
    category_id: str = Query(..., description="Data category ID"),
    access_type: str = Query("view", description="Access type (view, analyze, export, delete, share)"),
    log_access: bool = Query(True, description="Whether to log this access check")
) -> Dict[str, Any]:
    """
    Check if user has permission for specific data access
    
    Args:
        user_id: User identifier
        category_id: Data category identifier
        access_type: Type of access requested
        log_access: Whether to log this access check
        
    Returns:
        Permission check result
    """
    try:
        logger.info(f"Checking permission for user {user_id}, category {category_id}, access {access_type}")
        
        # Convert access type string to enum
        try:
            access_enum = AccessType(access_type.upper())
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid access type: {access_type}. Valid types: view, analyze, export, delete, share"
            )
        
        # Check permission
        has_permission = await privacy_service.check_permission(
            user_id=user_id,
            category_id=category_id,
            access_type=access_enum,
            log_access=log_access
        )
        
        return {
            "user_id": user_id,
            "category_id": category_id,
            "access_type": access_type,
            "has_permission": has_permission,
            "checked_at": datetime.utcnow().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error checking permission: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to check permission: {str(e)}"
        )


@router.post("/filter-data/{user_id}")
async def filter_data_by_permissions(
    user_id: str,
    data: Dict[str, Any],
    context: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Filter data based on user permissions with real-time enforcement
    
    Args:
        user_id: User identifier
        data: Complete data dictionary to filter
        context: Optional context for filtering decisions
        
    Returns:
        Filtered data dictionary
    """
    try:
        logger.info(f"Filtering data for user: {user_id}")
        
        # Filter data based on permissions
        filtered_data = await privacy_service.filter_data_by_permissions(
            user_id=user_id,
            data=data,
            context=context
        )
        
        return {
            "status": "success",
            "filtered_data": filtered_data,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error filtering data for {user_id}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to filter data: {str(e)}"
        )


@router.get("/audit-trail/{user_id}")
async def get_audit_trail(
    user_id: str,
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of entries"),
    action_filter: Optional[List[str]] = Query(None, description="Filter by specific actions")
) -> Dict[str, Any]:
    """
    Get user's audit trail
    
    Args:
        user_id: User identifier
        limit: Maximum number of entries to return
        action_filter: Optional filter for specific actions
        
    Returns:
        User's audit trail
    """
    try:
        logger.info(f"Fetching audit trail for user: {user_id}")
        
        # Convert action filter strings to enums if provided
        audit_action_filter = None
        if action_filter:
            try:
                audit_action_filter = [AuditAction(action.upper()) for action in action_filter]
            except ValueError as e:
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid action in filter: {str(e)}"
                )
        
        # Get audit trail
        audit_entries = await privacy_service.get_audit_trail(
            user_id=user_id,
            limit=limit,
            action_filter=audit_action_filter
        )
        
        return {
            "user_id": user_id,
            "audit_trail": audit_entries,
            "total_entries": len(audit_entries),
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching audit trail for {user_id}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch audit trail: {str(e)}"
        )


@router.get("/categories")
async def get_data_categories() -> Dict[str, Any]:
    """
    Get all available data categories with details
    
    Returns:
        List of data categories with comprehensive information
    """
    try:
        logger.info("Fetching data categories")
        
        categories = privacy_service.get_data_categories()
        
        # Group categories by sensitivity level for easier understanding
        categories_by_sensitivity = {}
        for category in categories:
            sensitivity = category["sensitivity_level"]
            if sensitivity not in categories_by_sensitivity:
                categories_by_sensitivity[sensitivity] = []
            categories_by_sensitivity[sensitivity].append(category)
        
        return {
            "categories": categories,
            "categories_by_sensitivity": categories_by_sensitivity,
            "total_categories": len(categories),
            "sensitivity_levels": {
                1: "Very Low - Basic operational data",
                2: "Low - General preferences and settings",
                3: "Medium - Analytics and insights data",
                4: "High - Financial transaction data",
                5: "Very High - Sensitive financial information"
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error fetching data categories: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch data categories: {str(e)}"
        )


@router.post("/export/{user_id}")
async def request_data_export(
    user_id: str,
    export_request: DataExportRequest
) -> Dict[str, Any]:
    """
    Request data export for specified categories
    
    Args:
        user_id: User identifier
        export_request: Export request details
        
    Returns:
        Export request confirmation
    """
    try:
        logger.info(f"Processing data export request for user: {user_id}")
        
        # Validate format
        valid_formats = ["json", "csv"]
        if export_request.format not in valid_formats:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid format: {export_request.format}. Valid formats: {valid_formats}"
            )
        
        # Process export request
        export_result = await privacy_service.request_data_export(
            user_id=user_id,
            categories=export_request.categories,
            format=export_request.format
        )
        
        return {
            "status": "success",
            "message": "Data export request submitted successfully",
            "export_details": export_result,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing data export for {user_id}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process data export: {str(e)}"
        )


@router.post("/delete/{user_id}")
async def request_data_deletion(
    user_id: str,
    deletion_request: DataDeletionRequest
) -> Dict[str, Any]:
    """
    Request data deletion for specified categories
    
    Args:
        user_id: User identifier
        deletion_request: Deletion request details
        
    Returns:
        Deletion request confirmation
    """
    try:
        logger.info(f"Processing data deletion request for user: {user_id}")
        
        # Process deletion request
        deletion_result = await privacy_service.request_data_deletion(
            user_id=user_id,
            categories=deletion_request.categories,
            reason=deletion_request.reason
        )
        
        return {
            "status": "success",
            "message": "Data deletion request submitted successfully",
            "deletion_details": deletion_result,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error processing data deletion for {user_id}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process data deletion: {str(e)}"
        )


@router.put("/settings/{user_id}")
async def update_privacy_settings(
    user_id: str,
    settings_request: PrivacySettingsRequest
) -> Dict[str, Any]:
    """
    Update privacy settings for a user
    
    Args:
        user_id: User identifier
        settings_request: Privacy settings update
        
    Returns:
        Updated privacy settings
    """
    try:
        logger.info(f"Updating privacy settings for user: {user_id}")
        
        # Validate privacy level
        if settings_request.privacy_level:
            valid_levels = ["basic", "standard", "strict"]
            if settings_request.privacy_level not in valid_levels:
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid privacy level: {settings_request.privacy_level}. Valid levels: {valid_levels}"
                )
        
        # Get current profile or create if doesn't exist
        if user_id not in privacy_service._privacy_profiles:
            await privacy_service.create_privacy_profile(user_id)
        
        profile = privacy_service._privacy_profiles[user_id]
        
        # Update settings
        if settings_request.privacy_level is not None:
            profile.privacy_level = settings_request.privacy_level
        
        if settings_request.data_minimization is not None:
            profile.data_minimization = settings_request.data_minimization
        
        profile.last_updated = datetime.utcnow()
        
        # Log settings update
        await privacy_service._add_audit_entry(
            user_id=user_id,
            action=AuditAction.PRIVACY_SETTINGS_UPDATED,
            details={
                "privacy_level": profile.privacy_level,
                "data_minimization": profile.data_minimization
            }
        )
        
        return {
            "status": "success",
            "message": "Privacy settings updated successfully",
            "settings": {
                "privacy_level": profile.privacy_level,
                "data_minimization": profile.data_minimization,
                "last_updated": profile.last_updated.isoformat()
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating privacy settings for {user_id}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to update privacy settings: {str(e)}"
        )


@router.post("/cleanup/expired-permissions")
async def cleanup_expired_permissions() -> Dict[str, Any]:
    """
    Clean up expired permissions across all users
    
    Returns:
        Cleanup summary
    """
    try:
        logger.info("Starting cleanup of expired permissions")
        
        expired_count = await privacy_service.cleanup_expired_permissions()
        
        return {
            "status": "success",
            "message": f"Cleaned up {expired_count} expired permissions",
            "expired_count": expired_count,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error cleaning up expired permissions: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to cleanup expired permissions: {str(e)}"
        )


@router.get("/compliance/{user_id}")
async def get_compliance_status(user_id: str) -> Dict[str, Any]:
    """
    Get compliance status for a user
    
    Args:
        user_id: User identifier
        
    Returns:
        Compliance status information
    """
    try:
        logger.info(f"Fetching compliance status for user: {user_id}")
        
        if user_id not in privacy_service._privacy_profiles:
            raise HTTPException(
                status_code=404,
                detail=f"Privacy profile not found for user: {user_id}"
            )
        
        profile = privacy_service._privacy_profiles[user_id]
        
        # Calculate compliance metrics
        total_categories = len(privacy_service._data_categories)
        granted_permissions = sum(
            1 for perm in profile.permissions.values()
            if perm.permission_level != PermissionLevel.NONE
        )
        
        # Check for high-sensitivity data with full access (potential compliance risk)
        high_risk_permissions = []
        for cat_id, permission in profile.permissions.items():
            category = privacy_service._data_categories[cat_id]
            if (category.sensitivity_level >= 4 and 
                permission.permission_level in [PermissionLevel.FULL, PermissionLevel.ADMIN]):
                high_risk_permissions.append(category.display_name)
        
        return {
            "user_id": user_id,
            "compliance_status": {
                "gdpr_compliant": True,
                "consent_given": profile.consent_timestamp.isoformat(),
                "data_minimization_enabled": profile.data_minimization,
                "audit_trail_available": len(profile.audit_trail) > 0,
                "privacy_level": profile.privacy_level
            },
            "risk_assessment": {
                "total_permissions": total_categories,
                "granted_permissions": granted_permissions,
                "permission_ratio": granted_permissions / total_categories,
                "high_risk_permissions": high_risk_permissions,
                "risk_level": "low" if len(high_risk_permissions) == 0 else "medium" if len(high_risk_permissions) <= 2 else "high"
            },
            "audit_summary": {
                "total_audit_entries": len(profile.audit_trail),
                "last_audit_entry": max(
                    (entry.timestamp for entry in profile.audit_trail),
                    default=profile.consent_timestamp
                ).isoformat()
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching compliance status for {user_id}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch compliance status: {str(e)}"
        )


# Health check endpoint
@router.get("/health")
async def privacy_health_check() -> Dict[str, Any]:
    """
    Privacy service health check
    
    Returns:
        Service health status
    """
    try:
        total_profiles = len(privacy_service._privacy_profiles)
        total_categories = len(privacy_service._data_categories)
        cached_audit_entries = len(privacy_service._audit_cache)
        
        return {
            "status": "healthy",
            "service": "Enhanced Privacy Service",
            "metrics": {
                "total_user_profiles": total_profiles,
                "total_data_categories": total_categories,
                "cached_audit_entries": cached_audit_entries,
                "audit_storage_enabled": privacy_service.audit_storage_path is not None
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Privacy service health check failed: {str(e)}")
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }