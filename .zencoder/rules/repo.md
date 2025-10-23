---
description: Repository Information Overview
alwaysApply: true
---

# Senti-Clean Information

## Summary
Senti-Clean is a production-ready web application for real-time toxicity detection and content moderation powered by transformer-based machine learning models. It identifies harmful content and provides AI-powered alternatives to rewrite toxic text into constructive feedback using Groq's Llama 3.1 API. The system features real-time detection, high accuracy toxicity classification using BERT/RoBERTa models, AI rewriting capabilities, sentiment analysis, and a modern responsive web interface.

## Structure
- **app.py**: Main Flask application entry point
- **detoxify/**: Core toxicity detection module
- **rewriter.py**: Hybrid rewriting system (Groq API + rule-based)
- **configs/**: Model configuration files
- **static/**: Frontend assets (CSS, JavaScript)
- **templates/**: HTML templates
- **model_eval/**: Model evaluation utilities
- **src/**: Source code utilities
- **tests/**: Test files and test data
- **uploads/**: Directory for uploaded files

## Language & Runtime
**Language**: Python
**Version**: 3.9-3.12 (requires >=3.9,<3.13)
**Framework**: Flask 2.0+
**Build System**: setuptools
**Package Manager**: pip

## Dependencies
**Main Dependencies**:
- torch >=2.0
- transformers >=3.0
- flask >=2.2.5
- groq >=0.32.0
- textblob >=0.19.0
- detoxify >=0.5.2
- python-dotenv >=1.1.1
- pytorch-lightning >=2.5.5

**Development Dependencies**:
- pytest
- pandas >=1.1.2
- scikit-learn >=0.23.2
- pre-commit
- pyright

## Build & Installation
```bash
pip install -r requirements.txt
python app.py
```

## Docker
No explicit Docker configuration found in the repository.

## Testing
**Framework**: pytest
**Test Location**: tests/
**Configuration**: pyproject.toml [tool.pytest.ini_options]
**Run Command**:
```bash
pytest tests/
```

## Main Files
**Entry Point**: app.py
**Core Components**:
- **detoxify.py**: Toxicity detection model implementation
- **rewriter.py**: Hybrid text rewriting system
- **app.py**: Flask web application
- **static/script.js**: Frontend JavaScript for UI interactions
- **templates/index.html**: Main web interface

## API Endpoints
- **/api/analyze**: Analyzes text for toxicity and provides rewrite suggestions
- **/api/rewrite**: AI-powered text rewriting endpoint
- **/api/upload**: File upload endpoint for batch analysis
- **/api/health**: Health check endpoint

## Features
- Real-time toxicity detection (under 3 seconds)
- 92%+ toxicity classification accuracy
- AI-powered text rewriting with Groq API
- Sentiment analysis with TextBlob
- File upload and batch analysis
- Responsive web interface