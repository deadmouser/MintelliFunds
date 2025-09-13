from flask import Flask, request, jsonify
import torch
import json
import numpy as np
from model import FinancialAdvisorModel
from utils import load_model

app = Flask(__name__)

# Load the trained model
input_size = 15  # This should match the number of features used in training
num_classes = 1
model = load_model(FinancialAdvisorModel(input_size, num_classes), 'financial_model.pth')
model.eval()

def get_recommendations(data):
    """
    Generates financial recommendations based on user data.
    """
    recommendations = []
    if data['liabilities']['credit_card_debt'] > 50000:
        recommendations.append("Prioritize paying off high-interest credit card debt.")
    if data['investments']['stocks'] == 0 and data['investments']['mutual_funds'] == 0:
        recommendations.append("Consider starting to invest in low-cost index funds to build wealth.")
    if data['transactions']['expenses'] > data['transactions']['income'] * 0.7:
        recommendations.append("Your expenses are high compared to your income. Look for areas to cut back.")
    return recommendations

def detect_unusual_spending(data):
    """
    Detects unusual spending patterns. This is a simplified example.
    """
    # In a real-world scenario, you'd compare current spending to historical averages.
    # For this example, let's just flag high expenses.
    unusual_spending = []
    if data['transactions']['expenses'] > 100000:
         unusual_spending.append({"category": "General", "amount": data['transactions']['expenses'], "reason": "High monthly expense."})
    return unusual_spending

@app.route('/predict', methods=['POST'])
def predict():
    if request.is_json:
        data = request.get_json()

        # Preprocess the input data similarly to the training data
        features = []
        features.append(data['assets']['cash'])
        features.append(data['assets']['bank_balances'])
        features.append(data['assets']['property'])
        features.append(data['liabilities']['loans'])
        features.append(data['liabilities']['credit_card_debt'])
        features.append(data['transactions']['income'])
        features.append(data['transactions']['expenses'])
        features.append(data['transactions']['transfers'])
        features.append(data['epf_retirement_balance']['contributions'])
        features.append(data['epf_retirement_balance']['employer_match'])
        features.append(data['epf_retirement_balance']['current_balance'])
        features.append(data['credit_score']['score'])
        rating_map = {'Poor': 0, 'Average': 1, 'Good': 2, 'Excellent': 3}
        features.append(rating_map.get(data['credit_score']['rating'], 1))
        features.append(data['investments']['stocks'])
        features.append(data['investments']['mutual_funds'])
        features.append(data['investments']['bonds'])

        # We need to reshape and normalize as we did in preprocessing
        features_np = np.array(features[1:], dtype=np.float32) # Exclude target variable
        features_np = (features_np - np.mean(features_np)) / (np.std(features_np) + 1e-6)

        input_tensor = torch.tensor(features_np, dtype=torch.float32).unsqueeze(0)

        with torch.no_grad():
            prediction = model(input_tensor)

        predicted_savings = prediction.item()

        # Get additional insights
        unusual_spending = detect_unusual_spending(data)
        recommendations = get_recommendations(data)

        return jsonify({
            'predicted_savings': predicted_savings,
            'unusual_spending': unusual_spending,
            'recommendations': recommendations
        })
    else:
        return jsonify({"error": "Request must be JSON"}), 400

if __name__ == '__main__':
    app.run(debug=True)
