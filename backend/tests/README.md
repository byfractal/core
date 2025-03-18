# Backend Tests

This directory contains tests for the different components of the backend.

## Test Structure

### API Tests (`test_api.py`)
- Tests FastAPI endpoints
- Verifies main routes functionality
- Includes tests for:
  - Root endpoint
  - Health endpoint
  - Feedback endpoints
  - Analysis endpoints

### Feedback Analysis Tests (`test_feedback_analyzer.py`)
- Tests the feedback analysis module
- Verifies feedback data processing
- Tests various analysis parameters

### PostHog Extraction Tests (`test_posthog_extract.py`)
- Tests PostHog integration
- Verifies data retrieval
- Tests different PostHog APIs:
  - Events API
  - Session recordings API

### Prompt Tests (`test_prompts.py`)
- Tests LangChain prompt templates
- Verifies prompt generation for:
  - Sentiment classification
  - Emotion/theme extraction
  - Feedback summarization

### Recommendation Pipeline Tests (`test_recommendations_pipeline.py`)
- Complete test of the recommendation pipeline
- Includes:
  - PostHog integration tests
  - Recommendation generation tests
  - System automated tests

## Running Tests

To run the tests, use the following commands:

1. API Tests:
```bash
python tests/test_api.py
```

2. Feedback Analysis Tests:
```bash
python tests/test_feedback_analyzer.py
```

3. PostHog Tests:
```bash
python tests/test_posthog_extract.py
```

4. Prompt Tests:
```bash
python tests/test_prompts.py
```

5. Complete Pipeline Tests:
```bash
python tests/test_recommendations_pipeline.py
```

## Archived Tests

Obsolete or redundant tests are stored in the `backend/archive/` directory for future reference. 