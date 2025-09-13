"""
Privacy and Permission Management System

This module handles:
- User data access permissions
- Privacy-preserving analysis
- Data masking and anonymization
- Audit logging
- Consent management
"""

import json
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Set, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import hashlib
from loguru import logger
from data_preprocessing import UserPermissions
import sqlite3
import os

class PermissionLevel(Enum):
    """Permission levels for data access"""
    DENIED = "denied"
    READ_ONLY = "read_only"
    FULL_ACCESS = "full_access"

class DataCategory(Enum):
    """Financial data categories"""
    ASSETS = "assets"
    LIABILITIES = "liabilities"
    TRANSACTIONS = "transactions"
    EPF_RETIREMENT = "epf_retirement_balance"
    CREDIT_SCORE = "credit_score"
    INVESTMENTS = "investments"

@dataclass
class ConsentRecord:
    """Records user consent for data processing"""
    user_id: str
    category: str
    permission_level: PermissionLevel
    granted_at: datetime
    expires_at: Optional[datetime] = None
    purpose: str = "financial_analysis"
    revoked: bool = False
    revoked_at: Optional[datetime] = None

@dataclass
class AccessLog:
    """Logs data access events"""
    log_id: str
    user_id: str
    accessed_categories: List[str]
    access_time: datetime
    purpose: str
    result_hash: Optional[str] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None

@dataclass
class PrivacySettings:
    """User privacy preferences"""
    user_id: str
    data_retention_days: int = 365
    allow_analytics: bool = True
    allow_personalization: bool = True
    require_explicit_consent: bool = True
    anonymize_insights: bool = False
    audit_frequency: str = "monthly"  # daily, weekly, monthly

