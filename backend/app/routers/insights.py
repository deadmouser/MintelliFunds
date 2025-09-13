"""
API router for financial insights endpoint
"""
from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any
import logging
from datetime import datetime

from ..models.requests import InsightsRequest, InsightsResponse, Permissions
from ..services.data_service import DataService
from ..services.privacy_service import PrivacyService
from ..services.nlp_service import NLPService
from ..services.analysis_service import AnalysisService
from ..services.ai_service import AIService

logger = logging.getLogger(__name__)

# Create router instance
router = APIRouter(prefix="/api", tags=["insights"])

# Initialize services
data_service = DataService()
privacy_service = PrivacyService()
nlp_service = NLPService()
analysis_service = AnalysisService()
ai_service = AIService()


@router.post("/insights", response_model=InsightsResponse)
async def get_financial_insights(request: InsightsRequest) -> InsightsResponse:
    """
    Get financial insights based on user query and permissions
    
    This endpoint processes natural language queries about financial data,
    performs NLP analysis, runs financial analysis, and returns results
    based on user permissions for privacy.
    
    Args:
        request: InsightsRequest containing user query and permissions
        
    Returns:
        InsightsResponse with analysis results and filtered data
        
    Raises:
        HTTPException: If there's an error processing the request
    """
    try:
        logger.info(f"Processing insights request for query: '{request.query[:50]}...'")
        
        # Validate permissions
        if not privacy_service.validate_permissions(request.permissions):
            raise HTTPException(
                status_code=400,
                detail="Invalid permissions structure"
            )
        
        # Process the natural language query
        logger.info("Processing natural language query...")
        nlp_result = nlp_service.process_query(request.query)
        intent = nlp_result.get("intent", "unknown")
        entities = nlp_result.get("entities", {})
        
        logger.info(f"Intent classified as: {intent}")
        logger.info(f"Entities extracted: {len(entities)} types")
        
        # Load all financial data
        logger.info("Loading financial data...")
        all_data = data_service.load_all_data()
        
        # Validate data structure
        if not data_service.validate_data_structure(all_data):
            raise HTTPException(
                status_code=500,
                detail="Invalid data structure in source files"
            )
        
        # Filter data based on permissions
        logger.info("Filtering data based on permissions...")
        filtered_data = privacy_service.filter_data_by_permissions(
            all_data, 
            request.permissions
        )
        
        # Perform financial analysis based on intent
        logger.info(f"Performing analysis for intent: {intent}")
        analysis_result = await _perform_financial_analysis(intent, filtered_data, entities)
        
        # Generate AI response from analysis results
        logger.info("Generating AI response from analysis results")
        ai_response = ai_service.generate_response(analysis_result, request.query)
        
        # Get permission summary for logging
        permission_summary = privacy_service.get_permission_summary(request.permissions)
        access_level = privacy_service.get_data_access_level(request.permissions)
        
        logger.info(f"Data access level: {access_level}")
        logger.info(f"Granted access to {permission_summary['granted_count']} data categories")
        logger.info(f"AI response generated: {len(ai_response)} characters")
        
        # Create response with AI-generated content
        response_data = {
            "ai_response": ai_response,
            "intent": intent,
            "analysis_type": analysis_result.get("analysis_type", "unknown"),
            "confidence": nlp_result.get("confidence", {}),
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "ai_available": ai_service.is_available()
        }
        
        # Create response
        response = InsightsResponse(
            query=request.query,
            filtered_data=response_data,
            timestamp=datetime.utcnow().isoformat() + "Z",
            status="success"
        )
        
        logger.info("Insights request processed successfully")
        return response
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"Unexpected error processing insights request: {str(e)}")
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
            # Try advanced spending analysis first
            try:
                if analysis_service.has_advanced_features:
                    user_id = "default_user"  # In real app, get from auth
                    timeframe_days = entities.get("time_periods", [{}])[0].get("days", 30)
                    advanced_result = await analysis_service.get_advanced_spending_analysis(
                        user_id, filtered_data.get("transactions", []), timeframe_days
                    )
                    analysis_result["results"] = advanced_result
                else:
                    analysis_result["results"] = analysis_service.calculate_spending(filtered_data, entities)
            except Exception as e:
                logger.warning(f"Advanced spending analysis failed: {e}")
                analysis_result["results"] = analysis_service.calculate_spending(filtered_data, entities)
            analysis_result["success"] = True
            
        elif intent == "project_future_balance" or intent == "get_savings_analysis":
            analysis_result["analysis_type"] = "savings_projection"
            # Try advanced balance forecasting first
            try:
                if analysis_service.has_advanced_features:
                    user_id = "default_user"  # In real app, get from auth
                    months_ahead = entities.get("time_periods", [{}])[0].get("months", 6)
                    advanced_result = await analysis_service.get_balance_forecast(
                        user_id,
                        filtered_data.get("accounts", []),
                        filtered_data.get("transactions", []),
                        months_ahead
                    )
                    analysis_result["results"] = advanced_result
                else:
                    analysis_result["results"] = analysis_service.project_savings(filtered_data, entities)
            except Exception as e:
                logger.warning(f"Advanced balance forecast failed: {e}")
                analysis_result["results"] = analysis_service.project_savings(filtered_data, entities)
            analysis_result["success"] = True
            
        elif intent == "check_affordability":
            analysis_result["analysis_type"] = "affordability_check"
            # Try advanced affordability analysis first
            try:
                if analysis_service.has_advanced_features:
                    user_id = "default_user"  # In real app, get from auth
                    # Extract purchase amount from entities
                    amounts = entities.get("amounts", [])
                    if amounts:
                        purchase_amount = amounts[0]
                        target_item = entities.get("items", ["purchase"])[0]
                        advanced_result = await analysis_service.analyze_purchase_affordability(
                            user_id,
                            filtered_data.get("accounts", []),
                            filtered_data.get("transactions", []),
                            filtered_data.get("liabilities", []),
                            purchase_amount,
                            target_item
                        )
                        analysis_result["results"] = advanced_result
                    else:
                        analysis_result["results"] = analysis_service.check_affordability(filtered_data, entities)
                else:
                    analysis_result["results"] = analysis_service.check_affordability(filtered_data, entities)
            except Exception as e:
                logger.warning(f"Advanced affordability analysis failed: {e}")
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
            # Try advanced financial health analysis first
            try:
                if analysis_service.has_advanced_features:
                    user_id = "default_user"  # In real app, get from auth
                    advanced_result = await analysis_service.get_financial_health_score(
                        user_id,
                        filtered_data.get("accounts", []),
                        filtered_data.get("liabilities", []),
                        filtered_data.get("transactions", []),
                        filtered_data.get("investments", [])
                    )
                    analysis_result["results"] = advanced_result
                else:
                    analysis_result["results"] = _analyze_financial_health(filtered_data, entities)
            except Exception as e:
                logger.warning(f"Advanced financial health analysis failed: {e}")
                analysis_result["results"] = _analyze_financial_health(filtered_data, entities)
            analysis_result["success"] = True
            
        else:
            # Default to spending analysis for unknown intents
            analysis_result["analysis_type"] = "spending_analysis"
            analysis_result["results"] = analysis_service.calculate_spending(filtered_data, entities)
            analysis_result["success"] = True
            analysis_result["note"] = "Unknown intent, defaulting to spending analysis"
        
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


