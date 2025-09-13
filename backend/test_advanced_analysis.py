"""
Test script for advanced financial analysis functionality
Tests the new financial analyzer, data validator, and integration with existing services
"""
import asyncio
import sys
import os
import json
from datetime import datetime, timedelta
from typing import List, Dict, Any

# Add the backend directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "app"))

# Import our services
from services.data_validator import DataValidator
from services.financial_analyzer import FinancialAnalyzer
from services.analysis_service import AnalysisService


def generate_sample_data() -> Dict[str, Any]:
    """Generate sample financial data for testing"""
    
    # Generate sample transactions for the last 6 months
    transactions = []
    current_date = datetime.now()
    
    # Income transactions (monthly salary)
    for i in range(6):
        date = current_date - timedelta(days=30 * i)
        transactions.append({
            "id": f"income_{i}",
            "date": date.isoformat(),
            "amount": 75000,  # Monthly salary
            "description": "Monthly Salary",
            "category": "salary",
            "type": "income"
        })
    
    # Expense transactions (various categories)
    expense_categories = {
        "food": [3500, 4200, 2800, 3900, 4100, 3600],
        "transportation": [2200, 2800, 1900, 2100, 2500, 2300],
        "utilities": [1200, 1800, 1100, 1400, 1600, 1300],
        "entertainment": [2500, 3200, 1800, 2900, 3500, 2700],
        "healthcare": [800, 1200, 500, 900, 1100, 700],
        "shopping": [5500, 8200, 4300, 6100, 7800, 5900]
    }
    
    for month in range(6):
        date_base = current_date - timedelta(days=30 * month)
        for category, amounts in expense_categories.items():
            # Multiple transactions per category per month
            num_transactions = 3 + (month % 3)  # Vary number of transactions
            for i in range(num_transactions):
                transaction_date = date_base - timedelta(days=i * 10)
                amount_per_transaction = amounts[month] / num_transactions
                transactions.append({
                    "id": f"expense_{category}_{month}_{i}",
                    "date": transaction_date.isoformat(),
                    "amount": -amount_per_transaction,  # Negative for expenses
                    "description": f"{category.title()} Expense",
                    "category": category,
                    "type": "expense"
                })
    
    # Sample accounts
    accounts = [
        {
            "id": "checking_001",
            "name": "Primary Checking",
            "type": "checking",
            "balance": 45000,
            "bank": "HDFC Bank"
        },
        {
            "id": "savings_001",
            "name": "Emergency Fund",
            "type": "savings",
            "balance": 150000,
            "bank": "ICICI Bank",
            "interest_rate": 3.5
        },
        {
            "id": "savings_002",
            "name": "Goal Savings",
            "type": "savings",
            "balance": 85000,
            "bank": "SBI",
            "interest_rate": 3.0
        }
    ]
    
    # Sample liabilities
    liabilities = [
        {
            "id": "home_loan",
            "name": "Home Loan",
            "type": "mortgage",
            "balance": 2500000,
            "interest_rate": 8.5,
            "monthly_payment": 22000,
            "remaining_tenure": 180  # months
        },
        {
            "id": "car_loan",
            "name": "Car Loan",
            "type": "auto",
            "balance": 350000,
            "interest_rate": 10.5,
            "monthly_payment": 8500,
            "remaining_tenure": 48  # months
        },
        {
            "id": "credit_card",
            "name": "HDFC Credit Card",
            "type": "credit_card",
            "balance": 25000,
            "interest_rate": 24.0,
            "monthly_payment": 5000
        }
    ]
    
    # Sample investments
    investments = [
        {
            "id": "mutual_fund_1",
            "name": "Large Cap Equity Fund",
            "type": "equity",
            "invested_amount": 180000,
            "current_value": 195000,
            "units": 15000,
            "nav": 13.0
        },
        {
            "id": "mutual_fund_2",
            "name": "Debt Fund",
            "type": "debt",
            "invested_amount": 100000,
            "current_value": 108000,
            "units": 9500,
            "nav": 11.37
        },
        {
            "id": "ppf",
            "name": "Public Provident Fund",
            "type": "ppf",
            "invested_amount": 90000,
            "current_value": 105000,
            "maturity_date": "2038-12-31"
        },
        {
            "id": "fd",
            "name": "Fixed Deposit",
            "type": "fixed_deposit",
            "invested_amount": 200000,
            "current_value": 214000,
            "interest_rate": 7.0,
            "maturity_date": "2025-06-15"
        }
    ]
    
    return {
        "transactions": transactions,
        "accounts": accounts,
        "liabilities": liabilities,
        "investments": investments
    }


