"""
AI-Powered Financial Insights Engine

This module provides comprehensive financial analysis capabilities including:
- Savings prediction and forecasting
- Spending anomaly detection
- Investment recommendations
- Debt optimization strategies
- Risk assessment
- Personalized financial advice
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime, timedelta
import json
from dataclasses import dataclass, asdict
from loguru import logger
from model import FinancialAdvisorModel, FinancialInsightGenerator
from data_preprocessing import UserPermissions, AdvancedDataPreprocessor
import torch

@dataclass
class FinancialGoal:
    """Represents a financial goal"""
    name: str
    target_amount: float
    current_amount: float
    target_date: datetime
    priority: int  # 1-10, 10 being highest
    category: str  # 'emergency', 'investment', 'purchase', 'retirement'

@dataclass
class SpendingPattern:
    """Represents spending pattern analysis"""
    category: str
    average_monthly: float
    trend: str  # 'increasing', 'decreasing', 'stable'
    variance: float
    anomaly_score: float

@dataclass
class InvestmentOpportunity:
    """Represents an investment opportunity"""
    type: str
    expected_return: float
    risk_level: str
    minimum_investment: float
    time_horizon: str
    description: str

class AdvancedInsightsEngine:
    """Advanced AI-powered financial insights engine"""
    
    def __init__(self, model_path: Optional[str] = None):
        """Initialize the insights engine"""
        self.model = FinancialAdvisorModel()
        self.insight_generator = FinancialInsightGenerator(self.model)
        self.preprocessor = AdvancedDataPreprocessor()
        
        if model_path:
            self.load_model(model_path)
            logger.info(f"Model loaded from {model_path}")
        
        # Initialize financial knowledge base
        self._init_knowledge_base()
    
    def _init_knowledge_base(self):
        """Initialize financial knowledge and rules"""
        self.financial_rules = {
            'emergency_fund_months': 6,
            'max_debt_to_income': 0.36,
            'min_savings_rate': 0.20,
            'max_housing_cost_ratio': 0.28,
            'retirement_savings_rate': 0.15,
            'high_yield_savings_threshold': 0.02
        }
        
        self.investment_categories = {
            'conservative': {'risk': 'low', 'expected_return': 0.04, 'volatility': 0.05},
            'moderate': {'risk': 'medium', 'expected_return': 0.07, 'volatility': 0.12},
            'aggressive': {'risk': 'high', 'expected_return': 0.10, 'volatility': 0.20}
        }
        
        self.debt_strategies = {
            'avalanche': {
                'description': 'Pay minimums on all debts, extra on highest interest rate',
                'best_for': 'Mathematically optimal, saves most on interest'
            },
            'snowball': {
                'description': 'Pay minimums on all debts, extra on smallest balance',
                'best_for': 'Psychological wins, builds momentum'
            },
            'hybrid': {
                'description': 'Combination of avalanche and snowball methods',
                'best_for': 'Balance between optimal savings and motivation'
            }
        }
    
    def generate_comprehensive_analysis(self, 
                                      financial_data: Dict[str, Any], 
                                      permissions: UserPermissions,
                                      goals: Optional[List[FinancialGoal]] = None) -> Dict[str, Any]:
        """Generate comprehensive financial analysis"""
        
        logger.info("Starting comprehensive financial analysis")
        
        # Generate base insights using the model
        base_insights = self.insight_generator.generate_comprehensive_insights(financial_data)
        
        # Enhance with advanced analysis
        enhanced_insights = {
            'base_analysis': base_insights,
            'advanced_analysis': self._generate_advanced_insights(financial_data, permissions),
            'goal_analysis': self._analyze_financial_goals(financial_data, goals) if goals else None,
            'spending_patterns': self._analyze_spending_patterns(financial_data),
            'investment_opportunities': self._identify_investment_opportunities(financial_data),
            'debt_optimization': self._optimize_debt_strategy(financial_data),
            'cash_flow_forecast': self._forecast_cash_flow(financial_data),
            'risk_assessment': self._comprehensive_risk_assessment(financial_data),
            'personalized_recommendations': self._generate_personalized_recommendations(financial_data),
            'action_plan': self._create_action_plan(financial_data, goals)
        }
        
        logger.info("Comprehensive financial analysis completed")
        return enhanced_insights
    
    def _generate_advanced_insights(self, financial_data: Dict[str, Any], permissions: UserPermissions) -> Dict[str, Any]:
        """Generate advanced insights beyond basic model predictions"""
        
        insights = {}
        
        # Financial health score
        insights['financial_health_score'] = self._calculate_financial_health_score(financial_data)
        
        # Net worth analysis
        insights['net_worth_analysis'] = self._analyze_net_worth(financial_data)
        
        # Cash flow analysis
        insights['cash_flow_analysis'] = self._analyze_cash_flow(financial_data)
        
        # Budget recommendations
        insights['budget_recommendations'] = self._generate_budget_recommendations(financial_data)
        
        # Tax optimization suggestions
        insights['tax_optimization'] = self._suggest_tax_optimizations(financial_data)
        
        return insights
    
    def _calculate_financial_health_score(self, financial_data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate overall financial health score (0-100)"""
        
        score_components = {}
        
        # Emergency fund score (0-25)
        assets = financial_data.get('assets', {})
        expenses = financial_data.get('transactions', {}).get('expenses', 0)
        liquid_assets = assets.get('cash', 0) + assets.get('bank_balances', 0)
        
        if expenses > 0:
            emergency_months = liquid_assets / expenses
            emergency_score = min(25, (emergency_months / 6) * 25)
        else:
            emergency_score = 0
        score_components['emergency_fund'] = emergency_score
        
        # Debt-to-income score (0-25)
        liabilities = financial_data.get('liabilities', {})
        total_debt = sum(liabilities.values())
        income = financial_data.get('transactions', {}).get('income', 0)
        
        if income > 0:
            debt_ratio = total_debt / (income * 12)  # Annual debt to income
            debt_score = max(0, 25 - (debt_ratio * 100))  # Lower debt = higher score
        else:
            debt_score = 0
        score_components['debt_management'] = debt_score
        
        # Savings rate score (0-25)
        if income > 0:
            savings_rate = (income - expenses) / income
            savings_score = min(25, (savings_rate / 0.20) * 25)  # 20% target
        else:
            savings_score = 0
        score_components['savings_rate'] = savings_score
        
        # Investment diversification score (0-25)
        investments = financial_data.get('investments', {})
        total_investments = sum(investments.values())
        
        if total_investments > 0:
            # Calculate diversification using entropy
            proportions = [v/total_investments for v in investments.values() if v > 0]
            if len(proportions) > 1:
                entropy = -sum(p * np.log(p) for p in proportions)
                max_entropy = np.log(len(proportions))
                diversification_score = (entropy / max_entropy) * 25
            else:
                diversification_score = 5  # Single investment type
        else:
            diversification_score = 0
        score_components['investment_diversification'] = diversification_score
        
        total_score = sum(score_components.values())
        
        # Determine health level
        if total_score >= 80:
            health_level = "Excellent"
        elif total_score >= 60:
            health_level = "Good"
        elif total_score >= 40:
            health_level = "Fair"
        else:
            health_level = "Needs Improvement"
        
        return {
            'total_score': total_score,
            'health_level': health_level,
            'components': score_components,
            'max_score': 100
        }
    
    def _analyze_net_worth(self, financial_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze net worth components and trends"""
        
        assets = financial_data.get('assets', {})
        liabilities = financial_data.get('liabilities', {})
        investments = financial_data.get('investments', {})
        
        total_assets = sum(assets.values()) + sum(investments.values())
        total_liabilities = sum(liabilities.values())
        net_worth = total_assets - total_liabilities
        
        # Asset allocation
        asset_breakdown = {
            'liquid_assets': assets.get('cash', 0) + assets.get('bank_balances', 0),
            'real_estate': assets.get('property', 0),
            'investments': sum(investments.values()),
            'total_assets': total_assets
        }
        
        # Liability breakdown
        liability_breakdown = {
            'secured_debt': liabilities.get('loans', 0),  # Assuming loans are secured
            'unsecured_debt': liabilities.get('credit_card_debt', 0),
            'total_liabilities': total_liabilities
        }
        
        # Net worth analysis
        income = financial_data.get('transactions', {}).get('income', 0)
        net_worth_to_income_ratio = net_worth / (income * 12) if income > 0 else 0
        
        return {
            'net_worth': net_worth,
            'total_assets': total_assets,
            'total_liabilities': total_liabilities,
            'asset_breakdown': asset_breakdown,
            'liability_breakdown': liability_breakdown,
            'net_worth_to_income_ratio': net_worth_to_income_ratio,
            'liquidity_ratio': asset_breakdown['liquid_assets'] / total_assets if total_assets > 0 else 0
        }
    
    def _analyze_cash_flow(self, financial_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze current cash flow situation"""
        
        transactions = financial_data.get('transactions', {})
        income = transactions.get('income', 0)
        expenses = transactions.get('expenses', 0)
        transfers = transactions.get('transfers', 0)
        
        net_cash_flow = income - expenses - transfers
        
        # Cash flow ratios
        expense_ratio = expenses / income if income > 0 else 1
        savings_rate = net_cash_flow / income if income > 0 else 0
        
        # Cash flow health
        if savings_rate >= 0.20:
            cash_flow_health = "Excellent"
        elif savings_rate >= 0.10:
            cash_flow_health = "Good"
        elif savings_rate >= 0:
            cash_flow_health = "Fair"
        else:
            cash_flow_health = "Poor"
        
        return {
            'monthly_income': income,
            'monthly_expenses': expenses,
            'monthly_transfers': transfers,
            'net_cash_flow': net_cash_flow,
            'expense_ratio': expense_ratio,
            'savings_rate': savings_rate,
            'cash_flow_health': cash_flow_health,
            'recommended_emergency_fund': expenses * 6
        }
    
    def _generate_budget_recommendations(self, financial_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate budget recommendations based on 50/30/20 rule and individual situation"""
        
        income = financial_data.get('transactions', {}).get('income', 0)
        expenses = financial_data.get('transactions', {}).get('expenses', 0)
        
        # 50/30/20 budget allocation
        needs_budget = income * 0.50  # Necessities
        wants_budget = income * 0.30  # Discretionary spending
        savings_budget = income * 0.20  # Savings and debt repayment
        
        current_savings = income - expenses
        
        recommendations = []
        
        if expenses > needs_budget + wants_budget:
            overspend = expenses - (needs_budget + wants_budget)
            recommendations.append(f"Consider reducing expenses by ${overspend:.2f} to align with recommended budget")
        
        if current_savings < savings_budget:
            savings_gap = savings_budget - current_savings
            recommendations.append(f"Increase savings by ${savings_gap:.2f} to reach 20% savings target")
        
        return {
            'recommended_allocation': {
                'needs': needs_budget,
                'wants': wants_budget,
                'savings': savings_budget
            },
            'current_spending': expenses,
            'current_savings': current_savings,
            'budget_gap': expenses - (needs_budget + wants_budget),
            'savings_gap': savings_budget - current_savings,
            'recommendations': recommendations
        }
    
    def _suggest_tax_optimizations(self, financial_data: Dict[str, Any]) -> Dict[str, Any]:
        """Suggest tax optimization strategies"""
        
        income = financial_data.get('transactions', {}).get('income', 0)
        epf_balance = financial_data.get('epf_retirement_balance', {}).get('current_balance', 0)
        investments = financial_data.get('investments', {})
        
        suggestions = []
        
        # EPF/401k optimization
        annual_income = income * 12
        if annual_income > 50000:  # Threshold for retirement savings advice
            max_epf_contribution = min(22500, annual_income * 0.15)  # Estimated max
            suggestions.append({
                'strategy': 'Maximize EPF Contributions',
                'description': f'Consider contributing up to ${max_epf_contribution:.0f} annually to reduce taxable income',
                'potential_savings': max_epf_contribution * 0.22  # Estimated tax rate
            })
        
        # Tax-loss harvesting for investments
        if sum(investments.values()) > 10000:
            suggestions.append({
                'strategy': 'Tax-Loss Harvesting',
                'description': 'Review investment portfolio for tax-loss harvesting opportunities',
                'potential_savings': 'Varies based on losses'
            })
        
        return {
            'suggestions': suggestions,
            'estimated_annual_income': annual_income,
            'retirement_savings_ratio': (epf_balance / annual_income) if annual_income > 0 else 0
        }
    
    def _analyze_financial_goals(self, financial_data: Dict[str, Any], goals: List[FinancialGoal]) -> Dict[str, Any]:
        """Analyze progress toward financial goals"""
        
        if not goals:
            return {}
        
        current_savings_rate = self._calculate_savings_rate(financial_data)
        monthly_savings = financial_data.get('transactions', {}).get('income', 0) * current_savings_rate
        
        goal_analysis = []
        
        for goal in goals:
            remaining_amount = goal.target_amount - goal.current_amount
            months_remaining = (goal.target_date - datetime.now()).days // 30
            
            if months_remaining > 0:
                required_monthly_savings = remaining_amount / months_remaining
                affordability = "Achievable" if required_monthly_savings <= monthly_savings * 0.8 else "Challenging"
            else:
                required_monthly_savings = remaining_amount
                affordability = "Overdue"
            
            goal_analysis.append({
                'goal': goal.name,
                'progress_percentage': (goal.current_amount / goal.target_amount) * 100,
                'remaining_amount': remaining_amount,
                'months_remaining': months_remaining,
                'required_monthly_savings': required_monthly_savings,
                'affordability': affordability,
                'priority': goal.priority
            })
        
        # Sort by priority
        goal_analysis.sort(key=lambda x: x['priority'], reverse=True)
        
        return {
            'goals': goal_analysis,
            'total_monthly_commitment': sum(g['required_monthly_savings'] for g in goal_analysis),
            'available_monthly_savings': monthly_savings
        }
    
    def _analyze_spending_patterns(self, financial_data: Dict[str, Any]) -> List[SpendingPattern]:
        """Analyze spending patterns and detect anomalies"""
        
        # This is a simplified version - in reality, you'd analyze historical data
        expenses = financial_data.get('transactions', {}).get('expenses', 0)
        income = financial_data.get('transactions', {}).get('income', 0)
        
        # Estimated spending categories based on typical patterns
        estimated_patterns = [
            SpendingPattern(
                category='Housing',
                average_monthly=expenses * 0.30,
                trend='stable',
                variance=0.05,
                anomaly_score=0.1
            ),
            SpendingPattern(
                category='Food',
                average_monthly=expenses * 0.15,
                trend='stable',
                variance=0.10,
                anomaly_score=0.2
            ),
            SpendingPattern(
                category='Transportation',
                average_monthly=expenses * 0.15,
                trend='stable',
                variance=0.15,
                anomaly_score=0.1
            ),
            SpendingPattern(
                category='Entertainment',
                average_monthly=expenses * 0.10,
                trend='increasing',
                variance=0.25,
                anomaly_score=0.3
            ),
            SpendingPattern(
                category='Other',
                average_monthly=expenses * 0.30,
                trend='stable',
                variance=0.20,
                anomaly_score=0.2
            )
        ]
        
        return estimated_patterns
    
    def _identify_investment_opportunities(self, financial_data: Dict[str, Any]) -> List[InvestmentOpportunity]:
        """Identify suitable investment opportunities based on profile"""
        
        income = financial_data.get('transactions', {}).get('income', 0)
        age_estimate = 35  # This would typically be provided or estimated
        risk_tolerance = self._estimate_risk_tolerance(financial_data)
        
        opportunities = []
        
        # Emergency fund
        liquid_assets = financial_data.get('assets', {}).get('cash', 0) + financial_data.get('assets', {}).get('bank_balances', 0)
        emergency_fund_target = financial_data.get('transactions', {}).get('expenses', 0) * 6
        
        if liquid_assets < emergency_fund_target:
            opportunities.append(InvestmentOpportunity(
                type='High-Yield Savings',
                expected_return=0.04,
                risk_level='Very Low',
                minimum_investment=100,
                time_horizon='Immediate',
                description='Build emergency fund before investing'
            ))
        
        # Investment recommendations based on risk tolerance
        if risk_tolerance == 'conservative':
            opportunities.extend([
                InvestmentOpportunity(
                    type='Government Bonds',
                    expected_return=0.03,
                    risk_level='Low',
                    minimum_investment=1000,
                    time_horizon='1-5 years',
                    description='Safe, government-backed bonds'
                ),
                InvestmentOpportunity(
                    type='Corporate Bonds',
                    expected_return=0.05,
                    risk_level='Low-Medium',
                    minimum_investment=1000,
                    time_horizon='3-7 years',
                    description='Higher yield corporate bonds'
                )
            ])
        elif risk_tolerance == 'moderate':
            opportunities.extend([
                InvestmentOpportunity(
                    type='Balanced Mutual Funds',
                    expected_return=0.07,
                    risk_level='Medium',
                    minimum_investment=500,
                    time_horizon='5-10 years',
                    description='Diversified stock and bond funds'
                ),
                InvestmentOpportunity(
                    type='Index Funds',
                    expected_return=0.08,
                    risk_level='Medium',
                    minimum_investment=100,
                    time_horizon='10+ years',
                    description='Low-cost market index funds'
                )
            ])
        else:  # aggressive
            opportunities.extend([
                InvestmentOpportunity(
                    type='Growth Stocks',
                    expected_return=0.12,
                    risk_level='High',
                    minimum_investment=1000,
                    time_horizon='10+ years',
                    description='High-growth potential stocks'
                ),
                InvestmentOpportunity(
                    type='Technology ETFs',
                    expected_return=0.10,
                    risk_level='High',
                    minimum_investment=100,
                    time_horizon='10+ years',
                    description='Technology sector exposure'
                )
            ])
        
        return opportunities
    
    def _estimate_risk_tolerance(self, financial_data: Dict[str, Any]) -> str:
        """Estimate risk tolerance based on financial situation"""
        
        # Simple risk assessment based on financial metrics
        income = financial_data.get('transactions', {}).get('income', 0)
        expenses = financial_data.get('transactions', {}).get('expenses', 0)
        debt = sum(financial_data.get('liabilities', {}).values())
        
        savings_rate = (income - expenses) / income if income > 0 else 0
        debt_to_income = debt / (income * 12) if income > 0 else 1
        
        # Conservative if high debt or low savings
        if debt_to_income > 0.4 or savings_rate < 0.1:
            return 'conservative'
        # Aggressive if high savings and low debt
        elif debt_to_income < 0.2 and savings_rate > 0.25:
            return 'aggressive'
        else:
            return 'moderate'
    
    def _optimize_debt_strategy(self, financial_data: Dict[str, Any]) -> Dict[str, Any]:
        """Optimize debt repayment strategy"""
        
        liabilities = financial_data.get('liabilities', {})
        total_debt = sum(liabilities.values())
        
        if total_debt == 0:
            return {'message': 'No debt to optimize'}
        
        income = financial_data.get('transactions', {}).get('income', 0)
        expenses = financial_data.get('transactions', {}).get('expenses', 0)
        available_for_debt = max(0, income - expenses - (income * 0.1))  # Keep 10% buffer
        
        # Debt payoff scenarios
        scenarios = {}
        
        # Minimum payments scenario
        scenarios['minimum_payments'] = {
            'strategy': 'Minimum Payments Only',
            'monthly_payment': total_debt * 0.02,  # Assume 2% minimum
            'payoff_time_months': 50 if total_debt > 0 else 0,  # Rough estimate
            'total_interest': total_debt * 0.5  # Rough estimate
        }
        
        # Aggressive payoff scenario
        if available_for_debt > scenarios['minimum_payments']['monthly_payment']:
            extra_payment = available_for_debt - scenarios['minimum_payments']['monthly_payment']
            accelerated_payment = scenarios['minimum_payments']['monthly_payment'] + extra_payment
            scenarios['accelerated_payoff'] = {
                'strategy': 'Accelerated Payoff',
                'monthly_payment': accelerated_payment,
                'payoff_time_months': max(6, total_debt / accelerated_payment),
                'total_interest': total_debt * 0.1  # Much less interest
            }
        
        return {
            'total_debt': total_debt,
            'available_for_debt_payment': available_for_debt,
            'scenarios': scenarios,
            'recommended_strategy': 'accelerated_payoff' if 'accelerated_payoff' in scenarios else 'minimum_payments'
        }
    
    def _forecast_cash_flow(self, financial_data: Dict[str, Any], months: int = 12) -> Dict[str, Any]:
        """Forecast cash flow for the next N months"""
        
        income = financial_data.get('transactions', {}).get('income', 0)
        expenses = financial_data.get('transactions', {}).get('expenses', 0)
        monthly_surplus = income - expenses
        
        # Simple linear forecast (in reality, you'd use more sophisticated modeling)
        forecast = []
        cumulative_savings = 0
        
        for month in range(1, months + 1):
            # Add some variability
            month_income = income * (1 + np.random.normal(0, 0.02))
            month_expenses = expenses * (1 + np.random.normal(0, 0.05))
            month_surplus = month_income - month_expenses
            cumulative_savings += month_surplus
            
            forecast.append({
                'month': month,
                'income': month_income,
                'expenses': month_expenses,
                'surplus': month_surplus,
                'cumulative_savings': cumulative_savings
            })
        
        return {
            'forecast_period_months': months,
            'monthly_forecast': forecast,
            'projected_annual_savings': cumulative_savings,
            'confidence_level': 'Medium'  # Based on data quality and variability
        }
    
    def _comprehensive_risk_assessment(self, financial_data: Dict[str, Any]) -> Dict[str, Any]:
        """Comprehensive risk assessment across multiple dimensions"""
        
        risks = {}
        
        # Income risk
        income = financial_data.get('transactions', {}).get('income', 0)
        risks['income_stability'] = {
            'level': 'Medium',  # Would analyze income history
            'description': 'Single income source detected - consider diversification'
        }
        
        # Liquidity risk
        liquid_assets = financial_data.get('assets', {}).get('cash', 0) + financial_data.get('assets', {}).get('bank_balances', 0)
        expenses = financial_data.get('transactions', {}).get('expenses', 0)
        liquidity_months = liquid_assets / expenses if expenses > 0 else 0
        
        if liquidity_months >= 6:
            liquidity_level = 'Low'
        elif liquidity_months >= 3:
            liquidity_level = 'Medium'
        else:
            liquidity_level = 'High'
        
        risks['liquidity_risk'] = {
            'level': liquidity_level,
            'months_coverage': liquidity_months,
            'description': f'Emergency fund covers {liquidity_months:.1f} months of expenses'
        }
        
        # Debt risk
        debt = sum(financial_data.get('liabilities', {}).values())
        debt_to_income = debt / (income * 12) if income > 0 else 0
        
        if debt_to_income <= 0.2:
            debt_risk_level = 'Low'
        elif debt_to_income <= 0.4:
            debt_risk_level = 'Medium'
        else:
            debt_risk_level = 'High'
        
        risks['debt_risk'] = {
            'level': debt_risk_level,
            'debt_to_income_ratio': debt_to_income,
            'description': f'Debt represents {debt_to_income:.1%} of annual income'
        }
        
        # Investment risk
        investments = financial_data.get('investments', {})
        total_investments = sum(investments.values())
        
        if total_investments == 0:
            investment_risk = 'High'
            description = 'No investments detected - inflation risk'
        else:
            # Simple diversification check
            non_zero_investments = len([v for v in investments.values() if v > 0])
            if non_zero_investments >= 3:
                investment_risk = 'Low'
                description = 'Well-diversified investment portfolio'
            elif non_zero_investments == 2:
                investment_risk = 'Medium'
                description = 'Moderately diversified investments'
            else:
                investment_risk = 'High'
                description = 'Poor investment diversification'
        
        risks['investment_risk'] = {
            'level': investment_risk,
            'diversification_score': non_zero_investments if total_investments > 0 else 0,
            'description': description
        }
        
        return risks
    
    def _generate_personalized_recommendations(self, financial_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate personalized recommendations based on comprehensive analysis"""
        
        recommendations = []
        
        # Emergency fund recommendation
        liquid_assets = financial_data.get('assets', {}).get('cash', 0) + financial_data.get('assets', {}).get('bank_balances', 0)
        expenses = financial_data.get('transactions', {}).get('expenses', 0)
        emergency_target = expenses * 6
        
        if liquid_assets < emergency_target:
            recommendations.append({
                'category': 'Emergency Fund',
                'priority': 'High',
                'action': f'Build emergency fund to ${emergency_target:.0f}',
                'timeline': '3-6 months',
                'impact': 'Reduces financial risk significantly'
            })
        
        # Debt reduction recommendation
        debt = sum(financial_data.get('liabilities', {}).values())
        if debt > 0:
            recommendations.append({
                'category': 'Debt Management',
                'priority': 'High',
                'action': 'Implement accelerated debt repayment strategy',
                'timeline': '1-3 years',
                'impact': 'Saves thousands in interest payments'
            })
        
        # Investment recommendation
        income = financial_data.get('transactions', {}).get('income', 0)
        savings_rate = (income - expenses) / income if income > 0 else 0
        
        if savings_rate > 0.15 and liquid_assets >= emergency_target:
            recommendations.append({
                'category': 'Investment',
                'priority': 'Medium',
                'action': 'Start investing in diversified portfolio',
                'timeline': 'Ongoing',
                'impact': 'Long-term wealth building'
            })
        
        # Savings rate improvement
        if savings_rate < 0.15:
            recommendations.append({
                'category': 'Budgeting',
                'priority': 'High',
                'action': 'Increase savings rate to 15-20%',
                'timeline': '1-3 months',
                'impact': 'Enables financial goal achievement'
            })
        
        return recommendations
    
    def _create_action_plan(self, financial_data: Dict[str, Any], goals: Optional[List[FinancialGoal]]) -> Dict[str, Any]:
        """Create a prioritized action plan"""
        
        action_items = []
        
        # Immediate actions (0-30 days)
        action_items.append({
            'timeframe': 'Immediate (0-30 days)',
            'actions': [
                'Review and categorize all expenses',
                'Set up automatic transfers to savings',
                'Check and optimize bank account interest rates'
            ]
        })
        
        # Short-term actions (1-6 months)
        short_term = [
            'Build emergency fund to target level',
            'Create and implement debt repayment plan'
        ]
        
        if goals:
            short_term.append('Set up goal-specific savings accounts')
        
        action_items.append({
            'timeframe': 'Short-term (1-6 months)',
            'actions': short_term
        })
        
        # Medium-term actions (6-24 months)
        action_items.append({
            'timeframe': 'Medium-term (6-24 months)',
            'actions': [
                'Maximize retirement contributions',
                'Diversify investment portfolio',
                'Consider tax optimization strategies'
            ]
        })
        
        # Long-term actions (2+ years)
        action_items.append({
            'timeframe': 'Long-term (2+ years)',
            'actions': [
                'Regularly rebalance investment portfolio',
                'Review and update financial goals',
                'Consider advanced tax strategies'
            ]
        })
        
        return {
            'action_plan': action_items,
            'success_metrics': [
                'Emergency fund fully funded',
                'Debt-to-income ratio below 20%',
                'Savings rate above 20%',
                'Investment portfolio properly diversified'
            ]
        }
    
    def _calculate_savings_rate(self, financial_data: Dict[str, Any]) -> float:
        """Calculate current savings rate"""
        income = financial_data.get('transactions', {}).get('income', 0)
        expenses = financial_data.get('transactions', {}).get('expenses', 0)
        return (income - expenses) / income if income > 0 else 0
    
    def load_model(self, model_path: str):
        """Load trained model from file"""
        self.model.load_state_dict(torch.load(model_path, map_location='cpu'))
        self.model.eval()
    
    def save_analysis(self, analysis: Dict[str, Any], output_file: str):
        """Save analysis results to file"""
        # Convert any numpy types to Python types for JSON serialization
        serializable_analysis = self._make_json_serializable(analysis)
        
        with open(output_file, 'w') as f:
            json.dump(serializable_analysis, f, indent=2, default=str)
        
        logger.info(f"Analysis saved to {output_file}")
    
    def _make_json_serializable(self, obj):
        """Convert numpy types and other non-serializable types to JSON-compatible types"""
        if isinstance(obj, dict):
            return {k: self._make_json_serializable(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self._make_json_serializable(v) for v in obj]
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        elif isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, datetime):
            return obj.isoformat()
        else:
            return obj

# Example usage and testing functions
def example_usage():
    """Example usage of the insights engine"""
    
    # Sample financial data
    sample_data = {
        "assets": {"cash": 32256, "bank_balances": 77090, "property": 0},
        "liabilities": {"loans": 0, "credit_card_debt": 0},
        "transactions": {"income": 89184, "expenses": 55829, "transfers": 2608},
        "epf_retirement_balance": {"contributions": 1800, "employer_match": 1800, "current_balance": 1692033},
        "credit_score": {"score": 632, "rating": "Average"},
        "investments": {"stocks": 156545, "mutual_funds": 179376, "bonds": 32856}
    }
    
    # Create permissions (all allowed)
    permissions = UserPermissions()
    
    # Create sample goals
    goals = [
        FinancialGoal(
            name="Emergency Fund",
            target_amount=200000,
            current_amount=100000,
            target_date=datetime.now() + timedelta(days=365),
            priority=10,
            category="emergency"
        ),
        FinancialGoal(
            name="House Down Payment",
            target_amount=500000,
            current_amount=50000,
            target_date=datetime.now() + timedelta(days=1095),  # 3 years
            priority=8,
            category="purchase"
        )
    ]
    
    # Initialize insights engine
    engine = AdvancedInsightsEngine()
    
    # Generate comprehensive analysis
    analysis = engine.generate_comprehensive_analysis(sample_data, permissions, goals)
    
    # Save results
    engine.save_analysis(analysis, 'sample_analysis.json')
    
    print("Sample analysis completed and saved to 'sample_analysis.json'")
    print(f"Financial Health Score: {analysis['advanced_analysis']['financial_health_score']['total_score']:.1f}/100")
    print(f"Health Level: {analysis['advanced_analysis']['financial_health_score']['health_level']}")

if __name__ == "__main__":
    example_usage()