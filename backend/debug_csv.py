#!/usr/bin/env python3
"""
Debug CSV ingestion issue
"""

import asyncio
import sys
import os
import csv
import tempfile
from pathlib import Path

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


async def debug_csv_ingestion():
    """Debug CSV ingestion step by step"""
    print("🔍 Debugging CSV ingestion...")
    
    # Create temporary directory
    temp_dir = Path(tempfile.mkdtemp())
    print(f"   Created temp directory: {temp_dir}")
    
    try:
        # Create CSV test data
        investments_csv_data = [
            ["id", "name", "type", "current_value", "units", "purchase_price"],
            ["inv_001", "Test Equity Fund", "mutual_fund", "85000.00", "1250.75", "80000.00"],
            ["inv_002", "Test Debt Fund", "mutual_fund", "55000.00", "2500.00", "50000.00"],
        ]
        
        csv_file_path = temp_dir / "investments.csv"
        with open(csv_file_path, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerows(investments_csv_data)
        
        print(f"   ✅ Created CSV file: {csv_file_path}")
        
        # Initialize services
        validator = DataValidator()
        ingestion_service = DataIngestionService(data_dir=str(temp_dir), validator=validator)
        
        # Register CSV data source
        csv_config = DataSourceConfig(
            name="investments_csv",
            source_type=DataSourceType.CSV,
            path_or_url="investments.csv",
            schema_name="investment"
        )
        ingestion_service.register_data_source(csv_config)
        print("   ✅ Registered CSV data source")
        
        # Test CSV loading first
        print("\n🔍 Testing raw CSV loading...")
        raw_data = await ingestion_service._load_csv_data(csv_config)
        print(f"   Raw CSV data loaded: {len(raw_data)} records")
        if raw_data:
            print(f"   First record: {raw_data[0]}")
        
        # Test validation on first CSV record
        if raw_data:
            print("\n🔍 Testing validation on first CSV record...")
            first_record = raw_data[0]
            validation_result = validator.validate_data(first_record, "investment")
            print(f"   Valid: {validation_result['valid']}")
            print(f"   Errors: {validation_result['errors']}")
            if validation_result['valid']:
                print(f"   Normalized: {validation_result['normalized_data']}")
        
        # Test full ingestion
        print("\n🔍 Testing full CSV ingestion...")
        result = await ingestion_service.ingest_data_source("investments_csv")
        
        print(f"   Status: {result.status}")
        print(f"   Total records: {result.total_records}")
        print(f"   Successful records: {result.successful_records}")
        print(f"   Failed records: {result.failed_records}")
        print(f"   Validation errors: {result.validation_errors}")
        print(f"   Processing time: {result.processing_time:.4f}s")
        
        # Check cached data
        cached_data = ingestion_service.get_cached_data("investments_csv")
        print(f"   Cached data: {len(cached_data)} records")
        if cached_data:
            print(f"   First cached record: {cached_data[0]}")
        
    except Exception as e:
        print(f"❌ Debug failed: {e}")
        import traceback
        traceback.print_exc()
        
    finally:
        # Cleanup
        import shutil
        if temp_dir.exists():
            shutil.rmtree(temp_dir)
            print(f"   🧹 Cleaned up: {temp_dir}")


if __name__ == "__main__":
    asyncio.run(debug_csv_ingestion())