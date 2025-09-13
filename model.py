import torch
import torch.nn as nn
import torch.nn.functional as F
import numpy as np
from typing import Dict, List, Tuple, Optional

class FinancialAdvisorModel(nn.Module):
    """
    Enhanced PyTorch model for comprehensive financial analysis including:
    - Savings prediction
    - Spending anomaly detection
    - Investment recommendations
    - Debt repayment optimization
    """
    def __init__(self, input_size: int = 16, hidden_sizes: List[int] = None):
        super(FinancialAdvisorModel, self).__init__()
        
        if hidden_sizes is None:
            hidden_sizes = [256, 128, 64, 32]
            
        self.input_size = input_size
        self.hidden_sizes = hidden_sizes
        
        # Feature extraction layers
        layers = []
        prev_size = input_size
        for hidden_size in hidden_sizes:
            layers.extend([
                nn.Linear(prev_size, hidden_size),
                nn.BatchNorm1d(hidden_size),
                nn.ReLU(),
                nn.Dropout(0.2)
            ])
            prev_size = hidden_size
        
        self.feature_extractor = nn.Sequential(*layers)
        
        # Task-specific heads
        self.savings_predictor = nn.Sequential(
            nn.Linear(prev_size, 32),
            nn.ReLU(),
            nn.Linear(32, 1)  # Predicted savings amount
        )
        
        self.anomaly_detector = nn.Sequential(
            nn.Linear(prev_size, 32),
            nn.ReLU(),
            nn.Linear(32, 1),  # Anomaly score
            nn.Sigmoid()
        )
        
        self.risk_assessor = nn.Sequential(
            nn.Linear(prev_size, 32),
            nn.ReLU(),
            nn.Linear(32, 5)  # Risk categories: Very Low, Low, Medium, High, Very High
        )
        
        self.investment_recommender = nn.Sequential(
            nn.Linear(prev_size, 64),
            nn.ReLU(),
            nn.Linear(64, 32),
            nn.ReLU(),
            nn.Linear(32, 10)  # Investment allocation recommendations
        )
        
        # Debt optimization head
        self.debt_optimizer = nn.Sequential(
            nn.Linear(prev_size, 32),
            nn.ReLU(),
            nn.Linear(32, 3)  # Payment strategy recommendations
        )
    
    def forward(self, x: torch.Tensor) -> Dict[str, torch.Tensor]:
        """
        Forward pass returning multiple predictions
        """
        # Extract features
        features = self.feature_extractor(x)
        
        # Get predictions from each head
        outputs = {
            'savings_prediction': self.savings_predictor(features),
            'anomaly_score': self.anomaly_detector(features),
            'risk_assessment': self.risk_assessor(features),
            'investment_recommendations': self.investment_recommender(features),
            'debt_optimization': self.debt_optimizer(features)
        }
        
        return outputs
    
    def predict_savings(self, x: torch.Tensor) -> torch.Tensor:
        """Predict future savings"""
        with torch.no_grad():
            features = self.feature_extractor(x)
            return self.savings_predictor(features)
    
    def detect_anomalies(self, x: torch.Tensor, threshold: float = 0.7) -> Tuple[torch.Tensor, List[str]]:
        """Detect unusual spending patterns"""
        with torch.no_grad():
            features = self.feature_extractor(x)
            anomaly_scores = self.anomaly_detector(features)
            
            anomalies = anomaly_scores > threshold
            anomaly_descriptions = []
            
            for i, is_anomaly in enumerate(anomalies):
                if is_anomaly:
                    score = anomaly_scores[i].item()
                    if score > 0.9:
                        anomaly_descriptions.append(f"Highly unusual spending pattern detected (confidence: {score:.2%})")
                    elif score > 0.8:
                        anomaly_descriptions.append(f"Unusual spending pattern detected (confidence: {score:.2%})")
                    else:
                        anomaly_descriptions.append(f"Potential spending anomaly (confidence: {score:.2%})")
            
            return anomaly_scores, anomaly_descriptions
    
    def get_investment_recommendations(self, x: torch.Tensor) -> Dict[str, float]:
        """Get investment allocation recommendations"""
        with torch.no_grad():
            features = self.feature_extractor(x)
            recommendations = self.investment_recommender(features)
            recommendations = F.softmax(recommendations, dim=-1)
            
            categories = [
                'Emergency Fund', 'Stocks', 'Bonds', 'Mutual Funds', 'Real Estate',
                'Cryptocurrency', 'Gold/Commodities', 'High-Yield Savings', 'Index Funds', 'Other'
            ]
            
            return {categories[i]: recommendations[0][i].item() for i in range(len(categories))}
    
    def get_debt_optimization(self, x: torch.Tensor) -> Dict[str, float]:
        """Get debt repayment strategy recommendations"""
        with torch.no_grad():
            features = self.feature_extractor(x)
            strategies = self.debt_optimizer(features)
            strategies = F.softmax(strategies, dim=-1)
            
            strategy_names = ['Avalanche Method', 'Snowball Method', 'Hybrid Approach']
            
            return {strategy_names[i]: strategies[0][i].item() for i in range(len(strategy_names))}

