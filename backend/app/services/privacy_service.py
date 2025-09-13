"""
Privacy service for filtering data based on user permissions
"""
from typing import Dict, Any, List
from ..models.requests import Permissions
import logging

logger = logging.getLogger(__name__)


class PrivacyService:
    """Service for filtering data based on user privacy permissions"""
    
    def __init__(self):
        """Initialize the privacy service"""
        pass
    
    def filter_data_by_permissions(self, data: Dict[str, Any], permissions: Permissions) -> Dict[str, Any]:
        """
        Filter financial data based on user permissions
        
        Args:
            data: Complete financial data dictionary
            permissions: User's data access permissions
            
        Returns:
            Filtered data dictionary containing only authorized data
        """
        try:
            filtered_data = {}
            
            # Map permission fields to data categories
            permission_mapping = {
                'transactions': 'transactions',
                'assets': 'assets',
                'liabilities': 'liabilities',
                'epf_balance': 'epf_balance',
                'credit_score': 'credit_score',
                'investments': 'investments',
                'accounts': 'accounts',
                'spending_trends': 'spending_trends',
                'category_breakdown': 'category_breakdown',
                'dashboard_insights': 'dashboard_insights'
            }
            
            # Filter data based on permissions
            for permission_field, data_category in permission_mapping.items():
                if hasattr(permissions, permission_field) and getattr(permissions, permission_field):
                    if data_category in data:
                        filtered_data[data_category] = data[data_category]
                        logger.info(f"Granted access to {data_category} data")
                    else:
                        logger.warning(f"Data category {data_category} not found in source data")
                        filtered_data[data_category] = []
                else:
                    # Include empty data for denied categories to maintain structure
                    filtered_data[data_category] = []
                    logger.info(f"Denied access to {data_category} data")
            
            # Add metadata about filtering
            filtered_data['_metadata'] = {
                'total_categories': len(permission_mapping),
                'granted_categories': len([k for k, v in filtered_data.items() if v and k != '_metadata']),
                'denied_categories': len([k for k, v in filtered_data.items() if not v and k != '_metadata']),
                'permissions_applied': permissions.dict()
            }
            
            logger.info(f"Data filtering completed. Granted access to {filtered_data['_metadata']['granted_categories']} categories")
            return filtered_data
            
        except Exception as e:
            logger.error(f"Error filtering data by permissions: {str(e)}")
            raise Exception(f"Failed to filter data by permissions: {str(e)}")
    
    def get_permission_summary(self, permissions: Permissions) -> Dict[str, Any]:
        """
        Get a summary of the user's permissions
        
        Args:
            permissions: User's data access permissions
            
        Returns:
            Dictionary containing permission summary
        """
        permission_dict = permissions.dict()
        granted_permissions = [k for k, v in permission_dict.items() if v]
        denied_permissions = [k for k, v in permission_dict.items() if not v]
        
        return {
            'total_permissions': len(permission_dict),
            'granted_permissions': granted_permissions,
            'denied_permissions': denied_permissions,
            'granted_count': len(granted_permissions),
            'denied_count': len(denied_permissions),
            'permission_ratio': len(granted_permissions) / len(permission_dict) if permission_dict else 0
        }
    
    def validate_permissions(self, permissions: Permissions) -> bool:
        """
        Validate that the permissions object is properly structured
        
        Args:
            permissions: User's data access permissions
            
        Returns:
            True if permissions are valid, False otherwise
        """
        try:
            # Check if permissions object has the expected fields
            expected_fields = [
                'transactions', 'assets', 'liabilities', 'epf_balance',
                'credit_score', 'investments', 'accounts', 'spending_trends',
                'category_breakdown', 'dashboard_insights'
            ]
            
            for field in expected_fields:
                if not hasattr(permissions, field):
                    logger.error(f"Missing permission field: {field}")
                    return False
                
                if not isinstance(getattr(permissions, field), bool):
                    logger.error(f"Permission field {field} should be boolean")
                    return False
            
            logger.info("Permissions validation passed")
            return True
            
        except Exception as e:
            logger.error(f"Error validating permissions: {str(e)}")
            return False
    
    def get_data_access_level(self, permissions: Permissions) -> str:
        """
        Determine the data access level based on permissions
        
        Args:
            permissions: User's data access permissions
            
        Returns:
            String describing the access level
        """
        permission_dict = permissions.dict()
        granted_count = sum(1 for v in permission_dict.values() if v)
        total_count = len(permission_dict)
        
        ratio = granted_count / total_count if total_count > 0 else 0
        
        if ratio >= 0.8:
            return "full_access"
        elif ratio >= 0.5:
            return "partial_access"
        elif ratio > 0:
            return "limited_access"
        else:
            return "no_access"