@router.get("/health")
async def health_check() -> Dict[str, Any]:
    """
    Health check endpoint to verify the API is running
    
    Returns:
        Dictionary with health status information
    """
    try:
        # Test data loading
        data_summary = data_service.get_data_summary()
        
        # Check AI service status
        ai_info = ai_service.get_model_info()
        
        return {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "data_categories_loaded": len(data_summary),
            "data_summary": data_summary,
            "ai_service": ai_info
        }
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        raise HTTPException(
            status_code=503,
            detail=f"Service unhealthy: {str(e)}"
        )


@router.get("/ai/status")
async def ai_status() -> Dict[str, Any]:
    """
    Check AI service status and configuration
    
    Returns:
        Dictionary with AI service information
    """
    try:
        ai_info = ai_service.get_model_info()
        return {
            "ai_service": ai_info,
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }
    except Exception as e:
        logger.error(f"AI status check failed: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"AI status check failed: {str(e)}"
        )


@router.get("/data/summary")
async def get_data_summary() -> Dict[str, Any]:
    """
    Get a summary of available financial data
    
    Returns:
        Dictionary with data summary information
    """
    try:
        data_summary = data_service.get_data_summary()
        return {
            "data_summary": data_summary,
            "total_categories": len(data_summary),
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }
    except Exception as e:
        logger.error(f"Error getting data summary: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get data summary: {str(e)}"
        )