class FinancialInsightGenerator:
    """
    Helper class to generate human-readable financial insights
    """
    def __init__(self, model: FinancialAdvisorModel):
        self.model = model
        self.model.eval()
    
    def generate_comprehensive_insights(self, financial_data: Dict) -> Dict:
        """
        Generate comprehensive financial insights from user data
        """
        # Convert financial data to tensor
        features = self._extract_features(financial_data)
        x = torch.tensor(features, dtype=torch.float32).unsqueeze(0)
        
        insights = {
            'savings_prediction': self._get_savings_insights(x, financial_data),
            'spending_analysis': self._get_spending_insights(x, financial_data),
            'investment_advice': self._get_investment_insights(x, financial_data),
            'debt_management': self._get_debt_insights(x, financial_data),
            'risk_assessment': self._get_risk_insights(x),
            'actionable_recommendations': []
        }
        
        # Generate actionable recommendations
        insights['actionable_recommendations'] = self._generate_recommendations(insights, financial_data)
        
        return insights
    
    def _extract_features(self, financial_data: Dict) -> List[float]:
        """Extract numerical features from financial data"""
        features = []
        
        # Assets
        features.append(financial_data.get('assets', {}).get('cash', 0))
        features.append(financial_data.get('assets', {}).get('bank_balances', 0))
        features.append(financial_data.get('assets', {}).get('property', 0))
        
        # Liabilities
        features.append(financial_data.get('liabilities', {}).get('loans', 0))
        features.append(financial_data.get('liabilities', {}).get('credit_card_debt', 0))
        
        # Transactions
        features.append(financial_data.get('transactions', {}).get('income', 0))
        features.append(financial_data.get('transactions', {}).get('expenses', 0))
        features.append(financial_data.get('transactions', {}).get('transfers', 0))
        
        # EPF/Retirement
        epf = financial_data.get('epf_retirement_balance', {})
        features.append(epf.get('contributions', 0))
        features.append(epf.get('employer_match', 0))
        features.append(epf.get('current_balance', 0))
        
        # Credit Score
        features.append(financial_data.get('credit_score', {}).get('score', 600))
        
        # Credit Rating (encoded)
        rating = financial_data.get('credit_score', {}).get('rating', 'Average')
        rating_map = {'Poor': 0, 'Average': 1, 'Fair': 1, 'Good': 2, 'Excellent': 3}
        features.append(rating_map.get(rating, 1))
        
        # Investments
        investments = financial_data.get('investments', {})
        features.append(investments.get('stocks', 0))
        features.append(investments.get('mutual_funds', 0))
        features.append(investments.get('bonds', 0))
        
        return features
    
    def _get_savings_insights(self, x: torch.Tensor, financial_data: Dict) -> Dict:
        """Generate savings-related insights"""
        predicted_savings = self.model.predict_savings(x).item()
        
        current_income = financial_data.get('transactions', {}).get('income', 0)
        current_expenses = financial_data.get('transactions', {}).get('expenses', 0)
        current_savings_rate = (current_income - current_expenses) / current_income if current_income > 0 else 0
        
        return {
            'predicted_monthly_savings': max(0, predicted_savings),
            'current_savings_rate': current_savings_rate * 100,
            'recommended_savings_rate': 20.0,  # Standard recommendation
            'savings_goal_timeline': self._calculate_savings_timeline(predicted_savings, financial_data)
        }
    
    def _get_spending_insights(self, x: torch.Tensor, financial_data: Dict) -> Dict:
        """Generate spending analysis insights"""
        anomaly_scores, anomaly_descriptions = self.model.detect_anomalies(x)
        
        current_expenses = financial_data.get('transactions', {}).get('expenses', 0)
        current_income = financial_data.get('transactions', {}).get('income', 0)
        expense_ratio = current_expenses / current_income if current_income > 0 else 1
        
        return {
            'unusual_spending_detected': len(anomaly_descriptions) > 0,
            'anomaly_details': anomaly_descriptions,
            'expense_to_income_ratio': expense_ratio * 100,
            'spending_health': 'Good' if expense_ratio < 0.7 else 'Needs Attention'
        }
    
    def _get_investment_insights(self, x: torch.Tensor, financial_data: Dict) -> Dict:
        """Generate investment recommendations"""
        recommendations = self.model.get_investment_recommendations(x)
        
        # Sort recommendations by priority
        sorted_recommendations = sorted(recommendations.items(), key=lambda x: x[1], reverse=True)
        
        current_investments = financial_data.get('investments', {})
        total_investments = sum(current_investments.values())
        
        return {
            'top_recommendations': sorted_recommendations[:3],
            'current_portfolio_value': total_investments,
            'diversification_score': self._calculate_diversification_score(current_investments),
            'recommended_allocations': recommendations
        }
    
    def _get_debt_insights(self, x: torch.Tensor, financial_data: Dict) -> Dict:
        """Generate debt management insights"""
        debt_strategies = self.model.get_debt_optimization(x)
        
        liabilities = financial_data.get('liabilities', {})
        total_debt = sum(liabilities.values())
        
        current_income = financial_data.get('transactions', {}).get('income', 0)
        debt_to_income = total_debt / (current_income * 12) if current_income > 0 else 0
        
        return {
            'total_debt': total_debt,
            'debt_to_income_ratio': debt_to_income * 100,
            'recommended_strategy': max(debt_strategies.items(), key=lambda x: x[1]),
            'all_strategies': debt_strategies,
            'debt_health': 'Good' if debt_to_income < 0.3 else 'Needs Attention'
        }
    
    def _get_risk_insights(self, x: torch.Tensor) -> Dict:
        """Generate risk assessment insights"""
        with torch.no_grad():
            features = self.model.feature_extractor(x)
            risk_scores = self.model.risk_assessor(features)
            risk_probs = F.softmax(risk_scores, dim=-1)
            
            risk_levels = ['Very Low', 'Low', 'Medium', 'High', 'Very High']
            risk_dict = {risk_levels[i]: risk_probs[0][i].item() for i in range(len(risk_levels))}
            
            primary_risk = max(risk_dict.items(), key=lambda x: x[1])
            
            return {
                'primary_risk_level': primary_risk[0],
                'confidence': primary_risk[1],
                'all_risk_scores': risk_dict
            }
    
    def _generate_recommendations(self, insights: Dict, financial_data: Dict) -> List[str]:
        """Generate actionable recommendations based on all insights"""
        recommendations = []
        
        # Savings recommendations
        savings_rate = insights['savings_prediction']['current_savings_rate']
        if savings_rate < 10:
            recommendations.append("Increase your savings rate to at least 10-15% of your income")
        elif savings_rate < 20:
            recommendations.append("You're doing well! Try to reach the recommended 20% savings rate")
        
        # Spending recommendations
        if insights['spending_analysis']['unusual_spending_detected']:
            recommendations.append("Review your recent spending patterns for potential cost-cutting opportunities")
        
        # Investment recommendations
        top_investment = insights['investment_advice']['top_recommendations'][0]
        recommendations.append(f"Consider increasing allocation to {top_investment[0]} based on your financial profile")
        
        # Debt recommendations
        if insights['debt_management']['total_debt'] > 0:
            strategy = insights['debt_management']['recommended_strategy'][0]
            recommendations.append(f"Use the {strategy} for optimal debt repayment")
        
        return recommendations
    
    def _calculate_savings_timeline(self, monthly_savings: float, financial_data: Dict) -> Dict:
        """Calculate timeline for various savings goals"""
        goals = {
            'Emergency Fund (3 months)': financial_data.get('transactions', {}).get('expenses', 0) * 3,
            'Emergency Fund (6 months)': financial_data.get('transactions', {}).get('expenses', 0) * 6,
            'House Down Payment (20%)': 100000,  # Estimated
        }
        
        timeline = {}
        for goal, amount in goals.items():
            if monthly_savings > 0:
                months = amount / monthly_savings
                timeline[goal] = f"{months:.1f} months"
            else:
                timeline[goal] = "Need to increase savings"
        
        return timeline
    
    def _calculate_diversification_score(self, investments: Dict) -> float:
        """Calculate portfolio diversification score (0-100)"""
        if not investments or sum(investments.values()) == 0:
            return 0.0
        
        values = list(investments.values())
        total = sum(values)
        proportions = [v/total for v in values if v > 0]
        
        # Calculate entropy-based diversification score
        entropy = -sum(p * np.log(p) for p in proportions if p > 0)
        max_entropy = np.log(len(proportions))
        
        return (entropy / max_entropy * 100) if max_entropy > 0 else 0.0
