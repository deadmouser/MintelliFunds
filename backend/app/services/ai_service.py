"""
AI service for generating natural language responses from financial analysis
"""
import logging
import json
from typing import Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

# Try to import Google Generative AI, fallback to mock if not available
try:
    import google.generativeai as genai
    GENAI_AVAILABLE = True
except ImportError:
    logger.warning("Google Generative AI not available. Using mock responses.")
    GENAI_AVAILABLE = False
    genai = None


class AIService:
    """Service for generating AI-powered financial advice responses"""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the AI service
        
        Args:
            api_key: Google AI API key. If None, will use environment variable GOOGLE_AI_API_KEY
        """
        self.api_key = api_key
        self.model = None
        self._initialize_model()
    
    def _initialize_model(self):
        """Initialize the Google Generative AI model"""
        if not GENAI_AVAILABLE:
            logger.warning("Google Generative AI not available. Using mock responses.")
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
                    logger.warning("No Google AI API key provided. AI responses will be mocked.")
                    return
            
            # Initialize the model
            self.model = genai.GenerativeModel('gemini-pro')
            logger.info("Google Generative AI model initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize AI model: {str(e)}")
            self.model = None
    
    def generate_response(self, analysis_results: Dict[str, Any], user_query: str) -> str:
        """
        Generate a natural language response from financial analysis results
        
        Args:
            analysis_results: Results from financial analysis services
            user_query: Original user query for context
            
        Returns:
            Natural language response from AI model
        """
        try:
            logger.info("Generating AI response for financial analysis")
            
            # If no model available, return mock response
            if not self.model:
                return self._generate_mock_response(analysis_results, user_query)
            
            # Construct the prompt
            prompt = self._construct_prompt(analysis_results, user_query)
            
            # Generate response from AI model
            response = self.model.generate_content(prompt)
            
            if response and response.text:
                logger.info("AI response generated successfully")
                return response.text.strip()
            else:
                logger.warning("Empty response from AI model, using fallback")
                return self._generate_fallback_response(analysis_results, user_query)
                
        except Exception as e:
            logger.error(f"Error generating AI response: {str(e)}")
            return self._generate_fallback_response(analysis_results, user_query)
    
    def _construct_prompt(self, analysis_results: Dict[str, Any], user_query: str) -> str:
        """
        Construct a detailed prompt for the AI model
        
        Args:
            analysis_results: Analysis results from financial services
            user_query: Original user query
            
        Returns:
            Formatted prompt string
        """
        # Extract key information from analysis results
        intent = analysis_results.get("intent", "unknown")
        analysis_type = analysis_results.get("analysis_type", "unknown")
        results = analysis_results.get("results", {})
        success = analysis_results.get("success", False)
        
        # Format the analysis data for the prompt
        analysis_summary = self._format_analysis_summary(results, analysis_type)
        
        # Construct the system instruction
        system_instruction = """You are an AI-powered financial advisor with expertise in personal finance. Your role is to:

1. Provide clear, concise, and actionable financial advice
2. Explain complex financial concepts in simple terms
3. Offer practical recommendations based on the user's financial data
4. Be encouraging and supportive while being honest about financial realities
5. Focus on helping users make informed financial decisions
6. Use a friendly, professional tone

Guidelines:
- Always base your advice on the provided financial data
- Be specific with numbers and percentages when available
- Suggest concrete next steps when appropriate
- Highlight both positive aspects and areas for improvement
- Keep responses conversational but informative
- Avoid giving specific investment advice (stick to general principles)"""
        
        # Construct the full prompt
        prompt = f"""{system_instruction}

USER QUERY: "{user_query}"

FINANCIAL ANALYSIS RESULTS:
Intent: {intent}
Analysis Type: {analysis_type}
Success: {success}

{analysis_summary}

