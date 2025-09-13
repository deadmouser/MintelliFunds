"""
Natural Language Processing service for financial queries
"""
import re
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

logger = logging.getLogger(__name__)


class NLPService:
    """Service for processing natural language financial queries"""
    
    def __init__(self):
        """Initialize the NLP service with intent patterns and entity extractors"""
        self.intent_patterns = {
            "get_spending_summary": [
                r"spending|expenses|expenditure|costs?|outgoings?",
                r"how much.*spent|what.*spent|total.*spent",
                r"spending.*summary|expense.*summary|cost.*breakdown",
                r"where.*money.*go|where.*spent"
            ],
            "get_spending_by_category": [
                r"spending.*category|categories|breakdown",
                r"how much.*groceries|food|dining|transport|housing",
                r"spent.*on.*groceries|food|dining|transport|housing",
                r"category.*spending|spending.*by.*category"
            ],
            "project_future_balance": [
                r"future.*balance|project.*balance|forecast.*balance",
                r"how much.*have.*next.*month|next.*quarter|next.*year",
                r"balance.*in.*month|quarter|year",
                r"project.*savings|forecast.*savings"
            ],
            "check_affordability": [
                r"can.*afford|afford.*to.*buy|afford.*purchase",
                r"should.*buy|worth.*buying|budget.*for",
                r"afford.*this|afford.*that|affordable",
                r"financial.*feasible|budget.*check"
            ],
            "get_income_summary": [
                r"income|earnings|salary|wages|revenue",
                r"how much.*earn|total.*income|monthly.*income",
                r"income.*summary|earnings.*summary"
            ],
            "get_savings_analysis": [
                r"savings|saved|saving.*rate|saving.*percentage",
                r"how much.*saved|saving.*goals|savings.*progress",
                r"saving.*analysis|savings.*summary"
            ],
            "get_debt_analysis": [
                r"debt|loans?|credit.*card|mortgage",
                r"how much.*owe|total.*debt|debt.*summary",
                r"debt.*analysis|loan.*analysis"
            ],
            "get_investment_summary": [
                r"investments?|portfolio|stocks?|shares?",
                r"investment.*value|portfolio.*value|investment.*summary",
                r"how much.*invested|investment.*performance"
            ],
            "get_transaction_history": [
                r"transactions?|recent.*transactions?|transaction.*history",
                r"what.*bought|purchases?|recent.*purchases?",
                r"transaction.*list|purchase.*history"
            ],
            "get_financial_health": [
                r"financial.*health|money.*situation|financial.*status",
                r"how.*am.*doing|financial.*overview|money.*overview",
                r"financial.*summary|overall.*financial"
            ]
        }
        
        self.entity_patterns = {
            "amount": [
                r"\$?(\d+(?:,\d{3})*(?:\.\d{2})?)\s*(?:dollars?|USD|usd)?",
                r"(\d+(?:,\d{3})*(?:\.\d{2})?)\s*(?:dollars?|USD|usd)",
                r"(\d+(?:,\d{3})*(?:\.\d{2})?)\s*\$"
            ],
            "category": [
                r"(?:groceries|food|dining|restaurant)",
                r"(?:transport|transportation|gas|fuel|uber|taxi)",
                r"(?:housing|rent|mortgage|utilities)",
                r"(?:entertainment|movies|games|subscriptions)",
                r"(?:health|medical|fitness|gym)",
                r"(?:shopping|clothes|clothing|retail)",
                r"(?:education|school|books|courses)",
                r"(?:travel|vacation|hotel|flight)",
                r"(?:insurance|insurance)",
                r"(?:savings|investment|retirement)"
            ],
            "time_period": [
                r"(?:this|current)\s+(?:month|week|year)",
                r"(?:last|previous)\s+(?:month|week|year|quarter)",
                r"(?:next|upcoming)\s+(?:month|week|year|quarter)",
                r"(?:past|last)\s+(\d+)\s+(?:months?|weeks?|years?|quarters?)",
                r"(?:next|upcoming)\s+(\d+)\s+(?:months?|weeks?|years?|quarters?)",
                r"(?:january|february|march|april|may|june|july|august|september|october|november|december)",
                r"(?:q1|q2|q3|q4|quarter\s*[1-4])",
                r"(?:202[0-9]|20[0-9][0-9])"
            ],
            "comparison": [
                r"(?:vs|versus|compared\s+to|against)",
                r"(?:more|less|higher|lower|better|worse)",
                r"(?:increase|decrease|up|down|rise|fall)"
            ]
        }
    
    def process_query(self, user_query: str) -> Dict[str, Any]:
        """
        Process a natural language query to extract intent and entities
        
        Args:
            user_query: The user's natural language query
            
        Returns:
            Dictionary containing intent and entities
        """
        try:
            logger.info(f"Processing query: '{user_query}'")
            
            # Clean and normalize the query
            normalized_query = self._normalize_query(user_query)
            
            # Extract intent
            intent = self._classify_intent(normalized_query)
            
            # Extract entities
            entities = self._extract_entities(normalized_query)
            
            # Add confidence scores
            intent_confidence = self._calculate_intent_confidence(normalized_query, intent)
            entity_confidence = self._calculate_entity_confidence(normalized_query, entities)
            
            result = {
                "intent": intent,
                "entities": entities,
                "confidence": {
                    "intent": intent_confidence,
                    "entities": entity_confidence,
                    "overall": (intent_confidence + entity_confidence) / 2
                },
                "original_query": user_query,
                "normalized_query": normalized_query
            }
            
            logger.info(f"Query processed - Intent: {intent}, Entities: {len(entities)}")
            return result
            
        except Exception as e:
            logger.error(f"Error processing query: {str(e)}")
            return {
                "intent": "unknown",
                "entities": {},
                "confidence": {"intent": 0.0, "entities": 0.0, "overall": 0.0},
                "original_query": user_query,
                "normalized_query": user_query,
                "error": str(e)
            }
    
    def _normalize_query(self, query: str) -> str:
        """Normalize the query for better pattern matching"""
        # Convert to lowercase
        normalized = query.lower().strip()
        
        # Remove extra whitespace
        normalized = re.sub(r'\s+', ' ', normalized)
        
        # Remove common punctuation that might interfere
        normalized = re.sub(r'[^\w\s$.,]', '', normalized)
        
        return normalized
    
    def _classify_intent(self, query: str) -> str:
        """Classify the intent of the query"""
        best_intent = "unknown"
        best_score = 0
        
        for intent, patterns in self.intent_patterns.items():
            score = 0
            for pattern in patterns:
                if re.search(pattern, query, re.IGNORECASE):
                    score += 1
            
            if score > best_score:
                best_score = score
                best_intent = intent
        
        # If no clear intent found, try to infer from keywords
        if best_score == 0:
            best_intent = self._infer_intent_from_keywords(query)
        
        return best_intent
    
    def _infer_intent_from_keywords(self, query: str) -> str:
        """Infer intent from key financial keywords"""
        if any(word in query for word in ["spend", "expense", "cost", "money"]):
            return "get_spending_summary"
        elif any(word in query for word in ["save", "savings", "invest"]):
            return "get_savings_analysis"
        elif any(word in query for word in ["afford", "buy", "purchase"]):
            return "check_affordability"
        elif any(word in query for word in ["future", "project", "forecast"]):
            return "project_future_balance"
        else:
            return "get_financial_health"
    
    def _extract_entities(self, query: str) -> Dict[str, Any]:
        """Extract entities from the query"""
        entities = {}
        
        # Extract amounts
        amounts = self._extract_amounts(query)
        if amounts:
            entities["amounts"] = amounts
        
        # Extract categories
        categories = self._extract_categories(query)
        if categories:
            entities["categories"] = categories
        
        # Extract time periods
        time_periods = self._extract_time_periods(query)
        if time_periods:
            entities["time_periods"] = time_periods
        
        # Extract comparisons
        comparisons = self._extract_comparisons(query)
        if comparisons:
            entities["comparisons"] = comparisons
        
        return entities
    
    def _extract_amounts(self, query: str) -> List[float]:
        """Extract monetary amounts from the query"""
        amounts = []
        for pattern in self.entity_patterns["amount"]:
            matches = re.findall(pattern, query, re.IGNORECASE)
            for match in matches:
                try:
                    # Remove commas and convert to float
                    amount_str = match.replace(',', '')
                    amount = float(amount_str)
                    amounts.append(amount)
                except ValueError:
                    continue
        return amounts
    
    def _extract_categories(self, query: str) -> List[str]:
        """Extract spending categories from the query"""
        categories = []
        for pattern in self.entity_patterns["category"]:
            matches = re.findall(pattern, query, re.IGNORECASE)
            categories.extend(matches)
        return list(set(categories))  # Remove duplicates
    
    def _extract_time_periods(self, query: str) -> List[Dict[str, Any]]:
        """Extract time periods from the query"""
        time_periods = []
        
        # Relative time periods
        if re.search(r"this\s+(month|week|year)", query, re.IGNORECASE):
            time_periods.append({"type": "current", "period": "month"})
        elif re.search(r"last\s+(month|week|year|quarter)", query, re.IGNORECASE):
            time_periods.append({"type": "previous", "period": "month"})
        elif re.search(r"next\s+(month|week|year|quarter)", query, re.IGNORECASE):
            time_periods.append({"type": "future", "period": "month"})
        
        # Specific number of periods
        past_match = re.search(r"past\s+(\d+)\s+(months?|weeks?|years?|quarters?)", query, re.IGNORECASE)
        if past_match:
            count = int(past_match.group(1))
            period = past_match.group(2).rstrip('s')
            time_periods.append({"type": "previous", "count": count, "period": period})
        
        future_match = re.search(r"next\s+(\d+)\s+(months?|weeks?|years?|quarters?)", query, re.IGNORECASE)
        if future_match:
            count = int(future_match.group(1))
            period = future_match.group(2).rstrip('s')
            time_periods.append({"type": "future", "count": count, "period": period})
        
        return time_periods
    
    def _extract_comparisons(self, query: str) -> List[str]:
        """Extract comparison indicators from the query"""
        comparisons = []
        for pattern in self.entity_patterns["comparison"]:
            matches = re.findall(pattern, query, re.IGNORECASE)
            comparisons.extend(matches)
        return list(set(comparisons))
    
    def _calculate_intent_confidence(self, query: str, intent: str) -> float:
        """Calculate confidence score for intent classification"""
        if intent == "unknown":
            return 0.0
        
        patterns = self.intent_patterns.get(intent, [])
        matches = 0
        total_patterns = len(patterns)
        
        for pattern in patterns:
            if re.search(pattern, query, re.IGNORECASE):
                matches += 1
        
        return matches / total_patterns if total_patterns > 0 else 0.0
    
    def _calculate_entity_confidence(self, query: str, entities: Dict[str, Any]) -> float:
        """Calculate confidence score for entity extraction"""
        if not entities:
            return 0.0
        
        total_entities = sum(len(v) if isinstance(v, list) else 1 for v in entities.values())
        return min(total_entities / 5.0, 1.0)  # Normalize to 0-1 range
    
    def get_supported_intents(self) -> List[str]:
        """Get list of supported intents"""
        return list(self.intent_patterns.keys())
    
    def get_supported_entities(self) -> List[str]:
        """Get list of supported entity types"""
        return list(self.entity_patterns.keys())
