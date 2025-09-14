"""
LLM-based Natural Language Processing Interface for Financial AI

This module provides:
- Integration with OpenRouter API for advanced NLP
- Natural language query understanding using LLMs
- Conversational context management
- Response generation with LLM assistance
"""

import os
import json
import uuid
import requests
from datetime import datetime
from typing import Dict, List, Optional, Any
from loguru import logger
from dataclasses import asdict

# Import required classes from the original NLP interface
from nlp_interface import ConversationContext, ConversationTurn, Intent

class LLMFinancialNLPProcessor:
    """LLM-based natural language processor for financial queries"""

    def __init__(self, insights_engine, privacy_manager):
        self.insights_engine = insights_engine
        self.privacy_manager = privacy_manager
        self.db_path = "conversations.db"

        # OpenRouter API configuration
        self.api_key = os.getenv("OPENROUTER_API_KEY", "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")
        self.api_base = "https://openrouter.ai/api/v1"
        self.default_model = os.getenv("OPENROUTER_MODEL", "meta-llama/llama-4-maverick:free")  # Default model

        # Initialize database (reuse existing methods from original NLP processor)
        self._init_database()

        logger.info("LLM Financial NLP processor initialized")

    def _init_database(self):
        """Initialize conversation database (reuse from original NLP processor)"""
        # We'll import the database initialization from the original NLP processor
        from nlp_interface import FinancialNLPProcessor
        original_nlp = FinancialNLPProcessor(self.insights_engine, self.privacy_manager)
        original_nlp._init_database()

    def process_query(self,
                     user_id: str,
                     query: str,
                     session_id: Optional[str] = None,
                     financial_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Process a natural language query using LLM"""

        if not session_id:
            session_id = str(uuid.uuid4())

        # Load or create conversation context
        context = self._get_or_create_context(user_id, session_id)

        # Generate response using LLM
        response_data = self._generate_llm_response(
            user_id, query, context, financial_data
        )

        # Update context
        context = self._update_context(context, query, response_data['response'])

        # Save conversation turn
        turn = ConversationTurn(
            turn_id=str(uuid.uuid4()),
            user_query=query,
            intent=Intent.GENERAL_HELP,  # LLM-generated intent
            entities=[],  # Entities extraction could be added later
            response=response_data['response'],
            timestamp=datetime.now(),
            context_used=asdict(context)
        )

        self._save_conversation_turn(session_id, user_id, turn)

        return {
            'session_id': session_id,
            'response': response_data['response'],
            'intent': Intent.GENERAL_HELP.value,  # Use enum value
            'entities': [],
            'context': asdict(context),
            'suggestions': response_data.get('suggestions', []),
            'data_needed': response_data.get('data_needed', []),
            'analysis_results': response_data.get('analysis_results')
        }

    def _get_or_create_context(self, user_id: str, session_id: str) -> ConversationContext:
        """Get or create conversation context (reuse from original NLP processor)"""
        try:
            from nlp_interface import FinancialNLPProcessor
            original_nlp = FinancialNLPProcessor(self.insights_engine, self.privacy_manager)
            return original_nlp._get_or_create_context(user_id, session_id)
        except Exception as e:
            logger.error(f"Error loading context: {e}")
            # Create new context
            return ConversationContext(user_id=user_id, session_id=session_id)

    def _update_context(self,
                       context: ConversationContext,
                       query: str,
                       response: str) -> ConversationContext:
        """Update conversation context"""
        # Update last interaction
        context.last_analysis_type = "llm_response"

        # Save context to database
        try:
            import sqlite3
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
                    json.dumps(getattr(context, 'mentioned_amounts', [])),
                    json.dumps(getattr(context, 'mentioned_goals', [])),
                    json.dumps(getattr(context, 'mentioned_timeframes', [])),
                    context.last_analysis_type,
                    json.dumps(getattr(context, 'user_preferences', {})),
                    datetime.now()
                ))
                conn.commit()
        except Exception as e:
            logger.error(f"Error saving context: {e}")

        return context

    def _save_conversation_turn(self, session_id: str, user_id: str, turn: ConversationTurn):
        """Save conversation turn to database (reuse from original NLP processor)"""
        try:
            from nlp_interface import FinancialNLPProcessor
            original_nlp = FinancialNLPProcessor(self.insights_engine, self.privacy_manager)
            original_nlp._save_conversation_turn(session_id, user_id, turn)
        except Exception as e:
            logger.error(f"Error saving conversation turn: {e}")

    def get_conversation_history(self, session_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Get conversation history for a session (reuse from original NLP processor)"""
        try:
            from nlp_interface import FinancialNLPProcessor
            original_nlp = FinancialNLPProcessor(self.insights_engine, self.privacy_manager)
            return original_nlp.get_conversation_history(session_id, limit)
        except Exception as e:
            logger.error(f"Error getting conversation history: {e}")
            return []

    def _generate_llm_response(self,
                              user_id: str,
                              query: str,
                              context: ConversationContext,
                              financial_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Generate response using LLM with financial context"""

        # Check if API key is available
        if not self.api_key:
            return {
                'response': "LLM integration requires an API key. Please set OPENROUTER_API_KEY environment variable.",
                'suggestions': ["Set up API key for advanced AI responses"],
                'data_needed': []
            }

        # Prepare the prompt with financial context
        system_prompt = self._create_system_prompt(financial_data, user_id)
        user_prompt = query

        # Prepare messages for LLM
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]

        # Add conversation history for context
        if context and hasattr(context, 'session_id'):
            history = self.get_conversation_history(context.session_id, limit=3)
            # Insert history in the correct order (oldest first)
            for turn in history[-3:]:  # Last 3 turns
                messages.insert(-1, {"role": "user", "content": turn['user_query']})
                messages.insert(-1, {"role": "assistant", "content": turn['response']})

        # Call OpenRouter API
        try:
            response = self._call_openrouter(messages)

            if response and 'choices' in response and len(response['choices']) > 0:
                llm_response = response['choices'][0]['message']['content']

                # Extract suggestions and data needs from LLM response if structured
                suggestions = self._extract_suggestions(llm_response)
                data_needed = self._extract_data_needs(query, financial_data)

                # Get analysis results if financial data is available
                analysis_results = None
                if financial_data:
                    try:
                        permissions = self.privacy_manager.get_user_permissions(user_id)
                        analysis_results = self.insights_engine.generate_comprehensive_analysis(
                            financial_data, permissions
                        )
                    except Exception as e:
                        logger.error(f"Error generating analysis: {e}")

                return {
                    'response': llm_response,
                    'suggestions': suggestions,
                    'data_needed': data_needed,
                    'analysis_results': analysis_results
                }
            else:
                return {
                    'response': "I'm having trouble processing your request right now. Please try again.",
                    'suggestions': ["Try rephrasing your question", "Check your network connection"],
                    'data_needed': []
                }

        except Exception as e:
            logger.error(f"Error calling LLM: {e}")
            return {
                'response': f"AI service is temporarily unavailable: {str(e)}",
                'suggestions': ["Try again in a moment", "Use the legacy analysis endpoints"],
                'data_needed': []
            }

    def _create_system_prompt(self, financial_data: Optional[Dict[str, Any]], user_id: str) -> str:
        """Create system prompt with financial context"""
        
        prompt = """You are FinAI, an expert financial advisor AI assistant. You help users understand their financial situation and provide personalized advice while strictly respecting their privacy preferences.

# YOUR ROLE & CAPABILITIES
- Analyze financial data (assets, liabilities, income, expenses, investments)
- Provide savings recommendations with specific calculations
- Offer investment advice tailored to risk tolerance and goals
- Help with debt management strategies (snowball, avalanche methods)
- Create budget plans using 50/30/20 or other frameworks
- Set and track financial goals with timelines
- Explain complex financial concepts in simple terms
- Forecast future financial scenarios

# FINANCIAL DATA CATEGORIES
1. ASSETS: Cash, bank balances, property, investments
2. LIABILITIES: Loans, credit card debt, mortgages
3. TRANSACTIONS: Income, expenses, transfers
4. EPF/RETIREMENT: Contributions, employer match, current balance
5. CREDIT: Score (300-900), rating (Poor, Average, Good, Excellent)
6. INVESTMENTS: Stocks, mutual funds, bonds, other securities

# PRIVACY & USER CONTROL
Users can hide/restrict access to any financial category. Always:
- Respect data visibility permissions strictly
- NEVER mention or analyze data categories the user has hidden
- If asked about hidden data, politely explain it's not available
- Focus analysis only on visible data categories

# RESPONSE GUIDELINES
- Be professional, helpful, and encouraging
- Use emojis sparingly (maximum 2-3 per response)
- Provide specific numbers and calculations when possible
- Format with clear sections using markdown headers
- Keep responses concise but comprehensive
- Prioritize actionable advice over generic information
- Acknowledge data limitations if categories are hidden

# FINANCIAL BEST PRACTICES TO FOLLOW
- Emergency fund: 3-6 months expenses
- Debt-to-income ratio: Below 36%
- Savings rate: 20% of income (50/30/20 budgeting)
- Investment diversification: Spread across asset classes
- Retirement: Maximize employer matches first

# WHAT TO AVOID
- Never recommend specific stocks or investment products
- Don't provide tax advice (suggest consulting professionals)
- Avoid making promises about future returns
- Don't criticize user's current financial choices
- Never ask for sensitive personal information
- Don't make decisions for the user - provide options

# FORMATTING EXAMPLES
## Financial Overview
### Assets: $250,000
### Liabilities: $150,000
### Net Worth: $100,000

## Recommendations
1. ✅ Pay off high-interest credit card debt first
2. 📈 Maximize employer 401(k) match ($4,000/year)
3. 🏦 Build emergency fund to $25,000 (3 months expenses)

# FINANCIAL ANALYSIS FRAMEWORK
When analyzing user data, always consider:
1. Liquidity (emergency fund adequacy)
2. Solvency (debt management)
3. Savings rate and progress toward goals
4. Investment diversification
5. Cash flow health
6. Risk exposure

"""
        
        # Add financial data context if available
        if financial_data:
            # Mask data based on user permissions
            masked_data = self._mask_financial_data(financial_data, user_id)
            prompt += f"\n# USER'S CURRENT FINANCIAL SITUATION:\n"
            prompt += json.dumps(masked_data, indent=2)
            
            # Get user permissions
            try:
                permissions = self.privacy_manager.get_user_permissions(user_id)
                allowed_categories = list(permissions.get_allowed_categories())
                prompt += f"\n\n# USER DATA PERMISSIONS:\n"
                prompt += f"Allowed categories: {', '.join(allowed_categories)}\n"
                prompt += f"Restricted categories: {', '.join(set(['assets', 'liabilities', 'transactions', 'epf_retirement_balance', 'credit_score', 'investments']) - set(allowed_categories))}"
            except Exception as e:
                logger.error(f"Error getting user permissions: {e}")
        else:
            prompt += "\n# NOTE: User hasn't provided financial data yet. Ask them to share their financial information for personalized advice."
        
        return prompt

    def _mask_financial_data(self, financial_data: Dict[str, Any], user_id: str) -> Dict[str, Any]:
        """Mask financial data based on user permissions"""
        try:
            permissions = self.privacy_manager.get_user_permissions(user_id)
            return permissions.mask_data(financial_data)
        except Exception as e:
            logger.error(f"Error masking financial data: {e}")
            return financial_data  # Return original data if masking fails

    def _call_openrouter(self, messages: List[Dict[str, str]]) -> Dict[str, Any]:
        """Call OpenRouter API with messages"""

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        data = {
            "model": self.default_model,
            "messages": messages
        }

        response = requests.post(
            f"{self.api_base}/chat/completions",
            headers=headers,
            json=data
        )

        if response.status_code == 200:
            return response.json()
        else:
            logger.error(f"OpenRouter API error: {response.status_code} - {response.text}")
            return None

    def _extract_suggestions(self, response: str) -> List[str]:
        """Extract suggestions from LLM response (placeholder implementation)"""
        # In a more advanced implementation, we could use the LLM to extract suggestions
        # For now, we'll return generic suggestions
        return [
            "Ask about savings strategies",
            "Request investment advice",
            "Get debt management tips",
            "Explore budget planning"
        ]

    def _extract_data_needs(self, query: str, financial_data: Optional[Dict[str, Any]]) -> List[str]:
        """Determine what financial data is needed based on the query"""
        # If we already have financial data, we may not need more
        if financial_data:
            return []
            
        # Determine what data is needed based on the query
        query_lower = query.lower()
        data_needs = set()
        
        if any(word in query_lower for word in ['asset', 'property', 'cash', 'bank']):
            data_needs.add('assets')
            
        if any(word in query_lower for word in ['debt', 'loan', 'credit', 'mortgage']):
            data_needs.add('liabilities')
            
        if any(word in query_lower for word in ['income', 'expense', 'spend', 'budget', 'salary']):
            data_needs.add('transactions')
            
        if any(word in query_lower for word in ['epf', 'retirement', 'pension', '401k', 'contribution']):
            data_needs.add('epf_retirement_balance')
            
        if any(word in query_lower for word in ['credit score', 'credit rating']):
            data_needs.add('credit_score')
            
        if any(word in query_lower for word in ['invest', 'stock', 'mutual fund', 'bond', 'portfolio']):
            data_needs.add('investments')
            
        # If no specific needs identified, request all categories
        if not data_needs:
            return ['assets', 'liabilities', 'transactions', 'investments']
            
        return list(data_needs)