"""
Enhanced data validation and normalization service
"""
import json
import jsonschema
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


class DataValidator:
    """Enhanced data validation and normalization service"""
    
    def __init__(self):
        """Initialize validator with schemas"""
        self.schemas = self._load_schemas()
    
    def _load_schemas(self) -> Dict[str, Any]:
        """Load JSON schemas for validation"""
        return {
            "transaction": {
                "type": "object",
                "required": ["id", "date", "amount", "description", "category"],
                "properties": {
                    "id": {"type": "string", "minLength": 1},
                    "date": {"type": "string", "format": "date-time"},
                    "amount": {"type": "number"},
                    "description": {"type": "string", "minLength": 1, "maxLength": 500},
                    "category": {"type": "string", "minLength": 1, "maxLength": 100},
                    "account": {"type": "string", "maxLength": 100},
                    "merchant": {"type": ["string", "null"], "maxLength": 200},
                    "tags": {"type": "array", "items": {"type": "string"}},
                    "location": {"type": ["object", "null"]},
                    "reference": {"type": ["string", "null"]}
                }
            },
            "account": {
                "type": "object",
                "required": ["id", "name", "type", "balance"],
                "properties": {
                    "id": {"type": "string", "minLength": 1},
                    "name": {"type": "string", "minLength": 1, "maxLength": 200},
                    "type": {"type": "string", "enum": ["savings", "current", "credit", "investment", "epf", "checking"]},
                    "balance": {"type": "number", "minimum": 0},
                    "currency": {"type": "string", "enum": ["INR", "USD", "EUR"], "default": "INR"},
                    "bank": {"type": ["string", "null"], "maxLength": 100},
                    "account_number": {"type": ["string", "null"]},
                    "is_active": {"type": "boolean", "default": True},
                    "last_updated": {"type": ["string", "null"], "format": "date-time"}
                }
            },
            "investment": {
                "type": "object",
                "required": ["id", "name", "type", "current_value"],
                "properties": {
                    "id": {"type": "string", "minLength": 1},
                    "name": {"type": "string", "minLength": 1, "maxLength": 200},
                    "type": {"type": "string", "enum": ["mutual_fund", "stock", "bond", "fd", "ppf", "elss", "etf", "equity", "debt", "fixed_deposit"]},
                    "current_value": {"type": ["number", "string"], "minimum": 0},
                    "units": {"type": ["number", "string", "null"], "minimum": 0},
                    "purchase_price": {"type": ["number", "string", "null"], "minimum": 0},
                    "purchase_date": {"type": ["string", "null"], "format": "date"},
                    "returns": {"type": ["number", "null"]},
                    "risk_level": {"type": "string", "enum": ["low", "medium", "high"], "default": "medium"},
                    "portfolio_percentage": {"type": ["number", "null"], "minimum": 0, "maximum": 100}
                }
            },
            "asset": {
                "type": "object",
                "required": ["id", "name", "type", "value"],
                "properties": {
                    "id": {"type": "string", "minLength": 1},
                    "name": {"type": "string", "minLength": 1, "maxLength": 200},
                    "type": {"type": "string", "enum": ["property", "vehicle", "jewelry", "electronics", "other"]},
                    "value": {"type": "number", "minimum": 0},
                    "purchase_date": {"type": ["string", "null"], "format": "date"},
                    "depreciation_rate": {"type": ["number", "null"], "minimum": 0, "maximum": 100},
                    "location": {"type": ["string", "null"]},
                    "description": {"type": ["string", "null"], "maxLength": 500}
                }
            },
            "liability": {
                "type": "object",
                "required": ["id", "name", "type", "balance", "interest_rate"],
                "properties": {
                    "id": {"type": "string", "minLength": 1},
                    "name": {"type": "string", "minLength": 1, "maxLength": 200},
                    "type": {"type": "string", "enum": ["home_loan", "personal_loan", "car_loan", "credit_card", "other", "mortgage", "auto"]},
                    "balance": {"type": "number", "minimum": 0},
                    "original_amount": {"type": ["number", "null"], "minimum": 0},
                    "interest_rate": {"type": "number", "minimum": 0, "maximum": 100},
                    "monthly_payment": {"type": ["number", "null"], "minimum": 0},
                    "emi_date": {"type": ["integer", "null"], "minimum": 1, "maximum": 31},
                    "tenure_months": {"type": ["integer", "null"], "minimum": 1},
                    "remaining_months": {"type": ["integer", "null"], "minimum": 0}
                }
            }
        }
    
    def validate_data(self, data: Any, schema_name: str) -> Dict[str, Any]:
        """
        Validate data against schema
        
        Args:
            data: Data to validate
            schema_name: Name of schema to use
            
        Returns:
            Validation result with errors and normalized data
        """
        result = {
            "valid": False,
            "errors": [],
            "warnings": [],
            "normalized_data": None
        }
        
        try:
            schema = self.schemas.get(schema_name)
            if not schema:
                result["errors"].append(f"Schema '{schema_name}' not found")
                return result
            
            # Validate against schema
            jsonschema.validate(data, schema)
            
            # Normalize the data
            normalized_data = self._normalize_data(data, schema_name)
            
            result.update({
                "valid": True,
                "normalized_data": normalized_data
            })
            
        except jsonschema.ValidationError as e:
            result["errors"].append({
                "field": ".".join(str(p) for p in e.absolute_path),
                "message": e.message,
                "invalid_value": e.instance
            })
        except Exception as e:
            result["errors"].append(f"Validation error: {str(e)}")
        
        return result
    
    def _normalize_data(self, data: Dict[str, Any], schema_name: str) -> Dict[str, Any]:
        """Normalize data according to business rules"""
        normalized = data.copy()
        
        if schema_name == "transaction":
            # Normalize transaction data
            normalized = self._normalize_transaction(normalized)
        elif schema_name == "account":
            # Normalize account data
            normalized = self._normalize_account(normalized)
        elif schema_name == "investment":
            # Normalize investment data
            normalized = self._normalize_investment(normalized)
        elif schema_name == "asset":
            # Normalize asset data
            normalized = self._normalize_asset(normalized)
        elif schema_name == "liability":
            # Normalize liability data
            normalized = self._normalize_liability(normalized)
        
        return normalized
    
    def _normalize_transaction(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize transaction data"""
        # Standardize date format
        if "date" in data:
            data["date"] = self._normalize_datetime(data["date"])
        
        # Normalize amount to proper decimal
        if "amount" in data:
            data["amount"] = self._normalize_currency(data["amount"])
        
        # Standardize category names
        if "category" in data:
            data["category"] = self._normalize_category(data["category"])
        
        # Clean description
        if "description" in data:
            data["description"] = data["description"].strip()[:500]
        
        # Add metadata
        data["processed_at"] = datetime.now(timezone.utc).isoformat()
        
        return data
    
    def _normalize_account(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize account data"""
        # Normalize balance
        if "balance" in data:
            data["balance"] = self._normalize_currency(data["balance"])
        
        # Set default currency
        if "currency" not in data:
            data["currency"] = "INR"
        
        # Update timestamp
        data["last_updated"] = datetime.now(timezone.utc).isoformat()
        
        return data
    
    def _normalize_investment(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize investment data"""
        # Normalize monetary values
        for field in ["current_value", "purchase_price"]:
            if field in data and data[field] is not None:
                data[field] = self._normalize_currency(data[field])
        
        # Normalize units field (may come as string from CSV)
        if "units" in data and data["units"] is not None:
            try:
                if isinstance(data["units"], str):
                    data["units"] = float(data["units"])
                elif isinstance(data["units"], (int, float)):
                    data["units"] = float(data["units"])
            except (ValueError, TypeError):
                logger.warning(f"Could not normalize units: {data['units']}")
                data["units"] = 0.0
        
        # Calculate returns if possible
        if all(k in data and data[k] is not None for k in ["current_value", "purchase_price"]):
            purchase_price = float(data["purchase_price"])
            if purchase_price > 0:
                returns = ((float(data["current_value"]) - purchase_price) / purchase_price) * 100
                data["returns"] = round(returns, 2)
        
        return data
    
    def _normalize_asset(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize asset data"""
        # Normalize value
        if "value" in data:
            data["value"] = self._normalize_currency(data["value"])
        
        # Calculate current value with depreciation if applicable
        if all(k in data and data[k] is not None for k in ["value", "purchase_date", "depreciation_rate"]):
            data["depreciated_value"] = self._calculate_depreciated_value(
                data["value"], data["purchase_date"], data["depreciation_rate"]
            )
        
        return data
    
    def _normalize_liability(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize liability data"""
        # Normalize monetary values
        for field in ["balance", "original_amount", "monthly_payment"]:
            if field in data and data[field] is not None:
                data[field] = self._normalize_currency(data[field])
        
        # Calculate remaining tenure
        if all(k in data and data[k] is not None for k in ["balance", "monthly_payment", "interest_rate"]):
            data["estimated_payoff_months"] = self._calculate_loan_tenure(
                data["balance"], data["monthly_payment"], data["interest_rate"]
            )
        
        return data
    
    def _normalize_datetime(self, date_str: str) -> str:
        """Normalize datetime string to ISO format"""
        try:
            # Parse various date formats
            if date_str.endswith('Z'):
                dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
            else:
                dt = datetime.fromisoformat(date_str)
            
            # Ensure UTC timezone
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            
            return dt.isoformat()
        except ValueError:
            # Fallback to current time if parsing fails
            logger.warning(f"Could not parse date: {date_str}")
            return datetime.now(timezone.utc).isoformat()
    
    def _normalize_currency(self, amount: Any) -> float:
        """Normalize currency amount to float"""
        try:
            if isinstance(amount, str):
                # Remove currency symbols and commas
                amount = amount.replace('₹', '').replace(',', '').replace('Rs.', '').strip()
            
            return float(Decimal(str(amount)))
        except (InvalidOperation, ValueError) as e:
            logger.warning(f"Could not normalize currency amount: {amount} - {e}")
            return 0.0
    
    def _normalize_category(self, category: str) -> str:
        """Normalize transaction category"""
        category_mapping = {
            # Food related
            "food": "food_dining",
            "restaurant": "food_dining",
            "dining": "food_dining",
            "groceries": "food_dining",
            "grocery": "food_dining",
            
            # Transport related
            "transport": "transportation",
            "taxi": "transportation",
            "uber": "transportation",
            "ola": "transportation",
            "fuel": "transportation",
            "petrol": "transportation",
            
            # Bills related
            "utilities": "bills_utilities",
            "electricity": "bills_utilities",
            "phone": "bills_utilities",
            "internet": "bills_utilities",
            
            # Entertainment
            "entertainment": "entertainment",
            "movies": "entertainment",
            "gaming": "entertainment",
            
            # Shopping
            "shopping": "shopping",
            "retail": "shopping",
            "clothes": "shopping",
            "clothing": "shopping"
        }
        
        normalized = category.lower().strip()
        return category_mapping.get(normalized, normalized)
    
    def _calculate_depreciated_value(self, original_value: float, purchase_date: str, depreciation_rate: float) -> float:
        """Calculate current value after depreciation"""
        try:
            purchase_dt = datetime.fromisoformat(purchase_date.replace('Z', '+00:00'))
            years_elapsed = (datetime.now(timezone.utc) - purchase_dt).days / 365.25
            
            # Simple straight-line depreciation
            depreciation_amount = original_value * (depreciation_rate / 100) * years_elapsed
            current_value = original_value - depreciation_amount
            
            return max(0.0, round(current_value, 2))
        except Exception as e:
            logger.warning(f"Could not calculate depreciated value: {e}")
            return original_value
    
    def _calculate_loan_tenure(self, balance: float, monthly_payment: float, interest_rate: float) -> int:
        """Calculate remaining loan tenure in months"""
        try:
            if monthly_payment <= 0 or balance <= 0:
                return 0
            
            monthly_rate = interest_rate / 100 / 12
            if monthly_rate == 0:
                return int(balance / monthly_payment)
            
            # EMI calculation formula
            months = -(1/12) * (1/monthly_rate) * math.log(1 - (balance * monthly_rate) / monthly_payment)
            return max(0, int(round(months)))
        except Exception as e:
            logger.warning(f"Could not calculate loan tenure: {e}")
            return 0
    
    def validate_bulk_data(self, data_list: List[Dict[str, Any]], schema_name: str) -> Dict[str, Any]:
        """
        Validate multiple data items
        
        Args:
            data_list: List of data items to validate
            schema_name: Schema to validate against
            
        Returns:
            Bulk validation results
        """
        results = {
            "total_count": len(data_list),
            "valid_count": 0,
            "invalid_count": 0,
            "valid_items": [],
            "invalid_items": [],
            "summary_errors": []
        }
        
        for i, item in enumerate(data_list):
            validation_result = self.validate_data(item, schema_name)
            
            if validation_result["valid"]:
                results["valid_count"] += 1
                results["valid_items"].append({
                    "index": i,
                    "data": validation_result["normalized_data"]
                })
            else:
                results["invalid_count"] += 1
                results["invalid_items"].append({
                    "index": i,
                    "data": item,
                    "errors": validation_result["errors"]
                })
        
        # Generate summary
        if results["invalid_count"] > 0:
            error_summary = {}
            for item in results["invalid_items"]:
                for error in item["errors"]:
                    field = error.get("field", "unknown") if isinstance(error, dict) else "general"
                    error_summary[field] = error_summary.get(field, 0) + 1
            
            results["summary_errors"] = [
                {"field": field, "count": count} for field, count in error_summary.items()
            ]
        
        return results
    
    async def validate_transactions(self, transactions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Validate and normalize transaction data
        
        Args:
            transactions: List of transaction dictionaries
            
        Returns:
            List of validated and normalized transactions
        """
        validated_transactions = []
        
        for transaction in transactions:
            try:
                # Validate transaction against schema
                result = self.validate_data(transaction, "transaction")
                
                if result["valid"]:
                    validated_transactions.append(result["normalized_data"])
                else:
                    logger.warning(f"Invalid transaction {transaction.get('id', 'unknown')}: {result['errors']}")
                    # Include the transaction anyway with a warning flag
                    transaction["validation_warnings"] = result["errors"]
                    validated_transactions.append(transaction)
            except Exception as e:
                logger.error(f"Error validating transaction: {e}")
                transaction["validation_error"] = str(e)
                validated_transactions.append(transaction)
        
        return validated_transactions
    
    async def validate_accounts(self, accounts: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Validate and normalize account data
        
        Args:
            accounts: List of account dictionaries
            
        Returns:
            List of validated and normalized accounts
        """
        validated_accounts = []
        
        for account in accounts:
            try:
                # Validate account against schema
                result = self.validate_data(account, "account")
                
                if result["valid"]:
                    validated_accounts.append(result["normalized_data"])
                else:
                    logger.warning(f"Invalid account {account.get('id', 'unknown')}: {result['errors']}")
                    # Include the account anyway with a warning flag
                    account["validation_warnings"] = result["errors"]
                    validated_accounts.append(account)
            except Exception as e:
                logger.error(f"Error validating account: {e}")
                account["validation_error"] = str(e)
                validated_accounts.append(account)
        
        return validated_accounts
    
    async def validate_liabilities(self, liabilities: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Validate and normalize liability data
        
        Args:
            liabilities: List of liability dictionaries
            
        Returns:
            List of validated and normalized liabilities
        """
        validated_liabilities = []
        
        for liability in liabilities:
            try:
                # Validate liability against schema
                result = self.validate_data(liability, "liability")
                
                if result["valid"]:
                    validated_liabilities.append(result["normalized_data"])
                else:
                    logger.warning(f"Invalid liability {liability.get('id', 'unknown')}: {result['errors']}")
                    # Include the liability anyway with a warning flag
                    liability["validation_warnings"] = result["errors"]
                    validated_liabilities.append(liability)
            except Exception as e:
                logger.error(f"Error validating liability: {e}")
                liability["validation_error"] = str(e)
                validated_liabilities.append(liability)
        
        return validated_liabilities
    
    async def validate_investments(self, investments: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Validate and normalize investment data
        
        Args:
            investments: List of investment dictionaries
            
        Returns:
            List of validated and normalized investments
        """
        validated_investments = []
        
        for investment in investments:
            try:
                # Validate investment against schema
                result = self.validate_data(investment, "investment")
                
                if result["valid"]:
                    validated_investments.append(result["normalized_data"])
                else:
                    logger.warning(f"Invalid investment {investment.get('id', 'unknown')}: {result['errors']}")
                    # Include the investment anyway with a warning flag
                    investment["validation_warnings"] = result["errors"]
                    validated_investments.append(investment)
            except Exception as e:
                logger.error(f"Error validating investment: {e}")
                investment["validation_error"] = str(e)
                validated_investments.append(investment)
        
        return validated_investments


# Import math for loan calculations
import math