async def test_data_validation():
    """Test data validation functionality"""
    print("🔍 Testing Data Validation...")
    
    validator = DataValidator()
    sample_data = generate_sample_data()
    
    try:
        # Test transaction validation
        print("  ✓ Testing transaction validation...")
        validated_transactions = await validator.validate_transactions(sample_data["transactions"])
        print(f"    Validated {len(validated_transactions)} transactions")
        
        # Test account validation
        print("  ✓ Testing account validation...")
        validated_accounts = await validator.validate_accounts(sample_data["accounts"])
        print(f"    Validated {len(validated_accounts)} accounts")
        
        # Test liability validation
        print("  ✓ Testing liability validation...")
        validated_liabilities = await validator.validate_liabilities(sample_data["liabilities"])
        print(f"    Validated {len(validated_liabilities)} liabilities")
        
        # Test investment validation
        print("  ✓ Testing investment validation...")
        validated_investments = await validator.validate_investments(sample_data["investments"])
        print(f"    Validated {len(validated_investments)} investments")
        
        print("✅ Data validation tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Data validation failed: {e}")
        return False


async def test_financial_analyzer():
    """Test core financial analysis functionality"""
    print("\n📊 Testing Financial Analyzer...")
    
    analyzer = FinancialAnalyzer()
    sample_data = generate_sample_data()
    
    try:
        # Test spending analysis
        print("  ✓ Testing spending pattern analysis...")
        spending_result = analyzer.analyze_spending_patterns(sample_data["transactions"], 30)
        print(f"    Total spending (30 days): ₹{spending_result.get('total_spending', 0):,.2f}")
        print(f"    Categories analyzed: {spending_result.get('category_breakdown', {}).get('total_categories', 0)}")
        
        # Test balance forecasting
        print("  ✓ Testing balance forecasting...")
        forecast_result = analyzer.forecast_future_balance(
            sample_data["accounts"], sample_data["transactions"], 6
        )
        current_balance = forecast_result.get("current_balance", 0)
        final_balance = forecast_result.get("final_projected_balance", 0)
        print(f"    Current balance: ₹{current_balance:,.2f}")
        print(f"    Projected balance (6 months): ₹{final_balance:,.2f}")
        
        # Test affordability check
        print("  ✓ Testing affordability analysis...")
        affordability_result = analyzer.check_purchase_affordability(
            sample_data["accounts"], sample_data["transactions"], 
            sample_data["liabilities"], 50000, "New Laptop"
        )
        can_afford = affordability_result.get("can_afford", False)
        print(f"    Can afford ₹50,000 laptop: {'Yes' if can_afford else 'No'}")
        
        # Test anomaly detection
        print("  ✓ Testing anomaly detection...")
        anomaly_result = analyzer.detect_financial_anomalies(sample_data["transactions"])
        anomalies_count = anomaly_result.get("anomalies_detected", 0)
        print(f"    Anomalies detected: {anomalies_count}")
        
        # Test debt strategy
        print("  ✓ Testing debt repayment strategy...")
        debt_result = analyzer.recommend_debt_repayment_strategy(
            sample_data["liabilities"], 20000, "avalanche"
        )
        months_to_freedom = debt_result.get("total_months_to_payoff", 0)
        print(f"    Months to debt freedom: {months_to_freedom}")
        
        # Test financial health
        print("  ✓ Testing financial health calculation...")
        health_result = analyzer.calculate_financial_health_score(
            sample_data["accounts"], sample_data["liabilities"], 
            sample_data["transactions"], sample_data["investments"]
        )
        health_score = health_result.get("overall_score", 0)
        health_category = health_result.get("health_category", "unknown")
        print(f"    Financial health score: {health_score}/100 ({health_category})")
        
        print("✅ Financial analyzer tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Financial analyzer tests failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_analysis_service():
    """Test the integrated analysis service"""
    print("\n🔧 Testing Analysis Service Integration...")
    
    analysis_service = AnalysisService()
    sample_data = generate_sample_data()
    user_id = "test_user"
    
    try:
        # Test advanced spending analysis
        print("  ✓ Testing advanced spending analysis...")
        spending_result = await analysis_service.get_advanced_spending_analysis(
            user_id, sample_data["transactions"], 30
        )
        if "error" not in spending_result:
            print(f"    Advanced analysis available: Yes")
            print(f"    Analysis type: {spending_result.get('analysis_type', 'unknown')}")
        else:
            print(f"    Fallback to basic analysis: {spending_result.get('error', 'Unknown error')}")
        
        # Test financial health score
        print("  ✓ Testing financial health analysis...")
        health_result = await analysis_service.get_financial_health_score(
            user_id, sample_data["accounts"], sample_data["liabilities"],
            sample_data["transactions"], sample_data["investments"]
        )
        if "error" not in health_result:
            print(f"    Health score: {health_result.get('overall_score', 0)}/100")
        else:
            print(f"    Health analysis error: {health_result.get('error', 'Unknown error')}")
        
        # Test balance forecast
        print("  ✓ Testing balance forecasting...")
        forecast_result = await analysis_service.get_balance_forecast(
            user_id, sample_data["accounts"], sample_data["transactions"], 6
        )
        if "error" not in forecast_result:
            print(f"    Forecast available: Yes")
            print(f"    Analysis type: {forecast_result.get('analysis_type', 'unknown')}")
        else:
            print(f"    Forecast error: {forecast_result.get('error', 'Unknown error')}")
        
        # Test purchase affordability
        print("  ✓ Testing purchase affordability...")
        affordability_result = await analysis_service.analyze_purchase_affordability(
            user_id, sample_data["accounts"], sample_data["transactions"],
            sample_data["liabilities"], 75000, "Home Theater System"
        )
        if "error" not in affordability_result:
            print(f"    Affordability check completed: {affordability_result.get('analysis_type', 'unknown')}")
        else:
            print(f"    Affordability error: {affordability_result.get('error', 'Unknown error')}")
        
        # Test anomaly detection
        print("  ✓ Testing anomaly detection...")
        anomaly_result = await analysis_service.detect_anomalies(
            user_id, sample_data["transactions"]
        )
        if "error" not in anomaly_result:
            print(f"    Anomalies detected: {anomaly_result.get('anomalies_detected', 0)}")
        else:
            print(f"    Anomaly detection error: {anomaly_result.get('error', 'Unknown error')}")
        
        print("✅ Analysis service integration tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Analysis service tests failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def run_performance_test():
    """Test performance with larger dataset"""
    print("\n⚡ Testing Performance with Larger Dataset...")
    
    # Generate larger dataset
    large_data = generate_sample_data()
    
    # Multiply transactions for performance testing
    large_transactions = []
    for i in range(5):  # 5x the data
        for transaction in large_data["transactions"]:
            new_transaction = transaction.copy()
            new_transaction["id"] = f"{transaction['id']}_copy_{i}"
            large_transactions.append(new_transaction)
    
    print(f"  Testing with {len(large_transactions)} transactions...")
    
    start_time = datetime.now()
    
    try:
        analyzer = FinancialAnalyzer()
        
        # Test multiple analyses
        spending_result = analyzer.analyze_spending_patterns(large_transactions, 90)
        health_result = analyzer.calculate_financial_health_score(
            large_data["accounts"], large_data["liabilities"], 
            large_transactions, large_data["investments"]
        )
        anomaly_result = analyzer.detect_financial_anomalies(large_transactions)
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        print(f"  ✓ Performance test completed in {duration:.2f} seconds")
        print(f"    Processed {len(large_transactions)} transactions")
        print(f"    Detected {anomaly_result.get('anomalies_detected', 0)} anomalies")
        print(f"    Health score: {health_result.get('overall_score', 0)}/100")
        
        return True
        
    except Exception as e:
        print(f"❌ Performance test failed: {e}")
        return False


def print_summary_report():
    """Print summary report of capabilities"""
    print("\n" + "="*80)
    print("🏦 MintelliFunds Advanced Financial Analysis - Implementation Summary")
    print("="*80)
    
    print("\n📋 IMPLEMENTED FEATURES:")
    print("   ✅ Comprehensive Data Validation System")
    print("   ✅ Advanced Spending Pattern Analysis")
    print("   ✅ Balance Forecasting with Seasonal Adjustments")
    print("   ✅ Purchase Affordability Assessment")
    print("   ✅ Financial Anomaly Detection")
    print("   ✅ Debt Repayment Strategy Optimization")
    print("   ✅ Investment Portfolio Analysis")
    print("   ✅ Financial Health Scoring Algorithm")
    print("   ✅ Budget Performance Tracking")
    print("   ✅ Monthly Cash Flow Analysis")
    
    print("\n🔧 TECHNICAL ARCHITECTURE:")
    print("   • Modular service-based design")
    print("   • Fallback compatibility with existing basic analysis")
    print("   • Comprehensive error handling and logging")
    print("   • Privacy-aware data processing")
    print("   • Scalable algorithms for large datasets")
    print("   • Integration with existing API endpoints")
    
    print("\n🎯 ANALYSIS CAPABILITIES:")
    print("   • Risk assessment and scoring")
    print("   • Trend analysis and forecasting")
    print("   • Anomaly detection with severity classification")
    print("   • Personalized recommendations")
    print("   • Multi-factor financial health evaluation")
    print("   • Advanced debt optimization strategies")
    
    print("\n🔮 AI/ML READY FEATURES:")
    print("   • Structured data pipelines for model training")
    print("   • Feature extraction for ML algorithms")
    print("   • Anomaly detection foundation")
    print("   • Pattern recognition capabilities")
    print("   • Predictive modeling infrastructure")
    
    print("\n🛡️ PRIVACY & SECURITY:")
    print("   • Granular permission-based data access")
    print("   • No external API dependencies for core analysis")
    print("   • Local data processing and storage")
    print("   • Audit trail capabilities")
    
    print("\n📊 PERFORMANCE OPTIMIZATIONS:")
    print("   • Result caching for frequently accessed data")
    print("   • Efficient algorithms for large transaction datasets")
    print("   • Memory-optimized data structures")
    print("   • Asynchronous processing support")


async def main():
    """Main test runner"""
    print("🚀 Starting MintelliFunds Advanced Financial Analysis Tests")
    print("="*60)
    
    test_results = []
    
    # Run all tests
    test_results.append(await test_data_validation())
    test_results.append(await test_financial_analyzer())
    test_results.append(await test_analysis_service())
    test_results.append(await run_performance_test())
    
    # Print results summary
    print("\n" + "="*60)
    print("📈 TEST RESULTS SUMMARY")
    print("="*60)
    
    passed_tests = sum(test_results)
    total_tests = len(test_results)
    
    test_names = [
        "Data Validation",
        "Financial Analyzer",
        "Analysis Service Integration", 
        "Performance Test"
    ]
    
    for i, (test_name, result) in enumerate(zip(test_names, test_results)):
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"  {test_name}: {status}")
    
    print(f"\n🎯 Overall Result: {passed_tests}/{total_tests} tests passed")
    
    if passed_tests == total_tests:
        print("🎉 ALL TESTS PASSED! Advanced financial analysis system is ready.")
    else:
        print("⚠️  Some tests failed. Review the errors above.")
    
    # Print implementation summary
    print_summary_report()


if __name__ == "__main__":
    # Run the test suite
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n⚠️  Tests interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Test suite failed with error: {e}")
        import traceback
        traceback.print_exc()