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

        prompt = """You are an expert financial advisor AI assistant. You help users understand their financial situation and provide personalized advice.

Your capabilities include:
1. Analyzing financial data (assets, liabilities, income, expenses, investments)
2. Providing savings recommendations
3. Offering investment advice
4. Helping with debt management
5. Creating budget plans
6. Setting financial goals
7. Explaining financial concepts in simple terms

Important guidelines:
- Always be professional, helpful, and clear
- Use emojis sparingly to make responses engaging
- Provide actionable advice with specific numbers when possible
- Respect user privacy and only discuss data they've shared
- If asked about topics outside finance, politely redirect to financial matters
- Format responses with clear sections using markdown-style headers
"""

        # Add financial data context if available
        if financial_data:
            prompt += f"\nUser's current financial situation:\n"
            prompt += json.dumps(financial_data, indent=2)

            # Get user permissions
            try:
                permissions = self.privacy_manager.get_user_permissions(user_id)
                allowed_categories = list(permissions.get_allowed_categories())
                prompt += f"\n\nUser has granted access to these financial categories: {', '.join(allowed_categories)}"
            except Exception as e:
                logger.error(f"Error getting user permissions: {e}")
        else:
            prompt += "\nNote: The user hasn't provided financial data yet. Ask them to share their financial information for personalized advice."

        return prompt

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
        # This is a simplified implementation - in practice, we could use the LLM to determine this
        if not financial_data:
            return ["assets", "liabilities", "transactions", "investments"]
        return []