class PrivacyManager:
    """Comprehensive privacy and permission management system"""
    
    def __init__(self, db_path: str = "privacy.db"):
        """Initialize the privacy manager"""
        self.db_path = db_path
        self._init_database()
        self.encryption_key = os.environ.get('PRIVACY_ENCRYPTION_KEY', 'default-key-change-in-production')
        
        # Privacy-preserving thresholds
        self.min_aggregation_size = 5  # Minimum group size for analytics
        self.noise_scale = 0.1  # Scale for differential privacy noise
        
        logger.info("Privacy manager initialized")
    
    def _init_database(self):
        """Initialize the privacy database"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Consent records table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS consent_records (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT NOT NULL,
                    category TEXT NOT NULL,
                    permission_level TEXT NOT NULL,
                    granted_at TIMESTAMP NOT NULL,
                    expires_at TIMESTAMP,
                    purpose TEXT NOT NULL,
                    revoked BOOLEAN DEFAULT FALSE,
                    revoked_at TIMESTAMP
                )
            ''')
            
            # Access logs table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS access_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    log_id TEXT UNIQUE NOT NULL,
                    user_id TEXT NOT NULL,
                    accessed_categories TEXT NOT NULL,
                    access_time TIMESTAMP NOT NULL,
                    purpose TEXT NOT NULL,
                    result_hash TEXT,
                    ip_address TEXT,
                    user_agent TEXT
                )
            ''')
            
            # Privacy settings table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS privacy_settings (
                    user_id TEXT PRIMARY KEY,
                    data_retention_days INTEGER DEFAULT 365,
                    allow_analytics BOOLEAN DEFAULT TRUE,
                    allow_personalization BOOLEAN DEFAULT TRUE,
                    require_explicit_consent BOOLEAN DEFAULT TRUE,
                    anonymize_insights BOOLEAN DEFAULT FALSE,
                    audit_frequency TEXT DEFAULT 'monthly',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            conn.commit()
        
        logger.info("Privacy database initialized")
    
    def request_permission(self, 
                          user_id: str, 
                          category: DataCategory, 
                          permission_level: PermissionLevel = PermissionLevel.READ_ONLY,
                          purpose: str = "financial_analysis",
                          duration_days: Optional[int] = None) -> bool:
        """Request permission for data access"""
        
        try:
            expires_at = None
            if duration_days:
                expires_at = datetime.now() + timedelta(days=duration_days)
            
            consent = ConsentRecord(
                user_id=user_id,
                category=category.value,
                permission_level=permission_level,
                granted_at=datetime.now(),
                expires_at=expires_at,
                purpose=purpose
            )
            
            # Store consent in database
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO consent_records 
                    (user_id, category, permission_level, granted_at, expires_at, purpose)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (consent.user_id, consent.category, consent.permission_level.value,
                      consent.granted_at, consent.expires_at, consent.purpose))
                conn.commit()
            
            logger.info(f"Permission granted for user {user_id}, category {category.value}")
            return True
            
        except Exception as e:
            logger.error(f"Error granting permission: {e}")
            return False
    
    def revoke_permission(self, user_id: str, category: DataCategory) -> bool:
        """Revoke permission for a data category"""
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    UPDATE consent_records 
                    SET revoked = TRUE, revoked_at = ?
                    WHERE user_id = ? AND category = ? AND revoked = FALSE
                ''', (datetime.now(), user_id, category.value))
                conn.commit()
            
            logger.info(f"Permission revoked for user {user_id}, category {category.value}")
            return True
            
        except Exception as e:
            logger.error(f"Error revoking permission: {e}")
            return False
    
    def check_permission(self, user_id: str, category: DataCategory) -> PermissionLevel:
        """Check current permission level for a data category"""
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT permission_level, expires_at FROM consent_records
                    WHERE user_id = ? AND category = ? AND revoked = FALSE
                    ORDER BY granted_at DESC LIMIT 1
                ''', (user_id, category.value))
                
                result = cursor.fetchone()
                
                if not result:
                    return PermissionLevel.DENIED
                
                permission_level, expires_at = result
                
                # Check if permission has expired
                if expires_at:
                    expire_date = datetime.fromisoformat(expires_at)
                    if datetime.now() > expire_date:
                        return PermissionLevel.DENIED
                
                return PermissionLevel(permission_level)
                
        except Exception as e:
            logger.error(f"Error checking permission: {e}")
            return PermissionLevel.DENIED
    
    def get_user_permissions(self, user_id: str) -> UserPermissions:
        """Get UserPermissions object based on current consent"""
        
        permissions = {}
        
        for category in DataCategory:
            permission_level = self.check_permission(user_id, category)
            permissions[category.value] = permission_level != PermissionLevel.DENIED
        
        return UserPermissions(**permissions)
    
    def apply_privacy_filters(self, 
                            user_id: str, 
                            financial_data: Dict[str, Any], 
                            analysis_results: Dict[str, Any]) -> Dict[str, Any]:
        """Apply privacy filters to analysis results"""
        
        settings = self.get_privacy_settings(user_id)
        filtered_results = analysis_results.copy()
        
        if settings.anonymize_insights:
            filtered_results = self._anonymize_results(filtered_results)
        
        if not settings.allow_analytics:
            # Remove detailed analytics that could be used for profiling
            filtered_results = self._remove_analytics(filtered_results)
        
        if not settings.allow_personalization:
            # Remove personalized recommendations
            filtered_results = self._remove_personalization(filtered_results)
        
        # Add differential privacy noise if needed
        filtered_results = self._add_privacy_noise(filtered_results)
        
        return filtered_results
    
    def log_access(self, 
                   user_id: str, 
                   accessed_categories: List[str],
                   purpose: str = "financial_analysis",
                   result_hash: Optional[str] = None,
                   ip_address: Optional[str] = None,
                   user_agent: Optional[str] = None) -> str:
        """Log data access event"""
        
        log_id = str(uuid.uuid4())
        
        access_log = AccessLog(
            log_id=log_id,
            user_id=user_id,
            accessed_categories=accessed_categories,
            access_time=datetime.now(),
            purpose=purpose,
            result_hash=result_hash,
            ip_address=ip_address,
            user_agent=user_agent
        )
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO access_logs 
                    (log_id, user_id, accessed_categories, access_time, purpose, 
                     result_hash, ip_address, user_agent)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (access_log.log_id, access_log.user_id, 
                      json.dumps(access_log.accessed_categories),
                      access_log.access_time, access_log.purpose,
                      access_log.result_hash, access_log.ip_address, 
                      access_log.user_agent))
                conn.commit()
            
            return log_id
            
        except Exception as e:
            logger.error(f"Error logging access: {e}")
            return ""
    
    def get_privacy_settings(self, user_id: str) -> PrivacySettings:
        """Get user's privacy settings"""
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT * FROM privacy_settings WHERE user_id = ?
                ''', (user_id,))
                
                result = cursor.fetchone()
                
                if result:
                    columns = [desc[0] for desc in cursor.description]
                    settings_dict = dict(zip(columns, result))
                    # Remove timestamps for dataclass creation
                    settings_dict.pop('created_at', None)
                    settings_dict.pop('updated_at', None)
                    return PrivacySettings(**settings_dict)
                else:
                    # Return default settings
                    return PrivacySettings(user_id=user_id)
                    
        except Exception as e:
            logger.error(f"Error getting privacy settings: {e}")
            return PrivacySettings(user_id=user_id)
    
    def update_privacy_settings(self, settings: PrivacySettings) -> bool:
        """Update user's privacy settings"""
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT OR REPLACE INTO privacy_settings 
                    (user_id, data_retention_days, allow_analytics, allow_personalization,
                     require_explicit_consent, anonymize_insights, audit_frequency, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (settings.user_id, settings.data_retention_days, settings.allow_analytics,
                      settings.allow_personalization, settings.require_explicit_consent,
                      settings.anonymize_insights, settings.audit_frequency, datetime.now()))
                conn.commit()
            
            logger.info(f"Privacy settings updated for user {settings.user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating privacy settings: {e}")
            return False
    
    def get_user_data_summary(self, user_id: str) -> Dict[str, Any]:
        """Get summary of user's data and permissions"""
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Get consent records
                cursor.execute('''
                    SELECT category, permission_level, granted_at, expires_at, revoked
                    FROM consent_records WHERE user_id = ?
                    ORDER BY granted_at DESC
                ''', (user_id,))
                consent_records = cursor.fetchall()
                
                # Get access logs
                cursor.execute('''
                    SELECT COUNT(*) FROM access_logs WHERE user_id = ?
                ''', (user_id,))
                access_count = cursor.fetchone()[0]
                
                # Get latest access
                cursor.execute('''
                    SELECT access_time FROM access_logs WHERE user_id = ?
                    ORDER BY access_time DESC LIMIT 1
                ''', (user_id,))
                latest_access = cursor.fetchone()
                
                return {
                    'user_id': user_id,
                    'consent_records': [
                        {
                            'category': record[0],
                            'permission_level': record[1],
                            'granted_at': record[2],
                            'expires_at': record[3],
                            'revoked': bool(record[4])
                        }
                        for record in consent_records
                    ],
                    'total_access_events': access_count,
                    'latest_access': latest_access[0] if latest_access else None,
                    'privacy_settings': asdict(self.get_privacy_settings(user_id))
                }
                
        except Exception as e:
            logger.error(f"Error getting user data summary: {e}")
            return {'error': str(e)}
    
    def export_user_data(self, user_id: str) -> Dict[str, Any]:
        """Export all user data (GDPR compliance)"""
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Export consent records
                cursor.execute('''
                    SELECT * FROM consent_records WHERE user_id = ?
                ''', (user_id,))
                consent_data = cursor.fetchall()
                consent_columns = [desc[0] for desc in cursor.description]
                
                # Export access logs
                cursor.execute('''
                    SELECT * FROM access_logs WHERE user_id = ?
                ''', (user_id,))
                access_data = cursor.fetchall()
                access_columns = [desc[0] for desc in cursor.description]
                
                # Export privacy settings
                cursor.execute('''
                    SELECT * FROM privacy_settings WHERE user_id = ?
                ''', (user_id,))
                settings_data = cursor.fetchone()
                settings_columns = [desc[0] for desc in cursor.description] if settings_data else []
                
                export_data = {
                    'user_id': user_id,
                    'export_date': datetime.now().isoformat(),
                    'consent_records': {
                        'columns': consent_columns,
                        'data': consent_data
                    },
                    'access_logs': {
                        'columns': access_columns,
                        'data': access_data
                    },
                    'privacy_settings': {
                        'columns': settings_columns,
                        'data': settings_data
                    } if settings_data else None
                }
                
                return export_data
                
        except Exception as e:
            logger.error(f"Error exporting user data: {e}")
            return {'error': str(e)}
    
    def delete_user_data(self, user_id: str, verify: bool = False) -> bool:
        """Delete all user data (GDPR right to be forgotten)"""
        
        if not verify:
            logger.warning("delete_user_data called without verification - ignoring")
            return False
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Delete consent records
                cursor.execute('DELETE FROM consent_records WHERE user_id = ?', (user_id,))
                consent_deleted = cursor.rowcount
                
                # Delete access logs
                cursor.execute('DELETE FROM access_logs WHERE user_id = ?', (user_id,))
                logs_deleted = cursor.rowcount
                
                # Delete privacy settings
                cursor.execute('DELETE FROM privacy_settings WHERE user_id = ?', (user_id,))
                settings_deleted = cursor.rowcount
                
                conn.commit()
                
                logger.info(f"Deleted user data for {user_id}: {consent_deleted} consents, "
                           f"{logs_deleted} logs, {settings_deleted} settings")
                return True
                
        except Exception as e:
            logger.error(f"Error deleting user data: {e}")
            return False
    
    def generate_privacy_report(self, user_id: str) -> Dict[str, Any]:
        """Generate privacy compliance report for user"""
        
        summary = self.get_user_data_summary(user_id)
        settings = self.get_privacy_settings(user_id)
        
        # Analyze compliance
        compliance_issues = []
        
        # Check for expired consents
        for consent in summary['consent_records']:
            if consent['expires_at'] and not consent['revoked']:
                expire_date = datetime.fromisoformat(consent['expires_at'])
                if datetime.now() > expire_date:
                    compliance_issues.append(f"Expired consent for {consent['category']}")
        
        # Check data retention
        if settings.data_retention_days > 0:
            retention_cutoff = datetime.now() - timedelta(days=settings.data_retention_days)
            # This would need to check actual financial data timestamps
            # For now, we'll check access logs
            try:
                with sqlite3.connect(self.db_path) as conn:
                    cursor = conn.cursor()
                    cursor.execute('''
                        SELECT COUNT(*) FROM access_logs 
                        WHERE user_id = ? AND access_time < ?
                    ''', (user_id, retention_cutoff))
                    old_logs = cursor.fetchone()[0]
                    
                    if old_logs > 0:
                        compliance_issues.append(f"{old_logs} access logs exceed retention period")
                        
            except Exception as e:
                compliance_issues.append(f"Error checking data retention: {e}")
        
        return {
            'user_id': user_id,
            'report_date': datetime.now().isoformat(),
            'privacy_settings': asdict(settings),
            'data_summary': summary,
            'compliance_status': 'Compliant' if not compliance_issues else 'Issues Found',
            'compliance_issues': compliance_issues,
            'recommendations': self._generate_privacy_recommendations(settings, compliance_issues)
        }
    
    def cleanup_expired_data(self) -> Dict[str, int]:
        """Clean up expired data according to retention policies"""
        
        cleanup_stats = {
            'expired_consents': 0,
            'old_access_logs': 0,
            'processed_users': 0
        }
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Get all users with privacy settings
                cursor.execute('SELECT user_id, data_retention_days FROM privacy_settings')
                users = cursor.fetchall()
                
                for user_id, retention_days in users:
                    if retention_days > 0:
                        cutoff_date = datetime.now() - timedelta(days=retention_days)
                        
                        # Delete old access logs
                        cursor.execute('''
                            DELETE FROM access_logs 
                            WHERE user_id = ? AND access_time < ?
                        ''', (user_id, cutoff_date))
                        cleanup_stats['old_access_logs'] += cursor.rowcount
                        
                        cleanup_stats['processed_users'] += 1
                
                # Mark expired consents as revoked
                cursor.execute('''
                    UPDATE consent_records 
                    SET revoked = TRUE, revoked_at = ?
                    WHERE expires_at < ? AND revoked = FALSE
                ''', (datetime.now(), datetime.now()))
                cleanup_stats['expired_consents'] = cursor.rowcount
                
                conn.commit()
                
            logger.info(f"Data cleanup completed: {cleanup_stats}")
            
        except Exception as e:
            logger.error(f"Error during data cleanup: {e}")
            cleanup_stats['error'] = str(e)
        
        return cleanup_stats
    
    def _anonymize_results(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Apply anonymization to analysis results"""
        
        anonymized = results.copy()
        
        # Remove or hash specific identifiers
        if 'user_id' in anonymized:
            anonymized['user_id'] = hashlib.sha256(
                anonymized['user_id'].encode()
            ).hexdigest()[:8]
        
        # Round financial amounts to reduce precision
        def round_amounts(obj, precision=100):
            if isinstance(obj, dict):
                return {k: round_amounts(v, precision) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [round_amounts(item, precision) for item in obj]
            elif isinstance(obj, (int, float)) and obj > 1000:  # Only round large amounts
                return round(obj / precision) * precision
            else:
                return obj
        
        anonymized = round_amounts(anonymized)
        
        return anonymized
    
    def _remove_analytics(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Remove detailed analytics from results"""
        
        filtered = results.copy()
        
        # Remove sections that could be used for detailed profiling
        sections_to_remove = [
            'spending_patterns',
            'cash_flow_forecast',
            'advanced_analysis'
        ]
        
        for section in sections_to_remove:
            if section in filtered:
                del filtered[section]
        
        return filtered
    
    def _remove_personalization(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Remove personalized recommendations"""
        
        filtered = results.copy()
        
        # Replace personalized recommendations with generic ones
        if 'personalized_recommendations' in filtered:
            filtered['general_recommendations'] = [
                "Review your budget regularly",
                "Build an emergency fund",
                "Consider diversifying investments",
                "Monitor your credit score"
            ]
            del filtered['personalized_recommendations']
        
        # Remove goal-specific analysis
        if 'goal_analysis' in filtered:
            del filtered['goal_analysis']
        
        return filtered
    
    def _add_privacy_noise(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Add differential privacy noise to numerical results"""
        
        import numpy as np
        
        def add_noise(obj):
            if isinstance(obj, dict):
                return {k: add_noise(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [add_noise(item) for item in obj]
            elif isinstance(obj, (int, float)) and obj != 0:
                # Add Laplace noise for differential privacy
                noise = np.random.laplace(0, self.noise_scale * abs(obj))
                return obj + noise
            else:
                return obj
        
        return add_noise(results)
    
    def _generate_privacy_recommendations(self, 
                                        settings: PrivacySettings, 
                                        issues: List[str]) -> List[str]:
        """Generate privacy recommendations"""
        
        recommendations = []
        
        if issues:
            recommendations.append("Review and update expired data consents")
            recommendations.append("Clean up old data according to retention policy")
        
        if not settings.require_explicit_consent:
            recommendations.append("Enable explicit consent requirement for better privacy")
        
        if settings.data_retention_days > 365:
            recommendations.append("Consider reducing data retention period")
        
        if not settings.anonymize_insights:
            recommendations.append("Consider enabling insight anonymization")
        
        recommendations.append("Regularly review access logs for unusual activity")
        recommendations.append("Update privacy preferences as needed")
        
        return recommendations

class ConsentManager:
    """Helper class for managing consent flows"""
    
    def __init__(self, privacy_manager: PrivacyManager):
        self.privacy_manager = privacy_manager
    
    def create_consent_flow(self, user_id: str) -> Dict[str, Any]:
        """Create a consent flow for new user"""
        
        categories = [
            {
                'id': DataCategory.ASSETS.value,
                'name': 'Assets',
                'description': 'Cash, bank balances, and property information',
                'required_for': ['Net worth calculation', 'Emergency fund analysis'],
                'sensitive_level': 'Medium'
            },
            {
                'id': DataCategory.LIABILITIES.value,
                'name': 'Liabilities',
                'description': 'Loans, credit card debt, and other obligations',
                'required_for': ['Debt optimization', 'Risk assessment'],
                'sensitive_level': 'High'
            },
            {
                'id': DataCategory.TRANSACTIONS.value,
                'name': 'Transactions',
                'description': 'Income, expenses, and spending patterns',
                'required_for': ['Budget recommendations', 'Savings analysis'],
                'sensitive_level': 'Very High'
            },
            {
                'id': DataCategory.EPF_RETIREMENT.value,
                'name': 'Retirement Savings',
                'description': 'EPF balance and retirement contributions',
                'required_for': ['Retirement planning', 'Tax optimization'],
                'sensitive_level': 'Medium'
            },
            {
                'id': DataCategory.CREDIT_SCORE.value,
                'name': 'Credit Information',
                'description': 'Credit score and credit rating',
                'required_for': ['Loan recommendations', 'Financial health score'],
                'sensitive_level': 'High'
            },
            {
                'id': DataCategory.INVESTMENTS.value,
                'name': 'Investments',
                'description': 'Stocks, mutual funds, and other investments',
                'required_for': ['Portfolio analysis', 'Investment recommendations'],
                'sensitive_level': 'Medium'
            }
        ]
        
        return {
            'user_id': user_id,
            'flow_id': str(uuid.uuid4()),
            'categories': categories,
            'privacy_notice': self._get_privacy_notice(),
            'terms': self._get_terms_of_service()
        }
    
    def process_consent_response(self, 
                                user_id: str, 
                                consents: Dict[str, Dict[str, Any]]) -> bool:
        """Process user's consent responses"""
        
        try:
            for category_id, consent_data in consents.items():
                if consent_data.get('granted', False):
                    category = DataCategory(category_id)
                    permission_level = PermissionLevel(
                        consent_data.get('permission_level', 'read_only')
                    )
                    duration = consent_data.get('duration_days')
                    
                    self.privacy_manager.request_permission(
                        user_id=user_id,
                        category=category,
                        permission_level=permission_level,
                        duration_days=duration
                    )
            
            return True
            
        except Exception as e:
            logger.error(f"Error processing consent response: {e}")
            return False
    
    def _get_privacy_notice(self) -> str:
        """Get privacy notice text"""
        return """
        Privacy Notice:
        
        We collect and process your financial data to provide personalized financial insights 
        and recommendations. Your data is:
        
        - Encrypted and securely stored
        - Never shared with third parties without consent
        - Processed only for the purposes you approve
        - Retained according to your preferences
        - Available for export or deletion at any time
        
        You can update your privacy preferences and revoke consent at any time.
        """
    
    def _get_terms_of_service(self) -> str:
        """Get terms of service text"""
        return """
        Terms of Service:
        
        By using our financial analysis service, you agree to:
        
        1. Provide accurate financial information
        2. Use insights for personal financial planning only
        3. Keep your account secure and confidential
        4. Notify us of any data breaches or security concerns
        
        We provide financial insights for informational purposes only and do not 
        provide investment, legal, or tax advice.
        """

# Example usage and testing functions
def example_usage():
    """Example usage of the privacy management system"""
    
    # Initialize privacy manager
    privacy_manager = PrivacyManager("example_privacy.db")
    consent_manager = ConsentManager(privacy_manager)
    
    user_id = "user_123"
    
    # Create consent flow
    consent_flow = consent_manager.create_consent_flow(user_id)
    print(f"Created consent flow with {len(consent_flow['categories'])} categories")
    
    # Simulate user granting permissions
    user_consents = {
        DataCategory.ASSETS.value: {
            'granted': True,
            'permission_level': 'read_only',
            'duration_days': 365
        },
        DataCategory.TRANSACTIONS.value: {
            'granted': True,
            'permission_level': 'full_access',
            'duration_days': 30
        },
        DataCategory.CREDIT_SCORE.value: {
            'granted': False
        }
    }
    
    # Process consents
    consent_manager.process_consent_response(user_id, user_consents)
    
    # Check permissions
    permissions = privacy_manager.get_user_permissions(user_id)
    print(f"User permissions: {permissions}")
    
    # Log access
    access_log_id = privacy_manager.log_access(
        user_id=user_id,
        accessed_categories=[DataCategory.ASSETS.value, DataCategory.TRANSACTIONS.value],
        purpose="financial_analysis"
    )
    print(f"Access logged with ID: {access_log_id}")
    
    # Generate privacy report
    report = privacy_manager.generate_privacy_report(user_id)
    print(f"Privacy report generated: {report['compliance_status']}")
    
    # Update privacy settings
    settings = PrivacySettings(
        user_id=user_id,
        data_retention_days=90,
        anonymize_insights=True,
        require_explicit_consent=True
    )
    privacy_manager.update_privacy_settings(settings)
    
    print("Privacy management example completed")

if __name__ == "__main__":
    example_usage()