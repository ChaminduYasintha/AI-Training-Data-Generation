# Enterprise AI Training Data Factory

An automated, end-to-end data pipeline designed to ingest raw data from URLs or documents, chunk the text preserving semantics, and dynamically generate high-quality QA/Summary/Classification datasets using Google Gemini, OpenAI, or Anthropic.

## Quick Start
1. Create a virtual environment: `python -m venv venv`
2. Activate it: `venv\Scripts\activate` (Windows)
3. Install dependencies: `pip install -r requirements.txt`
4. Copy `.env.example` to `.env` and fill in your API keys.
5. Launch the UI: `streamlit run app.py`
