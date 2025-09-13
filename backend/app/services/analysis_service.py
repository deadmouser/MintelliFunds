"""
Financial analysis service for processing financial data
"""
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import statistics

logger = logging.getLogger(__name__)


class AnalysisService:
    """Service for performing financial analysis on filtered data"""
    
    def __init__(self):
        """Initialize the analysis service"""
        pass
    
    def calculate_spending(self, data: Dict[str, Any], entities: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate spending analysis based on filtered data and entities
        
        Args:
            data: Filtered financial data
            entities: Extracted entities from NLP
            
        Returns:
            Dictionary containing spending analysis results
        """
        try:
            logger.info("Calculating spending analysis")
            
            transactions = data.get("transactions", [])
            if not transactions:
                return {
                    "total_spending": 0.0,
                    "category_breakdown": {},
                    "period": "no_data",
                    "transaction_count": 0,
                    "average_transaction": 0.0,
                    "top_categories": [],
                    "insights": ["No transaction data available"]
                }
            
            # Filter transactions by time period if specified
            filtered_transactions = self._filter_transactions_by_period(transactions, entities)
            
            # Calculate total spending (only expenses)
            expenses = [t for t in filtered_transactions if t.get("amount", 0) < 0]
            total_spending = abs(sum(t.get("amount", 0) for t in expenses))
            
            # Calculate category breakdown
            category_breakdown = self._calculate_category_breakdown(expenses)
            
            # Calculate additional metrics
            transaction_count = len(expenses)
            average_transaction = total_spending / transaction_count if transaction_count > 0 else 0
            
            # Get top spending categories
            top_categories = sorted(
                category_breakdown.items(), 
                key=lambda x: x[1]["amount"], 
                reverse=True
            )[:5]
            
            # Generate insights
            insights = self._generate_spending_insights(
                total_spending, category_breakdown, top_categories, entities
            )
            
            result = {
                "total_spending": round(total_spending, 2),
                "category_breakdown": category_breakdown,
                "period": self._get_analysis_period(entities),
                "transaction_count": transaction_count,
                "average_transaction": round(average_transaction, 2),
                "top_categories": [{"category": cat, "amount": amt["amount"]} for cat, amt in top_categories],
                "insights": insights,
                "raw_data": {
                    "filtered_transactions": len(filtered_transactions),
                    "total_transactions": len(transactions)
                }
            }
            
            logger.info(f"Spending analysis completed - Total: ${total_spending}")
            return result
            
        except Exception as e:
            logger.error(f"Error calculating spending: {str(e)}")
            return {
                "error": str(e),
                "total_spending": 0.0,
                "category_breakdown": {},
                "insights": ["Error calculating spending analysis"]
            }
    
    def project_savings(self, data: Dict[str, Any], entities: Dict[str, Any]) -> Dict[str, Any]:
        """
        Project future savings based on historical data
        
        Args:
            data: Filtered financial data
            entities: Extracted entities from NLP
            
        Returns:
            Dictionary containing savings projection results
        """
        try:
            logger.info("Calculating savings projection")
            
            transactions = data.get("transactions", [])
            accounts = data.get("accounts", [])
            
            if not transactions:
                return {
                    "current_savings": 0.0,
                    "projected_savings": {},
                    "savings_rate": 0.0,
                    "monthly_savings": 0.0,
                    "insights": ["No transaction data available for projection"]
                }
            
            # Calculate current savings from accounts
            current_savings = sum(acc.get("balance", 0) for acc in accounts if acc.get("type") == "savings")
            
            # Calculate historical savings rate
            savings_rate = self._calculate_savings_rate(transactions)
            
            # Calculate monthly income and expenses
            monthly_income = self._calculate_monthly_income(transactions)
            monthly_expenses = self._calculate_monthly_expenses(transactions)
            monthly_savings = monthly_income - monthly_expenses
            
            # Project future savings
            projection_periods = self._get_projection_periods(entities)
            projected_savings = {}
            
            for period, months in projection_periods.items():
                projected_amount = current_savings + (monthly_savings * months)
                projected_savings[period] = {
                    "amount": round(projected_amount, 2),
                    "months": months,
                    "monthly_contribution": round(monthly_savings, 2)
                }
            
            # Generate insights
            insights = self._generate_savings_insights(
                current_savings, monthly_savings, savings_rate, projected_savings
            )
            
            result = {
                "current_savings": round(current_savings, 2),
                "projected_savings": projected_savings,
                "savings_rate": round(savings_rate, 2),
                "monthly_savings": round(monthly_savings, 2),
                "monthly_income": round(monthly_income, 2),
                "monthly_expenses": round(monthly_expenses, 2),
                "insights": insights
            }
            
            logger.info(f"Savings projection completed - Current: ${current_savings}")
            return result
            
        except Exception as e:
            logger.error(f"Error projecting savings: {str(e)}")
            return {
                "error": str(e),
                "current_savings": 0.0,
                "projected_savings": {},
                "insights": ["Error calculating savings projection"]
            }
    
    def check_affordability(self, data: Dict[str, Any], entities: Dict[str, Any]) -> Dict[str, Any]:
        """
        Check if user can afford a specific expense
        
        Args:
            data: Filtered financial data
            entities: Extracted entities from NLP
            
        Returns:
            Dictionary containing affordability analysis results
        """
        try:
            logger.info("Checking affordability")
            
            # Extract target amount from entities
            target_amount = self._extract_target_amount(entities)
            if target_amount is None:
                return {
                    "affordable": False,
                    "target_amount": 0.0,
                    "available_funds": 0.0,
                    "shortfall": 0.0,
                    "insights": ["No target amount specified for affordability check"]
                }
            
            # Get current available funds
            accounts = data.get("accounts", [])
            available_funds = self._calculate_available_funds(accounts)
            
            # Calculate monthly cash flow
            transactions = data.get("transactions", [])
            monthly_income = self._calculate_monthly_income(transactions)
            monthly_expenses = self._calculate_monthly_expenses(transactions)
            monthly_cash_flow = monthly_income - monthly_expenses
            
            # Determine affordability
            is_affordable = available_funds >= target_amount
            shortfall = max(0, target_amount - available_funds)
            
            # Calculate time to save for the expense
            time_to_save = self._calculate_time_to_save(target_amount, available_funds, monthly_cash_flow)
            
            # Generate insights
            insights = self._generate_affordability_insights(
                target_amount, available_funds, monthly_cash_flow, is_affordable, time_to_save
            )
            
            result = {
                "affordable": is_affordable,
                "target_amount": target_amount,
                "available_funds": round(available_funds, 2),
                "shortfall": round(shortfall, 2),
                "monthly_cash_flow": round(monthly_cash_flow, 2),
                "time_to_save": time_to_save,
                "confidence": self._calculate_affordability_confidence(available_funds, monthly_cash_flow),
                "insights": insights
            }
            
            logger.info(f"Affordability check completed - Affordable: {is_affordable}")
            return result
            
        except Exception as e:
            logger.error(f"Error checking affordability: {str(e)}")
            return {
                "error": str(e),
                "affordable": False,
                "insights": ["Error checking affordability"]
            }
    
    def _filter_transactions_by_period(self, transactions: List[Dict], entities: Dict[str, Any]) -> List[Dict]:
        """Filter transactions by time period specified in entities"""
        time_periods = entities.get("time_periods", [])
        if not time_periods:
            return transactions
        
        # For now, return all transactions - in a real implementation,
        # you would filter by actual dates
        return transactions
    
    def _calculate_category_breakdown(self, expenses: List[Dict]) -> Dict[str, Dict[str, Any]]:
        """Calculate spending breakdown by category"""
        category_totals = {}
        
        for expense in expenses:
            category = expense.get("category", "Unknown")
            amount = abs(expense.get("amount", 0))
            
            if category not in category_totals:
                category_totals[category] = {"amount": 0, "count": 0}
            
            category_totals[category]["amount"] += amount
            category_totals[category]["count"] += 1
        
        # Calculate percentages
        total_amount = sum(cat["amount"] for cat in category_totals.values())
        for category_data in category_totals.values():
            category_data["percentage"] = round(
                (category_data["amount"] / total_amount * 100) if total_amount > 0 else 0, 2
            )
        
        return category_totals
    
    def _calculate_savings_rate(self, transactions: List[Dict]) -> float:
        """Calculate historical savings rate"""
        income = sum(t.get("amount", 0) for t in transactions if t.get("amount", 0) > 0)
        expenses = abs(sum(t.get("amount", 0) for t in transactions if t.get("amount", 0) < 0))
        
        if income == 0:
            return 0.0
        
        return ((income - expenses) / income) * 100
    
    def _calculate_monthly_income(self, transactions: List[Dict]) -> float:
        """Calculate average monthly income"""
        income_transactions = [t for t in transactions if t.get("amount", 0) > 0]
        if not income_transactions:
            return 0.0
        
        # Simple calculation - in reality, you'd group by month
        total_income = sum(t.get("amount", 0) for t in income_transactions)
        return total_income / 3  # Assuming 3 months of data
    
    def _calculate_monthly_expenses(self, transactions: List[Dict]) -> float:
        """Calculate average monthly expenses"""
        expense_transactions = [t for t in transactions if t.get("amount", 0) < 0]
        if not expense_transactions:
            return 0.0
        
        # Simple calculation - in reality, you'd group by month
        total_expenses = abs(sum(t.get("amount", 0) for t in expense_transactions))
        return total_expenses / 3  # Assuming 3 months of data
    
    def _get_projection_periods(self, entities: Dict[str, Any]) -> Dict[str, int]:
        """Get projection periods based on entities"""
        time_periods = entities.get("time_periods", [])
        
        if not time_periods:
            return {"1_month": 1, "3_months": 3, "6_months": 6, "1_year": 12}
        
        periods = {}
        for period in time_periods:
            if period.get("type") == "future":
                count = period.get("count", 1)
                period_name = f"{count}_{period['period']}"
                months = count * (1 if period["period"] == "month" else 3 if period["period"] == "quarter" else 12)
                periods[period_name] = months
        
        return periods if periods else {"1_month": 1, "3_months": 3, "6_months": 6, "1_year": 12}
    
    def _extract_target_amount(self, entities: Dict[str, Any]) -> Optional[float]:
        """Extract target amount from entities"""
        amounts = entities.get("amounts", [])
        return amounts[0] if amounts else None
    
    def _calculate_available_funds(self, accounts: List[Dict]) -> float:
        """Calculate total available funds from accounts"""
        return sum(acc.get("balance", 0) for acc in accounts if acc.get("type") in ["checking", "savings"])
    
    def _calculate_time_to_save(self, target_amount: float, available_funds: float, monthly_cash_flow: float) -> Dict[str, Any]:
        """Calculate time needed to save for target amount"""
        shortfall = max(0, target_amount - available_funds)
        
        if monthly_cash_flow <= 0:
            return {"months": float('inf'), "achievable": False}
        
        months_needed = shortfall / monthly_cash_flow
        
        return {
            "months": round(months_needed, 1),
            "achievable": months_needed < 60,  # Consider achievable if less than 5 years
            "years": round(months_needed / 12, 1)
        }
    
    def _calculate_affordability_confidence(self, available_funds: float, monthly_cash_flow: float) -> float:
        """Calculate confidence score for affordability assessment"""
        if available_funds > 0 and monthly_cash_flow > 0:
            return min(1.0, (available_funds + monthly_cash_flow * 3) / 10000)  # Normalize
        return 0.5
    
    def _get_analysis_period(self, entities: Dict[str, Any]) -> str:
        """Get the analysis period from entities"""
        time_periods = entities.get("time_periods", [])
        if time_periods:
            period = time_periods[0]
            return f"{period.get('type', 'current')} {period.get('period', 'month')}"
        return "all_time"
    
    def _generate_spending_insights(self, total_spending: float, category_breakdown: Dict, 
                                  top_categories: List, entities: Dict[str, Any]) -> List[str]:
        """Generate insights for spending analysis"""
        insights = []
        
        if total_spending > 0:
            insights.append(f"Total spending: ${total_spending:,.2f}")
            
            if top_categories:
                top_cat = top_categories[0]
                insights.append(f"Highest spending category: {top_cat[0]} (${top_cat[1]['amount']:,.2f})")
            
            # Spending trend insights
            if total_spending > 3000:
                insights.append("Consider reviewing your spending - total is above average")
            elif total_spending < 1000:
                insights.append("Great job keeping expenses low!")
        
        return insights
    
    def _generate_savings_insights(self, current_savings: float, monthly_savings: float, 
                                 savings_rate: float, projected_savings: Dict) -> List[str]:
        """Generate insights for savings projection"""
        insights = []
        
        insights.append(f"Current savings: ${current_savings:,.2f}")
        insights.append(f"Monthly savings: ${monthly_savings:,.2f}")
        insights.append(f"Savings rate: {savings_rate:.1f}%")
        
        if savings_rate > 20:
            insights.append("Excellent savings rate! You're on track for financial goals")
        elif savings_rate > 10:
            insights.append("Good savings rate, consider increasing if possible")
        else:
            insights.append("Consider increasing your savings rate for better financial security")
        
        return insights
    
    def _generate_affordability_insights(self, target_amount: float, available_funds: float, 
                                       monthly_cash_flow: float, is_affordable: bool, 
                                       time_to_save: Dict) -> List[str]:
        """Generate insights for affordability check"""
        insights = []
        
        insights.append(f"Target amount: ${target_amount:,.2f}")
        insights.append(f"Available funds: ${available_funds:,.2f}")
        
        if is_affordable:
            insights.append("✅ You can afford this purchase right now!")
        else:
            insights.append("❌ You cannot afford this purchase with current funds")
            
            if time_to_save["achievable"]:
                insights.append(f"💡 You could save for this in {time_to_save['months']:.1f} months")
            else:
                insights.append("💡 This purchase may not be financially feasible")
        
        return insights
