"""
Enhanced AI service with caching, real API integration, and performance optimizations
"""
Enhanced AI service for generating contextual financial responses
Provides advanced context-aware response generation with conversation memory
"""
import logging
import json
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime, timedelta
from enum import Enum
from dataclasses import dataclass, field
import hashlib

logger = logging.getLogger(__name__)

# Try to import Google Generative AI, fallback to mock if not available
try:
    import google.generativeai as genai
    GENAI_AVAILABLE = True
except ImportError:
    logger.warning("Google Generative AI not available. Using enhanced mock responses.")
    GENAI_AVAILABLE = False
    genai = None


class ResponseTone(Enum):
    """Response tone types"""
    INFORMATIVE = "informative"
    ADVISORY = "advisory"
    CLARIFYING = "clarifying"
    ENCOURAGING = "encouraging"
    CAUTIONARY = "cautionary"
    CELEBRATORY = "celebratory"


class ResponseComplexity(Enum):
    """Response complexity levels"""
    SIMPLE = "simple"
    DETAILED = "detailed"
    COMPREHENSIVE = "comprehensive"
    TECHNICAL = "technical"


@dataclass
class ResponseContext:
    """Context for response generation"""
    user_id: str
    session_id: str
    conversation_topic: Optional[str] = None
    user_preferences: Dict[str, Any] = field(default_factory=dict)
    response_history: List[str] = field(default_factory=list)
    financial_goals: List[str] = field(default_factory=list)
    risk_tolerance: str = "moderate"
    experience_level: str = "beginner"


@dataclass
class FinancialInsight:
    """Structured financial insight"""
    type: str  # "positive", "neutral", "concern", "opportunity"
    category: str  # "spending", "savings", "investment", etc.
    message: str
    priority: int  # 1-5 scale
    actionable: bool
    data_points: Dict[str, Any] = field(default_factory=dict)


class EnhancedAIService:
    """Enhanced AI service with advanced financial advisory capabilities"""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the enhanced AI service
        
        Args:
            api_key: Google AI API key. If None, will use environment variable
        """
        self.api_key = api_key
        self.model = None
        self.response_contexts: Dict[str, ResponseContext] = {}
        self._initialize_model()
        self._initialize_financial_knowledge()
        self._initialize_response_templates()
    
    def _initialize_model(self):
        """Initialize the Google Generative AI model"""
        if not GENAI_AVAILABLE:
            logger.warning("Google Generative AI not available. Using enhanced mock responses.")
            return
            
        try:
            # Configure the API key
            if self.api_key:
                genai.configure(api_key=self.api_key)
            else:
                # Try to get from environment variable
                import os
                api_key = os.getenv('GOOGLE_AI_API_KEY')
                if api_key:
                    genai.configure(api_key=api_key)
                else:
                    logger.warning("No Google AI API key provided. AI responses will be enhanced mocks.")
                    return
            
            # Initialize the model with enhanced configuration
            generation_config = {
                "temperature": 0.7,
                "top_p": 0.8,
                "top_k": 40,
                "max_output_tokens": 2048,
            }
            
            self.model = genai.GenerativeModel(
                'gemini-pro',
                generation_config=generation_config
            )
            logger.info("Enhanced Google Generative AI model initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize enhanced AI model: {str(e)}")
            self.model = None
    
    def _initialize_financial_knowledge(self):
        """Initialize financial domain knowledge"""
        self.financial_concepts = {
            "budgeting": {
                "50/30/20_rule": "Allocate 50% to needs, 30% to wants, 20% to savings",
                "zero_based_budgeting": "Every dollar has a purpose before the month begins",
                "envelope_method": "Physical or digital envelopes for different spending categories"
            },
            "savings": {
                "emergency_fund": "3-6 months of expenses for unexpected situations",
                "savings_rate": "Percentage of income saved; 10-20% is generally recommended",
                "compound_interest": "Interest earned on both principal and previously earned interest"
            },
            "investing": {
                "diversification": "Spreading investments across different asset types",
                "dollar_cost_averaging": "Regular investments regardless of market conditions",
                "risk_vs_return": "Higher potential returns usually come with higher risk"
            },
            "debt": {
                "debt_snowball": "Pay minimum on all debts, extra on smallest balance",
                "debt_avalanche": "Pay minimum on all debts, extra on highest interest rate",
                "debt_to_income_ratio": "Total monthly debt payments divided by gross monthly income"
            }
        }
        
        self.financial_thresholds = {
            "emergency_fund_months": {"good": 6, "adequate": 3, "concerning": 1},
            "savings_rate_percent": {"excellent": 20, "good": 15, "adequate": 10, "low": 5},
            "debt_to_income_ratio": {"good": 0.36, "acceptable": 0.43, "concerning": 0.5}
        }
    
    def _initialize_response_templates(self):
        """Initialize response templates for different scenarios"""
        self.response_templates = {
            "spending_analysis": {
                "high_confidence": [
                    "Based on your spending data, I can see some clear patterns that might interest you.",
                    "Let me break down your spending analysis for you.",
                    "Here's what your spending data reveals about your financial habits."
                ],
                "low_confidence": [
                    "I notice some spending patterns, though I'd like to clarify a few details.",
                    "From what I can see in your data, here are some initial observations.",
                    "Let me share what I can determine from your spending information."
                ]
            },
            "savings_analysis": {
                "positive": [
                    "Great news about your savings progress!",
                    "Your savings strategy is showing positive results.",
                    "I'm seeing some encouraging trends in your savings."
                ],
                "neutral": [
                    "Here's an overview of your current savings situation.",
                    "Let me walk you through your savings analysis.",
                    "Your savings data shows the following patterns."
                ],
                "concerning": [
                    "I notice some areas where we might improve your savings approach.",
                    "There are some opportunities to strengthen your savings strategy.",
                    "Let's look at ways to boost your savings performance."
                ]
            },
            "affordability": {
                "affordable": [
                    "Good news! Based on your financial situation, this appears to be within reach.",
                    "Your current finances suggest you can handle this expense.",
                    "This looks financially feasible given your current position."
                ],
                "tight": [
                    "This would be a stretch based on your current finances.",
                    "While possible, this purchase would significantly impact your budget.",
                    "You could afford this, but it would require careful planning."
                ],
                "unaffordable": [
                    "Based on your current financial situation, this might not be advisable right now.",
                    "This expense would strain your finances significantly.",
                    "I'd recommend building up more financial cushion before considering this."
                ]
            }
        }
    
    def generate_response(self, analysis_results: Dict[str, Any], user_query: str, 
                         nlp_context: Optional[Dict[str, Any]] = None,
                         user_id: str = "default", session_id: Optional[str] = None) -> str:
        """
        Generate an enhanced contextual response
        
        Args:
            analysis_results: Results from financial analysis services
            user_query: Original user query for context
            nlp_context: Enhanced NLP processing results
            user_id: User identifier for context management
            session_id: Session identifier
            
        Returns:
            Enhanced contextual AI response
        """
        try:
            logger.info("Generating enhanced AI response for financial analysis")
            
            # Get or create response context
            context_key = f"{user_id}:{session_id or 'default'}"
            context = self._get_or_create_response_context(context_key, user_id, session_id)
            
            # Analyze the query and results for insights
            insights = self._extract_financial_insights(analysis_results, nlp_context)
            
            # Determine response characteristics
            response_tone = self._determine_response_tone(insights, nlp_context)
            response_complexity = self._determine_response_complexity(context, nlp_context)
            
            # Generate response based on availability of AI model
            if self.model:
                response = self._generate_ai_response(
                    analysis_results, user_query, nlp_context, context, insights, 
                    response_tone, response_complexity
                )
            else:
                response = self._generate_enhanced_mock_response(
                    analysis_results, user_query, nlp_context, context, insights,
                    response_tone, response_complexity
                )
            
            # Update response context
            self._update_response_context(context, user_query, response, insights)
            
            logger.info(f"Enhanced AI response generated: {len(response)} characters")
            return response
            
        except Exception as e:
            logger.error(f"Error generating enhanced AI response: {str(e)}")
            return self._generate_fallback_response(analysis_results, user_query, nlp_context)
    
    def _get_or_create_response_context(self, context_key: str, user_id: str, 
                                      session_id: Optional[str]) -> ResponseContext:
        """Get existing or create new response context"""
        if context_key not in self.response_contexts:
            self.response_contexts[context_key] = ResponseContext(
                user_id=user_id,
                session_id=session_id or "default"
            )
        return self.response_contexts[context_key]
    
    def _extract_financial_insights(self, analysis_results: Dict[str, Any], 
                                  nlp_context: Optional[Dict[str, Any]]) -> List[FinancialInsight]:
        """Extract structured financial insights from analysis results"""
        insights = []
        results = analysis_results.get("results", {})
        analysis_type = analysis_results.get("analysis_type", "unknown")
        
        # Spending Analysis Insights
        if analysis_type == "spending_analysis":
            total_spending = results.get("total_spending", 0)
            category_breakdown = results.get("category_breakdown", {})
            
            # High spending insight
            if total_spending > 5000:  # Threshold can be made dynamic
                insights.append(FinancialInsight(
                    type="concern",
                    category="spending",
                    message=f"Your total spending of ${total_spending:,.2f} is quite substantial",
                    priority=3,
                    actionable=True,
                    data_points={"total_spending": total_spending}
                ))
            
            # Category concentration insight
            if category_breakdown:
                max_category = max(category_breakdown.items(), key=lambda x: x[1])
                if max_category[1] > total_spending * 0.4:  # More than 40% in one category
                    insights.append(FinancialInsight(
                        type="neutral",
                        category="spending",
                        message=f"Most of your spending ({max_category[1]/total_spending*100:.1f}%) is in {max_category[0]}",
                        priority=2,
                        actionable=True,
                        data_points={"dominant_category": max_category[0], "percentage": max_category[1]/total_spending*100}
                    ))
        
        # Savings Analysis Insights
        elif analysis_type == "savings_analysis":
            savings_rate = results.get("savings_rate", 0)
            current_savings = results.get("current_savings", 0)
            
            # Savings rate insight
            if savings_rate >= 20:
                insights.append(FinancialInsight(
                    type="positive",
                    category="savings",
                    message=f"Excellent savings rate of {savings_rate:.1f}%!",
                    priority=1,
                    actionable=False,
                    data_points={"savings_rate": savings_rate}
                ))
            elif savings_rate < 10:
                insights.append(FinancialInsight(
                    type="concern",
                    category="savings",
                    message=f"Your savings rate of {savings_rate:.1f}% could be improved",
                    priority=4,
                    actionable=True,
                    data_points={"savings_rate": savings_rate}
                ))
            
            # Emergency fund insight
            monthly_expenses = results.get("monthly_expenses", 0)
            if monthly_expenses > 0:
                emergency_fund_months = current_savings / monthly_expenses
                if emergency_fund_months < 3:
                    insights.append(FinancialInsight(
                        type="concern",
                        category="emergency_fund",
                        message=f"You have {emergency_fund_months:.1f} months of emergency fund",
                        priority=5,
                        actionable=True,
                        data_points={"emergency_months": emergency_fund_months}
                    ))
        
        # Affordability Insights
        elif analysis_type == "affordability_check":
            affordable = results.get("affordable", False)
            target_amount = results.get("target_amount", 0)
            available_funds = results.get("available_funds", 0)
            
            if affordable:
                insights.append(FinancialInsight(
                    type="positive",
                    category="affordability",
                    message=f"You can afford the ${target_amount:,.2f} expense",
                    priority=2,
                    actionable=False,
                    data_points={"target_amount": target_amount, "available_funds": available_funds}
                ))
            else:
                shortfall = target_amount - available_funds
                insights.append(FinancialInsight(
                    type="concern",
                    category="affordability", 
                    message=f"You're ${shortfall:,.2f} short for this ${target_amount:,.2f} expense",
                    priority=3,
                    actionable=True,
                    data_points={"shortfall": shortfall, "target_amount": target_amount}
                ))
        
        # Financial Health Insights
        elif analysis_type == "financial_health":
            health_score = results.get("health_score", 0)
            net_worth = results.get("net_worth", 0)
            
            if health_score >= 80:
                insights.append(FinancialInsight(
                    type="positive",
                    category="financial_health",
                    message=f"Strong financial health score of {health_score:.1f}/100",
                    priority=1,
                    actionable=False,
                    data_points={"health_score": health_score}
                ))
            elif health_score < 50:
                insights.append(FinancialInsight(
                    type="concern",
                    category="financial_health",
                    message=f"Financial health score of {health_score:.1f}/100 needs attention",
                    priority=5,
                    actionable=True,
                    data_points={"health_score": health_score}
                ))
        
        return insights
    
    def _determine_response_tone(self, insights: List[FinancialInsight], 
                               nlp_context: Optional[Dict[str, Any]]) -> ResponseTone:
        """Determine appropriate response tone based on insights"""
        if not insights:
            return ResponseTone.INFORMATIVE
        
        # Check for positive insights
        positive_insights = [i for i in insights if i.type == "positive"]
        concern_insights = [i for i in insights if i.type == "concern"]
        
        # Determine tone based on insight mix
        if len(positive_insights) > len(concern_insights):
            return ResponseTone.ENCOURAGING
        elif len(concern_insights) > len(positive_insights):
            return ResponseTone.CAUTIONARY
        elif nlp_context and nlp_context.get("confidence", {}).get("overall", 0) < 0.5:
            return ResponseTone.CLARIFYING
        else:
            return ResponseTone.INFORMATIVE
    
    def _determine_response_complexity(self, context: ResponseContext, 
                                     nlp_context: Optional[Dict[str, Any]]) -> ResponseComplexity:
        """Determine appropriate response complexity"""
        # Check user experience level
        if context.experience_level == "expert":
            return ResponseComplexity.TECHNICAL
        elif context.experience_level == "intermediate":
            return ResponseComplexity.DETAILED
        elif len(context.response_history) > 5:  # Experienced in conversation
            return ResponseComplexity.DETAILED
        else:
            return ResponseComplexity.SIMPLE
    
    def _generate_ai_response(self, analysis_results: Dict[str, Any], user_query: str,
                            nlp_context: Optional[Dict[str, Any]], context: ResponseContext,
                            insights: List[FinancialInsight], tone: ResponseTone, 
                            complexity: ResponseComplexity) -> str:
        """Generate response using the AI model"""
        try:
            # Construct enhanced prompt
            prompt = self._construct_enhanced_prompt(
                analysis_results, user_query, nlp_context, context, insights, tone, complexity
            )
            
            # Generate response with AI model
            response = self.model.generate_content(prompt)
            
            if response and response.text:
                return response.text.strip()
            else:
                logger.warning("Empty response from AI model, using fallback")
                return self._generate_enhanced_mock_response(
                    analysis_results, user_query, nlp_context, context, insights, tone, complexity
                )
                
        except Exception as e:
            logger.error(f"Error generating AI response: {str(e)}")
            return self._generate_enhanced_mock_response(
                analysis_results, user_query, nlp_context, context, insights, tone, complexity
            )
    
    def _construct_enhanced_prompt(self, analysis_results: Dict[str, Any], user_query: str,
                                 nlp_context: Optional[Dict[str, Any]], context: ResponseContext,
                                 insights: List[FinancialInsight], tone: ResponseTone, 
                                 complexity: ResponseComplexity) -> str:
        """Construct enhanced prompt for AI model"""
        # Base system instruction
        system_instruction = f"""You are an AI-powered financial advisor with expertise in personal finance. 

PERSONALITY & TONE:
- Response tone: {tone.value}
- Response complexity: {complexity.value}
- Be encouraging, supportive, and practical
- Use clear, conversational language
- Focus on actionable advice

CONTEXT AWARENESS:
- User experience level: {context.experience_level}
- Risk tolerance: {context.risk_tolerance}
- This is turn #{len(context.response_history) + 1} in the conversation
- Conversation topic: {context.conversation_topic or 'general financial inquiry'}

GUIDELINES:
1. Address the user's specific query directly
2. Reference the financial analysis results provided
3. Highlight key insights and patterns
4. Provide concrete, actionable recommendations
5. Use appropriate financial terminology for the user's level
6. Be encouraging about positive findings
7. Be constructive about concerning findings
8. Suggest follow-up questions when appropriate"""
        
        # Add NLP context if available
        nlp_info = ""
        if nlp_context:
            intent_info = nlp_context.get("intent", {})
            confidence_info = nlp_context.get("confidence", {})
            nlp_info = f"""
NLP PROCESSING RESULTS:
- Intent: {intent_info.get('name', 'unknown')} (confidence: {intent_info.get('confidence', 0):.2f})
- Intent category: {intent_info.get('category', 'general')}
- Overall confidence: {confidence_info.get('overall', 0):.2f}
- Confidence level: {confidence_info.get('level', 'unknown')}"""
        
        # Format insights
        insights_text = ""
        if insights:
            insights_text = "KEY INSIGHTS IDENTIFIED:\n"
            for insight in sorted(insights, key=lambda x: x.priority, reverse=True):
                insights_text += f"- {insight.type.upper()}: {insight.message}\n"
        
        # Format analysis results
        analysis_summary = self._format_enhanced_analysis_summary(analysis_results)
        
        # Construct full prompt
        prompt = f"""{system_instruction}

{nlp_info}

USER QUERY: "{user_query}"

FINANCIAL ANALYSIS RESULTS:
{analysis_summary}

{insights_text}

Please provide a helpful, personalized response that addresses the user's query, incorporates the analysis results, highlights the key insights, and offers actionable advice. Make it conversational and appropriate for the user's experience level."""
        
        return prompt
    
    def _format_enhanced_analysis_summary(self, analysis_results: Dict[str, Any]) -> str:
        """Format analysis results with enhanced context"""
        results = analysis_results.get("results", {})
        analysis_type = analysis_results.get("analysis_type", "unknown")
        success = analysis_results.get("success", False)
        
        if not success:
            return f"Analysis Type: {analysis_type}\nStatus: Failed\nError: {analysis_results.get('error', 'Unknown error')}"
        
        summary_parts = [f"Analysis Type: {analysis_type}", f"Status: Successful"]
        
        # Enhanced formatting based on analysis type
        if analysis_type == "spending_analysis":
            total = results.get("total_spending", 0)
            summary_parts.append(f"Total Spending: ${total:,.2f}")
            
            category_breakdown = results.get("category_breakdown", {})
            if category_breakdown:
                summary_parts.append("Category Breakdown:")
                sorted_categories = sorted(category_breakdown.items(), key=lambda x: x[1], reverse=True)
                for category, amount in sorted_categories[:5]:  # Top 5 categories
                    percentage = (amount / total * 100) if total > 0 else 0
                    summary_parts.append(f"  • {category.title()}: ${amount:,.2f} ({percentage:.1f}%)")
            
            insights_list = results.get("insights", [])
            if insights_list:
                summary_parts.append("Analysis Insights:")
                for insight in insights_list[:3]:  # Top 3 insights
                    summary_parts.append(f"  • {insight}")
        
        elif analysis_type == "savings_analysis":
            current_savings = results.get("current_savings", 0)
            monthly_savings = results.get("monthly_savings", 0)
            savings_rate = results.get("savings_rate", 0)
            
            summary_parts.extend([
                f"Current Savings: ${current_savings:,.2f}",
                f"Monthly Savings: ${monthly_savings:,.2f}",
                f"Savings Rate: {savings_rate:.1f}%"
            ])
            
            projected_savings = results.get("projected_savings", {})
            if projected_savings:
                summary_parts.append("Projected Savings:")
                for period, data in projected_savings.items():
                    if isinstance(data, dict):
                        amount = data.get("amount", 0)
                        summary_parts.append(f"  • {period.title()}: ${amount:,.2f}")
        
        elif analysis_type == "affordability_check":
            affordable = results.get("affordable", False)
            target_amount = results.get("target_amount", 0)
            available_funds = results.get("available_funds", 0)
            monthly_cash_flow = results.get("monthly_cash_flow", 0)
            
            summary_parts.extend([
                f"Target Amount: ${target_amount:,.2f}",
                f"Available Funds: ${available_funds:,.2f}",
                f"Monthly Cash Flow: ${monthly_cash_flow:,.2f}",
                f"Affordability: {'✓ Yes' if affordable else '✗ No'}"
            ])
            
            time_to_save = results.get("time_to_save", {})
            if time_to_save and time_to_save.get("achievable"):
                months = time_to_save.get("months", 0)
                summary_parts.append(f"Time to Save: {months:.1f} months")
        
        elif analysis_type == "financial_health":
            net_worth = results.get("net_worth", 0)
            health_score = results.get("health_score", 0)
            savings_rate = results.get("savings_rate", 0)
            
            summary_parts.extend([
                f"Net Worth: ${net_worth:,.2f}",
                f"Financial Health Score: {health_score:.1f}/100",
                f"Savings Rate: {savings_rate:.1f}%"
            ])
            
            # Add health assessment
            if health_score >= 80:
                assessment = "Excellent financial health"
            elif health_score >= 60:
                assessment = "Good financial health"
            elif health_score >= 40:
                assessment = "Fair financial health - room for improvement"
            else:
                assessment = "Poor financial health - needs attention"
            
            summary_parts.append(f"Assessment: {assessment}")
        
        return "\n".join(summary_parts)
    
    def _generate_enhanced_mock_response(self, analysis_results: Dict[str, Any], user_query: str,
                                       nlp_context: Optional[Dict[str, Any]], context: ResponseContext,
                                       insights: List[FinancialInsight], tone: ResponseTone,
                                       complexity: ResponseComplexity) -> str:
        """Generate enhanced mock response when AI model is not available"""
        analysis_type = analysis_results.get("analysis_type", "unknown")
        results = analysis_results.get("results", {})
        
        # Start with appropriate greeting/opener based on tone
        opener = self._get_tone_appropriate_opener(tone, context)
        
        # Generate main content based on analysis type
        if analysis_type == "spending_analysis":
            response = self._generate_spending_mock_response(results, insights, complexity)
        elif analysis_type == "savings_analysis":
            response = self._generate_savings_mock_response(results, insights, complexity)
        elif analysis_type == "affordability_check":
            response = self._generate_affordability_mock_response(results, insights, complexity)
        elif analysis_type == "financial_health":
            response = self._generate_health_mock_response(results, insights, complexity)
        else:
            response = self._generate_generic_mock_response(results, insights, complexity)
        
        # Add actionable recommendations based on insights
        recommendations = self._generate_recommendations(insights, complexity)
        
        # Combine all parts
        full_response = f"{opener}\n\n{response}"
        if recommendations:
            full_response += f"\n\n📋 **Recommendations:**\n{recommendations}"
        
        # Add follow-up question if appropriate
        follow_up = self._generate_follow_up_question(analysis_type, insights, context)
        if follow_up:
            full_response += f"\n\n{follow_up}"
        
        return full_response
    
    def _get_tone_appropriate_opener(self, tone: ResponseTone, context: ResponseContext) -> str:
        """Get appropriate opener based on tone"""
        openers = {
            ResponseTone.ENCOURAGING: [
                "Great question! Let me share some positive insights from your financial data.",
                "I'm excited to share what I found in your financial analysis!",
                "Your financial awareness is impressive! Here's what the data shows."
            ],
            ResponseTone.CAUTIONARY: [
                "Thank you for asking. I've identified some important areas to discuss.",
                "I appreciate you checking in on this. Let's review what I found.",
                "This is a smart question to ask. Here's what I see in your finances."
            ],
            ResponseTone.CLARIFYING: [
                "I want to make sure I understand your situation correctly.",
                "Let me clarify a few details about your financial picture.",
                "Based on the information available, here's what I can tell you."
            ],
            ResponseTone.INFORMATIVE: [
                "Here's a comprehensive look at your financial data.",
                "Let me break down your financial analysis for you.",
                "Based on your data, here's what I found."
            ],
            ResponseTone.ADVISORY: [
                "I'd like to share some strategic insights about your finances.",
                "Here are some key observations and recommendations.",
                "Let me provide some guidance based on your financial situation."
            ]
        }
        
        import random
        return random.choice(openers.get(tone, openers[ResponseTone.INFORMATIVE]))
    
    def _generate_spending_mock_response(self, results: Dict[str, Any], 
                                       insights: List[FinancialInsight], 
                                       complexity: ResponseComplexity) -> str:
        """Generate mock response for spending analysis"""
        total_spending = results.get("total_spending", 0)
        category_breakdown = results.get("category_breakdown", {})
        
        response = f"💰 **Spending Analysis Summary**\n\n"
        response += f"Your total spending is **${total_spending:,.2f}**. "
        
        if category_breakdown:
            top_category = max(category_breakdown.items(), key=lambda x: x[1])
            percentage = (top_category[1] / total_spending * 100) if total_spending > 0 else 0
            response += f"Your largest expense category is **{top_category[0]}** at **${top_category[1]:,.2f}** ({percentage:.1f}% of total spending)."
            
            if complexity in [ResponseComplexity.DETAILED, ResponseComplexity.COMPREHENSIVE]:
                response += f"\n\n📊 **Category Breakdown:**\n"
                sorted_categories = sorted(category_breakdown.items(), key=lambda x: x[1], reverse=True)
                for i, (category, amount) in enumerate(sorted_categories[:5]):
                    percentage = (amount / total_spending * 100) if total_spending > 0 else 0
                    response += f"{i+1}. {category.title()}: ${amount:,.2f} ({percentage:.1f}%)\n"
        
        # Add insights
        spending_insights = [i for i in insights if i.category == "spending"]
        if spending_insights:
            response += f"\n🔍 **Key Insights:**\n"
            for insight in spending_insights:
                icon = {"positive": "✅", "concern": "⚠️", "neutral": "ℹ️"}.get(insight.type, "•")
                response += f"{icon} {insight.message}\n"
        
        return response
    
    def _generate_savings_mock_response(self, results: Dict[str, Any], 
                                      insights: List[FinancialInsight],
                                      complexity: ResponseComplexity) -> str:
        """Generate mock response for savings analysis"""
        current_savings = results.get("current_savings", 0)
        monthly_savings = results.get("monthly_savings", 0)
        savings_rate = results.get("savings_rate", 0)
        
        response = f"💎 **Savings Analysis Summary**\n\n"
        response += f"Your current savings balance is **${current_savings:,.2f}** with a monthly savings rate of **${monthly_savings:,.2f}**. "
        response += f"This represents a **{savings_rate:.1f}% savings rate**. "
        
        # Provide context on savings rate
        if savings_rate >= 20:
            response += "This is an excellent savings rate! 🎉"
        elif savings_rate >= 15:
            response += "This is a very good savings rate! 👍"
        elif savings_rate >= 10:
            response += "This is a solid savings rate. 👌"
        elif savings_rate >= 5:
            response += "This is a modest savings rate with room for improvement."
        else:
            response += "This savings rate could benefit from some attention."
        
        # Add emergency fund analysis if we have expense data
        monthly_expenses = results.get("monthly_expenses", 0)
        if monthly_expenses > 0 and complexity in [ResponseComplexity.DETAILED, ResponseComplexity.COMPREHENSIVE]:
            emergency_months = current_savings / monthly_expenses
            response += f"\n\n🚨 **Emergency Fund Status:**\n"
            response += f"You have approximately **{emergency_months:.1f} months** of expenses saved. "
            
            if emergency_months >= 6:
                response += "Excellent emergency fund! You're well-prepared for unexpected expenses."
            elif emergency_months >= 3:
                response += "Good emergency fund foundation. Consider building toward 6 months if possible."
            else:
                response += "Your emergency fund could use some attention. Aim for 3-6 months of expenses."
        
        return response
    
    def _generate_affordability_mock_response(self, results: Dict[str, Any], 
                                            insights: List[FinancialInsight],
                                            complexity: ResponseComplexity) -> str:
        """Generate mock response for affordability check"""
        affordable = results.get("affordable", False)
        target_amount = results.get("target_amount", 0)
        available_funds = results.get("available_funds", 0)
        
        response = f"💳 **Affordability Assessment**\n\n"
        
        if affordable:
            response += f"✅ **Good news!** Based on your current financial situation, the **${target_amount:,.2f}** expense appears to be manageable. "
            response += f"You have **${available_funds:,.2f}** in available funds."
            
            if complexity in [ResponseComplexity.DETAILED, ResponseComplexity.COMPREHENSIVE]:
                remaining = available_funds - target_amount
                response += f"\n\nAfter this expense, you'd have approximately **${remaining:,.2f}** remaining in your budget. "
                
                if remaining < available_funds * 0.2:  # Less than 20% remaining
                    response += "However, this would use most of your available funds, so make sure it aligns with your priorities."
        else:
            shortfall = target_amount - available_funds
            response += f"⚠️ Based on your current finances, the **${target_amount:,.2f}** expense would be challenging. "
            response += f"You have **${available_funds:,.2f}** available, leaving a shortfall of **${shortfall:,.2f}**."
            
            if complexity in [ResponseComplexity.DETAILED, ResponseComplexity.COMPREHENSIVE]:
                monthly_cash_flow = results.get("monthly_cash_flow", 0)
                if monthly_cash_flow > 0:
                    months_to_save = shortfall / monthly_cash_flow
                    response += f"\n\nWith your current monthly cash flow of **${monthly_cash_flow:,.2f}**, you could save for this expense in approximately **{months_to_save:.1f} months**."
        
        return response
    
    def _generate_health_mock_response(self, results: Dict[str, Any], 
                                     insights: List[FinancialInsight],
                                     complexity: ResponseComplexity) -> str:
        """Generate mock response for financial health analysis"""
        net_worth = results.get("net_worth", 0)
        health_score = results.get("health_score", 0)
        savings_rate = results.get("savings_rate", 0)
        total_assets = results.get("total_assets", 0)
        total_debt = results.get("total_debt", 0)
        
        response = f"🏥 **Financial Health Overview**\n\n"
        response += f"Your financial health score is **{health_score:.1f}/100** with a net worth of **${net_worth:,.2f}**. "
        
        # Provide health assessment
        if health_score >= 80:
            response += "Excellent financial health! 🌟"
        elif health_score >= 60:
            response += "Good financial health with solid fundamentals. 👍"
        elif health_score >= 40:
            response += "Fair financial health with room for improvement. 📈"
        else:
            response += "Your financial health needs attention, but every step forward counts! 💪"
        
        if complexity in [ResponseComplexity.DETAILED, ResponseComplexity.COMPREHENSIVE]:
            response += f"\n\n📊 **Key Metrics:**\n"
            response += f"• **Total Assets:** ${total_assets:,.2f}\n"
            response += f"• **Total Debt:** ${total_debt:,.2f}\n"
            response += f"• **Net Worth:** ${net_worth:,.2f}\n"
            response += f"• **Savings Rate:** {savings_rate:.1f}%\n"
            
            # Debt-to-asset ratio
            if total_assets > 0:
                debt_ratio = total_debt / total_assets
                response += f"• **Debt-to-Asset Ratio:** {debt_ratio:.1%}\n"
        
        return response
    
    def _generate_generic_mock_response(self, results: Dict[str, Any], 
                                      insights: List[FinancialInsight],
                                      complexity: ResponseComplexity) -> str:
        """Generate generic mock response for unknown analysis types"""
        response = "📋 **Financial Analysis Summary**\n\n"
        response += "I've analyzed your financial data and found several interesting patterns. "
        
        if insights:
            response += f"Here are the key insights I identified:\n\n"
            for insight in insights[:3]:  # Top 3 insights
                icon = {"positive": "✅", "concern": "⚠️", "neutral": "ℹ️"}.get(insight.type, "•")
                response += f"{icon} {insight.message}\n"
        else:
            response += "Your financial situation shows various data points that we can work with to improve your financial strategy."
        
        return response
    
    def _generate_recommendations(self, insights: List[FinancialInsight], 
                                complexity: ResponseComplexity) -> str:
        """Generate actionable recommendations based on insights"""
        if not insights:
            return ""
        
        recommendations = []
        actionable_insights = [i for i in insights if i.actionable]
        
        for insight in actionable_insights[:3]:  # Top 3 actionable insights
            if insight.category == "spending" and insight.type == "concern":
                recommendations.append("Consider reviewing your spending categories to identify areas for reduction")
            elif insight.category == "savings" and insight.type == "concern":
                recommendations.append("Try increasing your savings rate by 1-2% to build financial resilience")
            elif insight.category == "emergency_fund" and insight.type == "concern":
                recommendations.append("Focus on building your emergency fund to 3-6 months of expenses")
            elif insight.category == "affordability" and insight.type == "concern":
                recommendations.append("Consider saving for a few months before making this purchase")
            elif insight.category == "financial_health" and insight.type == "concern":
                recommendations.append("Focus on debt reduction and increasing your savings rate")
        
        # Add general recommendations if none specific
        if not recommendations:
            recommendations = [
                "Continue monitoring your financial progress regularly",
                "Consider setting specific financial goals for the next quarter",
                "Review and adjust your budget monthly to stay on track"
            ]
        
        return "\n".join(f"• {rec}" for rec in recommendations)
    
    def _generate_follow_up_question(self, analysis_type: str, insights: List[FinancialInsight],
                                   context: ResponseContext) -> str:
        """Generate appropriate follow-up question"""
        follow_ups = {
            "spending_analysis": [
                "Would you like me to suggest ways to optimize your spending in specific categories?",
                "Shall I help you create a budget plan based on this analysis?",
                "Are you interested in comparing this month's spending to previous months?"
            ],
            "savings_analysis": [
                "Would you like to explore strategies to increase your savings rate?",
                "Shall I help you set savings goals for the next quarter?", 
                "Are you interested in investment options for your savings?"
            ],
            "affordability_check": [
                "Would you like me to create a savings plan for this expense?",
                "Shall I suggest ways to increase your available funds?",
                "Are there alternative options you'd like me to evaluate?"
            ],
            "financial_health": [
                "Would you like specific recommendations to improve your financial health score?",
                "Shall we create an action plan for your top priorities?",
                "Are you interested in setting financial goals for the next year?"
            ]
        }
        
        questions = follow_ups.get(analysis_type, [
            "Is there anything specific about your finances you'd like me to explain further?",
            "Would you like me to analyze a different aspect of your financial situation?"
        ])
        
        import random
        return f"❓ {random.choice(questions)}"
    
    def _generate_fallback_response(self, analysis_results: Dict[str, Any], user_query: str,
                                  nlp_context: Optional[Dict[str, Any]]) -> str:
        """Generate fallback response when everything else fails"""
        return f"""I've analyzed your financial query: '{user_query}' and processed the available data. 

While I encountered a technical issue generating a detailed response, I can share that your query relates to {analysis_results.get('analysis_type', 'financial analysis')} and the system {"successfully" if analysis_results.get("success") else "attempted to"} process your request.

I'm here to help with your financial questions. Could you please rephrase your query or let me know if you'd like me to focus on a specific aspect of your finances?"""
    
    def _update_response_context(self, context: ResponseContext, user_query: str, 
                               response: str, insights: List[FinancialInsight]):
        """Update response context with conversation information"""
        # Add to response history (keep last 10)
        context.response_history.append({
            "query": user_query,
            "response_length": len(response),
            "insights_count": len(insights),
            "timestamp": datetime.utcnow().isoformat()
        })
        context.response_history = context.response_history[-10:]
        
        # Update user preferences based on insights
        concern_insights = [i for i in insights if i.type == "concern"]
        if concern_insights:
            # User has financial concerns, adjust tone to be more supportive
            if context.user_preferences.get("support_level", "normal") == "normal":
                context.user_preferences["support_level"] = "high"
    
    def get_response_context_summary(self, user_id: str, session_id: str = "default") -> Dict[str, Any]:
        """Get summary of response context for a user session"""
        context_key = f"{user_id}:{session_id}"
        
        if context_key not in self.response_contexts:
            return {"error": "No response context found"}
        
        context = self.response_contexts[context_key]
        
        return {
            "user_id": user_id,
            "session_id": session_id,
            "response_count": len(context.response_history),
            "conversation_topic": context.conversation_topic,
            "user_preferences": context.user_preferences,
            "experience_level": context.experience_level,
            "risk_tolerance": context.risk_tolerance,
            "financial_goals": context.financial_goals
        }
    
    def is_available(self) -> bool:
        """Check if the AI service is available"""
        return self.model is not None or True  # Always available with enhanced mocks
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the AI model and service"""
        return {
            "ai_model_available": self.model is not None,
            "model_name": "gemini-pro" if self.model else "enhanced_mock",
            "provider": "Google Generative AI" if self.model else "Internal Enhanced Service",
            "features": [
                "contextual_responses",
                "financial_domain_expertise", 
                "conversation_awareness",
                "tone_adaptation",
                "complexity_adjustment",
                "insight_extraction",
                "recommendation_generation",
                "follow_up_suggestions"
            ],
            "response_tones": [tone.value for tone in ResponseTone],
            "complexity_levels": [level.value for level in ResponseComplexity],
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }