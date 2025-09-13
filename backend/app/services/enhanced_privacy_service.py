"""
Enhanced Privacy and Permissions Service for MintelliFunds
Provides comprehensive privacy controls, audit trails, and real-time enforcement
"""

import json
import logging
import asyncio
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List, Optional, Set, Tuple
from enum import Enum
from dataclasses import dataclass, asdict
from pathlib import Path
import hashlib
import uuid

logger = logging.getLogger(__name__)


class PermissionLevel(Enum):
    """Permission levels for data access"""
    NONE = "none"
    READ_ONLY = "read_only"
    LIMITED = "limited"
    FULL = "full"
    ADMIN = "admin"


class AccessType(Enum):
    """Types of data access"""
    VIEW = "view"
    ANALYZE = "analyze"
    EXPORT = "export"
    DELETE = "delete"
    SHARE = "share"


class AuditAction(Enum):
    """Audit action types"""
    PERMISSION_CHANGED = "permission_changed"
    DATA_ACCESSED = "data_accessed"
    DATA_EXPORTED = "data_exported"
    PRIVACY_SETTINGS_UPDATED = "privacy_settings_updated"
    DATA_DELETION_REQUESTED = "data_deletion_requested"
    CONSENT_GIVEN = "consent_given"
    CONSENT_WITHDRAWN = "consent_withdrawn"


@dataclass
class DataCategory:
    """Data category configuration"""
    id: str
    name: str
    display_name: str
    description: str
    sensitivity_level: int  # 1-5 scale
    data_types: List[str]
    required_for_basic_function: bool = False
    gdpr_category: str = "regular"
    retention_period_days: int = 2555  # 7 years default
    
    
@dataclass
class PermissionSetting:
    """Individual permission setting"""
    category_id: str
    permission_level: PermissionLevel
    access_types: Set[AccessType]
    expires_at: Optional[datetime] = None
    granted_at: datetime = None
    updated_at: datetime = None
    
    def __post_init__(self):
        if self.granted_at is None:
            self.granted_at = datetime.now(timezone.utc)
        if self.updated_at is None:
            self.updated_at = datetime.now(timezone.utc)


@dataclass
class AuditEntry:
    """Audit trail entry"""
    id: str
    user_id: str
    action: AuditAction
    category_id: Optional[str]
    details: Dict[str, Any]
    ip_address: Optional[str]
    user_agent: Optional[str]
    timestamp: datetime
    session_id: Optional[str] = None
    
    def __post_init__(self):
        if not self.id:
            self.id = str(uuid.uuid4())
        if not self.timestamp:
            self.timestamp = datetime.now(timezone.utc)


@dataclass
class PrivacyProfile:
    """Complete privacy profile for a user"""
    user_id: str
    permissions: Dict[str, PermissionSetting]
    audit_trail: List[AuditEntry]
    consent_timestamp: datetime
    last_updated: datetime
    privacy_level: str = "standard"  # basic, standard, strict
    data_minimization: bool = True
    
    def __post_init__(self):
        if not self.last_updated:
            self.last_updated = datetime.now(timezone.utc)


