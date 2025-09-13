"""
Advanced Financial Analysis Service
Implements comprehensive financial analysis algorithms as per prototype requirements
"""
import math
import statistics
from typing import Dict, Any, List, Tuple, Optional
from datetime import datetime, timedelta, timezone
from collections import defaultdict
import logging

logger = logging.getLogger(__name__)


class FinancialAnalyzer:
    """Advanced financial analysis service with comprehensive algorithms"""
    
    def __init__(self):
        """Initialize the analyzer"""
        self.analysis_cache = {}
        self.risk_profiles = {
            "conservative": {"equity_pct": 30, "debt_pct": 70},
            "moderate": {"equity_pct": 60, "debt_pct": 40},
            "aggressive": {"equity_pct": 80, "debt_pct": 20}
        }
    
    def analyze_spending_patterns(self, transactions: List[Dict[str, Any]], 
                                 timeframe_days: int = 30) -> Dict[str, Any]:
        """
        Comprehensive spending pattern analysis
        
        Args:
            transactions: List of transaction records
            timeframe_days: Analysis timeframe in days
            
        Returns:
            Detailed spending analysis
        """
        try:
            # Filter transactions by timeframe
            cutoff_date = datetime.now(timezone.utc) - timedelta(days=timeframe_days)
            recent_transactions = self._filter_transactions_by_date(transactions, cutoff_date)
            
            # Extract expense transactions
            expenses = [t for t in recent_transactions if self._is_expense(t)]
            
            if not expenses:
                return self._empty_spending_analysis()
            
            # Core calculations
            total_spending = sum(abs(t.get("amount", 0)) for t in expenses)
            daily_average = total_spending / timeframe_days
            transaction_count = len(expenses)
            
            # Category analysis
            category_breakdown = self._analyze_spending_by_category(expenses)
            
            # Trend analysis
            spending_trend = self._calculate_spending_trend(expenses, timeframe_days)
            
            # Anomaly detection
            anomalies = self._detect_spending_anomalies(expenses)
            
            # Insights generation
            insights = self._generate_spending_insights(
                total_spending, daily_average, category_breakdown, spending_trend, anomalies
            )
            
            return {
                "analysis_type": "spending_analysis",
                "timeframe_days": timeframe_days,
                "total_spending": round(total_spending, 2),
                "daily_average": round(daily_average, 2),
                "transaction_count": transaction_count,
                "category_breakdown": category_breakdown,
                "spending_trend": spending_trend,
                "anomalies": anomalies,
                "insights": insights,
                "recommendations": self._generate_spending_recommendations(
                    category_breakdown, spending_trend, anomalies
                ),
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        
        except Exception as e:
            logger.error(f"Error in spending pattern analysis: {e}")
            return {"error": str(e), "analysis_type": "spending_analysis"}
    
    def forecast_future_balance(self, accounts: List[Dict[str, Any]], 
                               transactions: List[Dict[str, Any]], 
                               months_ahead: int = 6) -> Dict[str, Any]:
        """
        Forecast future account balances based on historical patterns
        
        Args:
            accounts: Account information
            transactions: Transaction history
            months_ahead: Number of months to forecast
            
        Returns:
            Balance projection analysis
        """
        try:
            # Current total balance
            current_balance = sum(acc.get("balance", 0) for acc in accounts)
            
            # Calculate monthly cash flow patterns
            monthly_patterns = self._analyze_monthly_cash_flow(transactions, 6)  # Last 6 months
            
            if not monthly_patterns:
                return self._generate_conservative_forecast(current_balance, months_ahead)
            
            # Calculate averages
            avg_income = statistics.mean([month["income"] for month in monthly_patterns])
            avg_expenses = statistics.mean([month["expenses"] for month in monthly_patterns])
            avg_net_flow = avg_income - avg_expenses
            
            # Calculate volatility (standard deviation)
            net_flows = [month["income"] - month["expenses"] for month in monthly_patterns]
            volatility = statistics.stdev(net_flows) if len(net_flows) > 1 else 0
            
            # Generate monthly projections
            projections = []
            projected_balance = current_balance
            
            for month in range(1, months_ahead + 1):
                # Apply trend with confidence intervals
                projected_flow = avg_net_flow
                
                # Account for seasonal variations (simplified)
                seasonal_factor = self._calculate_seasonal_factor(month)
                projected_flow *= seasonal_factor
                
                projected_balance += projected_flow
                
                # Calculate confidence intervals
                confidence_margin = 1.96 * volatility  # 95% confidence interval
                
                projections.append({
                    "month": month,
                    "projected_balance": round(projected_balance, 2),
                    "net_flow": round(projected_flow, 2),
                    "confidence_low": round(projected_balance - confidence_margin, 2),
                    "confidence_high": round(projected_balance + confidence_margin, 2)
                })
            
            # Generate insights
            insights = self._generate_forecast_insights(
                current_balance, projections[-1]["projected_balance"], 
                avg_net_flow, volatility, months_ahead
            )
            
            return {
                "analysis_type": "savings_projection",
                "current_balance": round(current_balance, 2),
                "months_projected": months_ahead,
                "final_projected_balance": projections[-1]["projected_balance"],
                "monthly_projections": projections,
                "historical_patterns": {
                    "average_monthly_income": round(avg_income, 2),
                    "average_monthly_expenses": round(avg_expenses, 2),
                    "average_net_flow": round(avg_net_flow, 2),
                    "volatility": round(volatility, 2)
                },
                "insights": insights,
                "recommendations": self._generate_savings_recommendations(
                    avg_net_flow, volatility, projections
                ),
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error in balance forecasting: {e}")
            return {"error": str(e), "analysis_type": "savings_projection"}
    
    def check_purchase_affordability(self, accounts: List[Dict[str, Any]], 
                                   transactions: List[Dict[str, Any]], 
                                   liabilities: List[Dict[str, Any]],
                                   purchase_amount: float,
                                   target_item: str = "purchase") -> Dict[str, Any]:
        """
        Analyze affordability of a specific purchase
        
        Args:
            accounts: Account information
            transactions: Transaction history
            liabilities: Debt information
            purchase_amount: Amount of the intended purchase
            target_item: Description of the purchase
            
        Returns:
            Affordability analysis
        """
        try:
            # Current financial position
            total_balance = sum(acc.get("balance", 0) for acc in accounts)
            total_debt = sum(liab.get("balance", 0) for liab in liabilities)
            net_worth = total_balance - total_debt
            
            # Monthly cash flow analysis
            monthly_patterns = self._analyze_monthly_cash_flow(transactions, 3)
            avg_monthly_income = statistics.mean([m["income"] for m in monthly_patterns]) if monthly_patterns else 0
            avg_monthly_expenses = statistics.mean([m["expenses"] for m in monthly_patterns]) if monthly_patterns else 0
            monthly_surplus = avg_monthly_income - avg_monthly_expenses
            
            # Calculate affordability metrics
            liquid_available = total_balance * 0.8  # Keep 20% as buffer
            debt_to_income_ratio = (total_debt / (avg_monthly_income * 12)) if avg_monthly_income > 0 else 0
            
            # Emergency fund check (6 months expenses)
            recommended_emergency_fund = avg_monthly_expenses * 6
            current_emergency_fund = max(0, total_balance - purchase_amount)
            
            # Affordability decision matrix
            can_afford_outright = liquid_available >= purchase_amount
            can_afford_comfortably = (liquid_available >= purchase_amount and 
                                    current_emergency_fund >= recommended_emergency_fund)
            
            # Time to save calculation
            months_to_save = 0
            if not can_afford_outright and monthly_surplus > 0:
                shortfall = purchase_amount - liquid_available
                months_to_save = math.ceil(shortfall / monthly_surplus)
            
            # Risk assessment
            risk_level = self._assess_purchase_risk(
                purchase_amount, total_balance, monthly_surplus, debt_to_income_ratio
            )
            
            # Generate insights
            insights = self._generate_affordability_insights(
                can_afford_outright, can_afford_comfortably, risk_level,
                purchase_amount, total_balance, monthly_surplus
            )
            
            return {
                "analysis_type": "affordability_check",
                "target_item": target_item,
                "purchase_amount": round(purchase_amount, 2),
                "can_afford": can_afford_outright,
                "can_afford_comfortably": can_afford_comfortably,
                "financial_position": {
                    "total_balance": round(total_balance, 2),
                    "liquid_available": round(liquid_available, 2),
                    "net_worth": round(net_worth, 2),
                    "monthly_surplus": round(monthly_surplus, 2),
                    "debt_to_income_ratio": round(debt_to_income_ratio * 100, 1)
                },
                "emergency_fund": {
                    "recommended": round(recommended_emergency_fund, 2),
                    "after_purchase": round(current_emergency_fund, 2),
                    "adequate": current_emergency_fund >= recommended_emergency_fund
                },
                "timeline": {
                    "months_to_save": months_to_save,
                    "savings_required": round(max(0, purchase_amount - liquid_available), 2)
                },
                "risk_assessment": {
                    "level": risk_level,
                    "factors": self._get_risk_factors(risk_level, debt_to_income_ratio, monthly_surplus)
                },
                "insights": insights,
                "recommendations": self._generate_purchase_recommendations(
                    can_afford_comfortably, risk_level, months_to_save, target_item
                ),
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error in affordability analysis: {e}")
            return {"error": str(e), "analysis_type": "affordability_check"}
    
    def detect_financial_anomalies(self, transactions: List[Dict[str, Any]], 
                                  threshold_std: float = 2.0) -> Dict[str, Any]:
        """
        Detect unusual transactions and spending patterns
        
        Args:
            transactions: Transaction history
            threshold_std: Standard deviation threshold for anomaly detection
            
        Returns:
            Anomaly detection results
        """
        try:
            # Separate income and expense transactions
            expenses = [t for t in transactions if self._is_expense(t)]
            incomes = [t for t in transactions if not self._is_expense(t)]
            
            # Detect expense anomalies
            expense_anomalies = self._detect_amount_anomalies(expenses, threshold_std)
            
            # Detect income anomalies
            income_anomalies = self._detect_amount_anomalies(incomes, threshold_std)
            
            # Detect frequency anomalies (unusual merchant activity)
            merchant_anomalies = self._detect_merchant_anomalies(expenses)
            
            # Detect category anomalies
            category_anomalies = self._detect_category_anomalies(expenses)
            
            # Time-based anomalies (weekend vs weekday, time of day)
            temporal_anomalies = self._detect_temporal_anomalies(expenses)
            
            all_anomalies = (expense_anomalies + income_anomalies + 
                           merchant_anomalies + category_anomalies + temporal_anomalies)
            
            # Severity scoring
            scored_anomalies = self._score_anomalies(all_anomalies)
            
            # Generate summary
            summary = self._generate_anomaly_summary(scored_anomalies)
            
            return {
                "analysis_type": "anomaly_detection",
                "total_transactions_analyzed": len(transactions),
                "anomalies_detected": len(scored_anomalies),
                "summary": summary,
                "anomalies": scored_anomalies[:20],  # Top 20 anomalies
                "categories": {
                    "high_severity": len([a for a in scored_anomalies if a["severity"] == "high"]),
                    "medium_severity": len([a for a in scored_anomalies if a["severity"] == "medium"]),
                    "low_severity": len([a for a in scored_anomalies if a["severity"] == "low"])
                },
                "recommendations": self._generate_anomaly_recommendations(scored_anomalies),
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error in anomaly detection: {e}")
            return {"error": str(e), "analysis_type": "anomaly_detection"}
    
    def recommend_debt_repayment_strategy(self, liabilities: List[Dict[str, Any]], 
                                        monthly_surplus: float,
                                        strategy_type: str = "avalanche") -> Dict[str, Any]:
        """
        Generate optimal debt repayment strategy
        
        Args:
            liabilities: List of debt information
            monthly_surplus: Available monthly amount for debt repayment
            strategy_type: "avalanche" (highest interest first) or "snowball" (smallest balance first)
            
        Returns:
            Debt repayment strategy
        """
        try:
            if not liabilities or monthly_surplus <= 0:
                return self._empty_debt_strategy()
            
            # Prepare debt list with calculations
            debts = []
            total_minimum_payments = 0
            
            for debt in liabilities:
                balance = debt.get("balance", 0)
                interest_rate = debt.get("interest_rate", 0)
                min_payment = debt.get("monthly_payment", balance * 0.02)  # Default to 2% if not specified
                
                if balance > 0:
                    debts.append({
                        "id": debt.get("id", "unknown"),
                        "name": debt.get("name", "Unknown Debt"),
                        "type": debt.get("type", "other"),
                        "balance": balance,
                        "interest_rate": interest_rate,
                        "minimum_payment": min_payment,
                        "monthly_interest": (balance * interest_rate / 100) / 12
                    })
                    total_minimum_payments += min_payment
            
            if not debts:
                return self._empty_debt_strategy()
            
            # Check if surplus covers minimum payments
            extra_payment = monthly_surplus - total_minimum_payments
            if extra_payment <= 0:
                return self._insufficient_surplus_strategy(debts, monthly_surplus, total_minimum_payments)
            
            # Sort debts based on strategy
            if strategy_type == "avalanche":
                debts.sort(key=lambda x: x["interest_rate"], reverse=True)
            else:  # snowball
                debts.sort(key=lambda x: x["balance"])
            
            # Calculate payoff timeline
            payoff_schedule = self._calculate_debt_payoff_schedule(debts, extra_payment)
            
            # Calculate savings from strategy
            total_interest_saved = self._calculate_interest_savings(debts, payoff_schedule)
            
            # Generate insights
            insights = self._generate_debt_strategy_insights(
                debts, payoff_schedule, total_interest_saved, strategy_type
            )
            
            return {
                "analysis_type": "debt_strategy",
                "strategy_type": strategy_type,
                "monthly_surplus": round(monthly_surplus, 2),
                "total_debt": round(sum(d["balance"] for d in debts), 2),
                "total_minimum_payments": round(total_minimum_payments, 2),
                "extra_payment_available": round(extra_payment, 2),
                "debt_details": debts,
                "payoff_schedule": payoff_schedule,
                "projected_debt_free_date": payoff_schedule[-1]["date"] if payoff_schedule else None,
                "total_months_to_payoff": len(payoff_schedule),
                "total_interest_saved": round(total_interest_saved, 2),
                "insights": insights,
                "recommendations": self._generate_debt_recommendations(
                    strategy_type, payoff_schedule, total_interest_saved
                ),
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error in debt strategy analysis: {e}")
            return {"error": str(e), "analysis_type": "debt_strategy"}
    
    def analyze_investment_portfolio(self, investments: List[Dict[str, Any]], 
                                   risk_profile: str = "moderate") -> Dict[str, Any]:
        """
        Analyze investment portfolio and provide rebalancing recommendations
        
        Args:
            investments: Investment portfolio data
            risk_profile: User's risk profile (conservative, moderate, aggressive)
            
        Returns:
            Portfolio analysis and recommendations
        """
        try:
            if not investments:
                return self._empty_portfolio_analysis()
            
            # Current portfolio analysis
            total_value = sum(inv.get("current_value", 0) for inv in investments)
            
            # Asset allocation analysis
            asset_allocation = self._analyze_asset_allocation(investments, total_value)
            
            # Performance analysis
            performance_metrics = self._analyze_portfolio_performance(investments)
            
            # Risk analysis
            risk_metrics = self._analyze_portfolio_risk(investments, asset_allocation)
            
            # Target allocation based on risk profile
            target_allocation = self.risk_profiles.get(risk_profile, self.risk_profiles["moderate"])
            
            # Rebalancing recommendations
            rebalancing = self._generate_rebalancing_recommendations(
                asset_allocation, target_allocation, total_value
            )
            
            # Diversification analysis
            diversification = self._analyze_diversification(investments, asset_allocation)
            
            # Generate insights
            insights = self._generate_portfolio_insights(
                asset_allocation, performance_metrics, risk_metrics, diversification
            )
            
            return {
                "analysis_type": "portfolio_analysis",
                "total_portfolio_value": round(total_value, 2),
                "risk_profile": risk_profile,
                "current_allocation": asset_allocation,
                "target_allocation": target_allocation,
                "performance_metrics": performance_metrics,
                "risk_metrics": risk_metrics,
                "diversification_score": diversification["score"],
                "rebalancing_recommendations": rebalancing,
                "insights": insights,
                "recommendations": self._generate_investment_recommendations(
                    rebalancing, risk_metrics, diversification
                ),
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error in portfolio analysis: {e}")
            return {"error": str(e), "analysis_type": "portfolio_analysis"}
    
    def calculate_financial_health_score(self, accounts: List[Dict[str, Any]], 
                                       liabilities: List[Dict[str, Any]], 
                                       transactions: List[Dict[str, Any]], 
                                       investments: List[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Calculate comprehensive financial health score
        
        Args:
            accounts: Account information
            liabilities: Debt information
            transactions: Transaction history
            investments: Investment portfolio (optional)
            
        Returns:
            Financial health analysis with score
        """
        try:
            investments = investments or []
            
            # Core financial metrics
            total_assets = sum(acc.get("balance", 0) for acc in accounts)
            total_investments = sum(inv.get("current_value", 0) for inv in investments)
            total_debt = sum(liab.get("balance", 0) for liab in liabilities)
            net_worth = total_assets + total_investments - total_debt
            
            # Monthly cash flow
            monthly_patterns = self._analyze_monthly_cash_flow(transactions, 3)
            avg_monthly_income = statistics.mean([m["income"] for m in monthly_patterns]) if monthly_patterns else 0
            avg_monthly_expenses = statistics.mean([m["expenses"] for m in monthly_patterns]) if monthly_patterns else 0
            monthly_surplus = avg_monthly_income - avg_monthly_expenses
            
            # Calculate individual score components (0-100 each)
            scores = {}
            
            # 1. Liquidity Score (25% weight)
            emergency_fund_months = (total_assets / avg_monthly_expenses) if avg_monthly_expenses > 0 else 0
            scores["liquidity"] = min(100, emergency_fund_months * 16.67)  # 6 months = 100 points
            
            # 2. Debt Management Score (25% weight)
            if avg_monthly_income > 0:
                debt_to_income = (total_debt / (avg_monthly_income * 12))
                scores["debt_management"] = max(0, 100 - (debt_to_income * 200))  # 50% DTI = 0 points
            else:
                scores["debt_management"] = 50  # Neutral score if no income data
            
            # 3. Savings Rate Score (20% weight)
            if avg_monthly_income > 0:
                savings_rate = (monthly_surplus / avg_monthly_income) * 100
                scores["savings_rate"] = min(100, max(0, savings_rate * 5))  # 20% savings rate = 100 points
            else:
                scores["savings_rate"] = 0
            
            # 4. Investment Score (15% weight)
            if total_assets > 0:
                investment_ratio = (total_investments / (total_assets + total_investments)) * 100
                scores["investment"] = min(100, investment_ratio * 2)  # 50% invested = 100 points
            else:
                scores["investment"] = 0
            
            # 5. Net Worth Growth Score (15% weight)
            # Simplified: based on current net worth relative to annual income
            if avg_monthly_income > 0:
                net_worth_ratio = net_worth / (avg_monthly_income * 12)
                scores["net_worth"] = min(100, max(0, net_worth_ratio * 20))  # 5x annual income = 100 points
            else:
                scores["net_worth"] = max(0, min(100, net_worth / 1000))  # Basic score for positive net worth
            
            # Calculate weighted overall score
            weights = {
                "liquidity": 0.25,
                "debt_management": 0.25,
                "savings_rate": 0.20,
                "investment": 0.15,
                "net_worth": 0.15
            }
            
            overall_score = sum(scores[component] * weights[component] for component in scores)
            
            # Determine health category
            if overall_score >= 80:
                health_category = "excellent"
            elif overall_score >= 60:
                health_category = "good"
            elif overall_score >= 40:
                health_category = "fair"
            else:
                health_category = "poor"
            
            # Generate detailed insights
            insights = self._generate_financial_health_insights(
                scores, overall_score, health_category, net_worth, monthly_surplus
            )
            
            return {
                "analysis_type": "financial_health",
                "overall_score": round(overall_score, 1),
                "health_category": health_category,
                "component_scores": {k: round(v, 1) for k, v in scores.items()},
                "financial_metrics": {
                    "net_worth": round(net_worth, 2),
                    "total_assets": round(total_assets, 2),
                    "total_investments": round(total_investments, 2),
                    "total_debt": round(total_debt, 2),
                    "monthly_income": round(avg_monthly_income, 2),
                    "monthly_expenses": round(avg_monthly_expenses, 2),
                    "monthly_surplus": round(monthly_surplus, 2),
                    "emergency_fund_months": round(emergency_fund_months, 1)
                },
                "insights": insights,
                "recommendations": self._generate_health_recommendations(scores, health_category),
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error in financial health calculation: {e}")
            return {"error": str(e), "analysis_type": "financial_health"}
    
    # Helper methods for data processing and calculations
    def _filter_transactions_by_date(self, transactions: List[Dict[str, Any]], 
                                   cutoff_date: datetime) -> List[Dict[str, Any]]:
        """Filter transactions by date"""
        filtered = []
        for t in transactions:
            try:
                trans_date_str = t.get("date", "")
                if trans_date_str:
                    trans_date = datetime.fromisoformat(trans_date_str.replace('Z', '+00:00'))
                    if trans_date >= cutoff_date:
                        filtered.append(t)
            except (ValueError, TypeError):
                continue
        return filtered
    
    def _is_expense(self, transaction: Dict[str, Any]) -> bool:
        """Check if transaction is an expense"""
        return transaction.get("amount", 0) < 0
    
    def _analyze_spending_by_category(self, expenses: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze spending by category"""
        category_totals = defaultdict(float)
        category_counts = defaultdict(int)
        
        for expense in expenses:
            category = expense.get("category", "uncategorized")
            amount = abs(expense.get("amount", 0))
            category_totals[category] += amount
            category_counts[category] += 1
        
        total_spending = sum(category_totals.values())
        
        breakdown = []
        for category, amount in sorted(category_totals.items(), key=lambda x: x[1], reverse=True):
            percentage = (amount / total_spending * 100) if total_spending > 0 else 0
            breakdown.append({
                "category": category,
                "amount": round(amount, 2),
                "percentage": round(percentage, 1),
                "transaction_count": category_counts[category],
                "average_per_transaction": round(amount / category_counts[category], 2)
            })
        
        return {
            "categories": breakdown,
            "top_category": breakdown[0]["category"] if breakdown else None,
            "total_categories": len(breakdown)
        }
    
    def _calculate_spending_trend(self, expenses: List[Dict[str, Any]], 
                                timeframe_days: int) -> Dict[str, Any]:
        """Calculate spending trend over time"""
        if timeframe_days < 14:
            return {"trend": "insufficient_data", "change_percentage": 0}
        
        # Split timeframe in half for comparison
        mid_point = timeframe_days // 2
        cutoff_date = datetime.now(timezone.utc) - timedelta(days=mid_point)
        
        recent_expenses = []
        older_expenses = []
        
        for expense in expenses:
            try:
                expense_date = datetime.fromisoformat(expense.get("date", "").replace('Z', '+00:00'))
                if expense_date >= cutoff_date:
                    recent_expenses.append(expense)
                else:
                    older_expenses.append(expense)
            except (ValueError, TypeError):
                continue
        
        recent_total = sum(abs(e.get("amount", 0)) for e in recent_expenses)
        older_total = sum(abs(e.get("amount", 0)) for e in older_expenses)
        
        # Normalize by days (in case periods aren't exactly equal)
        recent_daily = recent_total / mid_point
        older_daily = older_total / (timeframe_days - mid_point)
        
        if older_daily > 0:
            change_percentage = ((recent_daily - older_daily) / older_daily) * 100
        else:
            change_percentage = 0
        
        if change_percentage > 10:
            trend = "increasing"
        elif change_percentage < -10:
            trend = "decreasing"
        else:
            trend = "stable"
        
        return {
            "trend": trend,
            "change_percentage": round(change_percentage, 1),
            "recent_daily_average": round(recent_daily, 2),
            "older_daily_average": round(older_daily, 2)
        }
    
    def _detect_spending_anomalies(self, expenses: List[Dict[str, Any]], 
                                 threshold_std: float = 2.0) -> List[Dict[str, Any]]:
        """Detect anomalous spending transactions"""
        if len(expenses) < 5:  # Need sufficient data
            return []
        
        amounts = [abs(e.get("amount", 0)) for e in expenses]
        mean_amount = statistics.mean(amounts)
        std_amount = statistics.stdev(amounts) if len(amounts) > 1 else 0
        
        anomalies = []
        for expense in expenses:
            amount = abs(expense.get("amount", 0))
            z_score = (amount - mean_amount) / std_amount if std_amount > 0 else 0
            
            if abs(z_score) > threshold_std:
                anomalies.append({
                    "transaction_id": expense.get("id", "unknown"),
                    "description": expense.get("description", "Unknown"),
                    "amount": amount,
                    "z_score": round(z_score, 2),
                    "date": expense.get("date", ""),
                    "category": expense.get("category", "uncategorized"),
                    "severity": "high" if abs(z_score) > 3 else "medium"
                })
        
        return sorted(anomalies, key=lambda x: abs(x["z_score"]), reverse=True)
    
    def _analyze_monthly_cash_flow(self, transactions: List[Dict[str, Any]], 
                                 months_back: int) -> List[Dict[str, Any]]:
        """Analyze monthly cash flow patterns"""
        monthly_data = defaultdict(lambda: {"income": 0, "expenses": 0})
        
        for transaction in transactions:
            try:
                trans_date = datetime.fromisoformat(transaction.get("date", "").replace('Z', '+00:00'))
                month_key = trans_date.strftime("%Y-%m")
                amount = transaction.get("amount", 0)
                
                if amount > 0:
                    monthly_data[month_key]["income"] += amount
                else:
                    monthly_data[month_key]["expenses"] += abs(amount)
            except (ValueError, TypeError):
                continue
        
        # Get last N months
        result = []
        for month_key in sorted(monthly_data.keys())[-months_back:]:
            data = monthly_data[month_key]
            result.append({
                "month": month_key,
                "income": data["income"],
                "expenses": data["expenses"],
                "net_flow": data["income"] - data["expenses"]
            })
        
        return result
    
    # Import helper functions
    def _calculate_seasonal_factor(self, month: int) -> float:
        """Calculate seasonal adjustment factor"""
        from .financial_analyzer_helpers import FinancialAnalyzerHelpers
        return FinancialAnalyzerHelpers.calculate_seasonal_factor(month)
    
    def _generate_conservative_forecast(self, current_balance: float, months_ahead: int) -> Dict[str, Any]:
        """Generate conservative forecast"""
        from .financial_analyzer_helpers import FinancialAnalyzerHelpers
        return FinancialAnalyzerHelpers.generate_conservative_forecast(current_balance, months_ahead)
    
    def _generate_forecast_insights(self, current_balance: float, final_balance: float,
                                   avg_net_flow: float, volatility: float, months_ahead: int) -> List[str]:
        """Generate forecast insights"""
        from .financial_analyzer_helpers import FinancialAnalyzerHelpers
        return FinancialAnalyzerHelpers.generate_forecast_insights(
            current_balance, final_balance, avg_net_flow, volatility, months_ahead
        )
    
    def _generate_savings_recommendations(self, avg_net_flow: float, volatility: float,
                                        projections: List[Dict[str, Any]]) -> List[str]:
        """Generate savings recommendations"""
        from .financial_analyzer_helpers import FinancialAnalyzerHelpers
        return FinancialAnalyzerHelpers.generate_savings_recommendations(
            avg_net_flow, volatility, projections
        )
    
    def _assess_purchase_risk(self, purchase_amount: float, total_balance: float,
                            monthly_surplus: float, debt_to_income_ratio: float) -> str:
        """Assess purchase risk level"""
        from .financial_analyzer_helpers import FinancialAnalyzerHelpers
        return FinancialAnalyzerHelpers.assess_purchase_risk(
            purchase_amount, total_balance, monthly_surplus, debt_to_income_ratio
        )
    
    def _generate_affordability_insights(self, can_afford_outright: bool, can_afford_comfortably: bool,
                                       risk_level: str, purchase_amount: float,
                                       total_balance: float, monthly_surplus: float) -> List[str]:
        """Generate affordability insights"""
        from .financial_analyzer_helpers import FinancialAnalyzerHelpers
        return FinancialAnalyzerHelpers.generate_affordability_insights(
            can_afford_outright, can_afford_comfortably, risk_level, 
            purchase_amount, total_balance, monthly_surplus
        )
    
    def _get_risk_factors(self, risk_level: str, debt_to_income_ratio: float, 
                         monthly_surplus: float) -> List[str]:
        """Get risk factors"""
        from .financial_analyzer_helpers import FinancialAnalyzerHelpers
        return FinancialAnalyzerHelpers.get_risk_factors(
            risk_level, debt_to_income_ratio, monthly_surplus
        )
    
    def _generate_purchase_recommendations(self, can_afford_comfortably: bool, risk_level: str,
                                         months_to_save: int, target_item: str) -> List[str]:
        """Generate purchase recommendations"""
        from .financial_analyzer_helpers import FinancialAnalyzerHelpers
        return FinancialAnalyzerHelpers.generate_purchase_recommendations(
            can_afford_comfortably, risk_level, months_to_save, target_item
        )
    
    def _detect_amount_anomalies(self, transactions: List[Dict[str, Any]], 
                                threshold_std: float = 2.0) -> List[Dict[str, Any]]:
        """Detect amount anomalies"""
        from .financial_analyzer_helpers import FinancialAnalyzerHelpers
        return FinancialAnalyzerHelpers.detect_amount_anomalies(transactions, threshold_std)
    
    def _detect_merchant_anomalies(self, expenses: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Detect merchant anomalies"""
        from .financial_analyzer_helpers import FinancialAnalyzerHelpers
        return FinancialAnalyzerHelpers.detect_merchant_anomalies(expenses)
    
    def _detect_category_anomalies(self, expenses: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Detect category anomalies"""
        from .financial_analyzer_helpers import FinancialAnalyzerHelpers
        return FinancialAnalyzerHelpers.detect_category_anomalies(expenses)
    
    def _detect_temporal_anomalies(self, expenses: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Detect temporal anomalies"""
        from .financial_analyzer_helpers import FinancialAnalyzerHelpers
        return FinancialAnalyzerHelpers.detect_temporal_anomalies(expenses)
    
    def _score_anomalies(self, anomalies: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Score anomalies"""
        from .financial_analyzer_helpers import FinancialAnalyzerHelpers
        return FinancialAnalyzerHelpers.score_anomalies(anomalies)
    
    def _generate_anomaly_summary(self, anomalies: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate anomaly summary"""
        from .financial_analyzer_helpers import FinancialAnalyzerHelpers
        return FinancialAnalyzerHelpers.generate_anomaly_summary(anomalies)
    
    def _generate_anomaly_recommendations(self, anomalies: List[Dict[str, Any]]) -> List[str]:
        """Generate anomaly recommendations"""
        from .financial_analyzer_helpers import FinancialAnalyzerHelpers
        return FinancialAnalyzerHelpers.generate_anomaly_recommendations(anomalies)
    
    def _empty_debt_strategy(self) -> Dict[str, Any]:
        """Empty debt strategy"""
        from .financial_analyzer_helpers import FinancialAnalyzerHelpers
        return FinancialAnalyzerHelpers.empty_debt_strategy()
    
    def _insufficient_surplus_strategy(self, debts: List[Dict[str, Any]], 
                                     monthly_surplus: float, 
                                     total_minimum_payments: float) -> Dict[str, Any]:
        """Handle insufficient surplus strategy"""
        from .financial_analyzer_helpers import FinancialAnalyzerHelpers
        return FinancialAnalyzerHelpers.insufficient_surplus_strategy(
            debts, monthly_surplus, total_minimum_payments
        )
    
    def _calculate_debt_payoff_schedule(self, debts: List[Dict[str, Any]], 
                                       extra_payment: float) -> List[Dict[str, Any]]:
        """Calculate debt payoff schedule"""
        from .financial_analyzer_helpers import FinancialAnalyzerHelpers
        return FinancialAnalyzerHelpers.calculate_debt_payoff_schedule(debts, extra_payment)
    
    def _calculate_interest_savings(self, debts: List[Dict[str, Any]], 
                                   payoff_schedule: List[Dict[str, Any]]) -> float:
        """Calculate interest savings"""
        from .financial_analyzer_helpers import FinancialAnalyzerHelpers
        return FinancialAnalyzerHelpers.calculate_interest_savings(debts, payoff_schedule)
    
    def _generate_debt_strategy_insights(self, debts: List[Dict[str, Any]], 
                                        payoff_schedule: List[Dict[str, Any]],
                                        interest_saved: float, 
                                        strategy_type: str) -> List[str]:
        """Generate debt strategy insights"""
        from .financial_analyzer_helpers import FinancialAnalyzerHelpers
        return FinancialAnalyzerHelpers.generate_debt_strategy_insights(
            debts, payoff_schedule, interest_saved, strategy_type
        )
    
    def _generate_debt_recommendations(self, strategy_type: str, 
                                      payoff_schedule: List[Dict[str, Any]],
                                      interest_saved: float) -> List[str]:
        """Generate debt recommendations"""
        from .financial_analyzer_helpers import FinancialAnalyzerHelpers
        return FinancialAnalyzerHelpers.generate_debt_recommendations(
            strategy_type, payoff_schedule, interest_saved
        )
    
    # Placeholder methods for investment and portfolio analysis
    # These would be implemented with more sophisticated financial algorithms
    def _empty_portfolio_analysis(self) -> Dict[str, Any]:
        """Return empty portfolio analysis"""
        return {
            "analysis_type": "portfolio_analysis",
            "total_portfolio_value": 0,
            "insights": ["No investment data available for analysis"],
            "recommendations": ["Consider starting an investment portfolio"]
        }
    
    def _analyze_asset_allocation(self, investments: List[Dict[str, Any]], 
                                 total_value: float) -> Dict[str, Any]:
        """Analyze asset allocation"""
        allocation = {"equity": 0, "debt": 0, "other": 0}
        
        for inv in investments:
            asset_type = inv.get("type", "other").lower()
            value = inv.get("current_value", 0)
            
            if "equity" in asset_type or "stock" in asset_type:
                allocation["equity"] += value
            elif "debt" in asset_type or "bond" in asset_type:
                allocation["debt"] += value
            else:
                allocation["other"] += value
        
        # Convert to percentages
        if total_value > 0:
            allocation = {k: (v / total_value) * 100 for k, v in allocation.items()}
        
        return allocation
    
    def _analyze_portfolio_performance(self, investments: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze portfolio performance"""
        total_invested = sum(inv.get("invested_amount", 0) for inv in investments)
        current_value = sum(inv.get("current_value", 0) for inv in investments)
        
        if total_invested > 0:
            returns = ((current_value - total_invested) / total_invested) * 100
        else:
            returns = 0
        
        return {
            "total_invested": round(total_invested, 2),
            "current_value": round(current_value, 2),
            "absolute_returns": round(current_value - total_invested, 2),
            "percentage_returns": round(returns, 2)
        }
    
    def _analyze_portfolio_risk(self, investments: List[Dict[str, Any]], 
                               asset_allocation: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze portfolio risk"""
        # Simplified risk analysis based on asset allocation
        equity_pct = asset_allocation.get("equity", 0)
        
        if equity_pct > 80:
            risk_level = "high"
        elif equity_pct > 50:
            risk_level = "medium"
        else:
            risk_level = "low"
        
        return {
            "risk_level": risk_level,
            "equity_percentage": round(equity_pct, 1),
            "volatility_estimate": "moderate"  # Placeholder
        }
    
    def _generate_rebalancing_recommendations(self, current_allocation: Dict[str, Any], 
                                            target_allocation: Dict[str, Any], 
                                            total_value: float) -> List[Dict[str, Any]]:
        """Generate rebalancing recommendations"""
        recommendations = []
        
        for asset_type, target_pct in target_allocation.items():
            if asset_type.endswith("_pct"):
                asset_key = asset_type.replace("_pct", "")
                current_pct = current_allocation.get(asset_key, 0)
                difference = target_pct - current_pct
                
                if abs(difference) > 5:  # Only recommend if difference > 5%
                    action = "increase" if difference > 0 else "decrease"
                    amount = abs(difference * total_value / 100)
                    
                    recommendations.append({
                        "asset_type": asset_key,
                        "action": action,
                        "target_percentage": target_pct,
                        "current_percentage": round(current_pct, 1),
                        "adjustment_amount": round(amount, 2)
                    })
        
        return recommendations
    
    def _analyze_diversification(self, investments: List[Dict[str, Any]], 
                               asset_allocation: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze portfolio diversification"""
        # Simple diversification score based on number of holdings and allocation spread
        num_holdings = len(investments)
        
        # Calculate concentration (higher concentration = lower diversification)
        max_allocation = max(asset_allocation.values()) if asset_allocation else 0
        
        if num_holdings < 3:
            diversification_score = 30
        elif num_holdings < 10:
            diversification_score = 60
        else:
            diversification_score = 80
        
        # Adjust for concentration
        if max_allocation > 70:
            diversification_score = max(20, diversification_score - 30)
        
        return {
            "score": diversification_score,
            "num_holdings": num_holdings,
            "concentration_risk": "high" if max_allocation > 70 else "moderate" if max_allocation > 50 else "low"
        }
    
    def _generate_portfolio_insights(self, asset_allocation: Dict[str, Any], 
                                   performance_metrics: Dict[str, Any],
                                   risk_metrics: Dict[str, Any], 
                                   diversification: Dict[str, Any]) -> List[str]:
        """Generate portfolio insights"""
        insights = []
        
        # Performance insights
        returns = performance_metrics.get("percentage_returns", 0)
        if returns > 15:
            insights.append(f"Excellent portfolio performance with {returns:.1f}% returns")
        elif returns > 8:
            insights.append(f"Good portfolio performance with {returns:.1f}% returns")
        elif returns > 0:
            insights.append(f"Positive portfolio returns of {returns:.1f}%")
        else:
            insights.append(f"Portfolio showing negative returns of {returns:.1f}%")
        
        # Risk insights
        risk_level = risk_metrics.get("risk_level", "medium")
        equity_pct = risk_metrics.get("equity_percentage", 0)
        insights.append(f"Portfolio risk level: {risk_level} ({equity_pct:.1f}% equity allocation)")
        
        # Diversification insights
        div_score = diversification.get("score", 0)
        if div_score < 40:
            insights.append("Portfolio lacks diversification - consider adding more holdings")
        elif div_score > 70:
            insights.append("Well-diversified portfolio across asset classes")
        
        return insights
    
    def _generate_investment_recommendations(self, rebalancing: List[Dict[str, Any]], 
                                           risk_metrics: Dict[str, Any], 
                                           diversification: Dict[str, Any]) -> List[str]:
        """Generate investment recommendations"""
        recommendations = []
        
        # Rebalancing recommendations
        if rebalancing:
            recommendations.append("Portfolio requires rebalancing to align with target allocation")
            for rebal in rebalancing[:2]:  # Top 2 recommendations
                action = rebal["action"]
                asset = rebal["asset_type"]
                recommendations.append(f"{action.title()} {asset} allocation to {rebal['target_percentage']}%")
        
        # Diversification recommendations
        div_score = diversification.get("score", 0)
        if div_score < 40:
            recommendations.append("Add more diverse holdings to reduce concentration risk")
        
        # Risk-based recommendations
        risk_level = risk_metrics.get("risk_level", "medium")
        if risk_level == "high":
            recommendations.append("Consider reducing equity allocation for better risk management")
        
        return recommendations if recommendations else ["Portfolio allocation appears balanced"]
    
    def _generate_financial_health_insights(self, scores: Dict[str, float], 
                                          overall_score: float, health_category: str,
                                          net_worth: float, monthly_surplus: float) -> List[str]:
        """Generate financial health insights"""
        insights = []
        
        # Overall health insight
        insights.append(f"Your financial health score is {overall_score:.1f}/100 ({health_category})")
        
        # Component-specific insights
        lowest_score = min(scores, key=scores.get)
        highest_score = max(scores, key=scores.get)
        
        insights.append(f"Strongest area: {highest_score.replace('_', ' ').title()} ({scores[highest_score]:.1f}/100)")
        insights.append(f"Area for improvement: {lowest_score.replace('_', ' ').title()} ({scores[lowest_score]:.1f}/100)")
        
        # Net worth insight
        if net_worth > 1000000:
            insights.append("Excellent net worth position")
        elif net_worth > 0:
            insights.append("Positive net worth - continue building wealth")
        else:
            insights.append("Negative net worth - focus on debt reduction")
        
        # Cash flow insight
        if monthly_surplus > 20000:
            insights.append("Strong monthly surplus available for investments")
        elif monthly_surplus > 0:
            insights.append("Positive monthly cash flow supports financial goals")
        else:
            insights.append("Monthly expenses exceed income - budget review needed")
        
        return insights
    
    def _generate_health_recommendations(self, scores: Dict[str, float], 
                                       health_category: str) -> List[str]:
        """Generate financial health recommendations"""
        recommendations = []
        
        # Recommendations based on lowest scores
        if scores.get("liquidity", 0) < 50:
            recommendations.append("Build emergency fund to 6 months of expenses")
        
        if scores.get("debt_management", 0) < 50:
            recommendations.append("Focus on debt reduction to improve debt-to-income ratio")
        
        if scores.get("savings_rate", 0) < 50:
            recommendations.append("Increase monthly savings rate to 15-20% of income")
        
        if scores.get("investment", 0) < 30:
            recommendations.append("Start investing in diversified portfolio for long-term growth")
        
        # Overall recommendations based on health category
        if health_category == "poor":
            recommendations.append("Create a comprehensive financial plan with professional guidance")
        elif health_category == "fair":
            recommendations.append("Focus on improving 2-3 key financial metrics")
        elif health_category == "good":
            recommendations.append("Fine-tune investment strategy and optimize tax planning")
        else:  # excellent
            recommendations.append("Consider advanced wealth management strategies")
        
        return recommendations if recommendations else ["Maintain current financial discipline"]
    
    def _empty_spending_analysis(self) -> Dict[str, Any]:
        """Return empty spending analysis structure"""
        return {
            "analysis_type": "spending_analysis",
            "total_spending": 0,
            "daily_average": 0,
            "transaction_count": 0,
            "insights": ["No spending data available for analysis"],
            "recommendations": []
        }
    
    def _generate_spending_insights(self, total_spending: float, daily_average: float,
                                  category_breakdown: Dict[str, Any], 
                                  spending_trend: Dict[str, Any],
                                  anomalies: List[Dict[str, Any]]) -> List[str]:
        """Generate spending insights"""
        insights = []
        
        # Total spending insight
        if daily_average > 1500:  # Example threshold
            insights.append(f"Your daily spending average of ₹{daily_average:.0f} is above recommended levels")
        
        # Category insights
        if category_breakdown.get("categories"):
            top_category = category_breakdown["categories"][0]
            if top_category["percentage"] > 40:
                insights.append(f"High concentration in {top_category['category']} ({top_category['percentage']:.1f}% of spending)")
        
        # Trend insights
        if spending_trend["trend"] == "increasing":
            insights.append(f"Spending trend is increasing by {spending_trend['change_percentage']:.1f}%")
        
        # Anomaly insights
        if len(anomalies) > 0:
            insights.append(f"Detected {len(anomalies)} unusual transactions requiring attention")
        
        return insights if insights else ["Your spending patterns appear normal"]
    
    def _generate_spending_recommendations(self, category_breakdown: Dict[str, Any],
                                         spending_trend: Dict[str, Any],
                                         anomalies: List[Dict[str, Any]]) -> List[str]:
        """Generate spending recommendations"""
        recommendations = []
        
        # Category-based recommendations
        if category_breakdown.get("categories"):
            top_categories = category_breakdown["categories"][:3]
            for cat in top_categories:
                if cat["percentage"] > 30:
                    recommendations.append(f"Consider reducing {cat['category']} expenses, currently {cat['percentage']:.1f}% of total")
        
        # Trend-based recommendations
        if spending_trend["trend"] == "increasing":
            recommendations.append("Set monthly spending limits to control increasing trend")
        
        # Anomaly-based recommendations
        if anomalies:
            recommendations.append("Review flagged transactions for potential unauthorized charges or overspending")
        
        return recommendations if recommendations else ["Continue monitoring spending patterns"]


# Additional supporting methods would be implemented here...
# This is a comprehensive framework showing the structure and key algorithms