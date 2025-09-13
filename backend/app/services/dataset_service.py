"""
Dataset Integration Service for MintelliFunds
Handles custom dataset loading, processing, and LLM integration
"""
import logging
import json
import os
from pathlib import Path
from typing import Dict, Any, List, Optional, Union
from datetime import datetime
import pandas as pd
import numpy as np
from dataclasses import dataclass, field
from enum import Enum

logger = logging.getLogger(__name__)

class DatasetType(Enum):
    """Supported dataset types"""
    FINANCIAL_TRANSACTIONS = "financial_transactions"
    MARKET_DATA = "market_data"
    USER_BEHAVIOR = "user_behavior"
    AI_TRAINING_DATA = "ai_training_data"
    CUSTOM_FINANCIAL_KNOWLEDGE = "custom_financial_knowledge"

class DatasetFormat(Enum):
    """Supported dataset formats"""
    CSV = "csv"
    JSON = "json"
    PARQUET = "parquet"
    JSONL = "jsonl"
    PICKLE = "pickle"

@dataclass
class DatasetMetadata:
    """Dataset metadata structure"""
    name: str
    type: DatasetType
    format: DatasetFormat
    version: str
    description: str
    file_path: str
    size_mb: float
    record_count: int
    columns: List[str]
    created_at: datetime
    updated_at: datetime
    schema: Dict[str, Any] = field(default_factory=dict)
    tags: List[str] = field(default_factory=list)
    preprocessing_config: Dict[str, Any] = field(default_factory=dict)