Please provide a helpful, personalized response to the user's financial query based on the analysis results above. Make it conversational, actionable, and easy to understand."""

        return prompt
    
    def _format_analysis_summary(self, results: Dict[str, Any], analysis_type: str) -> str:
        """
        Format analysis results into a readable summary for the AI prompt
        
        Args:
            results: Analysis results dictionary
            analysis_type: Type of analysis performed
            
        Returns:
            Formatted summary string
        """
        if not results:
            return "No analysis data available."
        
        summary_parts = []
        
        if analysis_type == "spending_analysis":
            total_spending = results.get("total_spending", 0)
            category_breakdown = results.get("category_breakdown", {})
            top_categories = results.get("top_categories", [])
            insights = results.get("insights", [])
            
            summary_parts.append(f"SPENDING ANALYSIS:")
            summary_parts.append(f"- Total Spending: ${total_spending:,.2f}")
            
            if top_categories:
                summary_parts.append(f"- Top Spending Categories:")
                for cat in top_categories[:3]:
                    summary_parts.append(f"  • {cat['category']}: ${cat['amount']:,.2f}")
            
            if insights:
                summary_parts.append(f"- Key Insights:")
                for insight in insights:
                    summary_parts.append(f"  • {insight}")
        
        elif analysis_type == "savings_projection":
            current_savings = results.get("current_savings", 0)
            monthly_savings = results.get("monthly_savings", 0)
            savings_rate = results.get("savings_rate", 0)
            projected_savings = results.get("projected_savings", {})
            insights = results.get("insights", [])
            
            summary_parts.append(f"SAVINGS PROJECTION:")
            summary_parts.append(f"- Current Savings: ${current_savings:,.2f}")
            summary_parts.append(f"- Monthly Savings: ${monthly_savings:,.2f}")
            summary_parts.append(f"- Savings Rate: {savings_rate:.1f}%")
            
            if projected_savings:
                summary_parts.append(f"- Projected Savings:")
                for period, data in projected_savings.items():
                    summary_parts.append(f"  • {period}: ${data['amount']:,.2f}")
            
            if insights:
                summary_parts.append(f"- Key Insights:")
                for insight in insights:
                    summary_parts.append(f"  • {insight}")
        
        elif analysis_type == "affordability_check":
            affordable = results.get("affordable", False)
            target_amount = results.get("target_amount", 0)
            available_funds = results.get("available_funds", 0)
            monthly_cash_flow = results.get("monthly_cash_flow", 0)
            time_to_save = results.get("time_to_save", {})
            insights = results.get("insights", [])
            
            summary_parts.append(f"AFFORDABILITY CHECK:")
            summary_parts.append(f"- Target Amount: ${target_amount:,.2f}")
            summary_parts.append(f"- Available Funds: ${available_funds:,.2f}")
            summary_parts.append(f"- Monthly Cash Flow: ${monthly_cash_flow:,.2f}")
            summary_parts.append(f"- Affordable: {'Yes' if affordable else 'No'}")
            
            if time_to_save and time_to_save.get("achievable"):
                months = time_to_save.get("months", 0)
                summary_parts.append(f"- Time to Save: {months:.1f} months")
            
            if insights:
                summary_parts.append(f"- Key Insights:")
                for insight in insights:
                    summary_parts.append(f"  • {insight}")
        
        elif analysis_type == "financial_health":
            net_worth = results.get("net_worth", 0)
            total_assets = results.get("total_assets", 0)
            total_debt = results.get("total_debt", 0)
            savings_rate = results.get("savings_rate", 0)
            health_score = results.get("health_score", 0)
            insights = results.get("insights", [])
            
            summary_parts.append(f"FINANCIAL HEALTH OVERVIEW:")
            summary_parts.append(f"- Net Worth: ${net_worth:,.2f}")
            summary_parts.append(f"- Total Assets: ${total_assets:,.2f}")
            summary_parts.append(f"- Total Debt: ${total_debt:,.2f}")
            summary_parts.append(f"- Savings Rate: {savings_rate:.1f}%")
            summary_parts.append(f"- Health Score: {health_score:.1f}/100")
            
            if insights:
                summary_parts.append(f"- Key Insights:")
                for insight in insights:
                    summary_parts.append(f"  • {insight}")
        
        else:
            # Generic analysis summary
            summary_parts.append(f"ANALYSIS RESULTS ({analysis_type}):")
            for key, value in results.items():
                if isinstance(value, (int, float)):
                    if 'amount' in key.lower() or 'value' in key.lower() or 'total' in key.lower():
                        summary_parts.append(f"- {key.replace('_', ' ').title()}: ${value:,.2f}")
                    elif 'rate' in key.lower() or 'percentage' in key.lower() or 'score' in key.lower():
                        summary_parts.append(f"- {key.replace('_', ' ').title()}: {value:.1f}%")
                    else:
                        summary_parts.append(f"- {key.replace('_', ' ').title()}: {value}")
                elif isinstance(value, list) and value:
                    summary_parts.append(f"- {key.replace('_', ' ').title()}: {len(value)} items")
                elif isinstance(value, dict) and value:
                    summary_parts.append(f"- {key.replace('_', ' ').title()}: {len(value)} categories")
        
        return "\n".join(summary_parts)
    
    def _generate_mock_response(self, analysis_results: Dict[str, Any], user_query: str) -> str:
        """
        Generate a mock response when AI model is not available
        
        Args:
            analysis_results: Analysis results from financial services
            user_query: Original user query
            
        Returns:
            Mock response string
        """
        intent = analysis_results.get("intent", "unknown")
        analysis_type = analysis_results.get("analysis_type", "unknown")
        results = analysis_results.get("results", {})
        
        if analysis_type == "spending_analysis":
            total_spending = results.get("total_spending", 0)
            return f"Based on your financial data, your total spending is ${total_spending:,.2f}. I can see your spending patterns and help you identify areas for improvement. Consider reviewing your top spending categories to find potential savings opportunities."
        
        elif analysis_type == "affordability_check":
            affordable = results.get("affordable", False)
            target_amount = results.get("target_amount", 0)
            return f"Regarding your question about affording ${target_amount:,.2f}: {'Yes, you can afford this purchase based on your current financial situation.' if affordable else 'You may need to save more or reconsider this purchase based on your current finances.'}"
        
        elif analysis_type == "savings_projection":
            current_savings = results.get("current_savings", 0)
            monthly_savings = results.get("monthly_savings", 0)
            return f"Your current savings are ${current_savings:,.2f} with a monthly savings rate of ${monthly_savings:,.2f}. Based on your current trajectory, you're building a solid financial foundation. Consider maintaining or increasing your savings rate for better financial security."
        
        else:
            return f"I've analyzed your financial data based on your query: '{user_query}'. The analysis shows various insights about your financial situation. I recommend reviewing the detailed breakdown and considering the suggestions provided to improve your financial health."
    
    def _generate_fallback_response(self, analysis_results: Dict[str, Any], user_query: str) -> str:
        """
        Generate a fallback response when AI generation fails
        
        Args:
            analysis_results: Analysis results from financial services
            user_query: Original user query
            
        Returns:
            Fallback response string
        """
        return f"I've analyzed your financial query: '{user_query}'. While I encountered a technical issue generating a personalized response, I can provide you with the key financial insights from your data. Please review the analysis results for detailed information about your financial situation."
    
    def is_available(self) -> bool:
        """
        Check if the AI service is available
        
        Returns:
            True if AI model is available, False otherwise
        """
        return self.model is not None
    
    def get_model_info(self) -> Dict[str, Any]:
        """
        Get information about the AI model
        
        Returns:
            Dictionary with model information
        """
        return {
            "available": self.is_available(),
            "model_name": "gemini-pro" if self.model else None,
            "provider": "Google Generative AI",
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }
