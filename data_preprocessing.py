import json
import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Set, Any, Tuple
from pydantic import BaseModel, Field, validator
from loguru import logger
from datetime import datetime
import hashlib

# Data validation models
class AssetsData(BaseModel):
    cash: float = Field(ge=0, description="Cash on hand")
    bank_balances: float = Field(ge=0, description="Total bank balances")
    property: float = Field(ge=0, description="Property value")

class LiabilitiesData(BaseModel):
    loans: float = Field(ge=0, description="Total loan amount")
    credit_card_debt: float = Field(ge=0, description="Credit card debt")

class TransactionsData(BaseModel):
    income: float = Field(ge=0, description="Monthly income")
    expenses: float = Field(ge=0, description="Monthly expenses")
    transfers: float = Field(ge=0, description="Monthly transfers")

class EPFData(BaseModel):
    contributions: float = Field(ge=0, description="EPF contributions")
    employer_match: float = Field(ge=0, description="Employer matching")
    current_balance: float = Field(ge=0, description="Current EPF balance")

class CreditScoreData(BaseModel):
    score: int = Field(ge=300, le=900, description="Credit score")  # Allow higher scores
    rating: str = Field(description="Credit rating")
    
    @validator('rating')
    def validate_rating(cls, v):
        valid_ratings = {'Poor', 'Average', 'Fair', 'Good', 'Excellent'}
        if v not in valid_ratings:
            raise ValueError(f'Rating must be one of {valid_ratings}')
        return v

class InvestmentsData(BaseModel):
    stocks: float = Field(ge=0, description="Stock investments")
    mutual_funds: float = Field(ge=0, description="Mutual fund investments")
    bonds: float = Field(ge=0, description="Bond investments")

class FinancialData(BaseModel):
    assets: AssetsData
    liabilities: LiabilitiesData
    transactions: TransactionsData
    epf_retirement_balance: EPFData
    credit_score: CreditScoreData
    investments: InvestmentsData
    user_id: Optional[str] = None
    timestamp: Optional[datetime] = None

class UserPermissions(BaseModel):
    """User data access permissions"""
    assets: bool = True
    liabilities: bool = True
    transactions: bool = True
    epf_retirement_balance: bool = True
    credit_score: bool = True
    investments: bool = True
    
    def get_allowed_categories(self) -> Set[str]:
        """Get list of allowed data categories"""
        return {k for k, v in self.dict().items() if v}
    
    def mask_data(self, financial_data: Dict[str, Any]) -> Dict[str, Any]:
        """Mask data based on permissions"""
        masked_data = {}
        
        for category, allowed in self.dict().items():
            if allowed and category in financial_data:
                masked_data[category] = financial_data[category]
            elif not allowed:
                # Use default/zero values for denied categories
                masked_data[category] = self._get_default_values(category)
        
        return masked_data
    
    def _get_default_values(self, category: str) -> Dict[str, Any]:
        """Get default values for masked categories"""
        defaults = {
            'assets': {'cash': 0, 'bank_balances': 0, 'property': 0},
            'liabilities': {'loans': 0, 'credit_card_debt': 0},
            'transactions': {'income': 0, 'expenses': 0, 'transfers': 0},
            'epf_retirement_balance': {'contributions': 0, 'employer_match': 0, 'current_balance': 0},
            'credit_score': {'score': 600, 'rating': 'Average'},
            'investments': {'stocks': 0, 'mutual_funds': 0, 'bonds': 0}
        }
        return defaults.get(category, {})

