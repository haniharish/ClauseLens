# ClauseLens — NLP Processing Module

> **Member 4 | AI Engineering & NLP**
> Part of the ClauseLens: Context-Aware Terms & Conditions Risk Summarization project.

---

## What This Module Does

The ClauseLens NLP module is a standalone FastAPI microservice that:

1. **Extracts text** from uploaded PDF documents (with optional OCR fallback for scanned PDFs).
2. **Cleans** the extracted text, removing structural noise while preserving all legal content.
3. **Segments** documents into individual, meaningful clauses using heading detection and fallback strategies.
4. **Classifies** each clause into one of 11 predefined legal categories (hybrid rule-based + zero-shot).
5. **Assigns severity priors** from the research paper's expert-set taxonomy.
6. **Generates semantic embeddings** using Sentence Transformers for downstream similarity and personalization.
7. **Summarizes** each clause in plain English using a configurable LLM provider.
8. **Supports diff-only reprocessing** for version updates (changed clauses only).
9. **Exposes a REST API** that the Django backend (Member 2) calls.

---

## Prerequisites

- Python 3.12+
- pip / venv
- (Optional) Tesseract OCR binary for scanned PDF support
- (Optional) GPU for faster zero-shot classification and embeddings

---

## Installation

```bash
# 1. Clone / navigate into the module
cd nlp-processing

# 2. Create a virtual environment
python -m venv .venv
.venv\Scripts\activate        # Windows
# source .venv/bin/activate   # macOS/Linux

# 3. Install dependencies
pip install -r requirements.txt

# 4. Download spaCy language model
python -m spacy download en_core_web_sm

# 5. Configure environment
copy .env.example .env
# Edit .env with your API keys and preferences
```

---

## Environment Variables

Copy `.env.example` to `.env` and configure:

| Variable | Description | Default |
|---|---|---|
| `ENVIRONMENT` | `development` / `production` / `test` | `development` |
| `API_HOST` | Host to bind | `0.0.0.0` |
| `API_PORT` | Port to listen on | `8001` |
| `EMBEDDING_MODEL` | HuggingFace Sentence Transformers model | `sentence-transformers/all-MiniLM-L6-v2` |
| `SPACY_MODEL` | spaCy model | `en_core_web_sm` |
| `LLM_PROVIDER` | `openai` / `google` / `anthropic` / `mock` | `mock` |
| `LLM_API_KEY` | Your LLM API key | *(empty)* |
| `LLM_MODEL` | Model name for chosen provider | `gpt-4o-mini` |
| `CLASSIFICATION_METHOD` | `rule_based` / `zero_shot` / `hybrid` | `hybrid` |
| `LIGHTWEIGHT_MODE` | `1` = skip heavy models (dev/CI use) | `0` |
| `MAX_DOCUMENT_SIZE_MB` | Maximum upload size | `20` |

> ⚠️ **Never commit your `.env` file or real API keys.**

---

## Model Downloads

The first run will auto-download models:

| Model | Size | Purpose |
|---|---|---|
| `en_core_web_sm` | ~12 MB | spaCy NLP preprocessing |
| `all-MiniLM-L6-v2` | ~90 MB | Semantic embeddings |
| `facebook/bart-large-mnli` | ~1.6 GB | Zero-shot classification (optional) |

For limited-resource machines, set `LIGHTWEIGHT_MODE=1` and `CLASSIFICATION_METHOD=rule_based` to skip large model downloads.

---

## Running the Service

```bash
# Development (auto-reload)
uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload

# Or using the entry point
python app/main.py

# Production
uvicorn app.main:app --host 0.0.0.0 --port 8001 --workers 2
```

The service will be available at:
- **API:** `http://localhost:8001`
- **Swagger UI:** `http://localhost:8001/docs`
- **ReDoc:** `http://localhost:8001/redoc`
- **Health:** `http://localhost:8001/api/nlp/health/`

---

## Testing API Endpoints

### Health Check
```bash
curl http://localhost:8001/api/nlp/health/
```

### Process a Document (text input)
```bash
curl -X POST http://localhost:8001/api/nlp/process-document/ \
  -F "text=1. Data Collection\n\nWe collect your name and email." \
  -F "document_name=test_policy" \
  -F "include_embeddings=false"
```

