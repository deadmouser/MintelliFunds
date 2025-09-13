"""
Natural Language Processing Interface for Financial AI

This module provides:
- Natural language query understanding
- Conversational context management
- Intent recognition for financial queries
- Response generation
- Multi-turn conversation support
"""

import re
import json
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any, Set
from dataclasses import dataclass, asdict
from enum import Enum
from loguru import logger
import sqlite3
from insights_engine import AdvancedInsightsEngine, FinancialGoal
from privacy_manager import PrivacyManager, DataCategory
from data_preprocessing import UserPermissions

class Intent(Enum):
    """Financial query intents"""
    SAVINGS_INQUIRY = "savings_inquiry"
    SPENDING_ANALYSIS = "spending_analysis"
    BUDGET_HELP = "budget_help"
    INVESTMENT_ADVICE = "investment_advice"
    DEBT_MANAGEMENT = "debt_management"
    GOAL_SETTING = "goal_setting"
    FINANCIAL_HEALTH = "financial_health"
    CREDIT_INQUIRY = "credit_inquiry"
    EMERGENCY_FUND = "emergency_fund"
    RETIREMENT_PLANNING = "retirement_planning"
    TAX_OPTIMIZATION = "tax_optimization"
    GENERAL_HELP = "general_help"
    GREETING = "greeting"
    GOODBYE = "goodbye"
    PRIVACY_INQUIRY = "privacy_inquiry"

class EntityType(Enum):
    """Entity types in financial queries"""
    AMOUNT = "amount"
    DATE = "date"
    DURATION = "duration"
    CATEGORY = "category"
    GOAL_TYPE = "goal_type"
    INVESTMENT_TYPE = "investment_type"
    ACCOUNT_TYPE = "account_type"

@dataclass
class Entity:
    """Extracted entity from user query"""
    type: EntityType
    value: Any
    raw_text: str
    confidence: float = 1.0

@dataclass
class ConversationTurn:
    """Single turn in conversation"""
    turn_id: str
    user_query: str
    intent: Intent
    entities: List[Entity]
    response: str
    timestamp: datetime
    context_used: Dict[str, Any] = None

@dataclass
class ConversationContext:
    """Context maintained across conversation"""
    user_id: str
    session_id: str
    current_topic: Optional[str] = None
    mentioned_amounts: List[float] = None
    mentioned_goals: List[str] = None
    mentioned_timeframes: List[str] = None
    last_analysis_type: Optional[str] = None
    user_preferences: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.mentioned_amounts is None:
            self.mentioned_amounts = []
        if self.mentioned_goals is None:
            self.mentioned_goals = []
        if self.mentioned_timeframes is None:
            self.mentioned_timeframes = []
        if self.user_preferences is None:
            self.user_preferences = {}

