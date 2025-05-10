# Changelog

## [1.1.0] - Prompt System Refactoring - 2023-10-13

### Additions
- New prompt templates incorporating techniques from leaked system prompts
- Implementation of "Tool-First" design with explicit JSON schemas
- Addition of step-by-step reasoning in all prompts
- Self-critique loops to improve analysis reliability
- New prompt for user journey analysis
- New prompt for DOM modification validation
- Complete documentation of the prompt system in `models/README.md`

### Changes
- Complete redesign of all existing prompt templates
- Improved error handling in sentiment analysis
- Systematic integration of JSON parsers in all processing chains
- Restructuring of specialized analyses to follow a consistent format
- Updated helper functions to support new formats

### Fixes
- Resolved JSON parsing issues in API responses
- Better handling of error cases and timeouts
- Reduction of hallucinations and malformatted responses

## [1.0.0] - Initial Version - 2023-09-01

### Features
- Sentiment analysis system for user feedback
- Extraction of emotions and UX/UI themes
- Generation of design recommendations
- Integration with user behavior analysis APIs
- Support for major LLM models via LangChain 