"""
Enhanced Data Ingestion Service for MintelliFunds
Provides comprehensive data loading, validation, normalization, and transformation capabilities
"""

import json
import csv
import os
import logging
import asyncio
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional, Union, Tuple
from pathlib import Path
from dataclasses import dataclass
from enum import Enum
import hashlib

# Import our validation service
from .data_validator import DataValidator

logger = logging.getLogger(__name__)


class DataSourceType(Enum):
    """Enumeration of supported data source types"""
    JSON = "json"
    CSV = "csv"
    API = "api"
    DATABASE = "database"
    MOCK = "mock"


class DataIngestionStatus(Enum):
    """Enumeration of data ingestion statuses"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    PARTIAL = "partial"


@dataclass
class DataIngestionResult:
    """Result of a data ingestion operation"""
    status: DataIngestionStatus
    total_records: int
    successful_records: int
    failed_records: int
    validation_errors: List[Dict[str, Any]]
    processing_time: float
    data_hash: str
    metadata: Dict[str, Any]


@dataclass
class DataSourceConfig:
    """Configuration for a data source"""
    name: str
    source_type: DataSourceType
    path_or_url: str
    schema_name: str
    enabled: bool = True
    refresh_interval: Optional[int] = None  # seconds
    last_updated: Optional[datetime] = None
    metadata: Optional[Dict[str, Any]] = None


class DataIngestionService:
    """Enhanced data ingestion service with comprehensive validation and normalization"""

    def __init__(self, data_dir: str = "data", validator: DataValidator = None):
        """
        Initialize the enhanced data ingestion service
        
        Args:
            data_dir: Directory containing data files
            validator: Data validator instance
        """
        self.data_dir = Path(data_dir)
        self.validator = validator or DataValidator()
        self._data_cache = {}
        self._ingestion_history = []
        self._source_configs = {}
        
        # Initialize default data source configurations
        self._initialize_default_sources()

    def _initialize_default_sources(self):
        """Initialize default data source configurations"""
        default_sources = [
            DataSourceConfig(
                name="transactions",
                source_type=DataSourceType.JSON,
                path_or_url="transactions.json",
                schema_name="transaction"
            ),
            DataSourceConfig(
                name="accounts",
                source_type=DataSourceType.JSON,
                path_or_url="accounts.json",
                schema_name="account"
            ),
            DataSourceConfig(
                name="investments",
                source_type=DataSourceType.JSON,
                path_or_url="investments.json",
                schema_name="investment"
            ),
            DataSourceConfig(
                name="liabilities",
                source_type=DataSourceType.JSON,
                path_or_url="liabilities.json",
                schema_name="liability"
            ),
            DataSourceConfig(
                name="assets",
                source_type=DataSourceType.JSON,
                path_or_url="assets.json",
                schema_name="asset"
            )
        ]
        
        for config in default_sources:
            self._source_configs[config.name] = config

    def register_data_source(self, config: DataSourceConfig):
        """
        Register a new data source configuration
        
        Args:
            config: Data source configuration
        """
        self._source_configs[config.name] = config
        logger.info(f"Registered data source: {config.name} ({config.source_type.value})")

    async def ingest_all_data(self, force_refresh: bool = False) -> Dict[str, DataIngestionResult]:
        """
        Ingest data from all registered sources
        
        Args:
            force_refresh: Force refresh even if data is cached
            
        Returns:
            Dictionary mapping source names to ingestion results
        """
        ingestion_results = {}
        
        logger.info(f"Starting ingestion of {len(self._source_configs)} data sources")
        
        # Process all sources concurrently
        enabled_sources = [(name, config) for name, config in self._source_configs.items() if config.enabled]
        tasks = [self.ingest_data_source(name, force_refresh) for name, config in enabled_sources]
        
        if tasks:
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            for i, (source_name, _) in enumerate(enabled_sources):
                result = results[i]
                if isinstance(result, Exception):
                    logger.error(f"Failed to ingest {source_name}: {result}")
                    ingestion_results[source_name] = DataIngestionResult(
                        status=DataIngestionStatus.FAILED,
                        total_records=0,
                        successful_records=0,
                        failed_records=0,
                        validation_errors=[{"error": str(result)}],
                        processing_time=0.0,
                        data_hash="",
                        metadata={"error": str(result)}
                    )
                else:
                    ingestion_results[source_name] = result
        
        # Update ingestion history
        self._ingestion_history.append({
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "sources_processed": len(ingestion_results),
            "results": {name: result.status.value for name, result in ingestion_results.items()}
        })
        
        return ingestion_results

    async def ingest_data_source(self, source_name: str, force_refresh: bool = False) -> DataIngestionResult:
        """
        Ingest data from a specific source
        
        Args:
            source_name: Name of the data source
            force_refresh: Force refresh even if data is cached
            
        Returns:
            Data ingestion result
        """
        start_time = datetime.now()
        
        if source_name not in self._source_configs:
            raise ValueError(f"Unknown data source: {source_name}")
        
        config = self._source_configs[source_name]
        
        # Check if refresh is needed
        if not force_refresh and self._is_data_fresh(config):
            cached_data = self._data_cache.get(source_name, [])
            if cached_data:  # Only use cache if it has actual data
                logger.info(f"Using cached data for {source_name}")
                return DataIngestionResult(
                    status=DataIngestionStatus.COMPLETED,
                    total_records=len(cached_data) if isinstance(cached_data, list) else 1,
                    successful_records=len(cached_data) if isinstance(cached_data, list) else 1,
                    failed_records=0,
                    validation_errors=[],
                    processing_time=0.0,
                    data_hash=self._calculate_data_hash(cached_data),
                    metadata={"source": "cache"}
                )
        
        logger.info(f"Ingesting data from {source_name} ({config.source_type.value})")
        
        try:
            # Load raw data
            raw_data = await self._load_raw_data(config)
            
            # Validate and normalize data
            if isinstance(raw_data, list):
                validation_result = await self._validate_bulk_data(raw_data, config.schema_name)
            else:
                validation_result = await self._validate_single_data(raw_data, config.schema_name)
            
            # Store validated data in cache
            self._data_cache[source_name] = validation_result["valid_data"]
            config.last_updated = datetime.now(timezone.utc)
            
            processing_time = (datetime.now() - start_time).total_seconds()
            
            return DataIngestionResult(
                status=DataIngestionStatus.COMPLETED if validation_result["failed_records"] == 0 else DataIngestionStatus.PARTIAL,
                total_records=validation_result["total_records"],
                successful_records=validation_result["successful_records"],
                failed_records=validation_result["failed_records"],
                validation_errors=validation_result["errors"],
                processing_time=processing_time,
                data_hash=self._calculate_data_hash(validation_result["valid_data"]),
                metadata={
                    "source_type": config.source_type.value,
                    "source_path": config.path_or_url,
                    "schema": config.schema_name
                }
            )
            
        except Exception as e:
            processing_time = (datetime.now() - start_time).total_seconds()
            logger.error(f"Error ingesting data from {source_name}: {e}")
            
            return DataIngestionResult(
                status=DataIngestionStatus.FAILED,
                total_records=0,
                successful_records=0,
                failed_records=0,
                validation_errors=[{"error": str(e)}],
                processing_time=processing_time,
                data_hash="",
                metadata={"error": str(e)}
            )

    async def _load_raw_data(self, config: DataSourceConfig) -> Union[List[Dict], Dict]:
        """
        Load raw data from the configured source
        
        Args:
            config: Data source configuration
            
        Returns:
            Raw data from the source
        """
        if config.source_type == DataSourceType.JSON:
            return await self._load_json_data(config)
        elif config.source_type == DataSourceType.CSV:
            return await self._load_csv_data(config)
        elif config.source_type == DataSourceType.MOCK:
            return await self._load_mock_data(config)
        else:
            raise NotImplementedError(f"Data source type {config.source_type} not implemented")

    async def _load_json_data(self, config: DataSourceConfig) -> Union[List[Dict], Dict]:
        """Load data from JSON file"""
        file_path = self.data_dir / config.path_or_url
        
        if not file_path.exists():
            logger.warning(f"JSON file not found: {file_path}")
            return []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            logger.info(f"Loaded JSON data from {file_path}")
            return data
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in {file_path}: {e}")
            raise ValueError(f"Invalid JSON format: {e}")
        except Exception as e:
            logger.error(f"Error reading {file_path}: {e}")
            raise

    async def _load_csv_data(self, config: DataSourceConfig) -> List[Dict]:
        """Load data from CSV file"""
        file_path = self.data_dir / config.path_or_url
        
        if not file_path.exists():
            logger.warning(f"CSV file not found: {file_path}")
            return []
        
        try:
            data = []
            with open(file_path, 'r', encoding='utf-8', newline='') as f:
                reader = csv.DictReader(f)
                for row_num, row in enumerate(reader, start=1):
                    if row:  # Skip empty rows
                        row['_source_row'] = row_num
                        data.append(row)
            
            logger.info(f"Loaded {len(data)} records from CSV: {file_path}")
            return data
        except Exception as e:
            logger.error(f"Error reading CSV {file_path}: {e}")
            raise

    async def _load_mock_data(self, config: DataSourceConfig) -> List[Dict]:
        """Generate mock data for testing"""
        mock_data_generators = {
            "transaction": self._generate_mock_transactions,
            "account": self._generate_mock_accounts,
            "investment": self._generate_mock_investments,
            "liability": self._generate_mock_liabilities,
            "asset": self._generate_mock_assets
        }
        
        generator = mock_data_generators.get(config.schema_name)
        if generator:
            return generator()
        else:
            logger.warning(f"No mock data generator for schema: {config.schema_name}")
            return []

    async def _validate_bulk_data(self, data: List[Dict], schema_name: str) -> Dict[str, Any]:
        """
        Validate and normalize bulk data
        
        Args:
            data: List of data items to validate
            schema_name: Schema to validate against
            
        Returns:
            Validation result dictionary
        """
        validation_result = self.validator.validate_bulk_data(data, schema_name)
        
        return {
            "total_records": validation_result["total_count"],
            "successful_records": validation_result["valid_count"],
            "failed_records": validation_result["invalid_count"],
            "valid_data": [item["data"] for item in validation_result["valid_items"]],
            "errors": validation_result["summary_errors"]
        }

    async def _validate_single_data(self, data: Dict, schema_name: str) -> Dict[str, Any]:
        """
        Validate and normalize single data item
        
        Args:
            data: Data item to validate
            schema_name: Schema to validate against
            
        Returns:
            Validation result dictionary
        """
        validation_result = self.validator.validate_data(data, schema_name)
        
        if validation_result["valid"]:
            return {
                "total_records": 1,
                "successful_records": 1,
                "failed_records": 0,
                "valid_data": validation_result["normalized_data"],
                "errors": []
            }
        else:
            return {
                "total_records": 1,
                "successful_records": 0,
                "failed_records": 1,
                "valid_data": {},
                "errors": validation_result["errors"]
            }

    def _is_data_fresh(self, config: DataSourceConfig) -> bool:
        """
        Check if cached data is still fresh based on refresh interval
        
        Args:
            config: Data source configuration
            
        Returns:
            True if data is fresh, False if refresh is needed
        """
        # Check if we have cached data
        if config.name not in self._data_cache:
            return False  # No cached data
        
        # If no refresh interval is set, cache is always fresh (once loaded)
        if config.refresh_interval is None:
            return config.last_updated is not None
        
        # If never loaded before
        if config.last_updated is None:
            return False
        
        # Check if data is within refresh interval
        time_since_update = (datetime.now(timezone.utc) - config.last_updated).total_seconds()
        return time_since_update < config.refresh_interval

    def _calculate_data_hash(self, data: Any) -> str:
        """
        Calculate hash of data for integrity checking
        
        Args:
            data: Data to hash
            
        Returns:
            SHA-256 hash of the data
        """
        try:
            data_str = json.dumps(data, sort_keys=True, default=str)
            return hashlib.sha256(data_str.encode()).hexdigest()
        except Exception:
            return ""

    def get_cached_data(self, source_name: str) -> Any:
        """
        Get cached data for a specific source
        
        Args:
            source_name: Name of the data source
            
        Returns:
            Cached data or empty list if not found
        """
        return self._data_cache.get(source_name, [])

    def get_all_cached_data(self) -> Dict[str, Any]:
        """
        Get all cached data
        
        Returns:
            Dictionary containing all cached data
        """
        return self._data_cache.copy()

    def get_ingestion_history(self) -> List[Dict[str, Any]]:
        """
        Get history of data ingestion operations
        
        Returns:
            List of ingestion history entries
        """
        return self._ingestion_history.copy()

    def get_data_source_status(self) -> Dict[str, Dict[str, Any]]:
        """
        Get status of all configured data sources
        
        Returns:
            Dictionary mapping source names to status information
        """
        status = {}
        for name, config in self._source_configs.items():
            cached_data = self._data_cache.get(name, [])
            status[name] = {
                "enabled": config.enabled,
                "source_type": config.source_type.value,
                "schema": config.schema_name,
                "last_updated": config.last_updated.isoformat() if config.last_updated else None,
                "cached_records": len(cached_data) if isinstance(cached_data, list) else 1 if cached_data else 0,
                "data_hash": self._calculate_data_hash(cached_data)
            }
        return status

    # Mock data generators for testing
    def _generate_mock_transactions(self) -> List[Dict]:
        """Generate mock transaction data"""
        from datetime import timedelta
        import random
        
        transactions = []
        base_date = datetime.now() - timedelta(days=90)
        
        categories = ["food_dining", "transportation", "bills_utilities", "entertainment", "shopping", "healthcare"]
        
        for i in range(100):
            date = base_date + timedelta(days=random.randint(0, 90))
            amount = -round(random.uniform(100, 5000), 2)
            category = random.choice(categories)
            
            transactions.append({
                "id": f"mock_txn_{i:04d}",
                "date": date.isoformat(),
                "amount": amount,
                "description": f"Mock {category} transaction",
                "category": category,
                "type": "expense"
            })
        
        return transactions

    def _generate_mock_accounts(self) -> List[Dict]:
        """Generate mock account data"""
        return [
            {
                "id": "mock_acc_001",
                "name": "Primary Savings",
                "type": "savings",
                "balance": 125000.50,
                "currency": "INR",
                "bank": "Mock Bank"
            },
            {
                "id": "mock_acc_002",
                "name": "Current Account",
                "type": "current",
                "balance": 45000.25,
                "currency": "INR",
                "bank": "Mock Bank"
            }
        ]

    def _generate_mock_investments(self) -> List[Dict]:
        """Generate mock investment data"""
        return [
            {
                "id": "mock_inv_001",
                "name": "Mock Equity Fund",
                "type": "mutual_fund",
                "current_value": 85000.00,
                "units": 1250.75,
                "purchase_price": 80000.00
            }
        ]

    def _generate_mock_liabilities(self) -> List[Dict]:
        """Generate mock liability data"""
        return [
            {
                "id": "mock_loan_001",
                "name": "Mock Home Loan",
                "type": "home_loan",
                "balance": 2500000.00,
                "interest_rate": 7.5,
                "monthly_payment": 18500.00
            }
        ]

    def _generate_mock_assets(self) -> List[Dict]:
        """Generate mock asset data"""
        return [
            {
                "id": "mock_asset_001",
                "name": "Mock Property",
                "type": "property",
                "value": 3500000.00,
                "purchase_date": "2020-01-15"
            }
        ]

    async def export_data(self, source_name: str, export_path: str, format: str = "json") -> bool:
        """
        Export cached data to file
        
        Args:
            source_name: Name of the data source to export
            export_path: Path to export the data to
            format: Export format ("json" or "csv")
            
        Returns:
            True if export successful, False otherwise
        """
        try:
            data = self.get_cached_data(source_name)
            
            if format.lower() == "json":
                with open(export_path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, default=str)
            elif format.lower() == "csv" and isinstance(data, list) and data:
                import pandas as pd
                df = pd.DataFrame(data)
                df.to_csv(export_path, index=False)
            else:
                raise ValueError(f"Unsupported export format: {format}")
            
            logger.info(f"Exported {source_name} data to {export_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error exporting data: {e}")
            return False

    def clear_cache(self, source_name: str = None):
        """
        Clear cached data
        
        Args:
            source_name: Specific source to clear, or None to clear all
        """
        if source_name:
            if source_name in self._data_cache:
                del self._data_cache[source_name]
                logger.info(f"Cleared cache for {source_name}")
        else:
            self._data_cache.clear()
            logger.info("Cleared all cached data")