class FinancialNLPProcessor:
    """Natural language processor for financial queries"""
    
    def __init__(self, insights_engine: AdvancedInsightsEngine, privacy_manager: PrivacyManager):
        self.insights_engine = insights_engine
        self.privacy_manager = privacy_manager
        self.db_path = "conversations.db"
        self._init_database()
        self._init_patterns()
        
        logger.info("Financial NLP processor initialized")
    
    def _init_database(self):
        """Initialize conversation database"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Conversations table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS conversations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT NOT NULL,
                    user_id TEXT NOT NULL,
                    turn_id TEXT UNIQUE NOT NULL,
                    user_query TEXT NOT NULL,
                    intent TEXT NOT NULL,
                    entities TEXT,
                    response TEXT NOT NULL,
                    timestamp TIMESTAMP NOT NULL,
                    context_data TEXT
                )
            ''')
            
            # Context table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS conversation_context (
                    session_id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    current_topic TEXT,
                    mentioned_amounts TEXT,
                    mentioned_goals TEXT,
                    mentioned_timeframes TEXT,
                    last_analysis_type TEXT,
                    user_preferences TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            conn.commit()
        
        logger.info("Conversation database initialized")
    
    def _init_patterns(self):
        """Initialize NLP patterns and keywords"""
        
        # Intent patterns
        self.intent_patterns = {
            Intent.SAVINGS_INQUIRY: [
                r'\b(save|saving|savings)\b',
                r'\bhow much.*save\b',
                r'\bsavings rate\b',
                r'\bemergency fund\b'
            ],
            Intent.SPENDING_ANALYSIS: [
                r'\b(spend|spending|expenses?)\b',
                r'\bwhere.*money.*go\b',
                r'\banalyze.*spending\b',
                r'\bexpenses? breakdown\b'
            ],
            Intent.BUDGET_HELP: [
                r'\bbudget\b',
                r'\bbudgeting\b',
                r'\bhow.*allocate\b',
                r'\b50/30/20\b'
            ],
            Intent.INVESTMENT_ADVICE: [
                r'\binvest\b',
                r'\binvestment\b',
                r'\bportfolio\b',
                r'\bstocks?\b',
                r'\bbonds?\b',
                r'\bmutual funds?\b'
            ],
            Intent.DEBT_MANAGEMENT: [
                r'\bdebt\b',
                r'\bloan\b',
                r'\bcredit card\b',
                r'\bpay off\b',
                r'\bowe\b'
            ],
            Intent.GOAL_SETTING: [
                r'\bgoal\b',
                r'\btarget\b',
                r'\bplan for\b',
                r'\bsave for\b'
            ],
            Intent.FINANCIAL_HEALTH: [
                r'\bfinancial health\b',
                r'\bhow.*doing\b',
                r'\bscore\b',
                r'\boverall.*financial\b'
            ],
            Intent.CREDIT_INQUIRY: [
                r'\bcredit score\b',
                r'\bcredit rating\b',
                r'\bcreditworthiness\b'
            ],
            Intent.RETIREMENT_PLANNING: [
                r'\bretirement\b',
                r'\bretire\b',
                r'\bepf\b',
                r'\bpension\b'
            ],
            Intent.GREETING: [
                r'\b(hi|hello|hey|good morning|good afternoon)\b',
                r'\bstart\b',
                r'\bhelp me\b'
            ],
            Intent.GOODBYE: [
                r'\b(bye|goodbye|thanks|thank you)\b',
                r'\bthat\'s all\b',
                r'\bend\b'
            ],
            Intent.PRIVACY_INQUIRY: [
                r'\bprivacy\b',
                r'\bdata\b',
                r'\bpermissions?\b',
                r'\bwhat.*data\b'
            ]
        }
        
        # Entity patterns
        self.entity_patterns = {
            EntityType.AMOUNT: [
                r'\$?(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)',
                r'\b(\d+(?:\.\d+)?)\s*(?:dollars?|ringgit|rm)\b',
                r'\b([\d,]+)\b'
            ],
            EntityType.DATE: [
                r'\b(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})\b',
                r'\b(january|february|march|april|may|june|july|august|september|october|november|december)\b',
                r'\b(next|last)\s+(month|year|week)\b',
                r'\b(this|coming)\s+(month|year|week)\b'
            ],
            EntityType.DURATION: [
                r'\b(\d+)\s*(months?|years?|weeks?|days?)\b',
                r'\bin\s+(\d+)\s*(months?|years?)\b'
            ],
            EntityType.GOAL_TYPE: [
                r'\b(house|home|car|vehicle|vacation|emergency|retirement|education)\b'
            ],
            EntityType.INVESTMENT_TYPE: [
                r'\b(stocks?|bonds?|mutual funds?|etf|index funds?|real estate|crypto|gold)\b'
            ]
        }
        
        # Common financial terms
        self.financial_terms = {
            'emergency_fund': ['emergency fund', 'emergency savings', 'rainy day fund'],
            'debt_payoff': ['pay off debt', 'debt payoff', 'eliminate debt'],
            'retirement': ['retirement', 'retire', 'epf', 'pension'],
            'investment': ['invest', 'investment', 'portfolio', 'stocks', 'bonds'],
            'budget': ['budget', 'budgeting', 'spending plan'],
            'savings': ['save', 'savings', 'saving money']
        }
    
    def process_query(self, 
                     user_id: str, 
                     query: str, 
                     session_id: Optional[str] = None,
                     financial_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Process a natural language query"""
        
        if not session_id:
            session_id = str(uuid.uuid4())
        
        # Load or create conversation context
        context = self._get_or_create_context(user_id, session_id)
        
        # Process the query
        intent = self._classify_intent(query)
        entities = self._extract_entities(query)
        
        # Generate response
        response_data = self._generate_response(
            user_id, query, intent, entities, context, financial_data
        )
        
        # Update context
        context = self._update_context(context, intent, entities, query)
        
        # Save conversation turn
        turn = ConversationTurn(
            turn_id=str(uuid.uuid4()),
            user_query=query,
            intent=intent,
            entities=entities,
            response=response_data['response'],
            timestamp=datetime.now(),
            context_used=asdict(context)
        )
        
        self._save_conversation_turn(session_id, user_id, turn)
        
        return {
            'session_id': session_id,
            'response': response_data['response'],
            'intent': intent.value,
            'entities': [asdict(e) for e in entities],
            'context': asdict(context),
            'suggestions': response_data.get('suggestions', []),
            'data_needed': response_data.get('data_needed', []),
            'analysis_results': response_data.get('analysis_results')
        }
    
    def _classify_intent(self, query: str) -> Intent:
        """Classify the intent of a user query"""
        
        query_lower = query.lower()
        intent_scores = {}
        
        for intent, patterns in self.intent_patterns.items():
            score = 0
            for pattern in patterns:
                matches = re.findall(pattern, query_lower)
                score += len(matches)
            
            if score > 0:
                intent_scores[intent] = score
        
        if intent_scores:
            return max(intent_scores, key=intent_scores.get)
        else:
            return Intent.GENERAL_HELP
    
    def _extract_entities(self, query: str) -> List[Entity]:
        """Extract entities from user query"""
        
        entities = []
        query_lower = query.lower()
        
        for entity_type, patterns in self.entity_patterns.items():
            for pattern in patterns:
                matches = re.finditer(pattern, query_lower)
                for match in matches:
                    value = match.group(1) if match.groups() else match.group(0)
                    
                    # Process entity value based on type
                    processed_value = self._process_entity_value(entity_type, value)
                    
                    entity = Entity(
                        type=entity_type,
                        value=processed_value,
                        raw_text=match.group(0),
                        confidence=0.8  # Simple confidence score
                    )
                    entities.append(entity)
        
        return entities
    
    def _process_entity_value(self, entity_type: EntityType, raw_value: str) -> Any:
        """Process raw entity value based on type"""
        
        if entity_type == EntityType.AMOUNT:
            # Clean up amount and convert to float
            cleaned = re.sub(r'[,$]', '', raw_value)
            try:
                return float(cleaned)
            except ValueError:
                return raw_value
        
        elif entity_type == EntityType.DURATION:
            # Extract number from duration
            match = re.search(r'(\d+)', raw_value)
            if match:
                return int(match.group(1))
            return raw_value
        
        else:
            return raw_value
    
    def _generate_response(self, 
                          user_id: str, 
                          query: str, 
                          intent: Intent, 
                          entities: List[Entity],
                          context: ConversationContext,
                          financial_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Generate response based on intent and context"""
        
        response_data = {
            'response': '',
            'suggestions': [],
            'data_needed': []
        }
        
        # Check if we need financial data for this intent
        needs_data_intents = {
            Intent.SAVINGS_INQUIRY, Intent.SPENDING_ANALYSIS, Intent.BUDGET_HELP,
            Intent.INVESTMENT_ADVICE, Intent.DEBT_MANAGEMENT, Intent.FINANCIAL_HEALTH,
            Intent.CREDIT_INQUIRY, Intent.RETIREMENT_PLANNING
        }
        
        if intent in needs_data_intents and not financial_data:
            response_data['response'] = self._get_data_request_message(intent)
            response_data['data_needed'] = self._get_required_data_categories(intent)
            return response_data
        
        # Generate intent-specific responses
        if intent == Intent.GREETING:
            response_data['response'] = self._handle_greeting(context)
            response_data['suggestions'] = [
                "What's my financial health score?",
                "How much should I save each month?",
                "Analyze my spending patterns",
                "Help me create a budget"
            ]
        
        elif intent == Intent.FINANCIAL_HEALTH and financial_data:
            response_data = self._handle_financial_health_query(financial_data, user_id)
        
        elif intent == Intent.SAVINGS_INQUIRY and financial_data:
            response_data = self._handle_savings_query(financial_data, entities, user_id)
        
        elif intent == Intent.SPENDING_ANALYSIS and financial_data:
            response_data = self._handle_spending_query(financial_data, entities, user_id)
        
        elif intent == Intent.BUDGET_HELP and financial_data:
            response_data = self._handle_budget_query(financial_data, entities, user_id)
        
        elif intent == Intent.INVESTMENT_ADVICE and financial_data:
            response_data = self._handle_investment_query(financial_data, entities, user_id)
        
        elif intent == Intent.DEBT_MANAGEMENT and financial_data:
            response_data = self._handle_debt_query(financial_data, entities, user_id)
        
        elif intent == Intent.GOAL_SETTING:
            response_data = self._handle_goal_setting(entities, context)
        
        elif intent == Intent.PRIVACY_INQUIRY:
            response_data = self._handle_privacy_query(user_id)
        
        elif intent == Intent.GOODBYE:
            response_data['response'] = self._handle_goodbye()
        
        else:
            response_data['response'] = self._handle_general_help()
            response_data['suggestions'] = [
                "Check my financial health",
                "Analyze my spending",
                "Investment advice",
                "Budget recommendations"
            ]
        
        return response_data
    
    def _handle_greeting(self, context: ConversationContext) -> str:
        """Handle greeting messages"""
        greetings = [
            f"Hello! I'm your AI financial advisor. How can I help you today?",
            f"Hi there! Ready to take control of your finances?",
            f"Welcome! I'm here to help you with your financial questions."
        ]
        
        import random
        return random.choice(greetings)
    
    def _handle_financial_health_query(self, financial_data: Dict[str, Any], user_id: str) -> Dict[str, Any]:
        """Handle financial health queries"""
        
        permissions = self.privacy_manager.get_user_permissions(user_id)
        analysis = self.insights_engine.generate_comprehensive_analysis(
            financial_data, permissions
        )
        
        health_score = analysis['advanced_analysis']['financial_health_score']
        score = health_score['total_score']
        level = health_score['health_level']
        
        response = f"Your financial health score is {score:.1f}/100, which is {level}.\n\n"
        
        # Add component breakdown
        components = health_score['components']
        response += "Here's how you're doing in each area:\n"
        for component, value in components.items():
            component_name = component.replace('_', ' ').title()
            response += f"• {component_name}: {value:.1f}/25\n"
        
        # Add recommendations
        recommendations = analysis.get('personalized_recommendations', [])
        if recommendations:
            response += "\n🎯 Key Recommendations:\n"
            for i, rec in enumerate(recommendations[:3], 1):
                response += f"{i}. {rec['action']}\n"
        
        suggestions = [
            "What can I do to improve my score?",
            "Show me my spending breakdown",
            "Help me create a budget",
            "Investment recommendations"
        ]
        
        return {
            'response': response,
            'suggestions': suggestions,
            'analysis_results': analysis
        }
    
    def _handle_savings_query(self, financial_data: Dict[str, Any], entities: List[Entity], user_id: str) -> Dict[str, Any]:
        """Handle savings-related queries"""
        
        permissions = self.privacy_manager.get_user_permissions(user_id)
        analysis = self.insights_engine.generate_comprehensive_analysis(
            financial_data, permissions
        )
        
        savings_analysis = analysis['advanced_analysis']['cash_flow_analysis']
        current_savings = savings_analysis['net_cash_flow']
        savings_rate = savings_analysis['savings_rate'] * 100
        
        response = f"💰 Your Current Savings:\n"
        response += f"• Monthly savings: RM {current_savings:,.2f}\n"
        response += f"• Savings rate: {savings_rate:.1f}% of income\n"
        response += f"• Status: {savings_analysis['cash_flow_health']}\n\n"
        
        # Add recommendations based on savings rate
        if savings_rate < 10:
            response += "💡 Your savings rate is below the recommended 10-15%. "
            response += "Consider reducing expenses or finding ways to increase income."
        elif savings_rate < 20:
            response += "👍 Good job! You're saving, but aim for 20% for optimal financial health."
        else:
            response += "🌟 Excellent savings rate! You're on track for financial success."
        
        # Add timeline for goals if any amounts mentioned
        amount_entities = [e for e in entities if e.type == EntityType.AMOUNT]
        if amount_entities and current_savings > 0:
            target_amount = amount_entities[0].value
            months_needed = target_amount / current_savings if current_savings > 0 else float('inf')
            response += f"\n\n📅 At your current savings rate, you'll reach RM {target_amount:,.0f} in about {months_needed:.0f} months."
        
        suggestions = [
            "How can I increase my savings rate?",
            "Show me my spending breakdown",
            "Help me set a savings goal",
            "Emergency fund recommendations"
        ]
        
        return {
            'response': response,
            'suggestions': suggestions,
            'analysis_results': analysis
        }
    
    def _handle_spending_query(self, financial_data: Dict[str, Any], entities: List[Entity], user_id: str) -> Dict[str, Any]:
        """Handle spending analysis queries"""
        
        permissions = self.privacy_manager.get_user_permissions(user_id)
        analysis = self.insights_engine.generate_comprehensive_analysis(
            financial_data, permissions
        )
        
        spending_analysis = analysis['advanced_analysis']['cash_flow_analysis']
        spending_patterns = analysis.get('spending_patterns', [])
        
        response = f"💳 Your Spending Analysis:\n"
        response += f"• Monthly expenses: RM {spending_analysis['monthly_expenses']:,.2f}\n"
        response += f"• Expense ratio: {spending_analysis['expense_ratio']*100:.1f}% of income\n\n"
        
        # Add spending breakdown
        response += "📊 Estimated spending by category:\n"
        for pattern in spending_patterns[:5]:  # Top 5 categories
            percentage = (pattern.average_monthly / spending_analysis['monthly_expenses']) * 100
            response += f"• {pattern.category}: RM {pattern.average_monthly:,.0f} ({percentage:.0f}%)\n"
        
        # Check for unusual spending
        unusual_spending = analysis['spending_analysis'].get('anomaly_details', [])
        if unusual_spending:
            response += f"\n⚠️ Unusual spending detected:\n"
            for anomaly in unusual_spending[:3]:
                response += f"• {anomaly}\n"
        
        suggestions = [
            "How can I reduce my expenses?",
            "Show me budget recommendations",
            "Which categories should I focus on?",
            "Help me create a spending plan"
        ]
        
        return {
            'response': response,
            'suggestions': suggestions,
            'analysis_results': analysis
        }
    
    def _handle_budget_query(self, financial_data: Dict[str, Any], entities: List[Entity], user_id: str) -> Dict[str, Any]:
        """Handle budget-related queries"""
        
        permissions = self.privacy_manager.get_user_permissions(user_id)
        analysis = self.insights_engine.generate_comprehensive_analysis(
            financial_data, permissions
        )
        
        budget_analysis = analysis['advanced_analysis']['budget_recommendations']
        
        response = "📋 Budget Recommendations (50/30/20 Rule):\n\n"
        
        allocation = budget_analysis['recommended_allocation']
        response += f"💰 Recommended monthly allocation:\n"
        response += f"• Needs (50%): RM {allocation['needs']:,.2f}\n"
        response += f"• Wants (30%): RM {allocation['wants']:,.2f}\n"
        response += f"• Savings (20%): RM {allocation['savings']:,.2f}\n\n"
        
        # Current vs recommended
        current_spending = budget_analysis['current_spending']
        current_savings = budget_analysis['current_savings']
        
        response += f"📊 Your current situation:\n"
        response += f"• Current spending: RM {current_spending:,.2f}\n"
        response += f"• Current savings: RM {current_savings:,.2f}\n"
        
        # Recommendations
        recommendations = budget_analysis.get('recommendations', [])
        if recommendations:
            response += f"\n💡 Recommendations:\n"
            for i, rec in enumerate(recommendations, 1):
                response += f"{i}. {rec}\n"
        
        suggestions = [
            "How can I stick to this budget?",
            "Show me my biggest expenses",
            "Help me reduce spending",
            "Track my progress"
        ]
        
        return {
            'response': response,
            'suggestions': suggestions,
            'analysis_results': analysis
        }
    
    def _handle_investment_query(self, financial_data: Dict[str, Any], entities: List[Entity], user_id: str) -> Dict[str, Any]:
        """Handle investment advice queries"""
        
        permissions = self.privacy_manager.get_user_permissions(user_id)
        analysis = self.insights_engine.generate_comprehensive_analysis(
            financial_data, permissions
        )
        
        investment_analysis = analysis['investment_advice']
        opportunities = analysis.get('investment_opportunities', [])
        
        response = "📈 Investment Recommendations:\n\n"
        
        # Current portfolio
        portfolio_value = investment_analysis['current_portfolio_value']
        diversification = investment_analysis['diversification_score']
        
        response += f"💼 Current Portfolio:\n"
        response += f"• Total value: RM {portfolio_value:,.2f}\n"
        response += f"• Diversification score: {diversification:.1f}/100\n\n"
        
        # Top recommendations
        top_recs = investment_analysis['top_recommendations']
        response += f"🎯 Top Investment Recommendations:\n"
        for i, (investment_type, allocation) in enumerate(top_recs[:3], 1):
            response += f"{i}. {investment_type}: {allocation:.1%} allocation\n"
        
        # Investment opportunities
        if opportunities:
            response += f"\n💡 Specific Opportunities:\n"
            for opp in opportunities[:3]:
                response += f"• {opp.type}: {opp.expected_return:.1%} expected return (Risk: {opp.risk_level})\n"
                response += f"  {opp.description}\n"
        
        suggestions = [
            "How much should I invest monthly?",
            "What's my risk tolerance?",
            "Explain index funds",
            "Retirement investment strategy"
        ]
        
        return {
            'response': response,
            'suggestions': suggestions,
            'analysis_results': analysis
        }
    
    def _handle_debt_query(self, financial_data: Dict[str, Any], entities: List[Entity], user_id: str) -> Dict[str, Any]:
        """Handle debt management queries"""
        
        permissions = self.privacy_manager.get_user_permissions(user_id)
        analysis = self.insights_engine.generate_comprehensive_analysis(
            financial_data, permissions
        )
        
        debt_analysis = analysis['debt_management']
        optimization = analysis.get('debt_optimization', {})
        
        total_debt = debt_analysis['total_debt']
        
        if total_debt == 0:
            response = "🎉 Great news! You currently have no debt. "
            response += "Focus on building your emergency fund and investing for the future."
        else:
            response = f"💳 Debt Analysis:\n\n"
            response += f"• Total debt: RM {total_debt:,.2f}\n"
            response += f"• Debt-to-income ratio: {debt_analysis['debt_to_income_ratio']:.1f}%\n"
            response += f"• Status: {debt_analysis['debt_health']}\n\n"
            
            # Recommended strategy
            strategy = debt_analysis['recommended_strategy']
            response += f"🎯 Recommended Strategy: {strategy[0]}\n"
            response += f"Confidence: {strategy[1]:.1%}\n\n"
            
            # Payoff scenarios
            if 'scenarios' in optimization:
                scenarios = optimization['scenarios']
                response += "📊 Payoff Scenarios:\n"
                for scenario_name, details in scenarios.items():
                    response += f"• {details['strategy']}: {details['payoff_time_months']:.0f} months\n"
        
        suggestions = [
            "How can I pay off debt faster?",
            "Debt avalanche vs snowball?",
            "Should I consolidate my debt?",
            "Emergency fund or debt payoff first?"
        ]
        
        return {
            'response': response,
            'suggestions': suggestions,
            'analysis_results': analysis
        }
    
    def _handle_goal_setting(self, entities: List[Entity], context: ConversationContext) -> Dict[str, Any]:
        """Handle goal setting queries"""
        
        # Extract goal information from entities
        goal_amounts = [e.value for e in entities if e.type == EntityType.AMOUNT]
        goal_types = [e.value for e in entities if e.type == EntityType.GOAL_TYPE]
        durations = [e.value for e in entities if e.type == EntityType.DURATION]
        
        response = "🎯 Let's set up your financial goal!\n\n"
        
        if goal_types:
            goal_type = goal_types[0]
            response += f"Goal type: {goal_type.title()}\n"
        
        if goal_amounts:
            amount = goal_amounts[0]
            response += f"Target amount: RM {amount:,.2f}\n"
        
        if durations:
            duration = durations[0]
            response += f"Time frame: {duration} months\n"
        
        if goal_amounts and durations:
            monthly_savings_needed = goal_amounts[0] / durations[0]
            response += f"\n💰 You'll need to save RM {monthly_savings_needed:,.2f} per month to reach this goal.\n"
        
        if not goal_types or not goal_amounts:
            response += "To help you better, please tell me:\n"
            if not goal_types:
                response += "• What type of goal? (house, car, vacation, etc.)\n"
            if not goal_amounts:
                response += "• How much do you need?\n"
            if not durations:
                response += "• When do you want to achieve this?\n"
        
        suggestions = [
            "I want to save for a house",
            "Help me plan for retirement",
            "Emergency fund goal",
            "Vacation savings plan"
        ]
        
        return {
            'response': response,
            'suggestions': suggestions
        }
    
    def _handle_privacy_query(self, user_id: str) -> Dict[str, Any]:
        """Handle privacy-related queries"""
        
        summary = self.privacy_manager.get_user_data_summary(user_id)
        settings = self.privacy_manager.get_privacy_settings(user_id)
        
        response = "🔒 Your Privacy & Data Settings:\n\n"
        
        # Show current permissions
        response += "📋 Current data permissions:\n"
        for record in summary['consent_records'][:5]:  # Show recent consents
            status = "Revoked" if record['revoked'] else "Active"
            response += f"• {record['category'].replace('_', ' ').title()}: {status}\n"
        
        response += f"\n📊 Privacy preferences:\n"
        response += f"• Data retention: {settings.data_retention_days} days\n"
        response += f"• Analytics allowed: {'Yes' if settings.allow_analytics else 'No'}\n"
        response += f"• Personalization: {'Yes' if settings.allow_personalization else 'No'}\n"
        response += f"• Anonymize insights: {'Yes' if settings.anonymize_insights else 'No'}\n"
        
        response += f"\n📈 Access summary:\n"
        response += f"• Total access events: {summary['total_access_events']}\n"
        if summary['latest_access']:
            response += f"• Last access: {summary['latest_access']}\n"
        
        suggestions = [
            "Update my privacy settings",
            "Revoke data permissions",
            "Export my data",
            "Delete my data"
        ]
        
        return {
            'response': response,
            'suggestions': suggestions
        }
    
    def _handle_goodbye(self) -> str:
        """Handle goodbye messages"""
        goodbyes = [
            "Thanks for using your AI financial advisor! Take care of your finances! 💰",
            "Goodbye! Remember, good financial habits build wealth over time. 📈",
            "See you later! Keep up the great work with your finances! 🌟"
        ]
        
        import random
        return random.choice(goodbyes)
    
    def _handle_general_help(self) -> str:
        """Handle general help requests"""
        return """I'm your AI financial advisor! Here's how I can help you:

💰 **Savings & Budget**
- Analyze your savings rate
- Create budget recommendations
- Emergency fund planning

📊 **Spending Analysis**
- Break down your expenses
- Identify unusual spending
- Find cost-cutting opportunities

📈 **Investment Advice**
- Portfolio recommendations
- Risk assessment
- Investment opportunities

💳 **Debt Management**
- Debt payoff strategies
- Consolidation advice
- Payment optimization

🎯 **Goal Setting**
- Financial goal planning
- Timeline calculations
- Progress tracking

🔒 **Privacy & Security**
- Manage data permissions
- Privacy settings
- Data export/deletion

Just ask me anything about your finances!"""
    
    def _get_data_request_message(self, intent: Intent) -> str:
        """Get message requesting financial data"""
        
        messages = {
            Intent.SAVINGS_INQUIRY: "To analyze your savings, I'll need access to your transaction data. Would you like to connect your financial accounts?",
            Intent.SPENDING_ANALYSIS: "To analyze your spending patterns, I need your transaction history. Please share your financial data.",
            Intent.BUDGET_HELP: "To create a personalized budget, I'll need your income and expense information.",
            Intent.INVESTMENT_ADVICE: "For investment recommendations, I need to see your current portfolio and financial situation.",
            Intent.DEBT_MANAGEMENT: "To help with debt management, I need information about your debts and income.",
            Intent.FINANCIAL_HEALTH: "To assess your financial health, I'll need access to your complete financial picture.",
            Intent.CREDIT_INQUIRY: "To discuss your credit, I need access to your credit score information.",
            Intent.RETIREMENT_PLANNING: "For retirement planning, I need your current savings and contribution data."
        }
        
        return messages.get(intent, "To provide personalized advice, I'll need access to your financial data.")
    
    def _get_required_data_categories(self, intent: Intent) -> List[str]:
        """Get required data categories for intent"""
        
        requirements = {
            Intent.SAVINGS_INQUIRY: ['transactions', 'assets'],
            Intent.SPENDING_ANALYSIS: ['transactions'],
            Intent.BUDGET_HELP: ['transactions'],
            Intent.INVESTMENT_ADVICE: ['investments', 'transactions', 'assets'],
            Intent.DEBT_MANAGEMENT: ['liabilities', 'transactions'],
            Intent.FINANCIAL_HEALTH: ['assets', 'liabilities', 'transactions', 'credit_score', 'investments'],
            Intent.CREDIT_INQUIRY: ['credit_score'],
            Intent.RETIREMENT_PLANNING: ['epf_retirement_balance', 'transactions']
        }
        
        return requirements.get(intent, ['transactions'])
    
    def _get_or_create_context(self, user_id: str, session_id: str) -> ConversationContext:
        """Get or create conversation context"""
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT * FROM conversation_context WHERE session_id = ?
                ''', (session_id,))
                
                result = cursor.fetchone()
                
                if result:
                    columns = [desc[0] for desc in cursor.description]
                    context_dict = dict(zip(columns, result))
                    
                    # Parse JSON fields
                    context_dict['mentioned_amounts'] = json.loads(context_dict['mentioned_amounts'] or '[]')
                    context_dict['mentioned_goals'] = json.loads(context_dict['mentioned_goals'] or '[]')
                    context_dict['mentioned_timeframes'] = json.loads(context_dict['mentioned_timeframes'] or '[]')
                    context_dict['user_preferences'] = json.loads(context_dict['user_preferences'] or '{}')
                    
                    # Remove database-specific fields
                    context_dict.pop('created_at', None)
                    context_dict.pop('updated_at', None)
                    
                    return ConversationContext(**context_dict)
        except Exception as e:
            logger.error(f"Error loading context: {e}")
        
        # Create new context
        return ConversationContext(user_id=user_id, session_id=session_id)
    
    def _update_context(self, 
                       context: ConversationContext, 
                       intent: Intent, 
                       entities: List[Entity],
                       query: str) -> ConversationContext:
        """Update conversation context"""
        
        # Update current topic
        topic_map = {
            Intent.SAVINGS_INQUIRY: 'savings',
            Intent.SPENDING_ANALYSIS: 'spending',
            Intent.BUDGET_HELP: 'budget',
            Intent.INVESTMENT_ADVICE: 'investment',
            Intent.DEBT_MANAGEMENT: 'debt',
            Intent.GOAL_SETTING: 'goals'
        }
        
        if intent in topic_map:
            context.current_topic = topic_map[intent]
        
        # Update mentioned entities
        for entity in entities:
            if entity.type == EntityType.AMOUNT:
                context.mentioned_amounts.append(entity.value)
            elif entity.type == EntityType.GOAL_TYPE:
                context.mentioned_goals.append(entity.value)
            elif entity.type == EntityType.DURATION:
                context.mentioned_timeframes.append(f"{entity.value} months")
        
        # Update last analysis type
        if intent in topic_map:
            context.last_analysis_type = topic_map[intent]
        
        # Save context to database
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT OR REPLACE INTO conversation_context
                    (session_id, user_id, current_topic, mentioned_amounts, 
                     mentioned_goals, mentioned_timeframes, last_analysis_type, 
                     user_preferences, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    context.session_id, context.user_id, context.current_topic,
                    json.dumps(context.mentioned_amounts[-10:]),  # Keep last 10
                    json.dumps(context.mentioned_goals[-10:]),
                    json.dumps(context.mentioned_timeframes[-10:]),
                    context.last_analysis_type,
                    json.dumps(context.user_preferences),
                    datetime.now()
                ))
                conn.commit()
        except Exception as e:
            logger.error(f"Error saving context: {e}")
        
        return context
    
    def _save_conversation_turn(self, session_id: str, user_id: str, turn: ConversationTurn):
        """Save conversation turn to database"""
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO conversations
                    (session_id, user_id, turn_id, user_query, intent, entities, 
                     response, timestamp, context_data)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    session_id, user_id, turn.turn_id, turn.user_query,
                    turn.intent.value, json.dumps([asdict(e) for e in turn.entities]),
                    turn.response, turn.timestamp, json.dumps(turn.context_used)
                ))
                conn.commit()
        except Exception as e:
            logger.error(f"Error saving conversation turn: {e}")
    
    def get_conversation_history(self, session_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Get conversation history for a session"""
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT user_query, response, intent, timestamp
                    FROM conversations 
                    WHERE session_id = ?
                    ORDER BY timestamp DESC
                    LIMIT ?
                ''', (session_id, limit))
                
                results = cursor.fetchall()
                
                history = []
                for row in results:
                    history.append({
                        'user_query': row[0],
                        'response': row[1],
                        'intent': row[2],
                        'timestamp': row[3]
                    })
                
                return list(reversed(history))  # Return chronological order
                
        except Exception as e:
            logger.error(f"Error getting conversation history: {e}")
            return []

# Example usage and testing
def example_usage():
    """Example usage of the NLP interface"""
    
    from insights_engine import AdvancedInsightsEngine
    from privacy_manager import PrivacyManager
    
    # Initialize components
    insights_engine = AdvancedInsightsEngine()
    privacy_manager = PrivacyManager("test_privacy.db")
    nlp_processor = FinancialNLPProcessor(insights_engine, privacy_manager)
    
    # Sample financial data
    financial_data = {
        "assets": {"cash": 32256, "bank_balances": 77090, "property": 0},
        "liabilities": {"loans": 0, "credit_card_debt": 0},
        "transactions": {"income": 89184, "expenses": 55829, "transfers": 2608},
        "epf_retirement_balance": {"contributions": 1800, "employer_match": 1800, "current_balance": 1692033},
        "credit_score": {"score": 632, "rating": "Average"},
        "investments": {"stocks": 156545, "mutual_funds": 179376, "bonds": 32856}
    }
    
    user_id = "test_user_123"
    
    # Test queries
    test_queries = [
        "Hi there!",
        "What's my financial health score?",
        "How much am I saving each month?",
        "Can I afford a $50000 car in 2 years?",
        "Help me create a budget",
        "What are my investment options?",
        "How can I pay off my debt faster?",
        "Thanks for your help!"
    ]
    
    print("=== Financial NLP Interface Demo ===\n")
    
    session_id = None
    for query in test_queries:
        print(f"User: {query}")
        
        result = nlp_processor.process_query(
            user_id=user_id,
            query=query,
            session_id=session_id,
            financial_data=financial_data
        )
        
        session_id = result['session_id']
        print(f"AI: {result['response']}")
        
        if result['suggestions']:
            print("Suggestions:")
            for suggestion in result['suggestions'][:3]:
                print(f"  • {suggestion}")
        
        print("-" * 50)

if __name__ == "__main__":
    example_usage()