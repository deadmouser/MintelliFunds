"""
API router for AI chat endpoints
"""
from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any, List, Optional
import logging
from datetime import datetime

from ..models.requests import Permissions
from ..services.data_service import DataService
from ..services.privacy_service import PrivacyService
from ..services.nlp_service import NLPService
from ..services.analysis_service import AnalysisService
from ..services.ai_service import AIService

logger = logging.getLogger(__name__)

# Create router instance
router = APIRouter(prefix="/api", tags=["chat"])

# Initialize services
data_service = DataService()
privacy_service = PrivacyService()
nlp_service = NLPService()
analysis_service = AnalysisService()
ai_service = AIService()

# In-memory chat history (in production, this would be stored in a database)
chat_history = []


def get_default_permissions() -> Permissions:
    """Get default permissions for testing (all enabled)"""
    return Permissions(
        transactions=True,
        accounts=True,
        assets=True,
        liabilities=True,
        epf_balance=True,
        credit_score=True,
        investments=True,
        spending_trends=True,
        category_breakdown=True,
        dashboard_insights=True
    )


@router.post("/chat")
async def send_chat_message(
    request_data: Dict[str, Any],
    permissions: Permissions = Depends(get_default_permissions)
) -> Dict[str, Any]:
    """
    Send a chat message and get AI response
    
    Args:
        request_data: Dictionary containing message and context
        permissions: User's data access permissions
        
    Returns:
        Dictionary containing AI response and chat metadata
    """
    try:
        message = request_data.get("message", "")
        context = request_data.get("context", {})
        
        if not message.strip():
            raise HTTPException(
                status_code=400,
                detail="Message cannot be empty"
            )
        
        logger.info(f"Processing chat message: {message[:50]}...")
        
        # Process the message with NLP
        nlp_result = nlp_service.process_query(message)
        intent = nlp_result.get("intent", "unknown")
        entities = nlp_result.get("entities", {})
        
        logger.info(f"Chat intent: {intent}")
        
        # Load and filter data based on permissions
        all_data = data_service.load_all_data()
        filtered_data = privacy_service.filter_data_by_permissions(all_data, permissions)
        
        # Perform analysis based on intent
        analysis_result = await _perform_financial_analysis(intent, filtered_data, entities)
        
        # Generate AI response
        ai_response = ai_service.generate_response(analysis_result, message)
        
        # Create chat entry
        chat_entry = {
            "id": f"chat_{datetime.utcnow().timestamp()}",
            "user_message": message,
            "ai_response": ai_response,
            "intent": intent,
            "analysis_type": analysis_result.get("analysis_type", "unknown"),
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "context": context
        }
        
        # Add to chat history
        chat_history.append(chat_entry)
        
        # Keep only last 100 messages
        if len(chat_history) > 100:
            chat_history.pop(0)
        
        logger.info(f"Chat response generated: {len(ai_response)} characters")
        
        return {
            "response": ai_response,
            "chat_id": chat_entry["id"],
            "intent": intent,
            "analysis_type": analysis_result.get("analysis_type", "unknown"),
            "confidence": nlp_result.get("confidence", {}),
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing chat message: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )


