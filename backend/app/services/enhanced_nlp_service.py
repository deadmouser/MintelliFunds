"""
Enhanced Natural Language Processing service for financial queries
Provides advanced intent classification, entity extraction, and context management
"""
import re
import logging
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from enum import Enum
from dataclasses import dataclass, field
import json
from collections import defaultdict

logger = logging.getLogger(__name__)


class IntentCategory(Enum):
    """High-level intent categories"""
    ANALYSIS = "analysis"
    TRANSACTION = "transaction"
    PLANNING = "planning"
    COMPARISON = "comparison"
    ALERT = "alert"
    GENERAL = "general"


class ConfidenceLevel(Enum):
    """Confidence levels for NLP results"""
    HIGH = "high"      # 0.8-1.0
    MEDIUM = "medium"  # 0.5-0.8
    LOW = "low"        # 0.2-0.5
    VERY_LOW = "very_low"  # 0.0-0.2


@dataclass
class Entity:
    """Enhanced entity representation"""
    type: str
    value: Any
    confidence: float
    start_pos: int = -1
    end_pos: int = -1
    context: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": self.type,
            "value": self.value,
            "confidence": self.confidence,
            "start_pos": self.start_pos,
            "end_pos": self.end_pos,
            "context": self.context
        }


@dataclass
class Intent:
    """Enhanced intent representation"""
    name: str
    category: IntentCategory
    confidence: float
    parameters: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "category": self.category.value,
            "confidence": self.confidence,
            "parameters": self.parameters
        }


@dataclass
class ConversationContext:
    """Context for maintaining conversation state"""
    user_id: str
    session_id: str
    previous_intents: List[str] = field(default_factory=list)
    mentioned_entities: Dict[str, List[Entity]] = field(default_factory=dict)
    conversation_topic: Optional[str] = None
    last_analysis_type: Optional[str] = None
    turn_count: int = 0
    created_at: datetime = field(default_factory=datetime.utcnow)


