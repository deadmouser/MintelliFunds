#!/usr/bin/env python3
"""
Comprehensive test script for all API endpoints
"""
import requests
import json
from datetime import datetime

def test_full_api():
    """Test all API endpoints comprehensively"""
    
    base_url = "http://localhost:8000"
    
    print("🚀 Testing Complete Financial AI Assistant API")
    print("=" * 60)
    
    # Test health check first
    print("\n📊 Testing Health Check...")
    try:
        response = requests.get(f"{base_url}/api/health", timeout=5)
        if response.status_code == 200:
            health_data = response.json()
            print(f"✅ Health Check: {health_data['status']}")
            print(f"✅ Data Categories: {health_data['data_categories_loaded']}")
            print(f"✅ AI Service: {health_data['ai_service']['available']}")
        else:
            print(f"❌ Health Check Failed: {response.status_code}")
            return
    except Exception as e:
        print(f"❌ Health Check Error: {str(e)}")
        return
    
    # Test Dashboard endpoints
    print("\n📈 Testing Dashboard Endpoints...")
    test_dashboard_endpoints(base_url)
    
    # Test Transaction endpoints
    print("\n💳 Testing Transaction Endpoints...")
    test_transaction_endpoints(base_url)
    
    # Test Account endpoints
    print("\n🏦 Testing Account Endpoints...")
    test_account_endpoints(base_url)
    
    # Test Investment endpoints
    print("\n📈 Testing Investment Endpoints...")
    test_investment_endpoints(base_url)
    
    # Test Privacy endpoints
    print("\n🔒 Testing Privacy Endpoints...")
    test_privacy_endpoints(base_url)
    
    # Test Chat endpoints
    print("\n💬 Testing Chat Endpoints...")
    test_chat_endpoints(base_url)
    
    # Test Insights endpoints
    print("\n🧠 Testing Insights Endpoints...")
    test_insights_endpoints(base_url)
    
    print("\n" + "=" * 60)
    print("🎉 Complete API Testing Finished!")


