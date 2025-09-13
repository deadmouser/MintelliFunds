# AI Dataset Structure for MintelliFunds

This directory contains the AI dataset structure for training and inference in the MintelliFunds Financial AI Assistant.

## Directory Structure

```
ai_dataset/
├── training/           # Training data for AI models
│   ├── intents/        # Intent classification training data
│   ├── entities/       # Named entity recognition data
│   ├── responses/      # Response generation training data
│   └── conversations/  # Complete conversation examples
├── inference/          # Data for real-time inference
│   ├── prompts/        # System prompts and templates
│   ├── context/        # Context management data
│   └── cache/          # Cached inference results
├── models/             # Trained AI models and weights
│   ├── intent_classifier/
│   ├── entity_extractor/
│   ├── response_generator/
│   └── embeddings/
├── prompts/            # Prompt templates and system messages
│   ├── system_prompts.json
│   ├── user_prompts.json
│   └── few_shot_examples.json
└── examples/           # Example inputs and outputs
    ├── financial_queries.json
    ├── analysis_examples.json
    └── response_examples.json
```

## Data Categories

### 1. Intent Classification
- Financial queries categorized by intent
- Spending analysis, investment queries, budget planning, etc.
- Privacy-aware intent handling

### 2. Entity Extraction
- Financial entities: amounts, dates, categories, account types
- Context-aware entity recognition
- Multi-currency and multi-language support

### 3. Response Generation
- Context-aware financial advice
- Privacy-respecting responses
- Personalized recommendations

### 4. Conversation Management
- Multi-turn conversations
- Context preservation
- Privacy boundary enforcement

## Privacy Considerations

- All training data is anonymized
- No real financial data is stored
- Privacy permissions are enforced at dataset level
- Audit trails for all data access

## Model Integration Points

1. **Real-time Inference**: `/api/insights` endpoint
2. **Chat Interface**: `/api/chat` endpoint
3. **Analysis Service**: Backend analysis components
4. **Privacy Service**: Permission-based data filtering

## Usage

### Training
```python
# Load training data
from ai_dataset.training import load_training_data
training_data = load_training_data('intents')

# Train model
model = train_intent_classifier(training_data)
```

### Inference
```python
# Load inference prompts
from ai_dataset.inference import load_prompts
prompts = load_prompts('financial_analysis')

# Generate response
response = generate_response(query, prompts, context)
```

## Data Format Standards

### Intent Data Format
```json
{
  "query": "How much did I spend on food last month?",
  "intent": "get_spending_by_category",
  "entities": {
    "category": "food",
    "timeframe": "last_month"
  },
  "privacy_requirements": ["transactions", "spending_trends"]
}
```

### Response Template Format
```json
{
  "intent": "get_spending_by_category",
  "template": "Based on your {category} spending, you spent ₹{amount} {timeframe}. This is {change}% compared to the previous period.",
  "privacy_fallback": "I need access to your transaction data to provide spending analysis.",
  "variables": ["category", "amount", "timeframe", "change"]
}
```

## Development Guidelines

1. **Data Quality**: Ensure high-quality, diverse training examples
2. **Privacy First**: All data must respect privacy boundaries
3. **Multilingual**: Support for Indian financial contexts (₹, EPF, etc.)
4. **Scalability**: Structure supports easy addition of new data
5. **Versioning**: Track dataset versions for model reproducibility

## Integration with Backend

The AI dataset integrates with:
- `AIService`: Main AI inference service
- `NLPService`: Natural language processing
- `AnalysisService`: Financial analysis logic
- `PrivacyService`: Data access control

## Future Enhancements

1. **Federated Learning**: Train on user data without collecting it
2. **Personalization**: User-specific model fine-tuning
3. **Real-time Learning**: Continuous model improvement
4. **Multi-modal**: Support for document/image analysis