### Process a PDF
```bash
curl -X POST http://localhost:8001/api/nlp/process-document/ \
  -F "file=@privacy_policy.pdf"
```

### Segment Text
```bash
curl -X POST http://localhost:8001/api/nlp/segment/ \
  -H "Content-Type: application/json" \
  -d '{"text": "1. Data Collection\n\nWe collect your data.\n\n2. Data Sharing\n\nWe share your data."}'
```

### Classify Clauses
```bash
curl -X POST http://localhost:8001/api/nlp/classify/ \
  -H "Content-Type: application/json" \
  -d '{"clauses": [{"clause_number": 1, "clause_title": "Test", "clause_text": "We collect your personal data."}]}'
```

---

## Running Tests

```bash
# All tests (lightweight mode — no model downloads)
LIGHTWEIGHT_MODE=1 LLM_PROVIDER=mock pytest tests/ -v

# Specific test file
pytest tests/test_classification.py -v

# With coverage
pytest tests/ --cov=app --cov-report=html
```

---

## Django Integration

The Django backend should call this service at:

```
NLP_SERVICE_URL=http://localhost:8001
```

See [`docs/API_CONTRACT.md`](docs/API_CONTRACT.md) for the full integration contract.

**Example Django call:**
```python
import httpx

async def process_document(pdf_bytes: bytes, filename: str):
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:8001/api/nlp/process-document/",
            files={"file": (filename, pdf_bytes, "application/pdf")},
            timeout=120.0,
        )
    return response.json()
```

---

## LLM Provider Configuration

| Provider | `LLM_PROVIDER` | `LLM_MODEL` examples |
|---|---|---|
| OpenAI | `openai` | `gpt-4o-mini`, `gpt-4o` |
| Google Gemini | `google` | `gemini-1.5-flash`, `gemini-1.5-pro` |
| Anthropic | `anthropic` | `claude-3-haiku-20240307` |
| Mock (dev/test) | `mock` | *(no key needed)* |

---

## Folder Structure

```
nlp-processing/
├── app/
│   ├── main.py                   # FastAPI application entry point
│   ├── config.py                 # Pydantic settings
│   ├── api/
│   │   ├── routes.py             # All API endpoints
│   │   └── schemas.py            # Pydantic request/response models
│   ├── extraction/
│   │   ├── pdf_extractor.py      # PyMuPDF PDF extraction + OCR fallback
│   │   ├── text_cleaner.py       # Text preprocessing
│   │   └── document_loader.py    # Unified document loader
│   ├── segmentation/
│   │   ├── clause_segmenter.py   # Heading-based + paragraph segmentation
│   │   └── sentence_splitter.py  # spaCy + rule-based sentence splitting
│   ├── classification/
│   │   ├── clause_classifier.py  # Hybrid rule-based + zero-shot classifier
│   │   ├── taxonomy.py           # 11-category taxonomy definition
│   │   └── severity_priors.py    # Expert-set severity weights
│   ├── embeddings/
│   │   ├── embedding_generator.py # Sentence Transformers embeddings
│   │   └── similarity.py          # Cosine similarity utilities
│   ├── summarization/
│   │   ├── summarizer.py          # Multi-provider LLM summarization
│   │   ├── prompts.py             # System and user prompts
│   │   └── explanation_generator.py # Assembles full clause records
│   ├── services/
│   │   ├── document_processor.py  # Full NLP pipeline orchestrator
│   │   └── change_processor.py    # Diff-only reprocessing (Member 6)
│   └── utils/
│       ├── logger.py              # Structured logging
│       └── validators.py          # Input validation
├── data/
│   └── sample_documents/          # Sample texts for testing
├── tests/                         # Pytest test suite
├── docs/                          # Architecture and integration docs
├── requirements.txt
├── .env.example
└── README.md
```

---

## Resource Requirements

| Mode | RAM | Disk | Notes |
|---|---|---|---|
| Lightweight (`LIGHTWEIGHT_MODE=1`) | ~256 MB | ~50 MB | Rule-based only, mock LLM |
| Standard (embedding + rule-based) | ~1 GB | ~200 MB | No zero-shot model |
| Full (all models) | ~4 GB | ~2 GB | BART + MiniLM + spaCy |

---

## Known Limitations

See [`docs/MODEL_DOCUMENTATION.md`](docs/MODEL_DOCUMENTATION.md) for detailed limitations.