class EnhancedNLPService:
    """Enhanced NLP service with advanced capabilities"""
    
    def __init__(self):
        """Initialize the enhanced NLP service"""
        self.conversation_contexts: Dict[str, ConversationContext] = {}
        self._initialize_patterns()
        self._initialize_entity_extractors()
        self._initialize_intent_classifiers()
    
    def _initialize_patterns(self):
        """Initialize enhanced pattern matching"""
        self.intent_patterns = {
            # Spending Analysis Intents
            "analyze_spending": {
                "category": IntentCategory.ANALYSIS,
                "patterns": [
                    r"(?:analyze|analysis|breakdown|review)\s+(?:my\s+)?spending",
                    r"where\s+(?:did|is)\s+my\s+money\s+go",
                    r"spending\s+(?:patterns?|trends?|habits?)",
                    r"expense\s+(?:analysis|breakdown|report)",
                    r"how\s+much\s+(?:did\s+i|have\s+i)\s+spent?"
                ],
                "keywords": ["spending", "expense", "analysis", "breakdown", "where", "money"],
                "priority": 1
            },
            
            "spending_by_category": {
                "category": IntentCategory.ANALYSIS,
                "patterns": [
                    r"spending\s+(?:by\s+category|categories|per\s+category)",
                    r"category\s+(?:wise\s+)?spending",
                    r"how\s+much\s+on\s+(?:food|groceries|entertainment|transport)",
                    r"break\s+down\s+(?:my\s+)?expenses?\s+by\s+category"
                ],
                "keywords": ["category", "breakdown", "by", "on"],
                "priority": 2
            },
            
            # Savings & Investment Intents  
            "savings_analysis": {
                "category": IntentCategory.ANALYSIS,
                "patterns": [
                    r"(?:how\s+much\s+)?(?:am\s+i|have\s+i)\s+sav(?:ed|ing)",
                    r"savings?\s+(?:rate|amount|analysis|summary)",
                    r"saving\s+(?:progress|goals?|performance)",
                    r"money\s+(?:saved|being\s+saved)"
                ],
                "keywords": ["saving", "saved", "savings", "rate"],
                "priority": 1
            },
            
            "investment_performance": {
                "category": IntentCategory.ANALYSIS,
                "patterns": [
                    r"investment\s+(?:performance|returns?|gains?)",
                    r"portfolio\s+(?:performance|value|summary)",
                    r"how\s+(?:are\s+my|well\s+are)\s+investments?\s+doing",
                    r"stock\s+(?:performance|returns?)"
                ],
                "keywords": ["investment", "portfolio", "stock", "returns", "gains"],
                "priority": 1
            },
            
            # Planning & Forecasting Intents
            "budget_planning": {
                "category": IntentCategory.PLANNING,
                "patterns": [
                    r"budget\s+(?:planning|plan|for|recommendations?)",
                    r"create\s+(?:a\s+)?budget",
                    r"budget\s+suggestions?",
                    r"help\s+(?:me\s+)?(?:with\s+)?budgeting"
                ],
                "keywords": ["budget", "planning", "plan", "create"],
                "priority": 1
            },
            
            "future_projection": {
                "category": IntentCategory.PLANNING,
                "patterns": [
                    r"future\s+(?:balance|savings?|projection)",
                    r"project\s+(?:my\s+)?(?:savings?|balance|finances?)",
                    r"forecast\s+(?:my\s+)?(?:savings?|money)",
                    r"where\s+will\s+i\s+be\s+(?:in|next)"
                ],
                "keywords": ["future", "project", "forecast", "projection"],
                "priority": 1
            },
            
            "affordability_check": {
                "category": IntentCategory.PLANNING,
                "patterns": [
                    r"can\s+i\s+afford",
                    r"afford(?:able)?\s+(?:to\s+buy|this|that)",
                    r"should\s+i\s+buy",
                    r"(?:is\s+)?(?:this\s+)?(?:within\s+)?(?:my\s+)?budget",
                    r"financial(?:ly)?\s+feasible"
                ],
                "keywords": ["afford", "buy", "budget", "feasible"],
                "priority": 2
            },
            
            # Comparison Intents
            "spending_comparison": {
                "category": IntentCategory.COMPARISON,
                "patterns": [
                    r"compar(?:e|ing|ison)\s+(?:my\s+)?spending",
                    r"spending\s+(?:vs|versus|compared\s+to)",
                    r"this\s+month\s+vs\s+last\s+month",
                    r"year\s+over\s+year\s+spending"
                ],
                "keywords": ["compare", "vs", "versus", "compared"],
                "priority": 2
            },
            
            # Alert & Notification Intents
            "spending_alerts": {
                "category": IntentCategory.ALERT,
                "patterns": [
                    r"alert\s+(?:me\s+)?(?:when|if)",
                    r"notify\s+(?:me\s+)?(?:when|if)",
                    r"overspend(?:ing)?",
                    r"spending\s+limit",
                    r"budget\s+(?:exceeded|over)"
                ],
                "keywords": ["alert", "notify", "limit", "exceeded", "over"],
                "priority": 2
            },
            
            # General Financial Health
            "financial_health": {
                "category": IntentCategory.GENERAL,
                "patterns": [
                    r"financial\s+(?:health|situation|status|overview)",
                    r"how\s+(?:am\s+i|are\s+my\s+finances?)\s+doing",
                    r"money\s+(?:situation|status|overview)",
                    r"overall\s+financial",
                    r"financial\s+summary"
                ],
                "keywords": ["financial", "health", "situation", "overview", "summary"],
                "priority": 1
            }
        }
    
    def _initialize_entity_extractors(self):
        """Initialize enhanced entity extraction patterns"""
        self.entity_patterns = {
            "monetary_amount": [
                r"(?:\$|USD\s*)?(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)\s*(?:dollars?|USD|usd|\$)?",
                r"(\d+(?:\.\d{2})?)\s*(?:k|K|thousand)(?:\s*dollars?)?",
                r"(\d+(?:\.\d{2})?)\s*(?:M|million)(?:\s*dollars?)?"
            ],
            
            "percentage": [
                r"(\d+(?:\.\d+)?)\s*(?:%|percent|percentage)",
                r"(\d+(?:\.\d+)?)\s*(?:basis\s*points?|bps)"
            ],
            
            "time_period": [
                r"(?:this|current|present)\s+(month|week|year|quarter)",
                r"(?:last|previous|past)\s+(month|week|year|quarter)",
                r"(?:next|upcoming|coming)\s+(month|week|year|quarter)",
                r"(?:past|last)\s+(\d+)\s+(months?|weeks?|years?|quarters?)",
                r"(?:next|coming)\s+(\d+)\s+(months?|weeks?|years?|quarters?)",
                r"(january|february|march|april|may|june|july|august|september|october|november|december)",
                r"(q1|q2|q3|q4|quarter\s*[1-4])",
                r"(20\d{2})"
            ],
            
            "spending_category": [
                r"(?:groceries|food|dining|restaurant|eating)",
                r"(?:transport|transportation|gas|fuel|uber|taxi|car)",
                r"(?:housing|rent|mortgage|utilities|home)",
                r"(?:entertainment|movies|games|subscriptions|fun)",
                r"(?:health|medical|fitness|gym|healthcare)",
                r"(?:shopping|clothes|clothing|retail|apparel)",
                r"(?:education|school|books|courses|learning)",
                r"(?:travel|vacation|hotel|flight|trip)",
                r"(?:insurance|medical\s+insurance|car\s+insurance)",
                r"(?:investment|savings|retirement|401k)"
            ],
            
            "financial_account": [
                r"(?:checking|savings|investment|retirement|401k|ira)\s*account",
                r"(?:credit\s+card|debit\s+card|bank\s+account)",
                r"(?:portfolio|brokerage|trading)\s*account"
            ],
            
            "comparison_operator": [
                r"(?:more|less|higher|lower|greater|smaller)\s*than",
                r"(?:above|below|over|under)",
                r"(?:increase|decrease|up|down|rise|fall)",
                r"(?:vs|versus|compared\s+to|against)"
            ]
        }
    
    def _initialize_intent_classifiers(self):
        """Initialize ML-like intent classification weights"""
        self.intent_weights = {
            # Financial keywords with category weights
            "spending": {"analyze_spending": 0.8, "spending_by_category": 0.6, "spending_comparison": 0.4},
            "savings": {"savings_analysis": 0.9, "future_projection": 0.3},
            "budget": {"budget_planning": 0.9, "affordability_check": 0.4},
            "investment": {"investment_performance": 0.9, "savings_analysis": 0.2},
            "compare": {"spending_comparison": 0.8, "investment_performance": 0.2},
            "afford": {"affordability_check": 0.9, "budget_planning": 0.3},
            "future": {"future_projection": 0.8, "budget_planning": 0.2},
            "alert": {"spending_alerts": 0.9},
            "health": {"financial_health": 0.9}
        }
    
    def process_query(self, user_query: str, user_id: str = "default", 
                     session_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Enhanced query processing with context management
        
        Args:
            user_query: The user's natural language query
            user_id: Unique user identifier
            session_id: Optional session identifier
            
        Returns:
            Enhanced dictionary with intent, entities, and context
        """
        try:
            logger.info(f"Processing enhanced query: '{user_query[:50]}...'")
            
            # Get or create conversation context
            context_key = f"{user_id}:{session_id or 'default'}"
            context = self._get_or_create_context(context_key, user_id, session_id)
            context.turn_count += 1
            
            # Normalize query
            normalized_query = self._advanced_normalize_query(user_query)
            
            # Extract entities first (for better intent classification)
            entities = self._enhanced_entity_extraction(normalized_query, context)
            
            # Classify intent with context
            intent = self._advanced_intent_classification(normalized_query, entities, context)
            
            # Update context with new information
            self._update_conversation_context(context, intent, entities)
            
            # Calculate overall confidence
            overall_confidence = self._calculate_overall_confidence(intent, entities)
            
            # Generate response metadata
            response_metadata = self._generate_response_metadata(intent, entities, context)
            
            result = {
                "intent": intent.to_dict(),
                "entities": {k: [e.to_dict() for e in v] for k, v in entities.items()},
                "confidence": {
                    "intent": intent.confidence,
                    "entities": self._calculate_entity_confidence(entities),
                    "overall": overall_confidence,
                    "level": self._get_confidence_level(overall_confidence).value
                },
                "context": {
                    "session_id": context.session_id,
                    "turn_count": context.turn_count,
                    "conversation_topic": context.conversation_topic,
                    "last_analysis": context.last_analysis_type
                },
                "query_info": {
                    "original": user_query,
                    "normalized": normalized_query,
                    "word_count": len(user_query.split()),
                    "contains_numbers": bool(re.search(r'\d', user_query))
                },
                "response_metadata": response_metadata,
                "processing_info": {
                    "timestamp": datetime.utcnow().isoformat() + "Z",
                    "processing_time_ms": 0  # Would be calculated in production
                }
            }
            
            logger.info(f"Enhanced query processed - Intent: {intent.name} ({intent.confidence:.2f}), "
                       f"Entities: {sum(len(v) for v in entities.values())}")
            return result
            
        except Exception as e:
            logger.error(f"Error in enhanced query processing: {str(e)}")
            return self._create_error_response(user_query, str(e))
    
    def _get_or_create_context(self, context_key: str, user_id: str, 
                              session_id: Optional[str]) -> ConversationContext:
        """Get existing or create new conversation context"""
        if context_key not in self.conversation_contexts:
            self.conversation_contexts[context_key] = ConversationContext(
                user_id=user_id,
                session_id=session_id or "default"
            )
        return self.conversation_contexts[context_key]
    
    def _advanced_normalize_query(self, query: str) -> str:
        """Advanced query normalization"""
        # Basic normalization
        normalized = query.lower().strip()
        
        # Remove extra whitespace
        normalized = re.sub(r'\s+', ' ', normalized)
        
        # Handle contractions
        contractions = {
            "i'm": "i am", "i've": "i have", "i'll": "i will", "i'd": "i would",
            "don't": "do not", "won't": "will not", "can't": "cannot",
            "shouldn't": "should not", "wouldn't": "would not"
        }
        
        for contraction, expansion in contractions.items():
            normalized = normalized.replace(contraction, expansion)
        
        # Normalize financial terms
        financial_normalizations = {
            r"\b(?:bucks?|dollars?)\b": "dollars",
            r"\b(?:k|thousand)\b": "thousand",
            r"\b(?:mil|million)\b": "million",
            r"\b(?:yr|years?)\b": "year",
            r"\b(?:mo|months?)\b": "month"
        }
        
        for pattern, replacement in financial_normalizations.items():
            normalized = re.sub(pattern, replacement, normalized, flags=re.IGNORECASE)
        
        return normalized
    
    def _enhanced_entity_extraction(self, query: str, 
                                  context: ConversationContext) -> Dict[str, List[Entity]]:
        """Enhanced entity extraction with context awareness"""
        entities = defaultdict(list)
        
        # Extract monetary amounts with enhanced processing
        amounts = self._extract_monetary_amounts(query)
        for amount_data in amounts:
            entity = Entity(
                type="monetary_amount",
                value=amount_data["value"],
                confidence=amount_data["confidence"],
                start_pos=amount_data.get("start", -1),
                end_pos=amount_data.get("end", -1),
                context={"normalized_value": amount_data["normalized"]}
            )
            entities["monetary_amount"].append(entity)
        
        # Extract time periods with context
        time_periods = self._extract_time_periods(query, context)
        entities["time_period"].extend(time_periods)
        
        # Extract spending categories
        categories = self._extract_spending_categories(query)
        entities["spending_category"].extend(categories)
        
        # Extract financial accounts
        accounts = self._extract_financial_accounts(query)
        entities["financial_account"].extend(accounts)
        
        # Extract percentages
        percentages = self._extract_percentages(query)
        entities["percentage"].extend(percentages)
        
        # Extract comparison operators
        comparisons = self._extract_comparisons(query)
        entities["comparison"].extend(comparisons)
        
        return dict(entities)
    
    def _extract_monetary_amounts(self, query: str) -> List[Dict[str, Any]]:
        """Extract monetary amounts with normalization"""
        amounts = []
        
        # Pattern for various monetary formats
        patterns = [
            r"(?:\$|USD\s*)?(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)\s*(?:dollars?|USD|usd|\$)?",
            r"(\d+(?:\.\d{2})?)\s*(?:k|K|thousand)(?:\s*dollars?)?",
            r"(\d+(?:\.\d{2})?)\s*(?:M|million)(?:\s*dollars?)?"
        ]
        
        for pattern in patterns:
            for match in re.finditer(pattern, query, re.IGNORECASE):
                amount_str = match.group(1)
                
                # Normalize based on pattern
                if 'k' in match.group(0).lower() or 'thousand' in match.group(0).lower():
                    normalized = float(amount_str) * 1000
                elif 'm' in match.group(0).lower() or 'million' in match.group(0).lower():
                    normalized = float(amount_str) * 1000000
                else:
                    normalized = float(amount_str.replace(',', ''))
                
                amounts.append({
                    "value": amount_str,
                    "normalized": normalized,
                    "confidence": 0.9,
                    "start": match.start(),
                    "end": match.end()
                })
        
        return amounts
    
    def _extract_time_periods(self, query: str, context: ConversationContext) -> List[Entity]:
        """Extract time periods with context awareness"""
        time_periods = []
        
        # Current time references
        current_patterns = [
            (r"\b(?:this|current)\s+(month|week|year|quarter)\b", "current"),
            (r"\b(?:last|previous)\s+(month|week|year|quarter)\b", "previous"),
            (r"\b(?:next|upcoming)\s+(month|week|year|quarter)\b", "next")
        ]
        
        for pattern, time_type in current_patterns:
            for match in re.finditer(pattern, query, re.IGNORECASE):
                period = match.group(1).lower()
                entity = Entity(
                    type="time_period",
                    value=f"{time_type}_{period}",
                    confidence=0.95,
                    context={
                        "period_type": period,
                        "relative_type": time_type,
                        "resolved_date": self._resolve_time_period(time_type, period)
                    }
                )
                time_periods.append(entity)
        
        # Specific months/years
        month_pattern = r"\b(january|february|march|april|may|june|july|august|september|october|november|december)\b"
        for match in re.finditer(month_pattern, query, re.IGNORECASE):
            month_name = match.group(1).lower()
            entity = Entity(
                type="time_period",
                value=month_name,
                confidence=0.9,
                context={"period_type": "month", "month_name": month_name}
            )
            time_periods.append(entity)
        
        return time_periods
    
    def _resolve_time_period(self, time_type: str, period: str) -> Dict[str, str]:
        """Resolve relative time periods to actual dates"""
        now = datetime.utcnow()
        
        if time_type == "current":
            if period == "month":
                start = now.replace(day=1)
                end = (start + relativedelta(months=1)) - timedelta(days=1)
            elif period == "year":
                start = now.replace(month=1, day=1)
                end = now.replace(month=12, day=31)
            else:  # week, quarter
                start = now - timedelta(days=7)
                end = now
        elif time_type == "previous":
            if period == "month":
                start = (now.replace(day=1) - relativedelta(months=1))
                end = now.replace(day=1) - timedelta(days=1)
            else:
                start = now - timedelta(days=30)
                end = now - timedelta(days=1)
        else:  # next
            if period == "month":
                start = (now.replace(day=1) + relativedelta(months=1))
                end = (start + relativedelta(months=1)) - timedelta(days=1)
            else:
                start = now + timedelta(days=1)
                end = now + timedelta(days=30)
        
        return {
            "start_date": start.isoformat(),
            "end_date": end.isoformat()
        }
    
    def _extract_spending_categories(self, query: str) -> List[Entity]:
        """Extract spending categories"""
        categories = []
        category_mapping = {
            r"\b(?:groceries|food|dining|restaurant|eating)\b": "food",
            r"\b(?:transport|transportation|gas|fuel|uber|taxi|car)\b": "transportation", 
            r"\b(?:housing|rent|mortgage|utilities|home)\b": "housing",
            r"\b(?:entertainment|movies|games|subscriptions|fun)\b": "entertainment",
            r"\b(?:health|medical|fitness|gym|healthcare)\b": "healthcare",
            r"\b(?:shopping|clothes|clothing|retail|apparel)\b": "shopping",
            r"\b(?:education|school|books|courses|learning)\b": "education",
            r"\b(?:travel|vacation|hotel|flight|trip)\b": "travel",
            r"\b(?:insurance)\b": "insurance"
        }
        
        for pattern, category in category_mapping.items():
            if re.search(pattern, query, re.IGNORECASE):
                entity = Entity(
                    type="spending_category",
                    value=category,
                    confidence=0.85,
                    context={"category_group": self._get_category_group(category)}
                )
                categories.append(entity)
        
        return categories
    
    def _get_category_group(self, category: str) -> str:
        """Get higher-level category group"""
        category_groups = {
            "food": "living_expenses",
            "transportation": "living_expenses", 
            "housing": "fixed_expenses",
            "utilities": "fixed_expenses",
            "entertainment": "discretionary",
            "healthcare": "essential",
            "shopping": "discretionary",
            "education": "investment",
            "travel": "discretionary",
            "insurance": "fixed_expenses"
        }
        return category_groups.get(category, "other")
    
    def _extract_financial_accounts(self, query: str) -> List[Entity]:
        """Extract financial account references"""
        accounts = []
        account_patterns = [
            (r"\b(checking|savings|investment|retirement|401k|ira)\s*account\b", "account"),
            (r"\b(credit\s+card|debit\s+card)\b", "card"),
            (r"\b(portfolio|brokerage|trading)\s*account\b", "investment_account")
        ]
        
        for pattern, account_type in account_patterns:
            for match in re.finditer(pattern, query, re.IGNORECASE):
                entity = Entity(
                    type="financial_account",
                    value=match.group(1).lower().replace(" ", "_"),
                    confidence=0.9,
                    context={"account_type": account_type}
                )
                accounts.append(entity)
        
        return accounts
    
    def _extract_percentages(self, query: str) -> List[Entity]:
        """Extract percentages"""
        percentages = []
        pattern = r"(\d+(?:\.\d+)?)\s*(?:%|percent|percentage)"
        
        for match in re.finditer(pattern, query, re.IGNORECASE):
            value = float(match.group(1))
            entity = Entity(
                type="percentage",
                value=value,
                confidence=0.95,
                context={"normalized_value": value / 100}
            )
            percentages.append(entity)
        
        return percentages
    
    def _extract_comparisons(self, query: str) -> List[Entity]:
        """Extract comparison operators"""
        comparisons = []
        comparison_patterns = [
            (r"\b(more|less|higher|lower|greater|smaller)\s*than\b", "comparative"),
            (r"\b(above|below|over|under)\b", "threshold"),
            (r"\b(vs|versus|compared\s+to|against)\b", "direct_comparison")
        ]
        
        for pattern, comp_type in comparison_patterns:
            for match in re.finditer(pattern, query, re.IGNORECASE):
                entity = Entity(
                    type="comparison",
                    value=match.group(1).lower(),
                    confidence=0.8,
                    context={"comparison_type": comp_type}
                )
                comparisons.append(entity)
        
        return comparisons
    
    def _advanced_intent_classification(self, query: str, entities: Dict[str, List[Entity]], 
                                      context: ConversationContext) -> Intent:
        """Advanced intent classification with ML-like scoring"""
        intent_scores = defaultdict(float)
        
        # Pattern-based scoring
        for intent_name, intent_data in self.intent_patterns.items():
            score = 0
            
            # Pattern matching
            for pattern in intent_data["patterns"]:
                if re.search(pattern, query, re.IGNORECASE):
                    score += 2.0
            
            # Keyword matching with TF-IDF-like scoring
            query_words = set(query.lower().split())
            intent_keywords = set(intent_data["keywords"])
            keyword_overlap = len(query_words.intersection(intent_keywords))
            
            if keyword_overlap > 0:
                score += keyword_overlap * 1.5
            
            # Priority weighting
            score *= intent_data.get("priority", 1)
            
            intent_scores[intent_name] = score
        
        # Entity-based scoring enhancement
        self._enhance_scores_with_entities(intent_scores, entities)
        
        # Context-based scoring enhancement
        self._enhance_scores_with_context(intent_scores, context)
        
        # Get the best intent
        if intent_scores:
            best_intent_name = max(intent_scores, key=intent_scores.get)
            best_score = intent_scores[best_intent_name]
            
            # Normalize confidence score
            confidence = min(1.0, best_score / 5.0)  # Normalize to 0-1 range
            
            intent_data = self.intent_patterns[best_intent_name]
            return Intent(
                name=best_intent_name,
                category=intent_data["category"],
                confidence=confidence,
                parameters=self._extract_intent_parameters(best_intent_name, entities)
            )
        
        # Fallback intent
        return Intent(
            name="general_inquiry",
            category=IntentCategory.GENERAL,
            confidence=0.3,
            parameters={}
        )
    
    def _enhance_scores_with_entities(self, intent_scores: Dict[str, float], 
                                    entities: Dict[str, List[Entity]]):
        """Enhance intent scores based on extracted entities"""
        # Monetary amounts suggest financial analysis
        if "monetary_amount" in entities:
            intent_scores["analyze_spending"] += 1.0
            intent_scores["affordability_check"] += 1.5
        
        # Time periods suggest temporal analysis
        if "time_period" in entities:
            intent_scores["spending_comparison"] += 1.0
            intent_scores["future_projection"] += 1.0
        
        # Categories suggest category analysis
        if "spending_category" in entities:
            intent_scores["spending_by_category"] += 2.0
            intent_scores["budget_planning"] += 1.0
        
        # Comparisons suggest comparative analysis
        if "comparison" in entities:
            intent_scores["spending_comparison"] += 2.0
        
        # Percentages suggest performance or rate analysis
        if "percentage" in entities:
            intent_scores["savings_analysis"] += 1.0
            intent_scores["investment_performance"] += 1.0
    
    def _enhance_scores_with_context(self, intent_scores: Dict[str, float], 
                                   context: ConversationContext):
        """Enhance intent scores based on conversation context"""
        # Recent intent continuity
        if context.previous_intents:
            last_intent = context.previous_intents[-1]
            
            # Boost similar or related intents
            intent_relationships = {
                "analyze_spending": ["spending_by_category", "spending_comparison"],
                "budget_planning": ["affordability_check", "future_projection"],
                "investment_performance": ["savings_analysis"],
                "financial_health": ["analyze_spending", "savings_analysis"]
            }
            
            if last_intent in intent_relationships:
                for related_intent in intent_relationships[last_intent]:
                    if related_intent in intent_scores:
                        intent_scores[related_intent] += 0.5
    
    def _extract_intent_parameters(self, intent_name: str, 
                                 entities: Dict[str, List[Entity]]) -> Dict[str, Any]:
        """Extract parameters specific to the identified intent"""
        parameters = {}
        
        if intent_name in ["analyze_spending", "spending_by_category"]:
            if "time_period" in entities:
                parameters["time_period"] = entities["time_period"][0].value
            if "spending_category" in entities:
                parameters["categories"] = [e.value for e in entities["spending_category"]]
        
        elif intent_name == "affordability_check":
            if "monetary_amount" in entities:
                parameters["target_amount"] = entities["monetary_amount"][0].context.get("normalized_value")
        
        elif intent_name == "future_projection":
            if "time_period" in entities:
                parameters["projection_period"] = entities["time_period"][0].value
        
        elif intent_name == "spending_comparison":
            if "time_period" in entities and len(entities["time_period"]) >= 2:
                parameters["compare_periods"] = [e.value for e in entities["time_period"]]
            if "comparison" in entities:
                parameters["comparison_type"] = entities["comparison"][0].value
        
        return parameters
    
    def _update_conversation_context(self, context: ConversationContext, 
                                   intent: Intent, entities: Dict[str, List[Entity]]):
        """Update conversation context with new information"""
        # Update previous intents (keep last 5)
        context.previous_intents.append(intent.name)
        context.previous_intents = context.previous_intents[-5:]
        
        # Update conversation topic based on intent category
        topic_mapping = {
            IntentCategory.ANALYSIS: "financial_analysis",
            IntentCategory.PLANNING: "financial_planning",
            IntentCategory.COMPARISON: "comparative_analysis",
            IntentCategory.ALERT: "monitoring",
            IntentCategory.GENERAL: "general_inquiry"
        }
        context.conversation_topic = topic_mapping.get(intent.category, "general")
        
        # Update last analysis type
        if intent.category == IntentCategory.ANALYSIS:
            context.last_analysis_type = intent.name
        
        # Store mentioned entities for context
        for entity_type, entity_list in entities.items():
            if entity_type not in context.mentioned_entities:
                context.mentioned_entities[entity_type] = []
            
            # Add new entities, avoid duplicates
            existing_values = {e.value for e in context.mentioned_entities[entity_type]}
            for entity in entity_list:
                if entity.value not in existing_values:
                    context.mentioned_entities[entity_type].append(entity)
            
            # Keep only recent entities (last 10)
            context.mentioned_entities[entity_type] = context.mentioned_entities[entity_type][-10:]
    
    def _calculate_entity_confidence(self, entities: Dict[str, List[Entity]]) -> float:
        """Calculate overall confidence for entity extraction"""
        if not entities:
            return 0.0
        
        total_confidence = 0
        total_entities = 0
        
        for entity_list in entities.values():
            for entity in entity_list:
                total_confidence += entity.confidence
                total_entities += 1
        
        return total_confidence / total_entities if total_entities > 0 else 0.0
    
    def _calculate_overall_confidence(self, intent: Intent, 
                                    entities: Dict[str, List[Entity]]) -> float:
        """Calculate overall confidence combining intent and entity confidence"""
        entity_confidence = self._calculate_entity_confidence(entities)
        
        # Weight intent confidence more heavily
        overall = (intent.confidence * 0.7) + (entity_confidence * 0.3)
        return min(1.0, overall)
    
    def _get_confidence_level(self, confidence: float) -> ConfidenceLevel:
        """Convert numerical confidence to confidence level"""
        if confidence >= 0.8:
            return ConfidenceLevel.HIGH
        elif confidence >= 0.5:
            return ConfidenceLevel.MEDIUM
        elif confidence >= 0.2:
            return ConfidenceLevel.LOW
        else:
            return ConfidenceLevel.VERY_LOW
    
    def _generate_response_metadata(self, intent: Intent, entities: Dict[str, List[Entity]], 
                                  context: ConversationContext) -> Dict[str, Any]:
        """Generate metadata to help with response generation"""
        return {
            "suggested_analysis": self._suggest_analysis_type(intent, entities),
            "required_data": self._determine_required_data(intent, entities),
            "context_hints": self._generate_context_hints(context),
            "response_tone": self._determine_response_tone(intent, context),
            "follow_up_suggestions": self._generate_follow_up_suggestions(intent, entities)
        }
    
    def _suggest_analysis_type(self, intent: Intent, entities: Dict[str, List[Entity]]) -> str:
        """Suggest the type of financial analysis needed"""
        analysis_mapping = {
            "analyze_spending": "spending_analysis",
            "spending_by_category": "category_spending_analysis", 
            "savings_analysis": "savings_analysis",
            "investment_performance": "investment_analysis",
            "affordability_check": "affordability_analysis",
            "future_projection": "projection_analysis",
            "spending_comparison": "comparative_analysis",
            "budget_planning": "budget_analysis",
            "financial_health": "comprehensive_analysis"
        }
        return analysis_mapping.get(intent.name, "general_analysis")
    
    def _determine_required_data(self, intent: Intent, entities: Dict[str, List[Entity]]) -> List[str]:
        """Determine what data is required for the analysis"""
        data_requirements = {
            "analyze_spending": ["transactions", "spending_trends"],
            "spending_by_category": ["transactions", "category_breakdown"],
            "savings_analysis": ["accounts", "transactions"],
            "investment_performance": ["investments"],
            "affordability_check": ["accounts", "transactions"],
            "future_projection": ["accounts", "transactions", "spending_trends"],
            "budget_planning": ["transactions", "spending_trends", "accounts"],
            "financial_health": ["accounts", "transactions", "investments", "liabilities"]
        }
        return data_requirements.get(intent.name, ["transactions", "accounts"])
    
    def _generate_context_hints(self, context: ConversationContext) -> List[str]:
        """Generate hints based on conversation context"""
        hints = []
        
        if context.turn_count > 1:
            hints.append("continuing_conversation")
        
        if context.conversation_topic:
            hints.append(f"topic_{context.conversation_topic}")
        
        if context.previous_intents:
            hints.append(f"previous_{context.previous_intents[-1]}")
        
        return hints
    
    def _determine_response_tone(self, intent: Intent, context: ConversationContext) -> str:
        """Determine appropriate response tone"""
        if intent.confidence < 0.5:
            return "clarifying"
        elif intent.category == IntentCategory.ALERT:
            return "informative_alert"
        elif intent.category == IntentCategory.PLANNING:
            return "advisory"
        else:
            return "informative"
    
    def _generate_follow_up_suggestions(self, intent: Intent, 
                                      entities: Dict[str, List[Entity]]) -> List[str]:
        """Generate follow-up question suggestions"""
        suggestions = []
        
        follow_up_mapping = {
            "analyze_spending": [
                "Would you like to see spending by category?",
                "Shall I compare with previous months?",
                "Do you want budget recommendations?"
            ],
            "savings_analysis": [
                "Would you like to see future projections?",
                "Shall I analyze your savings goals?",
                "Do you want investment recommendations?"
            ],
            "affordability_check": [
                "Would you like a savings plan?",
                "Shall I suggest budget adjustments?",
                "Do you want to see payment options?"
            ]
        }
        
        return follow_up_mapping.get(intent.name, [])
    
    def _create_error_response(self, query: str, error: str) -> Dict[str, Any]:
        """Create error response for failed processing"""
        return {
            "intent": {"name": "error", "category": "general", "confidence": 0.0},
            "entities": {},
            "confidence": {"intent": 0.0, "entities": 0.0, "overall": 0.0, "level": "very_low"},
            "context": {"error": True},
            "query_info": {"original": query, "normalized": query},
            "error": error,
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }
    
    def get_conversation_summary(self, user_id: str, session_id: str = "default") -> Dict[str, Any]:
        """Get conversation summary for a user session"""
        context_key = f"{user_id}:{session_id}"
        
        if context_key not in self.conversation_contexts:
            return {"error": "No conversation found"}
        
        context = self.conversation_contexts[context_key]
        
        return {
            "user_id": user_id,
            "session_id": session_id,
            "turn_count": context.turn_count,
            "conversation_topic": context.conversation_topic,
            "recent_intents": context.previous_intents[-5:],
            "mentioned_entities": {
                k: len(v) for k, v in context.mentioned_entities.items()
            },
            "session_duration": (datetime.utcnow() - context.created_at).total_seconds(),
            "last_activity": context.created_at.isoformat()
        }
    
    def clear_conversation_context(self, user_id: str, session_id: str = "default"):
        """Clear conversation context for a user session"""
        context_key = f"{user_id}:{session_id}"
        if context_key in self.conversation_contexts:
            del self.conversation_contexts[context_key]
            logger.info(f"Cleared conversation context for {context_key}")
    
    def get_supported_capabilities(self) -> Dict[str, Any]:
        """Get information about supported NLP capabilities"""
        return {
            "supported_intents": list(self.intent_patterns.keys()),
            "intent_categories": [cat.value for cat in IntentCategory],
            "supported_entities": list(self.entity_patterns.keys()),
            "confidence_levels": [level.value for level in ConfidenceLevel],
            "features": [
                "context_awareness",
                "entity_extraction", 
                "intent_classification",
                "confidence_scoring",
                "conversation_management",
                "temporal_resolution",
                "financial_entity_recognition"
            ]
        }