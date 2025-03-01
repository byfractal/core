## Prerequisites

- Python : latest version
- Required libraries (see `requirements.txt`)
- Remove any existing files in the `data/raw/`, `data/processed/`, and `data/filtered/` directories to test the application.

## Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/byfractal/core.git
   cd core
   ```

2. Create a virtual environment:

   ```bash
   python -m venv .venv
   ```

3. Activate the virtual environment:

   - On Windows:
     ```bash
     .venv\Scripts\activate
     ```
   - On macOS/Linux:
     ```bash
     source .venv/bin/activate
     ```

4. Install the dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

### Data Collection and Processing

1. Configure your `.env` file with the necessary variables.
2. Run the application:
   ```bash
   python app/api.py
   ```

### Feedback Analysis Pipeline

The project includes a complete feedback analysis pipeline that processes user feedback using LLM chains:

1. To analyze feedback data from Amplitude or other sources:

   ```bash
   python backend/analyze_feedback.py --input path/to/feedback.json --page homepage
   ```

   Options:

   - `--input`: Path to the input JSON file containing feedback data
   - `--output`: Path to save the analysis results
   - `--page`: Filter feedback by page ID
   - `--days`: Number of days to look back for feedback (default: 30)
   - `--model`: OpenAI model to use for analysis (default: gpt-4o)

2. To generate design recommendations based on feedback analysis:
   ```bash
   python backend/models/design_recommendations.py
   ```

## Project Structure

```
core/
├── backend/
│   ├── models/
│   │   ├── embeddings.py         # OpenAI embeddings configuration
│   │   ├── vector_store.py       # FAISS vector store for RAG
│   │   ├── chain.py              # Basic conversation chain
│   │   ├── prompts.py            # Prompt templates for analysis
│   │   ├── analysis_chains.py    # LLM chains for feedback analysis
│   │   └── design_recommendations.py # Design recommendation generator
│   ├── services/
│   │   └── amplitude/            # Amplitude API integration
│   └── analyze_feedback.py       # Main entry point for analysis
├── datasets/                     # Sample datasets for testing
└── (other files)
```

## Feedback Analysis Features

The feedback analysis system consists of three main components:

1. **Sentiment Analysis**: Classifies feedback as positive, negative, or neutral with confidence scores.

2. **Emotion/Theme Extraction**: Identifies key emotions, themes, and specific UI/UX issues from feedback.

3. **Feedback Summarization**: Generates concise summaries of multiple feedback items, highlighting patterns and key issues.

4. **Design Recommendations**: Provides concrete UI/UX improvement suggestions based on feedback analysis.

## Contributing

Steps:

1. Fork the project.
2. Create a new branch (`git checkout -b feature/YourFeature`).
3. Make your changes and commit (`git commit -m 'Add some feature'`).
4. Push to the branch (`git push origin feature/YourFeature`).
5. Open a Pull Request.
