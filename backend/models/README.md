# Prompt System for the UX/UI Optimization Extension

This document explains the architecture and principles behind the prompt system used in our Chrome UX/UI optimization extension.

## Prompt Architecture

Our prompts have been enhanced based on advanced prompt engineering techniques derived from the analysis of leaked system prompts from popular AI tools such as Cursor, Replit Agent, and Devin.

### Key Principles

1. **Tool-First Design**
   - Each prompt begins with explicit JSON schemas for inputs and outputs
   - Models know exactly what data formats they need to produce
   - Guarantees structured output that can be automatically parsed

2. **Step-by-Step Reasoning and Self-Critique**
   - Prompts guide the model through a sequential analysis process
   - Explicitly numbered steps for methodical analysis
   - Self-verification loops to improve response reliability

3. **Strict Style Guides**
   - Precise formatting instructions for outputs
   - Avoids hallucinations by constraining the output format
   - Facilitates integration and post-processing of results

4. **Domain-Specialized Functions**
   - Each type of analysis is associated with a specific optimized prompt
   - Use of JSON parsers to ensure output validity
   - Modular and composable prompt chains

## Prompt Types

### Sentiment Analysis
- Classifies user feedback sentiment (positive, negative, neutral)
- Includes confidence level and justification
- Implements a self-verification loop for low-confidence cases

### Emotion and Theme Extraction
- Identifies emotions, UX/UI themes, and specific issues
- Evaluates problem severity
- Additional validation for long and complex feedback

### Feedback Summary
- Synthesizes multiple pieces of feedback to extract patterns
- Identifies key issues and positive aspects
- Proposes prioritized recommendations

### Design Recommendations
- Generates concrete and actionable UX/UI improvement suggestions
- Includes precise details on modifications to be made
- Specifies expected impact and data-driven justification

### DOM Modification Validator
- Verifies that proposed modifications are technically correct
- Improves CSS selectors and code if necessary
- Identifies potential side effects of changes

### User Journey Analyzer
- Analyzes session recordings to identify friction points
- Detects problematic behavior patterns
- Suggests improvements based on behavioral analysis

## Self-Critique Loops

To ensure the quality and reliability of analyses, we have implemented self-critique loops:

1. **Primary Validation**
   - Applied to sentiment analyses with low confidence
   - Forces the model to reevaluate its initial analysis

2. **Secondary Validation**
   - For long and complex feedback
   - Verifies that all relevant aspects have been extracted

3. **Final Validation**
   - Complete review of the analysis to detect inconsistencies or omissions
   - Adds missing elements if necessary

## Best Practices

- **Maintain schema consistency** between prompts and code
- **Regularly test** prompts with different types of feedback
- **Compare results** between different versions of prompts (A/B testing)
- **Collect errors** to identify areas for improvement
- **Iterate** on prompts based on observed performance

## Next Steps

- Evaluate the impact of new prompts on recommendation quality
- Optimize prompt length and complexity to balance performance and precision
- Explore the use of the Function API for even more seamless integration
- Implement an automated prompt evaluation system

## References

- [AI System Prompts Revealed: Inside the Architecture of Leading AI Tools](https://www.prompthacker.ai/p/ai-system-prompts-revealed-inside-the-architecture-of-leading-ai-tools)
- [Leaked Prompts Repository](https://github.com/linexjlin/leak-system-prompts/) 