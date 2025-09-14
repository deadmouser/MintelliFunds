"""
Comprehensive API Server for Financial AI Assistant

This server provides:
- Financial analysis endpoints
- Natural language chat interface
- Privacy and consent management
- User session management
- Data validation and processing
- Real-time insights generation
"""

import os
import json
import uuid
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
from flask import Flask, request, jsonify, session
from flask_cors import CORS
from loguru import logger
import sqlite3
from functools import wraps
import hashlib

# Import our custom modules
from model import FinancialAdvisorModel, FinancialInsightGenerator
from insights_engine import AdvancedInsightsEngine, FinancialGoal
from privacy_manager import PrivacyManager, ConsentManager, DataCategory, PermissionLevel
from nlp_interface import FinancialNLPProcessor
from data_preprocessing import AdvancedDataPreprocessor, UserPermissions

# Import LLM NLP processor (optional)
try:
    from llm_nlp_interface import LLMFinancialNLPProcessor
    LLM_AVAILABLE = True
except ImportError:
    LLM_AVAILABLE = False
    logger.warning("LLM NLP processor not available. Using rule-based NLP processor.")

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'dev-key-change-in-production')
CORS(app, supports_credentials=True)

# Configure logging
logger.add("api_server.log", rotation="10 MB", level="INFO")

# Initialize components
insights_engine = AdvancedInsightsEngine()
privacy_manager = PrivacyManager("production_privacy.db")
consent_manager = ConsentManager(privacy_manager)

# Use LLM-based NLP processor if available and configured, otherwise use rule-based
if LLM_AVAILABLE and os.getenv("USE_LLM_NLP", "false").lower() == "true":
    try:
        nlp_processor = LLMFinancialNLPProcessor(insights_engine, privacy_manager)
        logger.info("Using LLM-based NLP processor")
    except Exception as e:
        logger.error(f"Failed to initialize LLM NLP processor: {e}")
        nlp_processor = FinancialNLPProcessor(insights_engine, privacy_manager)
        logger.info("Falling back to rule-based NLP processor")
else:
    nlp_processor = FinancialNLPProcessor(insights_engine, privacy_manager)
    logger.info("Using rule-based NLP processor")

data_preprocessor = AdvancedDataPreprocessor()

logger.info("Financial AI API Server initialized")

# Authentication and session management
def require_auth(f):
    """Decorator to require authentication"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'error': 'Authentication required'}), 401
        return f(*args, **kwargs)
    return decorated_function

def get_current_user() -> Optional[str]:
    """Get current user ID from session"""
    return session.get('user_id')

def log_api_access(endpoint: str, user_id: str, request_data: Dict[str, Any] = None):
    """Log API access for audit purposes"""
    try:
        access_data = {
            'endpoint': endpoint,
            'user_id': user_id,
            'timestamp': datetime.now().isoformat(),
            'ip_address': request.remote_addr,
            'user_agent': request.headers.get('User-Agent'),
            'request_hash': hashlib.md5(json.dumps(request_data or {}, sort_keys=True).encode()).hexdigest()
        }
        logger.info(f"API Access: {json.dumps(access_data)}")
    except Exception as e:
        logger.error(f"Error logging API access: {e}")

# Authentication endpoints
@app.route('/api/auth/login', methods=['POST'])
def login():
    """Authenticate user (simplified for demo)"""
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        
        if not user_id:
            return jsonify({'error': 'user_id required'}), 400
        
        # In production, you'd validate credentials here
        session['user_id'] = user_id
        session['login_time'] = datetime.now().isoformat()
        
        logger.info(f"User {user_id} logged in")
        
        return jsonify({
            'message': 'Login successful',
            'user_id': user_id,
            'session_id': session.get('session_id', str(uuid.uuid4()))
        })
        
    except Exception as e:
        logger.error(f"Login error: {e}")
        return jsonify({'error': 'Login failed'}), 500

@app.route('/api/auth/logout', methods=['POST'])
@require_auth
def logout():
    """Logout user"""
    user_id = get_current_user()
    session.clear()
    logger.info(f"User {user_id} logged out")
    return jsonify({'message': 'Logout successful'})

# Consent and privacy endpoints
@app.route('/api/consent/flow', methods=['GET'])
@require_auth
def get_consent_flow():
    """Get consent flow for user"""
    try:
        user_id = get_current_user()
        log_api_access('consent_flow', user_id)
        
        flow = consent_manager.create_consent_flow(user_id)
        return jsonify(flow)
        
    except Exception as e:
        logger.error(f"Consent flow error: {e}")
        return jsonify({'error': 'Failed to create consent flow'}), 500

@app.route('/api/consent/submit', methods=['POST'])
@require_auth
def submit_consent():
    """Submit user consent responses"""
    try:
        user_id = get_current_user()
        data = request.get_json()
        log_api_access('consent_submit', user_id, data)
        
        consents = data.get('consents', {})
        success = consent_manager.process_consent_response(user_id, consents)
        
        if success:
            return jsonify({'message': 'Consent processed successfully'})
        else:
            return jsonify({'error': 'Failed to process consent'}), 500
            
    except Exception as e:
        logger.error(f"Consent submission error: {e}")
        return jsonify({'error': 'Failed to submit consent'}), 500

@app.route('/api/privacy/settings', methods=['GET'])
@require_auth
def get_privacy_settings():
    """Get user's privacy settings"""
    try:
        user_id = get_current_user()
        log_api_access('privacy_settings_get', user_id)
        
        settings = privacy_manager.get_privacy_settings(user_id)
        return jsonify({
            'settings': {
                'data_retention_days': settings.data_retention_days,
                'allow_analytics': settings.allow_analytics,
                'allow_personalization': settings.allow_personalization,
                'require_explicit_consent': settings.require_explicit_consent,
                'anonymize_insights': settings.anonymize_insights,
                'audit_frequency': settings.audit_frequency
            }
        })
        
    except Exception as e:
        logger.error(f"Privacy settings error: {e}")
        return jsonify({'error': 'Failed to get privacy settings'}), 500

