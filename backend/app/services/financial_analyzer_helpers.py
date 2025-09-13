"""
Helper methods for Financial Analyzer
Contains all supporting calculation and utility functions
"""
import math
import statistics
from typing import Dict, Any, List, Tuple, Optional
from datetime import datetime, timedelta, timezone
from collections import defaultdict
import logging

logger = logging.getLogger(__name__)


class FinancialAnalyzerHelpers:
    """Helper methods for financial analysis calculations"""
    
    @staticmethod
    def calculate_seasonal_factor(month: int) -> float:
        """
        Calculate seasonal adjustment factor for cash flow projections
        
        Args:
            month: Month number (1-12)
            
        Returns:
            Seasonal adjustment factor
        """
        # Simplified seasonal factors (Indian context)
        seasonal_factors = {
            1: 0.95,   # January - post-holiday recovery
            2: 1.0,    # February - normal
            3: 1.05,   # March - year-end bonuses
            4: 1.0,    # April - normal
            5: 0.98,   # May - summer spending
            6: 0.97,   # June - summer spending
            7: 1.02,   # July - monsoon preparations
            8: 1.0,    # August - normal
            9: 1.05,   # September - festival season begins
            10: 1.1,   # October - festival peak (Diwali season)
            11: 1.08,  # November - continued festivities
            12: 0.92   # December - year-end savings
        }
        
        # Use modulo to handle projection beyond 12 months
        month_index = ((month - 1) % 12) + 1
        return seasonal_factors.get(month_index, 1.0)
    
    @staticmethod
    def generate_conservative_forecast(current_balance: float, 
                                     months_ahead: int) -> Dict[str, Any]:
        """
        Generate conservative forecast when insufficient historical data
        
        Args:
            current_balance: Current account balance
            months_ahead: Number of months to forecast
            
        Returns:
            Conservative forecast structure
        """
        # Assume minimal growth (0.5% monthly for savings accounts)
        monthly_growth_rate = 0.005
        projections = []
        
        projected_balance = current_balance
        for month in range(1, months_ahead + 1):
            projected_balance *= (1 + monthly_growth_rate)
            projections.append({
                "month": month,
                "projected_balance": round(projected_balance, 2),
                "net_flow": round(projected_balance - current_balance, 2),
                "confidence_low": round(projected_balance * 0.95, 2),
                "confidence_high": round(projected_balance * 1.05, 2)
            })
        
        return {
            "analysis_type": "savings_projection",
            "current_balance": round(current_balance, 2),
            "months_projected": months_ahead,
            "final_projected_balance": projections[-1]["projected_balance"],
            "monthly_projections": projections,
            "historical_patterns": {
                "note": "Insufficient historical data - using conservative estimates"
            },
            "insights": ["Forecast based on conservative estimates due to limited transaction history"],
            "recommendations": ["Continue tracking expenses to improve forecast accuracy"],
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    
    @staticmethod
    def generate_forecast_insights(current_balance: float, final_balance: float,
                                 avg_net_flow: float, volatility: float,
                                 months_ahead: int) -> List[str]:
        """Generate insights for balance forecasting"""
        insights = []
        
        # Growth analysis
        total_growth = final_balance - current_balance
        monthly_growth_rate = (total_growth / current_balance / months_ahead) * 100 if current_balance > 0 else 0
        
        if total_growth > 0:
            insights.append(f"Projected growth of ₹{total_growth:,.0f} over {months_ahead} months")
            if monthly_growth_rate > 5:
                insights.append("Strong positive cash flow trend detected")
        else:
            insights.append(f"Projected decline of ₹{abs(total_growth):,.0f} - review spending patterns")
        
        # Volatility analysis
        if volatility > abs(avg_net_flow) * 0.5:
            insights.append("High cash flow volatility detected - consider budgeting strategies")
        
        # Net flow analysis
        if avg_net_flow < 0:
            insights.append("Monthly expenses exceed income on average - budget adjustments needed")
        elif avg_net_flow > current_balance * 0.1:
            insights.append("Excellent savings rate - consider investment opportunities")
        
        return insights
    
    @staticmethod
    def generate_savings_recommendations(avg_net_flow: float, volatility: float,
                                       projections: List[Dict[str, Any]]) -> List[str]:
        """Generate savings recommendations"""
        recommendations = []
        
        if avg_net_flow < 0:
            recommendations.append("Create a budget to reduce monthly expenses below income")
            recommendations.append("Track discretionary spending to identify cost-cutting opportunities")
        elif avg_net_flow < 10000:  # Less than ₹10k monthly surplus
            recommendations.append("Aim to increase monthly surplus through income growth or expense reduction")
        
        if volatility > 15000:  # High volatility
            recommendations.append("Build emergency fund to handle cash flow fluctuations")
            recommendations.append("Consider smoothing irregular income through better planning")
        
        # Check for declining trend in projections
        if len(projections) >= 3:
            recent_trend = projections[-1]["projected_balance"] - projections[-3]["projected_balance"]
            if recent_trend < 0:
                recommendations.append("Address declining balance trend through budget review")
        
        return recommendations if recommendations else [
            "Maintain current savings discipline",
            "Consider investment options for surplus funds"
        ]
    
    @staticmethod
    def assess_purchase_risk(purchase_amount: float, total_balance: float,
                           monthly_surplus: float, debt_to_income_ratio: float) -> str:
        """Assess risk level for a purchase"""
        risk_score = 0
        
        # Balance impact (40% of score)
        balance_impact = purchase_amount / total_balance if total_balance > 0 else 1
        if balance_impact > 0.8:
            risk_score += 40
        elif balance_impact > 0.5:
            risk_score += 25
        elif balance_impact > 0.3:
            risk_score += 10
        
        # Monthly surplus impact (30% of score)
        if monthly_surplus <= 0:
            risk_score += 30
        elif purchase_amount > monthly_surplus * 6:  # More than 6 months of surplus
            risk_score += 20
        elif purchase_amount > monthly_surplus * 3:  # More than 3 months of surplus
            risk_score += 10
        
        # Debt situation (30% of score)
        if debt_to_income_ratio > 0.4:  # High debt
            risk_score += 30
        elif debt_to_income_ratio > 0.2:  # Moderate debt
            risk_score += 15
        
        # Determine risk level
        if risk_score >= 60:
            return "high"
        elif risk_score >= 30:
            return "medium"
        else:
            return "low"
    
    @staticmethod
    def generate_affordability_insights(can_afford_outright: bool, can_afford_comfortably: bool,
                                      risk_level: str, purchase_amount: float,
                                      total_balance: float, monthly_surplus: float) -> List[str]:
        """Generate affordability insights"""
        insights = []
        
        if can_afford_comfortably:
            insights.append("Purchase can be made without compromising financial stability")
            if monthly_surplus > purchase_amount * 0.2:
                insights.append("Strong cash flow supports this purchase decision")
        elif can_afford_outright:
            insights.append("Purchase is technically affordable but may impact emergency fund")
            if risk_level == "high":
                insights.append("High risk due to limited remaining liquidity")
        else:
            insights.append("Purchase exceeds current liquid assets")
            months_to_save = math.ceil(purchase_amount / max(monthly_surplus, 1))
            insights.append(f"Would require {months_to_save} months of current surplus to afford")
        
        # Balance impact insight
        balance_impact_pct = (purchase_amount / total_balance) * 100 if total_balance > 0 else 100
        if balance_impact_pct > 50:
            insights.append(f"Purchase would consume {balance_impact_pct:.1f}% of total balance")
        
        return insights
    
    @staticmethod
    def get_risk_factors(risk_level: str, debt_to_income_ratio: float, 
                        monthly_surplus: float) -> List[str]:
        """Get risk factors for purchase decision"""
        factors = []
        
        if risk_level == "high":
            factors.append("High impact on liquidity")
            if debt_to_income_ratio > 0.3:
                factors.append("Existing high debt levels")
            if monthly_surplus <= 0:
                factors.append("Negative or minimal cash flow")
        elif risk_level == "medium":
            factors.append("Moderate impact on financial flexibility")
            if debt_to_income_ratio > 0.2:
                factors.append("Moderate existing debt")
        else:
            factors.append("Low financial impact")
            factors.append("Adequate liquidity buffer maintained")
        
        return factors
    
    @staticmethod
    def generate_purchase_recommendations(can_afford_comfortably: bool, risk_level: str,
                                        months_to_save: int, target_item: str) -> List[str]:
        """Generate purchase recommendations"""
        recommendations = []
        
        if can_afford_comfortably:
            recommendations.append(f"Proceed with {target_item} purchase")
            recommendations.append("Consider timing purchase with upcoming income")
        elif risk_level == "low":
            recommendations.append("Purchase is feasible with minor impact")
            recommendations.append("Ensure emergency fund remains adequate")
        elif risk_level == "medium":
            recommendations.append("Consider delaying purchase to improve financial position")
            recommendations.append("Evaluate if this is a need vs. want")
        else:  # high risk
            recommendations.append("Strongly advise postponing this purchase")
            recommendations.append("Focus on improving cash flow and reducing debt first")
            
        if months_to_save > 0:
            recommendations.append(f"Alternative: Save for {months_to_save} months to afford comfortably")
            
        return recommendations
    
    @staticmethod
    def detect_amount_anomalies(transactions: List[Dict[str, Any]], 
                               threshold_std: float = 2.0) -> List[Dict[str, Any]]:
        """Detect anomalous transaction amounts"""
        if len(transactions) < 5:
            return []
        
        amounts = [abs(t.get("amount", 0)) for t in transactions]
        if not amounts:
            return []
            
        mean_amount = statistics.mean(amounts)
        std_amount = statistics.stdev(amounts) if len(amounts) > 1 else 0
        
        anomalies = []
        for transaction in transactions:
            amount = abs(transaction.get("amount", 0))
            z_score = (amount - mean_amount) / std_amount if std_amount > 0 else 0
            
            if abs(z_score) > threshold_std:
                anomalies.append({
                    "transaction_id": transaction.get("id", "unknown"),
                    "description": transaction.get("description", "Unknown"),
                    "amount": amount,
                    "z_score": round(z_score, 2),
                    "date": transaction.get("date", ""),
                    "category": transaction.get("category", "uncategorized"),
                    "type": "amount_anomaly",
                    "severity": "high" if abs(z_score) > 3 else "medium"
                })
        
        return anomalies
    
    @staticmethod
    def detect_merchant_anomalies(expenses: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Detect unusual merchant activity patterns"""
        merchant_counts = defaultdict(int)
        merchant_amounts = defaultdict(list)
        
        for expense in expenses:
            merchant = expense.get("merchant", expense.get("description", "Unknown"))
            amount = abs(expense.get("amount", 0))
            merchant_counts[merchant] += 1
            merchant_amounts[merchant].append(amount)
        
        anomalies = []
        
        # Detect merchants with unusually high frequency
        if merchant_counts:
            avg_frequency = statistics.mean(merchant_counts.values())
            std_frequency = statistics.stdev(merchant_counts.values()) if len(merchant_counts) > 1 else 0
            
            for merchant, count in merchant_counts.items():
                if std_frequency > 0:
                    z_score = (count - avg_frequency) / std_frequency
                    if z_score > 2:  # Unusually high frequency
                        avg_amount = statistics.mean(merchant_amounts[merchant])
                        anomalies.append({
                            "merchant": merchant,
                            "transaction_count": count,
                            "average_amount": round(avg_amount, 2),
                            "total_amount": round(sum(merchant_amounts[merchant]), 2),
                            "z_score": round(z_score, 2),
                            "type": "merchant_frequency_anomaly",
                            "severity": "medium",
                            "description": f"Unusually high activity with {merchant}"
                        })
        
        return anomalies[:10]  # Limit to top 10
    
    @staticmethod
    def detect_category_anomalies(expenses: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Detect unusual spending patterns by category"""
        category_monthly = defaultdict(lambda: defaultdict(float))
        
        # Group expenses by category and month
        for expense in expenses:
            try:
                date = datetime.fromisoformat(expense.get("date", "").replace('Z', '+00:00'))
                month_key = date.strftime("%Y-%m")
                category = expense.get("category", "uncategorized")
                amount = abs(expense.get("amount", 0))
                category_monthly[category][month_key] += amount
            except (ValueError, TypeError):
                continue
        
        anomalies = []
        
        for category, monthly_data in category_monthly.items():
            if len(monthly_data) < 2:  # Need at least 2 months for comparison
                continue
                
            amounts = list(monthly_data.values())
            if len(amounts) > 1:
                mean_amount = statistics.mean(amounts)
                std_amount = statistics.stdev(amounts)
                
                # Find months with unusual spending
                for month, amount in monthly_data.items():
                    if std_amount > 0:
                        z_score = (amount - mean_amount) / std_amount
                        if abs(z_score) > 1.5:  # Less strict threshold for monthly patterns
                            anomalies.append({
                                "category": category,
                                "month": month,
                                "amount": round(amount, 2),
                                "average_amount": round(mean_amount, 2),
                                "z_score": round(z_score, 2),
                                "type": "category_spending_anomaly",
                                "severity": "low",
                                "description": f"Unusual {category} spending in {month}"
                            })
        
        return sorted(anomalies, key=lambda x: abs(x["z_score"]), reverse=True)[:10]
    
    @staticmethod
    def detect_temporal_anomalies(expenses: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Detect time-based spending anomalies"""
        weekend_amounts = []
        weekday_amounts = []
        night_amounts = []  # After 10 PM or before 6 AM
        day_amounts = []
        
        for expense in expenses:
            try:
                date = datetime.fromisoformat(expense.get("date", "").replace('Z', '+00:00'))
                amount = abs(expense.get("amount", 0))
                
                # Weekend vs weekday
                if date.weekday() >= 5:  # Saturday = 5, Sunday = 6
                    weekend_amounts.append(amount)
                else:
                    weekday_amounts.append(amount)
                
                # Night vs day (simplified - using hour if available)
                hour = date.hour
                if hour >= 22 or hour < 6:  # 10 PM to 6 AM
                    night_amounts.append((expense, amount))
                else:
                    day_amounts.append(amount)
                    
            except (ValueError, TypeError):
                continue
        
        anomalies = []
        
        # Check for unusual night spending
        if night_amounts and len(night_amounts) > len(day_amounts) * 0.3:  # More than 30% night spending
            total_night = sum(amt for _, amt in night_amounts)
            anomalies.append({
                "type": "temporal_anomaly",
                "pattern": "high_night_spending",
                "night_transaction_count": len(night_amounts),
                "total_night_amount": round(total_night, 2),
                "severity": "medium",
                "description": "Unusually high nighttime spending detected"
            })
        
        return anomalies
    
    @staticmethod
    def score_anomalies(anomalies: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Score and rank anomalies by importance"""
        for anomaly in anomalies:
            base_score = 0
            
            # Score based on type
            if anomaly.get("type") == "amount_anomaly":
                z_score = abs(anomaly.get("z_score", 0))
                base_score = min(100, z_score * 15)  # Max 100 points
            elif anomaly.get("type") == "merchant_frequency_anomaly":
                base_score = 60
            elif anomaly.get("type") == "category_spending_anomaly":
                base_score = 40
            elif anomaly.get("type") == "temporal_anomaly":
                base_score = 30
            
            # Adjust based on severity
            severity = anomaly.get("severity", "medium")
            if severity == "high":
                base_score *= 1.2
            elif severity == "low":
                base_score *= 0.8
            
            anomaly["score"] = round(base_score, 1)
        
        # Sort by score (highest first)
        return sorted(anomalies, key=lambda x: x.get("score", 0), reverse=True)
    
    @staticmethod
    def generate_anomaly_summary(anomalies: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate summary of detected anomalies"""
        if not anomalies:
            return {
                "total_anomalies": 0,
                "risk_level": "low",
                "primary_concern": "none"
            }
        
        high_severity = len([a for a in anomalies if a.get("severity") == "high"])
        medium_severity = len([a for a in anomalies if a.get("severity") == "medium"])
        
        # Determine overall risk
        if high_severity > 3:
            risk_level = "high"
            primary_concern = "multiple_high_risk_anomalies"
        elif high_severity > 0 or medium_severity > 5:
            risk_level = "medium" 
            primary_concern = "notable_anomalies_detected"
        else:
            risk_level = "low"
            primary_concern = "minor_irregularities"
        
        return {
            "total_anomalies": len(anomalies),
            "risk_level": risk_level,
            "primary_concern": primary_concern,
            "high_severity_count": high_severity,
            "medium_severity_count": medium_severity
        }
    
    @staticmethod
    def generate_anomaly_recommendations(anomalies: List[Dict[str, Any]]) -> List[str]:
        """Generate recommendations based on detected anomalies"""
        if not anomalies:
            return ["No anomalies detected - transaction patterns appear normal"]
        
        recommendations = []
        
        high_severity = [a for a in anomalies if a.get("severity") == "high"]
        amount_anomalies = [a for a in anomalies if a.get("type") == "amount_anomaly"]
        merchant_anomalies = [a for a in anomalies if a.get("type") == "merchant_frequency_anomaly"]
        
        if high_severity:
            recommendations.append("Review high-severity anomalies immediately for potential fraud")
        
        if amount_anomalies:
            recommendations.append("Verify large or unusual transaction amounts")
        
        if merchant_anomalies:
            recommendations.append("Check for recurring charges or subscriptions")
        
        if len(anomalies) > 10:
            recommendations.append("Consider reviewing transaction categorization and budgeting")
        
        recommendations.append("Set up transaction alerts for unusual activity")
        
        return recommendations
    
    @staticmethod
    def empty_debt_strategy() -> Dict[str, Any]:
        """Return empty debt strategy structure"""
        return {
            "analysis_type": "debt_strategy",
            "total_debt": 0,
            "insights": ["No debt data available for analysis"],
            "recommendations": ["Maintain current debt-free status"]
        }
    
    @staticmethod
    def insufficient_surplus_strategy(debts: List[Dict[str, Any]], 
                                    monthly_surplus: float,
                                    total_minimum_payments: float) -> Dict[str, Any]:
        """Handle case where surplus doesn't cover minimum payments"""
        shortfall = total_minimum_payments - monthly_surplus
        
        return {
            "analysis_type": "debt_strategy",
            "monthly_surplus": round(monthly_surplus, 2),
            "total_debt": round(sum(d["balance"] for d in debts), 2),
            "total_minimum_payments": round(total_minimum_payments, 2),
            "shortfall": round(shortfall, 2),
            "insights": [
                "Current surplus insufficient to cover minimum debt payments",
                f"Need additional ₹{shortfall:,.0f} monthly to meet obligations"
            ],
            "recommendations": [
                "Focus on increasing income or reducing expenses",
                "Contact creditors to discuss payment restructuring",
                "Consider debt consolidation options",
                "Seek financial counseling assistance"
            ],
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    
    @staticmethod
    def calculate_debt_payoff_schedule(debts: List[Dict[str, Any]], 
                                     extra_payment: float) -> List[Dict[str, Any]]:
        """Calculate debt payoff schedule using debt avalanche/snowball strategy"""
        schedule = []
        remaining_debts = [debt.copy() for debt in debts]  # Don't modify original
        month = 0
        remaining_extra = extra_payment
        
        while any(debt["balance"] > 0 for debt in remaining_debts) and month < 600:  # Max 50 years
            month += 1
            current_date = datetime.now() + timedelta(days=30 * month)
            
            # Apply minimum payments to all debts
            total_paid_this_month = 0
            for debt in remaining_debts:
                if debt["balance"] > 0:
                    min_payment = min(debt["minimum_payment"], debt["balance"])
                    debt["balance"] -= min_payment
                    total_paid_this_month += min_payment
            
            # Apply extra payment to first debt in sorted order
            if remaining_extra > 0:
                for debt in remaining_debts:
                    if debt["balance"] > 0:
                        extra_applied = min(remaining_extra, debt["balance"])
                        debt["balance"] -= extra_applied
                        total_paid_this_month += extra_applied
                        break
            
            # Record this month's progress
            remaining_balance = sum(debt["balance"] for debt in remaining_debts)
            schedule.append({
                "month": month,
                "date": current_date.strftime("%Y-%m"),
                "total_payment": round(total_paid_this_month, 2),
                "remaining_balance": round(remaining_balance, 2),
                "debts_remaining": len([d for d in remaining_debts if d["balance"] > 0])
            })
            
            if remaining_balance <= 0:
                break
        
        return schedule
    
    @staticmethod
    def calculate_interest_savings(debts: List[Dict[str, Any]], 
                                 payoff_schedule: List[Dict[str, Any]]) -> float:
        """Calculate interest savings from accelerated payoff strategy"""
        # Simplified calculation - estimate interest saved vs minimum payments only
        total_debt = sum(debt["balance"] for debt in debts)
        avg_interest_rate = statistics.mean([debt["interest_rate"] for debt in debts if debt["interest_rate"] > 0])
        
        if not payoff_schedule or avg_interest_rate <= 0:
            return 0
        
        # Estimate interest with strategy
        months_to_payoff = len(payoff_schedule)
        strategy_interest = total_debt * (avg_interest_rate / 100) * (months_to_payoff / 12) * 0.5  # Rough estimate
        
        # Estimate interest with minimum payments only (rough calculation)
        min_payment_months = total_debt / sum(debt.get("minimum_payment", 0) for debt in debts) if sum(debt.get("minimum_payment", 0) for debt in debts) > 0 else 120
        minimum_only_interest = total_debt * (avg_interest_rate / 100) * (min_payment_months / 12) * 0.7
        
        return max(0, minimum_only_interest - strategy_interest)
    
    @staticmethod
    def generate_debt_strategy_insights(debts: List[Dict[str, Any]], 
                                      payoff_schedule: List[Dict[str, Any]],
                                      interest_saved: float, 
                                      strategy_type: str) -> List[str]:
        """Generate insights for debt repayment strategy"""
        insights = []
        
        if payoff_schedule:
            months_to_freedom = len(payoff_schedule)
            years = months_to_freedom // 12
            months = months_to_freedom % 12
            
            if years > 0:
                insights.append(f"Debt-free in {years} years, {months} months using {strategy_type} method")
            else:
                insights.append(f"Debt-free in {months} months using {strategy_type} method")
        
        if interest_saved > 0:
            insights.append(f"Save approximately ₹{interest_saved:,.0f} in interest payments")
        
        # Analyze debt composition
        high_interest_debts = [d for d in debts if d.get("interest_rate", 0) > 15]
        if high_interest_debts:
            insights.append(f"{len(high_interest_debts)} high-interest debts require immediate attention")
        
        total_debt = sum(debt["balance"] for debt in debts)
        if total_debt > 500000:  # ₹5 lakh
            insights.append("Consider debt consolidation for better management")
        
        return insights
    
    @staticmethod
    def generate_debt_recommendations(strategy_type: str, 
                                    payoff_schedule: List[Dict[str, Any]],
                                    interest_saved: float) -> List[str]:
        """Generate debt repayment recommendations"""
        recommendations = []
        
        recommendations.append(f"Follow {strategy_type} strategy for optimal debt payoff")
        
        if interest_saved > 10000:  # Significant savings
            recommendations.append("Maintain extra payments to maximize interest savings")
        
        if payoff_schedule and len(payoff_schedule) > 36:  # More than 3 years
            recommendations.append("Consider increasing monthly payment to accelerate payoff")
        
        recommendations.extend([
            "Avoid taking on additional debt during payoff period",
            "Set up automatic payments to ensure consistency",
            "Review progress monthly and adjust strategy as needed"
        ])
        
        return recommendations


# Additional specialized helper functions can be added here as needed
# This provides a comprehensive foundation for all financial analysis calculations