@router.post("/analysis/anomalies")
async def detect_anomalies(request: InsightsRequest) -> Dict[str, Any]:
    """
    Detect financial anomalies in transaction data
    """
    try:
        logger.info("Detecting financial anomalies")
        
        # Load and filter data
        all_data = data_service.load_all_data()
        filtered_data = privacy_service.filter_data_by_permissions(all_data, request.permissions)
        
        # Use advanced anomaly detection if available
        if analysis_service.has_advanced_features:
            user_id = "default_user"  # In real app, get from auth
            result = await analysis_service.detect_anomalies(
                user_id, filtered_data.get("transactions", [])
            )
        else:
            result = {"error": "Advanced anomaly detection not available", "anomalies": []}
        
        return {
            "anomaly_analysis": result,
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }
        
    except Exception as e:
        logger.error(f"Error detecting anomalies: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.post("/analysis/debt-strategy")
async def get_debt_strategy(request: InsightsRequest) -> Dict[str, Any]:
    """
    Get optimal debt repayment strategy
    """
    try:
        logger.info("Analyzing debt repayment strategy")
        
        # Load and filter data
        all_data = data_service.load_all_data()
        filtered_data = privacy_service.filter_data_by_permissions(all_data, request.permissions)
        
        # Use advanced debt strategy analysis if available
        if analysis_service.has_advanced_features:
            user_id = "default_user"  # In real app, get from auth
            # Extract strategy type from query (avalanche or snowball)
            strategy_type = "avalanche"  # Default
            if "snowball" in request.query.lower():
                strategy_type = "snowball"
            
            # Try to use suggest_debt_strategy method
            try:
                result = await analysis_service.suggest_debt_strategy(
                    user_id,
                    filtered_data.get("liabilities", []),
                    filtered_data.get("transactions", []),
                    strategy_type
                )
            except AttributeError:
                # Method doesn't exist, fall back to basic analysis
                result = _analyze_debt(filtered_data, {})
        else:
            result = _analyze_debt(filtered_data, {})
        
        return {
            "debt_strategy": result,
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }
        
    except Exception as e:
        logger.error(f"Error analyzing debt strategy: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.post("/analysis/portfolio")
async def analyze_portfolio(request: InsightsRequest) -> Dict[str, Any]:
    """
    Analyze investment portfolio allocation and performance
    """
    try:
        logger.info("Analyzing investment portfolio")
        
        # Load and filter data
        all_data = data_service.load_all_data()
        filtered_data = privacy_service.filter_data_by_permissions(all_data, request.permissions)
        
        # Use advanced portfolio analysis if available
        if analysis_service.has_advanced_features:
            user_id = "default_user"  # In real app, get from auth
            # Extract risk profile from query
            risk_profile = "moderate"  # Default
            if "conservative" in request.query.lower():
                risk_profile = "conservative"
            elif "aggressive" in request.query.lower():
                risk_profile = "aggressive"
            
            # Try to use analyze_investment_portfolio method
            try:
                result = await analysis_service.analyze_investment_portfolio(
                    user_id,
                    filtered_data.get("investments", []),
                    risk_profile
                )
            except AttributeError:
                # Method doesn't exist, fall back to basic analysis
                result = _analyze_investments(filtered_data, {})
        else:
            result = _analyze_investments(filtered_data, {})
        
        return {
            "portfolio_analysis": result,
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }
        
    except Exception as e:
        logger.error(f"Error analyzing portfolio: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.post("/analysis/budget")
async def analyze_budget(request: InsightsRequest, budget_data: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    Analyze budget performance against actual spending
    """
    try:
        logger.info("Analyzing budget performance")
        
        # Load and filter data
        all_data = data_service.load_all_data()
        filtered_data = privacy_service.filter_data_by_permissions(all_data, request.permissions)
        
        # Create a sample budget if none provided
        if not budget_data:
            budget_data = {
                "month": datetime.now().strftime("%Y-%m"),
                "categories": {
                    "food": 15000,
                    "transportation": 8000,
                    "entertainment": 5000,
                    "utilities": 3000,
                    "shopping": 10000
                }
            }
        
        # Use advanced budget analysis if available
        if analysis_service.has_advanced_features:
            user_id = "default_user"  # In real app, get from auth
            # Try to use analyze_budget_performance method
            try:
                result = await analysis_service.analyze_budget_performance(
                    user_id,
                    filtered_data.get("transactions", []),
                    budget_data
                )
            except AttributeError:
                # Method doesn't exist, fall back to basic analysis
                result = _analyze_spending_vs_budget(filtered_data, budget_data)
        else:
            result = _analyze_spending_vs_budget(filtered_data, budget_data)
        
        return {
            "budget_analysis": result,
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }
        
    except Exception as e:
        logger.error(f"Error analyzing budget: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


def _analyze_spending_vs_budget(filtered_data: Dict[str, Any], budget_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Basic budget vs spending analysis fallback
    """
    transactions = filtered_data.get("transactions", [])
    budget_month = budget_data.get("month", datetime.now().strftime("%Y-%m"))
    budget_categories = budget_data.get("categories", {})
    
    # Filter transactions for the budget month
    month_transactions = [
        t for t in transactions 
        if t.get("date", "").startswith(budget_month) and t.get("amount", 0) < 0
    ]
    
    # Calculate spending by category
    spending_by_category = {}
    for transaction in month_transactions:
        category = transaction.get("category", "other")
        amount = abs(transaction.get("amount", 0))
        if category in spending_by_category:
            spending_by_category[category] += amount
        else:
            spending_by_category[category] = amount
    
    # Compare with budget
    results = []
    total_budget = sum(budget_categories.values())
    total_spent = sum(spending_by_category.values())
    
    for category, budget_amount in budget_categories.items():
        spent = spending_by_category.get(category, 0)
        percentage = (spent / budget_amount * 100) if budget_amount > 0 else 0
        status = "over" if percentage > 100 else "on_track"
        
        results.append({
            "category": category,
            "budget": budget_amount,
            "spent": round(spent, 2),
            "percentage": round(percentage, 1),
            "status": status
        })
    
    return {
        "budget_period": budget_month,
        "total_budget": total_budget,
        "total_spent": round(total_spent, 2),
        "overall_percentage": round((total_spent / total_budget * 100) if total_budget > 0 else 0, 1),
        "categories": results,
        "insights": [
            f"Total spending: ₹{total_spent:,.2f} vs budget: ₹{total_budget:,.2f}",
            f"Overall budget usage: {(total_spent / total_budget * 100) if total_budget > 0 else 0:.1f}%"
        ]
    }


@router.post("/insights/generate")
async def generate_insights(
    permissions: Permissions = Depends(lambda: Permissions(
        transactions=True, accounts=True, assets=True, liabilities=True,
        epf_balance=True, credit_score=True, investments=True,
        spending_trends=True, category_breakdown=True, dashboard_insights=True
    ))
) -> Dict[str, Any]:
    """
    Generate AI insights for the dashboard
    
    Args:
        permissions: User's data access permissions
        
    Returns:
        Dictionary containing generated insights
    """
    try:
        logger.info("Generating AI insights")
        
        # Load and filter data
        all_data = data_service.load_all_data()
        filtered_data = privacy_service.filter_data_by_permissions(all_data, permissions)
        
        # Generate insights using AI service
        mock_analysis = {
            "intent": "get_financial_health",
            "analysis_type": "financial_health",
            "results": _analyze_financial_health(filtered_data, {}),
            "success": True
        }
        
        ai_response = ai_service.generate_response(mock_analysis, "Generate financial insights for my dashboard")
        
        return {
            "insights": [
                {
                    "id": "1",
                    "type": "AI Insight",
                    "text": ai_response
                }
            ],
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }
        
    except Exception as e:
        logger.error(f"Error generating insights: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )
