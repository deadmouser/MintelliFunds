#!/usr/bin/env python3
"""
Test script for AI integration
"""
import requests
import json
from datetime import datetime

def test_ai_integration():
    """Test the AI integration with various queries"""
    
    base_url = "http://localhost:8000"
    
    print("🤖 Testing AI Integration")
    print("=" * 50)
    
    # Test AI status first
    print("\n📊 Checking AI Service Status...")
    try:
        response = requests.get(f"{base_url}/api/ai/status", timeout=5)
        if response.status_code == 200:
            ai_status = response.json()
            print(f"✅ AI Service Available: {ai_status['ai_service']['available']}")
            print(f"✅ Model: {ai_status['ai_service'].get('model_name', 'N/A')}")
            print(f"✅ Provider: {ai_status['ai_service'].get('provider', 'N/A')}")
        else:
            print(f"❌ AI Status Check Failed: {response.status_code}")
    except Exception as e:
        print(f"❌ AI Status Check Error: {str(e)}")
    
    # Test queries with AI responses
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
            "query": "What's my overall financial health?",
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
    
    print(f"\n🧪 Testing {len(test_queries)} AI-Generated Responses")
    print("=" * 50)
    
    for i, test_case in enumerate(test_queries, 1):
        print(f"\n📝 Test {i}: {test_case['query']}")
        print("-" * 60)
        
        try:
            response = requests.post(
                f"{base_url}/api/insights",
                json=test_case,
                headers={"Content-Type": "application/json"},
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Extract AI response
                ai_response = data.get("filtered_data", {}).get("ai_response", "No AI response")
                intent = data.get("filtered_data", {}).get("intent", "unknown")
                analysis_type = data.get("filtered_data", {}).get("analysis_type", "unknown")
                ai_available = data.get("filtered_data", {}).get("ai_available", False)
                
                print(f"✅ Intent: {intent}")
                print(f"✅ Analysis Type: {analysis_type}")
                print(f"✅ AI Available: {ai_available}")
                print(f"\n🤖 AI Response:")
                print(f"   {ai_response}")
                
            else:
                print(f"❌ Error: {response.status_code}")
                print(f"Response: {response.text}")
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Request failed: {str(e)}")
        except Exception as e:
            print(f"❌ Unexpected error: {str(e)}")
    
    print("\n" + "=" * 50)
    print("🎉 AI Integration Testing Completed!")

if __name__ == "__main__":
    test_ai_integration()
