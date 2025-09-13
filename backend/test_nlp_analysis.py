#!/usr/bin/env python3
"""
Test script for NLP and Analysis integration
"""
import requests
import json
from datetime import datetime

# Test the NLP and Analysis integration
def test_insights_api():
    """Test the insights API with various queries"""
    
    base_url = "http://localhost:8000"
    
    # Test queries with different intents
    test_queries = [
        {
            "query": "What are my spending patterns this month?",
            "permissions": {
                "transactions": True,
                "spending_trends": True,
                "category_breakdown": True,
                "assets": False,
                "liabilities": False,
                "epf_balance": False,
                "credit_score": False,
                "investments": False,
                "accounts": False,
                "dashboard_insights": False
            }
        },
        {
            "query": "Can I afford to buy a $5000 laptop?",
            "permissions": {
                "transactions": True,
                "accounts": True,
                "assets": False,
                "liabilities": False,
                "epf_balance": False,
                "credit_score": False,
                "investments": False,
                "spending_trends": False,
                "category_breakdown": False,
                "dashboard_insights": False
            }
        },
        {
            "query": "How much will I have saved in 6 months?",
            "permissions": {
                "transactions": True,
                "accounts": True,
                "assets": False,
                "liabilities": False,
                "epf_balance": False,
                "credit_score": False,
                "investments": False,
                "spending_trends": False,
                "category_breakdown": False,
                "dashboard_insights": False
            }
        },
        {
            "query": "What's my financial health overall?",
            "permissions": {
                "transactions": True,
                "accounts": True,
                "assets": True,
                "liabilities": True,
                "epf_balance": False,
                "credit_score": False,
                "investments": True,
                "spending_trends": False,
                "category_breakdown": False,
                "dashboard_insights": False
            }
        }
    ]
    
    print("🧪 Testing NLP and Analysis Integration")
    print("=" * 50)
    
    for i, test_case in enumerate(test_queries, 1):
        print(f"\n📝 Test {i}: {test_case['query']}")
        print("-" * 30)
        
        try:
            response = requests.post(
                f"{base_url}/api/insights",
                json=test_case,
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Extract analysis results
                analysis = data.get("filtered_data", {}).get("_analysis", {})
                intent = analysis.get("intent", "unknown")
                analysis_type = analysis.get("analysis_result", {}).get("analysis_type", "unknown")
                results = analysis.get("analysis_result", {}).get("results", {})
                
                print(f"✅ Intent: {intent}")
                print(f"✅ Analysis Type: {analysis_type}")
                
                if "insights" in results:
                    print("💡 Insights:")
                    for insight in results["insights"][:3]:  # Show first 3 insights
                        print(f"   • {insight}")
                
                # Show key metrics based on analysis type
                if analysis_type == "spending_analysis":
                    total = results.get("total_spending", 0)
                    print(f"💰 Total Spending: ${total:,.2f}")
                    
                elif analysis_type == "affordability_check":
                    affordable = results.get("affordable", False)
                    target = results.get("target_amount", 0)
                    print(f"💳 Target Amount: ${target:,.2f}")
                    print(f"✅ Affordable: {'Yes' if affordable else 'No'}")
                    
                elif analysis_type == "savings_projection":
                    current = results.get("current_savings", 0)
                    monthly = results.get("monthly_savings", 0)
                    print(f"💰 Current Savings: ${current:,.2f}")
                    print(f"💰 Monthly Savings: ${monthly:,.2f}")
                    
                elif analysis_type == "financial_health":
                    net_worth = results.get("net_worth", 0)
                    health_score = results.get("health_score", 0)
                    print(f"💎 Net Worth: ${net_worth:,.2f}")
                    print(f"🏆 Health Score: {health_score}/100")
                
            else:
                print(f"❌ Error: {response.status_code}")
                print(f"Response: {response.text}")
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Request failed: {str(e)}")
        except Exception as e:
            print(f"❌ Unexpected error: {str(e)}")
    
    print("\n" + "=" * 50)
    print("🎉 Testing completed!")

if __name__ == "__main__":
    test_insights_api()