class AdvancedDataPreprocessor:
    """Advanced data preprocessing with permissions and validation"""
    
    def __init__(self):
        self.feature_names = [
            'cash', 'bank_balances', 'property',  # Assets
            'loans', 'credit_card_debt',  # Liabilities
            'income', 'expenses', 'transfers',  # Transactions
            'epf_contributions', 'epf_employer_match', 'epf_balance',  # EPF
            'credit_score', 'credit_rating_encoded',  # Credit
            'stocks', 'mutual_funds', 'bonds'  # Investments
        ]
        self.rating_map = {'Poor': 0, 'Average': 1, 'Fair': 1, 'Good': 2, 'Excellent': 3}
        self.normalization_stats = None
        
    def validate_financial_data(self, data: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """Validate financial data structure and values"""
        errors = []
        
        try:
            # Attempt to create FinancialData object for validation
            FinancialData(**data)
            return True, []
        except Exception as e:
            errors.append(str(e))
            return False, errors
    
    def preprocess_single_record(self, 
                                financial_data: Dict[str, Any], 
                                permissions: UserPermissions,
                                normalize: bool = True) -> Tuple[np.ndarray, Dict[str, Any]]:
        """Preprocess a single financial record with permissions"""
        
        # Validate data
        is_valid, errors = self.validate_financial_data(financial_data)
        if not is_valid:
            logger.warning(f"Data validation errors: {errors}")
        
        # Apply permissions masking
        masked_data = permissions.mask_data(financial_data)
        
        # Extract features
        features = self._extract_features(masked_data)
        
        # Normalize if requested
        if normalize and self.normalization_stats is not None:
            features = self._normalize_features(features)
        
        # Create metadata
        metadata = {
            'permissions_used': permissions.get_allowed_categories(),
            'data_hash': self._calculate_data_hash(financial_data),
            'processing_timestamp': datetime.now().isoformat(),
            'feature_names': self.feature_names
        }
        
        return features, metadata
    
    def preprocess_batch_data(self, 
                             input_data: List[Dict[str, Any]], 
                             permissions_list: Optional[List[UserPermissions]] = None,
                             calculate_normalization: bool = True) -> Dict[str, Any]:
        """Preprocess batch of financial data"""
        
        if permissions_list is None:
            # Default to full permissions for all records
            permissions_list = [UserPermissions() for _ in input_data]
        
        processed_features = []
        metadata_list = []
        valid_records = 0
        
        # First pass: extract features and calculate normalization stats
        all_features = []
        for i, (data, permissions) in enumerate(zip(input_data, permissions_list)):
            try:
                features, metadata = self.preprocess_single_record(
                    data, permissions, normalize=False
                )
                all_features.append(features)
                processed_features.append(features)
                metadata_list.append(metadata)
                valid_records += 1
            except Exception as e:
                logger.error(f"Error processing record {i}: {e}")
                continue
        
        # Calculate normalization statistics
        if calculate_normalization and all_features:
            features_matrix = np.vstack(all_features)
            self.normalization_stats = {
                'mean': np.mean(features_matrix, axis=0),
                'std': np.std(features_matrix, axis=0) + 1e-6  # Add epsilon
            }
        
        # Second pass: normalize features
        normalized_features = []
        for features in processed_features:
            normalized = self._normalize_features(features)
            normalized_features.append(normalized)
        
        return {
            'features': np.array(normalized_features),
            'metadata': metadata_list,
            'normalization_stats': self.normalization_stats,
            'feature_names': self.feature_names,
            'valid_records': valid_records,
            'total_records': len(input_data)
        }
    
    def _extract_features(self, financial_data: Dict[str, Any]) -> np.ndarray:
        """Extract numerical features from financial data"""
        features = []
        
        # Assets
        assets = financial_data.get('assets', {})
        features.extend([
            float(assets.get('cash', 0)),
            float(assets.get('bank_balances', 0)),
            float(assets.get('property', 0))
        ])
        
        # Liabilities
        liabilities = financial_data.get('liabilities', {})
        features.extend([
            float(liabilities.get('loans', 0)),
            float(liabilities.get('credit_card_debt', 0))
        ])
        
        # Transactions
        transactions = financial_data.get('transactions', {})
        features.extend([
            float(transactions.get('income', 0)),
            float(transactions.get('expenses', 0)),
            float(transactions.get('transfers', 0))
        ])
        
        # EPF/Retirement
        epf = financial_data.get('epf_retirement_balance', {})
        features.extend([
            float(epf.get('contributions', 0)),
            float(epf.get('employer_match', 0)),
            float(epf.get('current_balance', 0))
        ])
        
        # Credit Score
        credit = financial_data.get('credit_score', {})
        features.append(float(credit.get('score', 600)))
        
        # Credit Rating (encoded)
        rating = credit.get('rating', 'Average')
        features.append(float(self.rating_map.get(rating, 1)))
        
        # Investments
        investments = financial_data.get('investments', {})
        features.extend([
            float(investments.get('stocks', 0)),
            float(investments.get('mutual_funds', 0)),
            float(investments.get('bonds', 0))
        ])
        
        return np.array(features, dtype=np.float32)
    
    def _normalize_features(self, features: np.ndarray) -> np.ndarray:
        """Normalize features using stored statistics"""
        if self.normalization_stats is None:
            logger.warning("No normalization statistics available")
            return features
        
        mean = self.normalization_stats['mean']
        std = self.normalization_stats['std']
        
        return (features - mean) / std
    
    def _calculate_data_hash(self, data: Dict[str, Any]) -> str:
        """Calculate hash of financial data for integrity checking"""
        data_str = json.dumps(data, sort_keys=True)
        return hashlib.md5(data_str.encode()).hexdigest()
    
    def save_processed_data(self, processed_data: Dict[str, Any], output_file: str):
        """Save processed data to file"""
        # Convert numpy arrays to lists for JSON serialization
        serializable_data = {
            'features': processed_data['features'].tolist(),
            'metadata': processed_data['metadata'],
            'normalization_stats': {
                'mean': processed_data['normalization_stats']['mean'].tolist(),
                'std': processed_data['normalization_stats']['std'].tolist()
            } if processed_data['normalization_stats'] else None,
            'feature_names': processed_data['feature_names'],
            'valid_records': processed_data['valid_records'],
            'total_records': processed_data['total_records'],
            'processing_date': datetime.now().isoformat()
        }
        
        with open(output_file, 'w') as f:
            json.dump(serializable_data, f, indent=2)
        
        logger.info(f"Processed data saved to {output_file}")
        logger.info(f"Processed {processed_data['valid_records']}/{processed_data['total_records']} records successfully")
    
    def load_processed_data(self, input_file: str) -> Dict[str, Any]:
        """Load previously processed data"""
        with open(input_file, 'r') as f:
            data = json.load(f)
        
        # Convert lists back to numpy arrays
        data['features'] = np.array(data['features'])
        if data['normalization_stats']:
            data['normalization_stats'] = {
                'mean': np.array(data['normalization_stats']['mean']),
                'std': np.array(data['normalization_stats']['std'])
            }
            self.normalization_stats = data['normalization_stats']
        
        return data

def preprocess_data(input_file='data.json', output_file='processed_data.json', 
                   permissions_file=None):
    """
    Enhanced data preprocessing with validation and permissions
    
    Args:
        input_file (str): Path to input JSON file
        output_file (str): Path to save processed data
        permissions_file (str): Optional path to permissions configuration
    """
    
    preprocessor = AdvancedDataPreprocessor()
    
    # Load raw data
    with open(input_file, 'r') as f:
        raw_data = json.load(f)
    
    logger.info(f"Loaded {len(raw_data)} records from {input_file}")
    
    # Load permissions if provided
    permissions_list = None
    if permissions_file:
        try:
            with open(permissions_file, 'r') as f:
                permissions_data = json.load(f)
            permissions_list = [UserPermissions(**perm) for perm in permissions_data]
            logger.info(f"Loaded permissions for {len(permissions_list)} users")
        except Exception as e:
            logger.warning(f"Could not load permissions file: {e}")
    
    # Process data
    processed_data = preprocessor.preprocess_batch_data(
        raw_data, permissions_list
    )
    
    # Save processed data
    preprocessor.save_processed_data(processed_data, output_file)
    
    return processed_data

if __name__ == '__main__':
    import sys
    
    # Configure logging
    logger.add("data_processing.log", rotation="1 MB")
    
    input_file = sys.argv[1] if len(sys.argv) > 1 else 'data.json'
    output_file = sys.argv[2] if len(sys.argv) > 2 else 'processed_data.json'
    permissions_file = sys.argv[3] if len(sys.argv) > 3 else None
    
    preprocess_data(input_file, output_file, permissions_file)