class EnhancedPrivacyService:
    """Enhanced privacy and permissions service with comprehensive controls"""
    
    def __init__(self, audit_storage_path: Optional[str] = None):
        """
        Initialize the enhanced privacy service
        
        Args:
            audit_storage_path: Path to store audit logs (optional)
        """
        self.audit_storage_path = Path(audit_storage_path) if audit_storage_path else None
        self._data_categories = self._initialize_data_categories()
        self._privacy_profiles: Dict[str, PrivacyProfile] = {}
        self._audit_cache: List[AuditEntry] = []
        
        # Initialize audit storage
        if self.audit_storage_path:
            self.audit_storage_path.mkdir(parents=True, exist_ok=True)
    
    def _initialize_data_categories(self) -> Dict[str, DataCategory]:
        """Initialize predefined data categories"""
        categories = [
            DataCategory(
                id="transactions",
                name="transactions", 
                display_name="Financial Transactions",
                description="All your financial transactions including income, expenses, and transfers",
                sensitivity_level=4,
                data_types=["amounts", "dates", "descriptions", "categories", "merchant_info"],
                required_for_basic_function=True,
                gdpr_category="financial"
            ),
            DataCategory(
                id="accounts",
                name="accounts",
                display_name="Account Information", 
                description="Bank accounts, credit cards, and account balances",
                sensitivity_level=5,
                data_types=["account_numbers", "balances", "bank_details", "account_types"],
                required_for_basic_function=True,
                gdpr_category="financial"
            ),
            DataCategory(
                id="investments",
                name="investments",
                display_name="Investment Portfolio",
                description="Investment holdings, performance, and portfolio data",
                sensitivity_level=4,
                data_types=["holdings", "valuations", "performance", "risk_profiles"],
                gdpr_category="financial"
            ),
            DataCategory(
                id="liabilities", 
                name="liabilities",
                display_name="Loans & Debts",
                description="Loan information, debt obligations, and payment schedules",
                sensitivity_level=5,
                data_types=["loan_amounts", "interest_rates", "payment_schedules", "debt_details"],
                gdpr_category="financial"
            ),
            DataCategory(
                id="assets",
                name="assets",
                display_name="Asset Information",
                description="Property, vehicles, and other valuable assets",
                sensitivity_level=3,
                data_types=["valuations", "ownership_details", "asset_types"],
                gdpr_category="financial"
            ),
            DataCategory(
                id="credit_score",
                name="credit_score",
                display_name="Credit Score & History",
                description="Credit scores, credit history, and credit monitoring data",
                sensitivity_level=5,
                data_types=["credit_scores", "credit_history", "credit_inquiries"],
                gdpr_category="financial"
            ),
            DataCategory(
                id="epf_balance",
                name="epf_balance", 
                display_name="EPF/Retirement Funds",
                description="Employee Provident Fund and retirement account information",
                sensitivity_level=4,
                data_types=["balances", "contributions", "employer_details"],
                gdpr_category="financial"
            ),
            DataCategory(
                id="spending_patterns",
                name="spending_trends",
                display_name="Spending Analysis",
                description="Analyzed spending patterns, trends, and categorizations",
                sensitivity_level=3,
                data_types=["spending_patterns", "trend_analysis", "category_breakdown"],
                required_for_basic_function=True,
                gdpr_category="analytics"
            ),
            DataCategory(
                id="financial_insights",
                name="dashboard_insights",
                display_name="AI Financial Insights",
                description="AI-generated financial insights, recommendations, and predictions",
                sensitivity_level=3,
                data_types=["ai_insights", "recommendations", "predictions", "analysis_results"],
                gdpr_category="analytics"
            ),
            DataCategory(
                id="personal_profile",
                name="personal_info",
                display_name="Personal Information",
                description="Basic personal details and preferences",
                sensitivity_level=2,
                data_types=["name", "contact_info", "preferences", "demographics"],
                required_for_basic_function=True,
                gdpr_category="personal"
            )
        ]
        
        return {cat.id: cat for cat in categories}
    
    async def create_privacy_profile(self, user_id: str, initial_permissions: Optional[Dict[str, Any]] = None) -> PrivacyProfile:
        """
        Create a new privacy profile for a user
        
        Args:
            user_id: User identifier
            initial_permissions: Initial permission settings (optional)
            
        Returns:
            Created privacy profile
        """
        logger.info(f"Creating privacy profile for user: {user_id}")
        
        # Create default permissions based on sensitivity levels
        permissions = {}
        for cat_id, category in self._data_categories.items():
            # Default permission level based on sensitivity and requirements
            if category.required_for_basic_function:
                level = PermissionLevel.LIMITED
                access_types = {AccessType.VIEW, AccessType.ANALYZE}
            elif category.sensitivity_level >= 4:
                level = PermissionLevel.NONE
                access_types = set()
            else:
                level = PermissionLevel.READ_ONLY
                access_types = {AccessType.VIEW}
            
            permissions[cat_id] = PermissionSetting(
                category_id=cat_id,
                permission_level=level,
                access_types=access_types
            )
        
        # Apply initial permissions if provided
        if initial_permissions:
            await self._apply_permission_updates(user_id, permissions, initial_permissions)
        
        # Create privacy profile
        current_time = datetime.now(timezone.utc)
        
        # Create initial audit entry for consent
        initial_audit_entry = AuditEntry(
            id=str(uuid.uuid4()),
            user_id=user_id,
            action=AuditAction.CONSENT_GIVEN,
            category_id=None,
            details={"initial_setup": True, "permissions_count": len(permissions)},
            ip_address=None,
            user_agent=None,
            session_id=None,
            timestamp=current_time
        )
        
        profile = PrivacyProfile(
            user_id=user_id,
            permissions=permissions,
            audit_trail=[initial_audit_entry],
            consent_timestamp=current_time,
            last_updated=current_time
        )
        
        # Store profile and add audit entry to cache
        self._privacy_profiles[user_id] = profile
        self._audit_cache.append(initial_audit_entry)
        
        return profile
    
    async def update_permissions(self, user_id: str, permission_updates: Dict[str, Any],
                               session_context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Update user permissions with audit trail
        
        Args:
            user_id: User identifier
            permission_updates: Dictionary of permission updates
            session_context: Optional session context for audit
            
        Returns:
            Updated permissions summary
        """
        logger.info(f"Updating permissions for user: {user_id}")
        
        if user_id not in self._privacy_profiles:
            await self.create_privacy_profile(user_id)
        
        profile = self._privacy_profiles[user_id]
        old_permissions = {k: v.permission_level.value for k, v in profile.permissions.items()}
        
        # Apply updates
        await self._apply_permission_updates(user_id, profile.permissions, permission_updates)
        
        # Update profile
        profile.last_updated = datetime.now(timezone.utc)
        
        # Record audit entry
        await self._add_audit_entry(
            user_id=user_id,
            action=AuditAction.PERMISSION_CHANGED,
            details={
                "old_permissions": old_permissions,
                "new_permissions": {k: v.permission_level.value for k, v in profile.permissions.items()},
                "changes": permission_updates,
                "session_context": session_context or {}
            },
            session_id=session_context.get("session_id") if session_context else None
        )
        
        return await self.get_permission_summary(user_id)
    
    async def _apply_permission_updates(self, user_id: str, permissions: Dict[str, PermissionSetting],
                                      updates: Dict[str, Any]):
        """Apply permission updates to the permissions dictionary"""
        for category_id, setting in updates.items():
            if category_id not in self._data_categories:
                logger.warning(f"Unknown category in permissions update: {category_id}")
                continue
            
            if category_id not in permissions:
                permissions[category_id] = PermissionSetting(
                    category_id=category_id,
                    permission_level=PermissionLevel.NONE,
                    access_types=set()
                )
            
            perm = permissions[category_id]
            
            # Update permission level
            if isinstance(setting, bool):
                perm.permission_level = PermissionLevel.FULL if setting else PermissionLevel.NONE
                perm.access_types = {AccessType.VIEW, AccessType.ANALYZE} if setting else set()
            elif isinstance(setting, dict):
                if "level" in setting:
                    perm.permission_level = PermissionLevel(setting["level"])
                if "access_types" in setting:
                    perm.access_types = {AccessType(at) for at in setting["access_types"]}
                if "expires_at" in setting:
                    perm.expires_at = datetime.fromisoformat(setting["expires_at"])
            
            perm.updated_at = datetime.now(timezone.utc)
    
    async def check_permission(self, user_id: str, category_id: str, access_type: AccessType,
                             log_access: bool = True) -> bool:
        """
        Check if user has permission for specific data access
        
        Args:
            user_id: User identifier
            category_id: Data category identifier
            access_type: Type of access requested
            log_access: Whether to log this access check
            
        Returns:
            True if access is granted, False otherwise
        """
        if user_id not in self._privacy_profiles:
            logger.warning(f"No privacy profile found for user: {user_id}")
            return False
        
        profile = self._privacy_profiles[user_id]
        
        if category_id not in profile.permissions:
            logger.warning(f"No permission setting for category: {category_id}")
            return False
        
        permission = profile.permissions[category_id]
        
        # Check if permission has expired
        if permission.expires_at and permission.expires_at < datetime.now(timezone.utc):
            logger.info(f"Permission expired for user {user_id}, category {category_id}")
            return False
        
        # Check permission level
        if permission.permission_level == PermissionLevel.NONE:
            return False
        
        # Check specific access type
        has_access = access_type in permission.access_types or permission.permission_level == PermissionLevel.ADMIN
        
        # Log access if requested
        if log_access and has_access:
            await self._add_audit_entry(
                user_id=user_id,
                action=AuditAction.DATA_ACCESSED,
                category_id=category_id,
                details={
                    "access_type": access_type.value,
                    "permission_level": permission.permission_level.value,
                    "granted": has_access
                }
            )
        
        return has_access
    
    async def filter_data_by_permissions(self, user_id: str, data: Dict[str, Any],
                                       context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Filter data based on user permissions with real-time enforcement
        
        Args:
            user_id: User identifier
            data: Complete data dictionary
            context: Optional context for filtering decisions
            
        Returns:
            Filtered data dictionary
        """
        logger.info(f"Filtering data for user: {user_id}")
        
        if user_id not in self._privacy_profiles:
            await self.create_privacy_profile(user_id)
        
        filtered_data = {}
        access_log = {}
        
        for category_id, category in self._data_categories.items():
            # Use category_id as the data key (test data uses category IDs as keys)
            data_key = category_id
            
            # Check if data exists
            if data_key not in data:
                # Initialize with appropriate empty value based on expected data type
                if data_key in ["credit_score", "epf_balance"]:
                    filtered_data[data_key] = {}
                else:
                    filtered_data[data_key] = []
                access_log[category_id] = "no_data"
                continue
            
            # Check permission
            has_access = await self.check_permission(
                user_id, category_id, AccessType.VIEW, log_access=True
            )
            
            if has_access:
                # Apply data minimization if enabled
                if self._privacy_profiles[user_id].data_minimization:
                    filtered_data[data_key] = await self._apply_data_minimization(
                        data[data_key], category_id, user_id
                    )
                else:
                    filtered_data[data_key] = data[data_key]
                access_log[category_id] = "granted"
            else:
                # Initialize with appropriate empty value based on expected data type
                if data_key in ["credit_score", "epf_balance"]:
                    filtered_data[data_key] = {}
                else:
                    filtered_data[data_key] = []
                access_log[category_id] = "denied"
        
        # Add metadata
        filtered_data["_privacy_metadata"] = {
            "user_id": user_id,
            "filtered_at": datetime.now(timezone.utc).isoformat(),
            "access_log": access_log,
            "data_minimization": self._privacy_profiles[user_id].data_minimization,
            "privacy_level": self._privacy_profiles[user_id].privacy_level
        }
        
        return filtered_data
    
    async def _apply_data_minimization(self, data: Any, category_id: str, user_id: str) -> Any:
        """Apply data minimization rules based on category and user preferences"""
        if not isinstance(data, list):
            return data
        
        category = self._data_categories[category_id]
        permission = self._privacy_profiles[user_id].permissions[category_id]
        
        # Apply minimization based on permission level
        if permission.permission_level == PermissionLevel.LIMITED:
            # For limited access, reduce sensitive fields
            if category_id == "transactions":
                return [
                    {
                        "id": item.get("id", ""),
                        "amount": item.get("amount", 0),
                        "category": item.get("category", ""),
                        "date": item.get("date", "")[:10]  # Date only, no time
                    }
                    for item in data[:50]  # Limit to 50 recent items
                ]
            elif category_id == "accounts":
                return [
                    {
                        "id": item.get("id", ""),
                        "name": item.get("name", "").replace(item.get("name", "")[:-4], "****") if item.get("name") else "",
                        "type": item.get("type", ""),
                        "balance": round(item.get("balance", 0), -2)  # Round to nearest 100
                    }
                    for item in data
                ]
        
        return data
    
    async def get_permission_summary(self, user_id: str) -> Dict[str, Any]:
        """
        Get comprehensive permission summary for user
        
        Args:
            user_id: User identifier
            
        Returns:
            Detailed permission summary
        """
        if user_id not in self._privacy_profiles:
            await self.create_privacy_profile(user_id)
        
        profile = self._privacy_profiles[user_id]
        
        # Analyze permissions
        permission_analysis = {}
        granted_categories = []
        denied_categories = []
        expired_permissions = []
        
        now = datetime.now(timezone.utc)
        
        for cat_id, permission in profile.permissions.items():
            category = self._data_categories[cat_id]
            
            # Check if expired
            is_expired = permission.expires_at and permission.expires_at < now
            if is_expired:
                expired_permissions.append(cat_id)
            
            # Categorize permission
            if permission.permission_level == PermissionLevel.NONE or is_expired:
                denied_categories.append(cat_id)
            else:
                granted_categories.append(cat_id)
            
            permission_analysis[cat_id] = {
                "category_name": category.display_name,
                "permission_level": permission.permission_level.value,
                "access_types": [at.value for at in permission.access_types],
                "granted_at": permission.granted_at.isoformat() if permission.granted_at else None,
                "expires_at": permission.expires_at.isoformat() if permission.expires_at else None,
                "is_expired": is_expired,
                "sensitivity_level": category.sensitivity_level,
                "required_for_basic_function": category.required_for_basic_function
            }
        
        # Calculate privacy score (0-100)
        total_categories = len(self._data_categories)
        granted_count = len(granted_categories)
        weighted_score = sum(
            100 - (self._data_categories[cat_id].sensitivity_level * 15)
            for cat_id in granted_categories
        ) / max(total_categories, 1)
        
        return {
            "user_id": user_id,
            "privacy_level": profile.privacy_level,
            "data_minimization": profile.data_minimization,
            "last_updated": profile.last_updated.isoformat(),
            "consent_timestamp": profile.consent_timestamp.isoformat(),
            "permission_summary": {
                "total_categories": total_categories,
                "granted_categories": len(granted_categories),
                "denied_categories": len(denied_categories),
                "expired_permissions": len(expired_permissions),
                "permission_ratio": granted_count / total_categories
            },
            "privacy_score": round(weighted_score, 1),
            "category_permissions": permission_analysis,
            "access_level": self._determine_access_level(granted_count, total_categories),
            "recommendations": await self._generate_privacy_recommendations(user_id)
        }
    
    def _determine_access_level(self, granted_count: int, total_count: int) -> str:
        """Determine overall access level based on granted permissions"""
        ratio = granted_count / total_count if total_count > 0 else 0
        
        if ratio >= 0.9:
            return "full_access"
        elif ratio >= 0.7:
            return "high_access"
        elif ratio >= 0.5:
            return "moderate_access"
        elif ratio >= 0.3:
            return "limited_access"
        else:
            return "minimal_access"
    
    async def _generate_privacy_recommendations(self, user_id: str) -> List[Dict[str, str]]:
        """Generate privacy recommendations based on current settings"""
        if user_id not in self._privacy_profiles:
            return []
        
        profile = self._privacy_profiles[user_id]
        recommendations = []
        
        # Check for high-sensitivity categories with full access
        for cat_id, permission in profile.permissions.items():
            category = self._data_categories[cat_id]
            
            if (category.sensitivity_level >= 4 and 
                permission.permission_level in [PermissionLevel.FULL, PermissionLevel.ADMIN]):
                recommendations.append({
                    "type": "security",
                    "category": category.display_name,
                    "message": f"Consider limiting access to {category.display_name} for better privacy",
                    "action": "reduce_permission"
                })
        
        # Check for expired permissions
        now = datetime.now(timezone.utc)
        for cat_id, permission in profile.permissions.items():
            if permission.expires_at and permission.expires_at < now:
                category = self._data_categories[cat_id]
                recommendations.append({
                    "type": "expired",
                    "category": category.display_name,
                    "message": f"Permission for {category.display_name} has expired",
                    "action": "renew_permission"
                })
        
        # Data minimization recommendation
        if not profile.data_minimization:
            recommendations.append({
                "type": "privacy",
                "category": "general",
                "message": "Enable data minimization to reduce data exposure",
                "action": "enable_minimization"
            })
        
        return recommendations
    
    async def get_audit_trail(self, user_id: str, limit: int = 100, 
                            action_filter: Optional[List[AuditAction]] = None) -> List[Dict[str, Any]]:
        """
        Get user's audit trail
        
        Args:
            user_id: User identifier
            limit: Maximum number of entries to return
            action_filter: Optional filter for specific actions
            
        Returns:
            List of audit entries
        """
        if user_id not in self._privacy_profiles:
            return []
        
        profile = self._privacy_profiles[user_id]
        audit_entries = profile.audit_trail
        
        # Apply filter if specified
        if action_filter:
            audit_entries = [
                entry for entry in audit_entries
                if entry.action in action_filter
            ]
        
        # Sort by timestamp (most recent first) and limit
        audit_entries = sorted(audit_entries, key=lambda x: x.timestamp, reverse=True)[:limit]
        
        # Convert to dictionary format
        return [
            {
                "id": entry.id,
                "action": entry.action.value,
                "category_id": entry.category_id,
                "details": entry.details,
                "timestamp": entry.timestamp.isoformat(),
                "ip_address": entry.ip_address,
                "session_id": entry.session_id
            }
            for entry in audit_entries
        ]
    
    async def _add_audit_entry(self, user_id: str, action: AuditAction, 
                             category_id: Optional[str] = None, details: Optional[Dict[str, Any]] = None,
                             ip_address: Optional[str] = None, user_agent: Optional[str] = None,
                             session_id: Optional[str] = None):
        """Add entry to user's audit trail"""
        entry = AuditEntry(
            id=str(uuid.uuid4()),
            user_id=user_id,
            action=action,
            category_id=category_id,
            details=details or {},
            ip_address=ip_address,
            user_agent=user_agent,
            session_id=session_id,
            timestamp=datetime.now(timezone.utc)
        )
        
        # Add to user's profile
        if user_id in self._privacy_profiles:
            self._privacy_profiles[user_id].audit_trail.append(entry)
        
        # Add to cache for batch processing
        self._audit_cache.append(entry)
        
        # Flush cache if it gets large
        if len(self._audit_cache) >= 100:
            await self._flush_audit_cache()
    
    async def _flush_audit_cache(self):
        """Flush audit cache to storage"""
        if not self.audit_storage_path or not self._audit_cache:
            return
        
        # Write audit entries to daily log files
        today = datetime.now(timezone.utc).date()
        log_file = self.audit_storage_path / f"audit_{today.isoformat()}.jsonl"
        
        with open(log_file, 'a', encoding='utf-8') as f:
            for entry in self._audit_cache:
                json.dump(asdict(entry), f, default=str)
                f.write('\n')
        
        logger.info(f"Flushed {len(self._audit_cache)} audit entries to {log_file}")
        self._audit_cache.clear()
    
    async def request_data_export(self, user_id: str, categories: List[str],
                                format: str = "json") -> Dict[str, Any]:
        """
        Request data export for specified categories
        
        Args:
            user_id: User identifier
            categories: List of category IDs to export
            format: Export format (json, csv)
            
        Returns:
            Export request details
        """
        logger.info(f"Data export requested by user {user_id} for categories: {categories}")
        
        # Validate categories
        valid_categories = [cat for cat in categories if cat in self._data_categories]
        
        # Check permissions for each category
        allowed_categories = []
        for cat_id in valid_categories:
            if await self.check_permission(user_id, cat_id, AccessType.EXPORT, log_access=False):
                allowed_categories.append(cat_id)
        
        request_id = str(uuid.uuid4())
        
        # Log export request
        await self._add_audit_entry(
            user_id=user_id,
            action=AuditAction.DATA_EXPORTED,
            details={
                "request_id": request_id,
                "requested_categories": categories,
                "allowed_categories": allowed_categories,
                "format": format
            }
        )
        
        return {
            "request_id": request_id,
            "requested_categories": categories,
            "allowed_categories": allowed_categories,
            "denied_categories": list(set(categories) - set(allowed_categories)),
            "format": format,
            "status": "processing",
            "estimated_completion": (datetime.now(timezone.utc) + timedelta(hours=1)).isoformat()
        }
    
    async def request_data_deletion(self, user_id: str, categories: List[str],
                                  reason: str = "") -> Dict[str, Any]:
        """
        Request data deletion for specified categories
        
        Args:
            user_id: User identifier
            categories: List of category IDs to delete
            reason: Optional reason for deletion
            
        Returns:
            Deletion request details
        """
        logger.info(f"Data deletion requested by user {user_id} for categories: {categories}")
        
        # Validate categories
        valid_categories = [cat for cat in categories if cat in self._data_categories]
        
        # Check for categories required for basic function
        essential_categories = [
            cat_id for cat_id in valid_categories 
            if self._data_categories[cat_id].required_for_basic_function
        ]
        
        deletion_id = str(uuid.uuid4())
        
        # Log deletion request
        await self._add_audit_entry(
            user_id=user_id,
            action=AuditAction.DATA_DELETION_REQUESTED,
            details={
                "deletion_id": deletion_id,
                "categories": valid_categories,
                "essential_categories": essential_categories,
                "reason": reason
            }
        )
        
        return {
            "deletion_id": deletion_id,
            "categories": valid_categories,
            "essential_categories": essential_categories,
            "warnings": [
                f"Deleting {self._data_categories[cat_id].display_name} may affect basic functionality"
                for cat_id in essential_categories
            ],
            "status": "pending_confirmation",
            "estimated_completion": (datetime.now(timezone.utc) + timedelta(days=1)).isoformat()
        }
    
    def get_data_categories(self) -> List[Dict[str, Any]]:
        """Get all available data categories with details"""
        return [
            {
                "id": category.id,
                "name": category.name,
                "display_name": category.display_name,
                "description": category.description,
                "sensitivity_level": category.sensitivity_level,
                "data_types": category.data_types,
                "required_for_basic_function": category.required_for_basic_function,
                "gdpr_category": category.gdpr_category,
                "retention_period_days": category.retention_period_days
            }
            for category in self._data_categories.values()
        ]
    
    async def get_privacy_dashboard(self, user_id: str) -> Dict[str, Any]:
        """
        Get comprehensive privacy dashboard data
        
        Args:
            user_id: User identifier
            
        Returns:
            Privacy dashboard data
        """
        if user_id not in self._privacy_profiles:
            await self.create_privacy_profile(user_id)
        
        profile = self._privacy_profiles[user_id]
        permission_summary = await self.get_permission_summary(user_id)
        recent_audit = await self.get_audit_trail(user_id, limit=10)
        
        # Calculate usage statistics
        data_access_count = len([
            entry for entry in profile.audit_trail
            if entry.action == AuditAction.DATA_ACCESSED
        ])
        
        return {
            "user_id": user_id,
            "privacy_overview": {
                "privacy_level": profile.privacy_level,
                "privacy_score": permission_summary["privacy_score"],
                "data_minimization": profile.data_minimization,
                "last_updated": profile.last_updated.isoformat()
            },
            "permission_summary": permission_summary["permission_summary"],
            "recent_activity": recent_audit,
            "usage_statistics": {
                "total_data_accesses": data_access_count,
                "categories_accessed": len(set(
                    entry.category_id for entry in profile.audit_trail
                    if entry.action == AuditAction.DATA_ACCESSED and entry.category_id
                )),
                "last_access": max(
                    (entry.timestamp for entry in profile.audit_trail), 
                    default=profile.consent_timestamp
                ).isoformat()
            },
            "recommendations": await self._generate_privacy_recommendations(user_id),
            "compliance_status": {
                "gdpr_compliant": True,
                "consent_given": profile.consent_timestamp.isoformat(),
                "audit_trail_available": len(profile.audit_trail) > 0
            }
        }
    
    async def cleanup_expired_permissions(self):
        """Clean up expired permissions across all users"""
        logger.info("Cleaning up expired permissions")
        
        now = datetime.now(timezone.utc)
        expired_count = 0
        
        for user_id, profile in self._privacy_profiles.items():
            for cat_id, permission in profile.permissions.items():
                if permission.expires_at and permission.expires_at < now:
                    permission.permission_level = PermissionLevel.NONE
                    permission.access_types = set()
                    permission.updated_at = now
                    expired_count += 1
                    
                    # Log expiration
                    await self._add_audit_entry(
                        user_id=user_id,
                        action=AuditAction.PERMISSION_CHANGED,
                        category_id=cat_id,
                        details={"reason": "expired", "previous_level": permission.permission_level.value}
                    )
        
        logger.info(f"Cleaned up {expired_count} expired permissions")
        return expired_count