class DatasetService:
    """Service for managing custom datasets and LLM integration"""
    
    def __init__(self, datasets_directory: str = "data/datasets"):
        """
        Initialize dataset service
        
        Args:
            datasets_directory: Directory where datasets are stored
        """
        self.datasets_directory = Path(datasets_directory)
        self.datasets_directory.mkdir(parents=True, exist_ok=True)
        
        self.loaded_datasets: Dict[str, Dict[str, Any]] = {}
        self.dataset_metadata: Dict[str, DatasetMetadata] = {}
        
        # Initialize directories
        self._initialize_directories()
        
        # Load existing dataset metadata
        self._load_dataset_metadata()
        
    def _initialize_directories(self):
        """Initialize required directories for dataset management"""
        directories = [
            self.datasets_directory / "raw",
            self.datasets_directory / "processed", 
            self.datasets_directory / "embeddings",
            self.datasets_directory / "models",
            self.datasets_directory / "cache",
            self.datasets_directory / "exports"
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
            
        logger.info(f"Dataset directories initialized at: {self.datasets_directory}")
    
    def _load_dataset_metadata(self):
        """Load dataset metadata from storage"""
        metadata_file = self.datasets_directory / "metadata.json"
        
        if metadata_file.exists():
            try:
                with open(metadata_file, 'r') as f:
                    metadata_dict = json.load(f)
                
                for name, meta in metadata_dict.items():
                    self.dataset_metadata[name] = DatasetMetadata(
                        name=meta["name"],
                        type=DatasetType(meta["type"]),
                        format=DatasetFormat(meta["format"]),
                        version=meta["version"],
                        description=meta["description"],
                        file_path=meta["file_path"],
                        size_mb=meta["size_mb"],
                        record_count=meta["record_count"],
                        columns=meta["columns"],
                        created_at=datetime.fromisoformat(meta["created_at"]),
                        updated_at=datetime.fromisoformat(meta["updated_at"]),
                        schema=meta.get("schema", {}),
                        tags=meta.get("tags", []),
                        preprocessing_config=meta.get("preprocessing_config", {})
                    )
                    
                logger.info(f"Loaded metadata for {len(self.dataset_metadata)} datasets")
                
            except Exception as e:
                logger.error(f"Error loading dataset metadata: {e}")
    
    def _save_dataset_metadata(self):
        """Save dataset metadata to storage"""
        metadata_file = self.datasets_directory / "metadata.json"
        
        try:
            metadata_dict = {}
            for name, meta in self.dataset_metadata.items():
                metadata_dict[name] = {
                    "name": meta.name,
                    "type": meta.type.value,
                    "format": meta.format.value,
                    "version": meta.version,
                    "description": meta.description,
                    "file_path": meta.file_path,
                    "size_mb": meta.size_mb,
                    "record_count": meta.record_count,
                    "columns": meta.columns,
                    "created_at": meta.created_at.isoformat(),
                    "updated_at": meta.updated_at.isoformat(),
                    "schema": meta.schema,
                    "tags": meta.tags,
                    "preprocessing_config": meta.preprocessing_config
                }
            
            with open(metadata_file, 'w') as f:
                json.dump(metadata_dict, f, indent=2)
                
            logger.info("Dataset metadata saved successfully")
            
        except Exception as e:
            logger.error(f"Error saving dataset metadata: {e}")
    
    def register_dataset(
        self,
        name: str,
        file_path: str,
        dataset_type: DatasetType,
        dataset_format: DatasetFormat,
        description: str = "",
        version: str = "1.0.0",
        tags: List[str] = None,
        preprocessing_config: Dict[str, Any] = None
    ) -> bool:
        """
        Register a new dataset
        
        Args:
            name: Dataset name
            file_path: Path to dataset file
            dataset_type: Type of dataset
            dataset_format: Format of dataset
            description: Dataset description
            version: Dataset version
            tags: Dataset tags
            preprocessing_config: Preprocessing configuration
            
        Returns:
            Success status
        """
        try:
            file_path_obj = Path(file_path)
            
            if not file_path_obj.exists():
                logger.error(f"Dataset file not found: {file_path}")
                return False
            
            # Get file size
            size_mb = file_path_obj.stat().st_size / (1024 * 1024)
            
            # Load and analyze dataset
            columns, record_count, schema = self._analyze_dataset(file_path, dataset_format)
            
            # Create metadata
            metadata = DatasetMetadata(
                name=name,
                type=dataset_type,
                format=dataset_format,
                version=version,
                description=description,
                file_path=str(file_path),
                size_mb=size_mb,
                record_count=record_count,
                columns=columns,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
                schema=schema,
                tags=tags or [],
                preprocessing_config=preprocessing_config or {}
            )
            
            self.dataset_metadata[name] = metadata
            self._save_dataset_metadata()
            
            logger.info(f"Dataset '{name}' registered successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error registering dataset '{name}': {e}")
            return False
    
    def _analyze_dataset(self, file_path: str, dataset_format: DatasetFormat) -> tuple:
        """
        Analyze dataset to extract metadata
        
        Args:
            file_path: Path to dataset file
            dataset_format: Format of dataset
            
        Returns:
            Tuple of (columns, record_count, schema)
        """
        try:
            if dataset_format == DatasetFormat.CSV:
                df = pd.read_csv(file_path, nrows=1000)  # Sample first 1000 rows for analysis
                columns = list(df.columns)
                record_count = len(pd.read_csv(file_path))
                schema = {col: str(df[col].dtype) for col in df.columns}
                
            elif dataset_format == DatasetFormat.JSON:
                with open(file_path, 'r') as f:
                    data = json.load(f)
                
                if isinstance(data, list) and data:
                    columns = list(data[0].keys()) if data else []
                    record_count = len(data)
                    schema = {col: type(data[0].get(col)).__name__ for col in columns}
                else:
                    columns = list(data.keys()) if isinstance(data, dict) else []
                    record_count = 1
                    schema = {col: type(data.get(col)).__name__ for col in columns}
                    
            elif dataset_format == DatasetFormat.JSONL:
                columns = []
                record_count = 0
                schema = {}
                
                with open(file_path, 'r') as f:
                    for i, line in enumerate(f):
                        if i == 0:  # First line for column analysis
                            first_record = json.loads(line.strip())
                            columns = list(first_record.keys())
                            schema = {col: type(first_record.get(col)).__name__ for col in columns}
                        record_count += 1
                        
            else:
                # Default fallback
                columns = []
                record_count = 0
                schema = {}
                
            return columns, record_count, schema
            
        except Exception as e:
            logger.error(f"Error analyzing dataset: {e}")
            return [], 0, {}
    
    def load_dataset(self, name: str, max_records: Optional[int] = None) -> Optional[Dict[str, Any]]:
        """
        Load dataset into memory
        
        Args:
            name: Dataset name
            max_records: Maximum number of records to load
            
        Returns:
            Loaded dataset or None
        """
        try:
            if name not in self.dataset_metadata:
                logger.error(f"Dataset '{name}' not found")
                return None
            
            metadata = self.dataset_metadata[name]
            
            # Check if already loaded
            if name in self.loaded_datasets:
                logger.info(f"Dataset '{name}' already loaded from cache")
                return self.loaded_datasets[name]
            
            # Load based on format
            if metadata.format == DatasetFormat.CSV:
                df = pd.read_csv(metadata.file_path, nrows=max_records)
                data = {
                    "data": df,
                    "metadata": metadata,
                    "type": "dataframe"
                }
                
            elif metadata.format == DatasetFormat.JSON:
                with open(metadata.file_path, 'r') as f:
                    json_data = json.load(f)
                
                if max_records and isinstance(json_data, list):
                    json_data = json_data[:max_records]
                
                data = {
                    "data": json_data,
                    "metadata": metadata,
                    "type": "json"
                }
                
            elif metadata.format == DatasetFormat.JSONL:
                records = []
                with open(metadata.file_path, 'r') as f:
                    for i, line in enumerate(f):
                        if max_records and i >= max_records:
                            break
                        records.append(json.loads(line.strip()))
                
                data = {
                    "data": records,
                    "metadata": metadata,
                    "type": "jsonl"
                }
                
            else:
                logger.error(f"Unsupported dataset format: {metadata.format}")
                return None
            
            # Cache loaded dataset
            self.loaded_datasets[name] = data
            
            logger.info(f"Dataset '{name}' loaded successfully")
            return data
            
        except Exception as e:
            logger.error(f"Error loading dataset '{name}': {e}")
            return None
    
    def get_dataset_for_llm_training(self, dataset_name: str) -> Optional[Dict[str, Any]]:
        """
        Prepare dataset specifically for LLM training/fine-tuning
        
        Args:
            dataset_name: Name of dataset
            
        Returns:
            LLM-ready dataset
        """
        try:
            dataset = self.load_dataset(dataset_name)
            if not dataset:
                return None
            
            metadata = dataset["metadata"]
            
            if metadata.type == DatasetType.AI_TRAINING_DATA:
                # Already formatted for AI training
                return {
                    "training_data": dataset["data"],
                    "format": "conversation" if "prompt" in metadata.columns else "completion",
                    "metadata": metadata
                }
            
            elif metadata.type == DatasetType.FINANCIAL_TRANSACTIONS:
                # Convert financial data to training format
                training_data = self._convert_financial_to_training_data(dataset["data"])
                return {
                    "training_data": training_data,
                    "format": "financial_qa",
                    "metadata": metadata
                }
            
            elif metadata.type == DatasetType.CUSTOM_FINANCIAL_KNOWLEDGE:
                # Custom knowledge base for RAG
                return {
                    "knowledge_base": dataset["data"],
                    "format": "knowledge_base",
                    "metadata": metadata
                }
            
            else:
                logger.warning(f"Dataset type {metadata.type} not optimized for LLM training")
                return dataset
                
        except Exception as e:
            logger.error(f"Error preparing dataset for LLM: {e}")
            return None
    
    def _convert_financial_to_training_data(self, data) -> List[Dict[str, str]]:
        """Convert financial data to training format"""
        training_examples = []
        
        try:
            if isinstance(data, pd.DataFrame):
                # Convert transactions to Q&A format
                for _, row in data.iterrows():
                    # Example conversion - customize based on your data structure
                    prompt = f"Analyze this transaction: Amount: ${row.get('amount', 0)}, Category: {row.get('category', 'Unknown')}, Date: {row.get('date', 'Unknown')}"
                    completion = f"This is a {row.get('category', 'general')} transaction for ${row.get('amount', 0)}. " + \
                                f"Consider this in your spending analysis and budget planning."
                    
                    training_examples.append({
                        "prompt": prompt,
                        "completion": completion
                    })
            
            logger.info(f"Generated {len(training_examples)} training examples from financial data")
            return training_examples
            
        except Exception as e:
            logger.error(f"Error converting financial data to training format: {e}")
            return []
    
    def create_embeddings(self, dataset_name: str, embedding_model: str = "default") -> bool:
        """
        Create embeddings for dataset (placeholder for your custom implementation)
        
        Args:
            dataset_name: Name of dataset
            embedding_model: Embedding model to use
            
        Returns:
            Success status
        """
        try:
            dataset = self.load_dataset(dataset_name)
            if not dataset:
                return False
            
            embeddings_dir = self.datasets_directory / "embeddings" / dataset_name
            embeddings_dir.mkdir(parents=True, exist_ok=True)
            
            # Placeholder - implement your custom embedding logic here
            # This is where you would integrate with your LLM/embedding service
            
            embedding_info = {
                "dataset_name": dataset_name,
                "embedding_model": embedding_model,
                "created_at": datetime.utcnow().isoformat(),
                "status": "ready_for_custom_implementation"
            }
            
            with open(embeddings_dir / "info.json", 'w') as f:
                json.dump(embedding_info, f, indent=2)
            
            logger.info(f"Embeddings structure created for dataset '{dataset_name}'")
            return True
            
        except Exception as e:
            logger.error(f"Error creating embeddings for '{dataset_name}': {e}")
            return False
    
    def get_dataset_stats(self, dataset_name: str) -> Optional[Dict[str, Any]]:
        """Get comprehensive dataset statistics"""
        try:
            if dataset_name not in self.dataset_metadata:
                return None
            
            metadata = self.dataset_metadata[dataset_name]
            dataset = self.load_dataset(dataset_name, max_records=10000)  # Sample for stats
            
            if not dataset:
                return None
            
            stats = {
                "name": dataset_name,
                "type": metadata.type.value,
                "format": metadata.format.value,
                "size_mb": metadata.size_mb,
                "record_count": metadata.record_count,
                "columns": metadata.columns,
                "tags": metadata.tags,
                "created_at": metadata.created_at.isoformat(),
                "updated_at": metadata.updated_at.isoformat()
            }
            
            # Add data-specific stats
            if isinstance(dataset["data"], pd.DataFrame):
                df = dataset["data"]
                stats["column_stats"] = {
                    col: {
                        "type": str(df[col].dtype),
                        "null_count": int(df[col].isnull().sum()),
                        "unique_count": int(df[col].nunique())
                    } for col in df.columns
                }
            
            return stats
            
        except Exception as e:
            logger.error(f"Error getting dataset stats: {e}")
            return None
    
    def list_datasets(self) -> List[Dict[str, Any]]:
        """List all registered datasets"""
        datasets = []
        
        for name, metadata in self.dataset_metadata.items():
            datasets.append({
                "name": name,
                "type": metadata.type.value,
                "format": metadata.format.value,
                "description": metadata.description,
                "size_mb": metadata.size_mb,
                "record_count": metadata.record_count,
                "version": metadata.version,
                "tags": metadata.tags,
                "created_at": metadata.created_at.isoformat()
            })
        
        return sorted(datasets, key=lambda x: x["created_at"], reverse=True)
    
    def export_dataset_for_training(self, dataset_name: str, export_format: str = "jsonl") -> Optional[str]:
        """
        Export dataset in format suitable for LLM training
        
        Args:
            dataset_name: Name of dataset to export
            export_format: Export format (jsonl, json, csv)
            
        Returns:
            Path to exported file or None
        """
        try:
            training_data = self.get_dataset_for_llm_training(dataset_name)
            if not training_data:
                return None
            
            export_dir = self.datasets_directory / "exports"
            export_file = export_dir / f"{dataset_name}_training.{export_format}"
            
            if export_format == "jsonl":
                with open(export_file, 'w') as f:
                    for item in training_data["training_data"]:
                        f.write(json.dumps(item) + "\n")
            
            elif export_format == "json":
                with open(export_file, 'w') as f:
                    json.dump(training_data["training_data"], f, indent=2)
            
            elif export_format == "csv" and isinstance(training_data["training_data"], list):
                df = pd.DataFrame(training_data["training_data"])
                df.to_csv(export_file, index=False)
            
            logger.info(f"Dataset exported to: {export_file}")
            return str(export_file)
            
        except Exception as e:
            logger.error(f"Error exporting dataset: {e}")
            return None
    
    def cleanup_cache(self):
        """Clean up loaded datasets from memory"""
        self.loaded_datasets.clear()
        logger.info("Dataset cache cleared")
    
    def get_service_info(self) -> Dict[str, Any]:
        """Get dataset service information"""
        return {
            "datasets_directory": str(self.datasets_directory),
            "registered_datasets": len(self.dataset_metadata),
            "loaded_datasets": len(self.loaded_datasets),
            "supported_types": [t.value for t in DatasetType],
            "supported_formats": [f.value for f in DatasetFormat],
            "directories": {
                "raw": str(self.datasets_directory / "raw"),
                "processed": str(self.datasets_directory / "processed"),
                "embeddings": str(self.datasets_directory / "embeddings"),
                "models": str(self.datasets_directory / "models"),
                "exports": str(self.datasets_directory / "exports")
            }
        }