@app.route('/api/privacy/settings', methods=['PUT'])
@require_auth
def update_privacy_settings():
    """Update user's privacy settings"""
    try:
        user_id = get_current_user()
        data = request.get_json()
        log_api_access('privacy_settings_update', user_id, data)
        
        from privacy_manager import PrivacySettings
        settings = PrivacySettings(
            user_id=user_id,
            data_retention_days=data.get('data_retention_days', 365),
            allow_analytics=data.get('allow_analytics', True),
            allow_personalization=data.get('allow_personalization', True),
            require_explicit_consent=data.get('require_explicit_consent', True),
            anonymize_insights=data.get('anonymize_insights', False),
            audit_frequency=data.get('audit_frequency', 'monthly')
        )
        
        success = privacy_manager.update_privacy_settings(settings)
        
        if success:
            return jsonify({'message': 'Privacy settings updated successfully'})
        else:
            return jsonify({'error': 'Failed to update privacy settings'}), 500
            
    except Exception as e:
        logger.error(f"Privacy settings update error: {e}")
        return jsonify({'error': 'Failed to update privacy settings'}), 500

@app.route('/api/privacy/report', methods=['GET'])
@require_auth
def get_privacy_report():
    """Get privacy compliance report"""
    try:
        user_id = get_current_user()
        log_api_access('privacy_report', user_id)
        
        report = privacy_manager.generate_privacy_report(user_id)
        return jsonify(report)
        
    except Exception as e:
        logger.error(f"Privacy report error: {e}")
        return jsonify({'error': 'Failed to generate privacy report'}), 500

# Financial analysis endpoints
@app.route('/api/analysis/comprehensive', methods=['POST'])
@require_auth
def comprehensive_analysis():
    """Get comprehensive financial analysis"""
    try:
        user_id = get_current_user()
        data = request.get_json()
        log_api_access('comprehensive_analysis', user_id)
        
        # Validate financial data
        financial_data = data.get('financial_data')
        if not financial_data:
            return jsonify({'error': 'financial_data required'}), 400
        
        # Get user permissions
        permissions = privacy_manager.get_user_permissions(user_id)
        
        # Process goals if provided
        goals = None
        if 'goals' in data:
            goals = []
            for goal_data in data['goals']:
                goal = FinancialGoal(
                    name=goal_data['name'],
                    target_amount=goal_data['target_amount'],
                    current_amount=goal_data.get('current_amount', 0),
                    target_date=datetime.fromisoformat(goal_data['target_date']),
                    priority=goal_data.get('priority', 5),
                    category=goal_data.get('category', 'other')
                )
                goals.append(goal)
        
        # Generate comprehensive analysis
        analysis = insights_engine.generate_comprehensive_analysis(
            financial_data, permissions, goals
        )
        
        # Apply privacy filters
        filtered_analysis = privacy_manager.apply_privacy_filters(
            user_id, financial_data, analysis
        )
        
        # Log the access
        privacy_manager.log_access(
            user_id=user_id,
            accessed_categories=list(permissions.get_allowed_categories()),
            purpose="comprehensive_analysis",
            result_hash=hashlib.md5(json.dumps(filtered_analysis, sort_keys=True).encode()).hexdigest()
        )
        
        return jsonify({
            'analysis': filtered_analysis,
            'generated_at': datetime.now().isoformat(),
            'permissions_used': list(permissions.get_allowed_categories())
        })
        
    except Exception as e:
        logger.error(f"Comprehensive analysis error: {e}")
        return jsonify({'error': 'Analysis failed'}), 500

