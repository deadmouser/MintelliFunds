#!/usr/bin/env python3
"""
Debug Test Script for Enhanced Data Ingestion Service
Simple test to identify and fix issues
"""

import asyncio
import sys
import os
import json
import tempfile
from pathlib import Path
from datetime import datetime

# Add the backend directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "app"))

try:
    from services.data_ingestion_service import (
        DataIngestionService, DataSourceConfig, DataSourceType, DataIngestionStatus
    )
    from services.data_validator import DataValidator
    print("✅ Imports successful")
except ImportError as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)


async def test_basic_functionality():
    """Test basic functionality step by step"""
    print("🔧 Testing basic functionality...")
    
    # Create temporary directory
    temp_dir = Path(tempfile.mkdtemp())
    print(f"   Created temp directory: {temp_dir}")
    
    try:
        # Create simple test data
        test_transactions = [
            {
                "id": "test_001",
                "date": datetime.now().isoformat(),
                "amount": -1000.0,
                "description": "Test Transaction",
                "category": "food_dining",
                "type": "expense"
            }
        ]
        
        # Write test data to file
        with open(temp_dir / "transactions.json", 'w') as f:
            json.dump(test_transactions, f)
        print("   ✅ Created test data file")
        
        # Initialize data validator
        validator = DataValidator()
        print("   ✅ DataValidator initialized")
        
        # Test basic validation
        validation_result = validator.validate_data(test_transactions[0], "transaction")
        print(f"   ✅ Validation result: {validation_result['valid']}")
        
        # Initialize data ingestion service
        ingestion_service = DataIngestionService(data_dir=str(temp_dir), validator=validator)
        print("   ✅ DataIngestionService initialized")
        
        # Test single data source ingestion
        print("   🔄 Testing single source ingestion...")
        result = await ingestion_service.ingest_data_source("transactions")
        
        print(f"   📊 Ingestion result:")
        print(f"      Status: {result.status}")
        print(f"      Total records: {result.total_records}")
        print(f"      Successful: {result.successful_records}")
        print(f"      Failed: {result.failed_records}")
        print(f"      Processing time: {result.processing_time:.4f}s")
        print(f"      Errors: {result.validation_errors}")
        
        # Test cached data
        cached_data = ingestion_service.get_cached_data("transactions")
        print(f"   💾 Cached data: {len(cached_data)} items")
        
        print("✅ Basic functionality test completed successfully")
        return True
        
    except Exception as e:
        print(f"❌ Basic functionality test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
        
    finally:
        # Cleanup
        import shutil
        if temp_dir.exists():
            shutil.rmtree(temp_dir)
            print(f"   🧹 Cleaned up: {temp_dir}")


async def test_dataclass_creation():
    """Test dataclass creation"""
    print("🔧 Testing dataclass creation...")
    
    try:
        # Test DataSourceConfig creation
        config = DataSourceConfig(
            name="test",
            source_type=DataSourceType.JSON,
            path_or_url="test.json",
            schema_name="transaction"
        )
        print(f"   ✅ DataSourceConfig created: {config.name}")
        
        # Test DataIngestionResult creation
        from services.data_ingestion_service import DataIngestionResult
        result = DataIngestionResult(
            status=DataIngestionStatus.COMPLETED,
            total_records=1,
            successful_records=1,
            failed_records=0,
            validation_errors=[],
            processing_time=0.001,
            data_hash="test_hash",
            metadata={"test": "data"}
        )
        print(f"   ✅ DataIngestionResult created: {result.status}")
        
        print("✅ Dataclass creation test completed successfully")
        return True
        
    except Exception as e:
        print(f"❌ Dataclass creation test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """Main test runner"""
    print("🚀 Starting Debug Tests for Enhanced Data Ingestion Service")
    print("="*60)
    
    tests = [
        ("Dataclass Creation", test_dataclass_creation()),
        ("Basic Functionality", test_basic_functionality()),
    ]
    
    results = []
    
    for test_name, test_coro in tests:
        print(f"\n🧪 Running: {test_name}")
        try:
            result = await test_coro
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ Test {test_name} crashed: {e}")
            results.append((test_name, False))
    
    # Print summary
    print("\n" + "="*60)
    print("📋 DEBUG TEST SUMMARY")
    print("="*60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"   {test_name}: {status}")
    
    print(f"\n🎯 Overall Result: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All debug tests passed! Issues resolved.")
    else:
        print("⚠️ Some tests failed. Further debugging needed.")


if __name__ == "__main__":
    asyncio.run(main())