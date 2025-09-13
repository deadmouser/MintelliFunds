"""
Data service for loading and managing financial data
"""
import json
import os
from typing import Dict, Any, List
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class DataService:
    """Service for loading and managing financial data from JSON files"""
    
    def __init__(self, data_dir: str = "data"):
        """
        Initialize the data service
        
        Args:
            data_dir: Directory containing the JSON data files
        """
        self.data_dir = Path(data_dir)
        self._data_cache = {}
        
    def load_all_data(self) -> Dict[str, Any]:
        """
        Load all financial data from JSON files
        
        Returns:
            Dictionary containing all loaded data
        """
        try:
            data = {}
            
            # Define the data files to load
            data_files = {
                'transactions': 'transactions.json',
                'assets': 'assets.json',
                'liabilities': 'liabilities.json',
                'investments': 'investments.json',
                'accounts': 'accounts.json',
                'spending_trends': 'spending_trends.json',
                'category_breakdown': 'category_breakdown.json',
                'dashboard_insights': 'dashboard_insights.json',
                'epf_balance': 'epf_balance.json',
                'credit_score': 'credit_score.json'
            }
            
            for key, filename in data_files.items():
                file_path = self.data_dir / filename
                if file_path.exists():
                    with open(file_path, 'r', encoding='utf-8') as f:
                        data[key] = json.load(f)
                    logger.info(f"Loaded {key} data from {filename}")
                else:
                    logger.warning(f"Data file not found: {file_path}")
                    data[key] = []
            
            # Cache the data
            self._data_cache = data
            return data
            
        except Exception as e:
            logger.error(f"Error loading data: {str(e)}")
            raise Exception(f"Failed to load financial data: {str(e)}")
    
    def get_data_by_category(self, category: str) -> Any:
        """
        Get data for a specific category
        
        Args:
            category: The data category to retrieve
            
        Returns:
            Data for the specified category
        """
        if not self._data_cache:
            self.load_all_data()
        
        return self._data_cache.get(category, [])
    
    def validate_data_structure(self, data: Dict[str, Any]) -> bool:
        """
        Validate that the loaded data has the expected structure
        
        Args:
            data: The loaded data dictionary
            
        Returns:
            True if data structure is valid, False otherwise
        """
        required_categories = [
            'transactions', 'assets', 'liabilities', 'investments',
            'accounts', 'spending_trends', 'category_breakdown',
            'dashboard_insights', 'epf_balance', 'credit_score'
        ]
        
        for category in required_categories:
            if category not in data:
                logger.error(f"Missing required data category: {category}")
                return False
        
        # Validate that transactions is a list
        if not isinstance(data.get('transactions'), list):
            logger.error("Transactions data should be a list")
            return False
        
        # Validate that other categories are either lists or dicts
        for category in ['assets', 'liabilities', 'investments', 'accounts', 
                        'spending_trends', 'category_breakdown', 'dashboard_insights']:
            if not isinstance(data.get(category), list):
                logger.error(f"{category} data should be a list")
                return False
        
        # Validate that epf_balance and credit_score are dicts
        for category in ['epf_balance', 'credit_score']:
            if not isinstance(data.get(category), dict):
                logger.error(f"{category} data should be a dictionary")
                return False
        
        logger.info("Data structure validation passed")
        return True
    
    def get_data_summary(self) -> Dict[str, Any]:
        """
        Get a summary of the loaded data
        
        Returns:
            Dictionary containing data summary statistics
        """
        if not self._data_cache:
            self.load_all_data()
        
        summary = {}
        for category, data in self._data_cache.items():
            if isinstance(data, list):
                summary[category] = {
                    'count': len(data),
                    'type': 'list'
                }
            elif isinstance(data, dict):
                summary[category] = {
                    'count': len(data),
                    'type': 'dict',
                    'keys': list(data.keys())
                }
        
        return summary