def test_dashboard_endpoints(base_url):
    """Test dashboard-related endpoints"""
    endpoints = [
        ("/api/dashboard", "GET"),
        ("/api/spending-trend?period=1m", "GET"),
        ("/api/category-breakdown", "GET"),
        ("/api/insights/dashboard", "GET"),
        ("/api/insights/generate", "POST")
    ]
    
    for endpoint, method in endpoints:
        try:
            if method == "GET":
                response = requests.get(f"{base_url}{endpoint}", timeout=10)
            else:
                response = requests.post(f"{base_url}{endpoint}", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ {method} {endpoint}: {len(str(data))} chars")
            else:
                print(f"❌ {method} {endpoint}: {response.status_code}")
        except Exception as e:
            print(f"❌ {method} {endpoint}: {str(e)}")


def test_transaction_endpoints(base_url):
    """Test transaction-related endpoints"""
    endpoints = [
        ("/api/transactions", "GET"),
        ("/api/transactions?limit=5", "GET"),
        ("/api/transactions?category=food", "GET"),
        ("/api/transactions/recent?limit=3", "GET")
    ]
    
    for endpoint, method in endpoints:
        try:
            response = requests.get(f"{base_url}{endpoint}", timeout=10)
            if response.status_code == 200:
                data = response.json()
                if "transactions" in data:
                    print(f"✅ GET {endpoint}: {len(data['transactions'])} transactions")
                else:
                    print(f"✅ GET {endpoint}: {len(str(data))} chars")
            else:
                print(f"❌ GET {endpoint}: {response.status_code}")
        except Exception as e:
            print(f"❌ GET {endpoint}: {str(e)}")


def test_account_endpoints(base_url):
    """Test account-related endpoints"""
    endpoints = [
        ("/api/accounts", "GET"),
        ("/api/net-worth", "GET")
    ]
    
    for endpoint, method in endpoints:
        try:
            response = requests.get(f"{base_url}{endpoint}", timeout=10)
            if response.status_code == 200:
                data = response.json()
                if "accounts" in data:
                    print(f"✅ GET {endpoint}: {len(data['accounts'])} accounts")
                elif "net_worth" in data:
                    print(f"✅ GET {endpoint}: Net worth ${data['net_worth']:,.2f}")
                else:
                    print(f"✅ GET {endpoint}: {len(str(data))} chars")
            else:
                print(f"❌ GET {endpoint}: {response.status_code}")
        except Exception as e:
            print(f"❌ GET {endpoint}: {str(e)}")


def test_investment_endpoints(base_url):
    """Test investment-related endpoints"""
    endpoints = [
        ("/api/investments", "GET"),
        ("/api/assets", "GET"),
        ("/api/liabilities", "GET")
    ]
    
    for endpoint, method in endpoints:
        try:
            response = requests.get(f"{base_url}{endpoint}", timeout=10)
            if response.status_code == 200:
                data = response.json()
                if "investments" in data:
                    print(f"✅ GET {endpoint}: {len(data['investments'])} investments")
                elif "assets" in data:
                    print(f"✅ GET {endpoint}: {len(data['assets'])} assets")
                elif "liabilities" in data:
                    print(f"✅ GET {endpoint}: {len(data['liabilities'])} liabilities")
                else:
                    print(f"✅ GET {endpoint}: {len(str(data))} chars")
            else:
                print(f"❌ GET {endpoint}: {response.status_code}")
        except Exception as e:
            print(f"❌ GET {endpoint}: {str(e)}")


def test_privacy_endpoints(base_url):
    """Test privacy-related endpoints"""
    endpoints = [
        ("/api/privacy/settings", "GET"),
        ("/api/privacy/categories", "GET")
    ]
    
    for endpoint, method in endpoints:
        try:
            response = requests.get(f"{base_url}{endpoint}", timeout=10)
            if response.status_code == 200:
                data = response.json()
                print(f"✅ GET {endpoint}: {len(str(data))} chars")
            else:
                print(f"❌ GET {endpoint}: {response.status_code}")
        except Exception as e:
            print(f"❌ GET {endpoint}: {str(e)}")
    
    # Test updating privacy settings
    try:
        privacy_settings = {
            "transactions": True,
            "accounts": True,
            "assets": False,
            "liabilities": False,
            "epf_balance": True,
            "credit_score": False,
            "investments": True,
            "spending_trends": True,
            "category_breakdown": True,
            "dashboard_insights": True
        }
        
        response = requests.put(
            f"{base_url}/api/privacy/settings",
            json=privacy_settings,
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ PUT /api/privacy/settings: {data['data_access_level']}")
        else:
            print(f"❌ PUT /api/privacy/settings: {response.status_code}")
    except Exception as e:
        print(f"❌ PUT /api/privacy/settings: {str(e)}")


def test_chat_endpoints(base_url):
    """Test chat-related endpoints"""
    # Test sending a chat message
    try:
        chat_message = {
            "message": "What are my spending patterns this month?",
            "context": {}
        }
        
        response = requests.post(
            f"{base_url}/api/chat",
            json=chat_message,
            timeout=15
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ POST /api/chat: {len(data['response'])} chars response")
        else:
            print(f"❌ POST /api/chat: {response.status_code}")
    except Exception as e:
        print(f"❌ POST /api/chat: {str(e)}")
    
    # Test getting chat history
    try:
        response = requests.get(f"{base_url}/api/chat/history?limit=5", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ GET /api/chat/history: {len(data['messages'])} messages")
        else:
            print(f"❌ GET /api/chat/history: {response.status_code}")
    except Exception as e:
        print(f"❌ GET /api/chat/history: {str(e)}")


def test_insights_endpoints(base_url):
    """Test insights-related endpoints"""
    # Test the main insights endpoint
    try:
        insights_request = {
            "query": "Can I afford to buy a $2000 laptop?",
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
        }
        
        response = requests.post(
            f"{base_url}/api/insights",
            json=insights_request,
            timeout=15
        )
        
        if response.status_code == 200:
            data = response.json()
            ai_response = data.get("filtered_data", {}).get("ai_response", "")
            print(f"✅ POST /api/insights: {len(ai_response)} chars AI response")
        else:
            print(f"❌ POST /api/insights: {response.status_code}")
    except Exception as e:
        print(f"❌ POST /api/insights: {str(e)}")
    
    # Test AI status
    try:
        response = requests.get(f"{base_url}/api/ai/status", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ GET /api/ai/status: AI available = {data['ai_service']['available']}")
        else:
            print(f"❌ GET /api/ai/status: {response.status_code}")
    except Exception as e:
        print(f"❌ GET /api/ai/status: {str(e)}")


if __name__ == "__main__":
    test_full_api()