@app.route('/api/analysis/health-score', methods=['POST'])
@require_auth
def get_health_score():
    """Get financial health score"""
    try:
        user_id = get_current_user()
        data = request.get_json()
        log_api_access('health_score', user_id)
        
        financial_data = data.get('financial_data')
        if not financial_data:
            return jsonify({'error': 'financial_data required'}), 400
        
        permissions = privacy_manager.get_user_permissions(user_id)
        analysis = insights_engine.generate_comprehensive_analysis(
            financial_data, permissions
        )
        
        health_score = analysis['advanced_analysis']['financial_health_score']
        
        return jsonify({
            'health_score': health_score,
            'generated_at': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Health score error: {e}")
        return jsonify({'error': 'Health score calculation failed'}), 500

# Chat interface endpoints
@app.route('/api/chat/message', methods=['POST'])
@require_auth
def chat_message():
    """Process chat message"""
    try:
        user_id = get_current_user()
        data = request.get_json()
        log_api_access('chat_message', user_id, {'query_length': len(data.get('message', ''))})
        
        message = data.get('message')
        session_id = data.get('session_id')
        financial_data = data.get('financial_data')  # Optional
        
        if not message:
            return jsonify({'error': 'message required'}), 400
        
        # Process the message
        response = nlp_processor.process_query(
            user_id=user_id,
            query=message,
            session_id=session_id,
            financial_data=financial_data
        )
        
        return jsonify(response)
        
    except Exception as e:
        logger.error(f"Chat message error: {e}")
        return jsonify({'error': 'Failed to process message'}), 500

@app.route('/api/chat/history/<session_id>', methods=['GET'])
@require_auth
def get_chat_history(session_id):
    """Get chat history for session"""
    try:
        user_id = get_current_user()
        log_api_access('chat_history', user_id)
        
        limit = request.args.get('limit', 50, type=int)
        history = nlp_processor.get_conversation_history(session_id, limit)
        
        return jsonify({
            'session_id': session_id,
            'history': history
        })
        
    except Exception as e:
        logger.error(f"Chat history error: {e}")
        return jsonify({'error': 'Failed to get chat history'}), 500

# Data management endpoints
@app.route('/api/data/validate', methods=['POST'])
@require_auth
def validate_data():
    """Validate financial data structure"""
    try:
        user_id = get_current_user()
        data = request.get_json()
        log_api_access('data_validate', user_id)
        
        financial_data = data.get('financial_data')
        if not financial_data:
            return jsonify({'error': 'financial_data required'}), 400
        
        is_valid, errors = data_preprocessor.validate_financial_data(financial_data)
        
        return jsonify({
            'valid': is_valid,
            'errors': errors
        })
        
    except Exception as e:
        logger.error(f"Data validation error: {e}")
        return jsonify({'error': 'Validation failed'}), 500

@app.route('/api/data/export', methods=['GET'])
@require_auth
def export_user_data():
    """Export all user data (GDPR compliance)"""
    try:
        user_id = get_current_user()
        log_api_access('data_export', user_id)
        
        exported_data = privacy_manager.export_user_data(user_id)
        
        return jsonify({
            'export_data': exported_data,
            'export_format': 'json',
            'exported_at': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Data export error: {e}")
        return jsonify({'error': 'Export failed'}), 500

@app.route('/api/data/delete', methods=['DELETE'])
@require_auth
def delete_user_data():
    """Delete all user data (GDPR right to be forgotten)"""
    try:
        user_id = get_current_user()
        data = request.get_json()
        
        # Require explicit confirmation
        confirmation = data.get('confirmation')
        if confirmation != 'DELETE_ALL_MY_DATA':
            return jsonify({'error': 'Explicit confirmation required'}), 400
        
        log_api_access('data_delete', user_id)
        
        success = privacy_manager.delete_user_data(user_id, verify=True)
        
        if success:
            session.clear()  # Log out user
            return jsonify({'message': 'All user data deleted successfully'})
        else:
            return jsonify({'error': 'Failed to delete user data'}), 500
            
    except Exception as e:
        logger.error(f"Data deletion error: {e}")
        return jsonify({'error': 'Deletion failed'}), 500

# Goal management endpoints
@app.route('/api/goals', methods=['GET'])
@require_auth
def get_user_goals():
    """Get user's financial goals"""
    try:
        user_id = get_current_user()
        log_api_access('goals_get', user_id)
        
        # In a real implementation, you'd store goals in a database
        # For now, return empty list
        return jsonify({'goals': []})
        
    except Exception as e:
        logger.error(f"Get goals error: {e}")
        return jsonify({'error': 'Failed to get goals'}), 500

@app.route('/api/goals', methods=['POST'])
@require_auth
def create_goal():
    """Create a new financial goal"""
    try:
        user_id = get_current_user()
        data = request.get_json()
        log_api_access('goals_create', user_id, data)
        
        # Validate goal data
        required_fields = ['name', 'target_amount', 'target_date']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'{field} is required'}), 400
        
        goal = {
            'id': str(uuid.uuid4()),
            'user_id': user_id,
            'name': data['name'],
            'target_amount': data['target_amount'],
            'current_amount': data.get('current_amount', 0),
            'target_date': data['target_date'],
            'priority': data.get('priority', 5),
            'category': data.get('category', 'other'),
            'created_at': datetime.now().isoformat()
        }
        
        # In a real implementation, save to database
        return jsonify({
            'message': 'Goal created successfully',
            'goal': goal
        })
        
    except Exception as e:
        logger.error(f"Create goal error: {e}")
        return jsonify({'error': 'Failed to create goal'}), 500

# System health and monitoring
@app.route('/api/health', methods=['GET'])
def health_check():
    """System health check"""
    try:
        # Check database connections
        with sqlite3.connect(privacy_manager.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT 1')
        
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'version': '1.0.0',
            'components': {
                'database': 'healthy',
                'insights_engine': 'healthy',
                'nlp_processor': 'healthy',
                'privacy_manager': 'healthy'
            }
        })
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return jsonify({
            'status': 'unhealthy',
            'error': str(e)
        }), 503

# Legacy compatibility endpoint
@app.route('/predict', methods=['POST'])
def predict():
    """Legacy prediction endpoint for backwards compatibility"""
    try:
        data = request.json
        
        # Use the enhanced insights engine
        permissions = UserPermissions()  # Full permissions for legacy endpoint
        analysis = insights_engine.generate_comprehensive_analysis(data, permissions)
        
        # Extract key insights for legacy format
        health_score = analysis['advanced_analysis']['financial_health_score']
        cash_flow = analysis['advanced_analysis']['cash_flow_analysis']
        recommendations = analysis.get('personalized_recommendations', [])
        
        # Legacy response format
        response = {
            "predicted_savings": cash_flow['net_cash_flow'],
            "unusual_spending": [],
            "recommendations": [rec.get('action', str(rec)) for rec in recommendations[:3]],
            "financial_health_score": health_score['total_score'],
            "savings_rate": cash_flow['savings_rate'] * 100
        }
        
        return jsonify(response)
        
    except Exception as e:
        logger.error(f"Legacy prediction error: {e}")
        return jsonify({"error": str(e)}), 400

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    logger.error(f"Internal server error: {error}")
    return jsonify({'error': 'Internal server error'}), 500

@app.errorhandler(403)
def forbidden(error):
    return jsonify({'error': 'Access forbidden'}), 403

# API documentation endpoint
@app.route('/api/docs', methods=['GET'])
def api_documentation():
    """API documentation"""
    docs = {
        'title': 'Financial AI Assistant API',
        'version': '1.0.0',
        'description': 'Comprehensive API for AI-powered financial analysis and advice\n\n**LLM Integration**: This API can be configured to use advanced LLMs via OpenRouter for more sophisticated natural language understanding. Set the `USE_LLM_NLP=true` environment variable and provide an `OPENROUTER_API_KEY` to enable this feature.',
        'endpoints': {
            'Authentication': {
                'POST /api/auth/login': 'Authenticate user',
                'POST /api/auth/logout': 'Logout user'
            },
            'Privacy & Consent': {
                'GET /api/consent/flow': 'Get consent flow',
                'POST /api/consent/submit': 'Submit consent responses',
                'GET /api/privacy/settings': 'Get privacy settings',
                'PUT /api/privacy/settings': 'Update privacy settings',
                'GET /api/privacy/report': 'Get privacy compliance report'
            },
            'Financial Analysis': {
                'POST /api/analysis/comprehensive': 'Get comprehensive financial analysis',
                'POST /api/analysis/health-score': 'Get financial health score'
            },
            'Chat Interface': {
                'POST /api/chat/message': 'Send chat message',
                'GET /api/chat/history/<session_id>': 'Get chat history'
            },
            'Data Management': {
                'POST /api/data/validate': 'Validate financial data',
                'GET /api/data/export': 'Export user data (GDPR)',
                'DELETE /api/data/delete': 'Delete user data (GDPR)'
            },
            'Goals': {
                'GET /api/goals': 'Get user goals',
                'POST /api/goals': 'Create new goal'
            },
            'System': {
                'GET /api/health': 'System health check',
                'GET /api/docs': 'API documentation'
            },
            'Legacy': {
                'POST /predict': 'Legacy prediction endpoint'
            }
        }
    }
    
    return jsonify(docs)

if __name__ == '__main__':
    # Load environment variables
    host = os.environ.get('HOST', '127.0.0.1')
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('DEBUG', 'True').lower() == 'true'
    
    logger.info(f"Starting Financial AI API Server on {host}:{port}")
    app.run(host=host, port=port, debug=debug)