@router.get("/chat/history")
async def get_chat_history(
    limit: int = 50,
    permissions: Permissions = Depends(get_default_permissions)
) -> Dict[str, Any]:
    """
    Get chat history
    
    Args:
        limit: Maximum number of chat messages to return
        permissions: User's data access permissions
        
    Returns:
        Dictionary containing chat history
    """
    try:
        logger.info(f"Fetching chat history (limit: {limit})")
        
        # Get recent chat messages
        recent_messages = chat_history[-limit:] if chat_history else []
        
        return {
            "messages": recent_messages,
            "total_messages": len(chat_history),
            "limit": limit,
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }
        
    except Exception as e:
        logger.error(f"Error fetching chat history: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )


@router.delete("/chat/history")
async def clear_chat_history(
    permissions: Permissions = Depends(get_default_permissions)
) -> Dict[str, Any]:
    """
    Clear chat history
    
    Args:
        permissions: User's data access permissions
        
    Returns:
        Dictionary containing confirmation
    """
    try:
        logger.info("Clearing chat history")
        
        # Clear chat history
        global chat_history
        chat_history.clear()
        
        return {
            "message": "Chat history cleared successfully",
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }
        
    except Exception as e:
        logger.error(f"Error clearing chat history: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )


async def _perform_financial_analysis(intent: str, filtered_data: Dict[str, Any], entities: Dict[str, Any]) -> Dict[str, Any]:
    """
    Perform financial analysis based on intent and filtered data
    
    Args:
        intent: The classified intent from NLP
        filtered_data: Financial data filtered by permissions
        entities: Extracted entities from NLP
        
    Returns:
        Dictionary containing analysis results
    """
    try:
        analysis_result = {
            "intent": intent,
            "analysis_type": "unknown",
            "results": {},
            "success": False,
            "error": None
        }
        
        if intent == "get_spending_summary" or intent == "get_spending_by_category":
            analysis_result["analysis_type"] = "spending_analysis"
            analysis_result["results"] = analysis_service.calculate_spending(filtered_data, entities)
            analysis_result["success"] = True
            
        elif intent == "project_future_balance" or intent == "get_savings_analysis":
            analysis_result["analysis_type"] = "savings_projection"
            analysis_result["results"] = analysis_service.project_savings(filtered_data, entities)
            analysis_result["success"] = True
            
        elif intent == "check_affordability":
            analysis_result["analysis_type"] = "affordability_check"
            analysis_result["results"] = analysis_service.check_affordability(filtered_data, entities)
            analysis_result["success"] = True
            
        elif intent == "get_income_summary":
            analysis_result["analysis_type"] = "income_analysis"
            analysis_result["results"] = _analyze_income(filtered_data, entities)
            analysis_result["success"] = True
            
        elif intent == "get_debt_analysis":
            analysis_result["analysis_type"] = "debt_analysis"
            analysis_result["results"] = _analyze_debt(filtered_data, entities)
            analysis_result["success"] = True
            
        elif intent == "get_investment_summary":
            analysis_result["analysis_type"] = "investment_analysis"
            analysis_result["results"] = _analyze_investments(filtered_data, entities)
            analysis_result["success"] = True
            
        elif intent == "get_financial_health":
            analysis_result["analysis_type"] = "financial_health"
            analysis_result["results"] = _analyze_financial_health(filtered_data, entities)
            analysis_result["success"] = True
            
        else:
            # Default to general financial overview
            analysis_result["analysis_type"] = "general_overview"
            analysis_result["results"] = _analyze_general_overview(filtered_data, entities)
            analysis_result["success"] = True
            analysis_result["note"] = "General financial overview provided"
        
        return analysis_result
        
    except Exception as e:
        logger.error(f"Error performing financial analysis: {str(e)}")
        return {
            "intent": intent,
            "analysis_type": "error",
            "results": {},
            "success": False,
            "error": str(e)
        }


def _analyze_income(filtered_data: Dict[str, Any], entities: Dict[str, Any]) -> Dict[str, Any]:
    """Analyze income data"""
    transactions = filtered_data.get("transactions", [])
    income_transactions = [t for t in transactions if t.get("amount", 0) > 0]
    
    total_income = sum(t.get("amount", 0) for t in income_transactions)
    monthly_income = total_income / 3 if total_income > 0 else 0  # Assuming 3 months of data
    
    return {
        "total_income": round(total_income, 2),
        "monthly_income": round(monthly_income, 2),
        "transaction_count": len(income_transactions),
        "insights": [f"Total income: ${total_income:,.2f}", f"Monthly average: ${monthly_income:,.2f}"]
    }


def _analyze_debt(filtered_data: Dict[str, Any], entities: Dict[str, Any]) -> Dict[str, Any]:
    """Analyze debt data"""
    liabilities = filtered_data.get("liabilities", [])
    
    total_debt = sum(liab.get("balance", 0) for liab in liabilities)
    monthly_payments = sum(liab.get("monthly_payment", 0) for liab in liabilities)
    
    return {
        "total_debt": round(total_debt, 2),
        "monthly_payments": round(monthly_payments, 2),
        "debt_count": len(liabilities),
        "insights": [f"Total debt: ${total_debt:,.2f}", f"Monthly payments: ${monthly_payments:,.2f}"]
    }


def _analyze_investments(filtered_data: Dict[str, Any], entities: Dict[str, Any]) -> Dict[str, Any]:
    """Analyze investment data"""
    investments = filtered_data.get("investments", [])
    
    total_value = sum(inv.get("total_value", 0) for inv in investments)
    investment_count = len(investments)
    
    return {
        "total_value": round(total_value, 2),
        "investment_count": investment_count,
        "insights": [f"Total investment value: ${total_value:,.2f}", f"Number of investments: {investment_count}"]
    }


def _analyze_financial_health(filtered_data: Dict[str, Any], entities: Dict[str, Any]) -> Dict[str, Any]:
    """Analyze overall financial health"""
    # Get basic metrics
    accounts = filtered_data.get("accounts", [])
    liabilities = filtered_data.get("liabilities", [])
    transactions = filtered_data.get("transactions", [])
    
    # Calculate net worth
    total_assets = sum(acc.get("balance", 0) for acc in accounts)
    total_debt = sum(liab.get("balance", 0) for liab in liabilities)
    net_worth = total_assets - total_debt
    
    # Calculate savings rate
    income = sum(t.get("amount", 0) for t in transactions if t.get("amount", 0) > 0)
    expenses = abs(sum(t.get("amount", 0) for t in transactions if t.get("amount", 0) < 0))
    savings_rate = ((income - expenses) / income * 100) if income > 0 else 0
    
    # Generate health score
    health_score = min(100, max(0, (net_worth / 10000) * 20 + savings_rate))
    
    return {
        "net_worth": round(net_worth, 2),
        "total_assets": round(total_assets, 2),
        "total_debt": round(total_debt, 2),
        "savings_rate": round(savings_rate, 2),
        "health_score": round(health_score, 1),
        "insights": [
            f"Net worth: ${net_worth:,.2f}",
            f"Savings rate: {savings_rate:.1f}%",
            f"Financial health score: {health_score:.1f}/100"
        ]
    }


def _analyze_general_overview(filtered_data: Dict[str, Any], entities: Dict[str, Any]) -> Dict[str, Any]:
    """Provide a general financial overview"""
    accounts = filtered_data.get("accounts", [])
    transactions = filtered_data.get("transactions", [])
    investments = filtered_data.get("investments", [])
    
    total_balance = sum(acc.get("balance", 0) for acc in accounts)
    total_investments = sum(inv.get("total_value", 0) for inv in investments)
    
    return {
        "total_balance": round(total_balance, 2),
        "total_investments": round(total_investments, 2),
        "account_count": len(accounts),
        "investment_count": len(investments),
        "insights": [
            f"Total balance: ${total_balance:,.2f}",
            f"Total investments: ${total_investments:,.2f}",
            f"Accounts: {len(accounts)}, Investments: {len(investments)}"
        ]
    }
