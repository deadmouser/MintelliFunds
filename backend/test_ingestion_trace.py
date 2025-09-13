#!/usr/bin/env python3
"""
Trace test to identify exact issue in data ingestion
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


async def trace_validation_issue():
    """Trace step by step to find where the issue occurs"""
    print("🔍 Tracing validation issue...")
    
    # Create test data
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
    
    print(f"📋 Test data: {json.dumps(test_transactions[0], indent=2)}")
    
    # Initialize validator
    validator = DataValidator()
    
    # Test single validation
    print("\n🔍 Testing single validation...")
    single_result = validator.validate_data(test_transactions[0], "transaction")
    print(f"   Valid: {single_result['valid']}")
    print(f"   Errors: {single_result['errors']}")
    if single_result['valid']:
        print(f"   Normalized data: {json.dumps(single_result['normalized_data'], indent=2, default=str)}")
    
    # Test bulk validation
    print("\n🔍 Testing bulk validation...")
    bulk_result = validator.validate_bulk_data(test_transactions, "transaction")
    print(f"   Total count: {bulk_result['total_count']}")
    print(f"   Valid count: {bulk_result['valid_count']}")
    print(f"   Invalid count: {bulk_result['invalid_count']}")
    print(f"   Valid items: {len(bulk_result['valid_items'])}")
    print(f"   Invalid items: {len(bulk_result['invalid_items'])}")
    
    if bulk_result['valid_items']:
        print(f"   First valid item: {json.dumps(bulk_result['valid_items'][0], indent=2, default=str)}")
    if bulk_result['invalid_items']:
        print(f"   First invalid item: {json.dumps(bulk_result['invalid_items'][0], indent=2, default=str)}")
    
    # Test data ingestion service validation wrapper
    temp_dir = Path(tempfile.mkdtemp())
    try:
        with open(temp_dir / "transactions.json", 'w') as f:
            json.dump(test_transactions, f)
        
        ingestion_service = DataIngestionService(data_dir=str(temp_dir), validator=validator)
        
        print("\n🔍 Testing data ingestion service validation wrapper...")
        ingestion_validation_result = await ingestion_service._validate_bulk_data(test_transactions, "transaction")
        print(f"   Total records: {ingestion_validation_result['total_records']}")
        print(f"   Successful records: {ingestion_validation_result['successful_records']}")
        print(f"   Failed records: {ingestion_validation_result['failed_records']}")
        print(f"   Valid data: {len(ingestion_validation_result['valid_data'])}")
        print(f"   Errors: {ingestion_validation_result['errors']}")
        
        if ingestion_validation_result['valid_data']:
            print(f"   First valid data item: {json.dumps(ingestion_validation_result['valid_data'][0], indent=2, default=str)}")
        
        # Test full ingestion
        print("\n🔍 Testing full ingestion process...")
        ingestion_result = await ingestion_service.ingest_data_source("transactions")
        print(f"   Status: {ingestion_result.status}")
        print(f"   Total records: {ingestion_result.total_records}")
        print(f"   Successful records: {ingestion_result.successful_records}")
        print(f"   Failed records: {ingestion_result.failed_records}")
        print(f"   Processing time: {ingestion_result.processing_time:.4f}s")
        print(f"   Data hash: {ingestion_result.data_hash}")
        print(f"   Metadata: {ingestion_result.metadata}")
        
        # Check cached data
        cached_data = ingestion_service.get_cached_data("transactions")
        print(f"   Cached data length: {len(cached_data)}")
        if cached_data:
            print(f"   First cached item: {json.dumps(cached_data[0], indent=2, default=str)}")
        
    finally:
        import shutil
        if temp_dir.exists():
            shutil.rmtree(temp_dir)


if __name__ == "__main__":
    asyncio.run(trace_validation_issue())