# ClauseLens — NLP Architecture

## System Overview

The ClauseLens NLP module is a stateless FastAPI microservice responsible for all AI and NLP processing. It is called by the Django backend and returns structured results for storage in PostgreSQL.

```
┌─────────────────────────────────────────────────────────────┐
│                   ClauseLens NLP Service                    │
│                                                             │
│  ┌────────────┐  ┌────────────┐  ┌────────────────────┐    │
│  │  FastAPI   │  │  Pydantic  │  │   CORS Middleware   │    │
│  │  Routes    │  │  Schemas   │  │  (Django origin)   │    │
│  └─────┬──────┘  └────────────┘  └────────────────────┘    │
│        │                                                     │
│        ▼                                                     │
│  ┌─────────────────────────────────────────────────────┐    │
│  │            Document Processor (Pipeline)             │    │
│  │                                                     │    │
│  │  PDF Extraction → Cleaning → Segmentation →         │    │
│  │  Classification → Severity → Embeddings →            │    │
│  │  Summarization → Explanation Assembly                │    │
│  └─────────────────────────────────────────────────────┘    │
│        │                                                     │
│        ▼                                                     │
│  ┌─────────────────────────────────────────────────────┐    │
│  │  Modular NLP Components (each independently usable) │    │
│  │                                                     │    │
│  │  ┌───────────┐ ┌────────────┐ ┌──────────────────┐ │    │
│  │  │ Extractor │ │  Cleaner   │ │   Segmenter      │ │    │
│  │  │ (PyMuPDF) │ │  (spaCy/  │ │ (Heading detect/ │ │    │
│  │  │ + OCR     │ │   regex)  │ │  Paragraph fall) │ │    │
│  │  └───────────┘ └────────────┘ └──────────────────┘ │    │
│  │                                                     │    │
│  │  ┌───────────┐ ┌────────────┐ ┌──────────────────┐ │    │
│  │  │Classifier │ │ Embedding  │ │   Summarizer     │ │    │
│  │  │(Hybrid:   │ │ Generator  │ │  (OpenAI/Google/ │ │    │
│  │  │ Rule +    │ │(MiniLM-L6) │ │  Anthropic/Mock) │ │    │
│  │  │ ZeroShot) │ └────────────┘ └──────────────────┘ │    │
│  │  └───────────┘                                      │    │
│  └─────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────┘
```

---

## Pipeline Steps

### Step 1: PDF Extraction (`app/extraction/pdf_extractor.py`)

- Uses **PyMuPDF (fitz)** for fast, accurate text extraction.
- Preserves page numbers via `[Page N]` markers.
- Detects scanned PDFs by checking average characters per page.
- Falls back to **pytesseract OCR** (300 DPI rendering) for scanned PDFs if available.
- Returns `ExtractionResult` with status: `success` | `scanned` | `error`.

### Step 2: Text Cleaning (`app/extraction/text_cleaner.py`)

- Removes page markers, non-breaking spaces, soft hyphens.
- Fixes PDF word-wrap artifacts (hyphenated line breaks).
- Removes standalone page numbers (digit-only lines).
- Collapses excessive whitespace.
- **Preserves all legal text** — no sentence-level removal.
- Optionally removes repeated header/footer lines (aggressive mode, disabled by default).
- Stores original text separately from cleaned text.

### Step 3: Clause Segmentation (`app/segmentation/clause_segmenter.py`)

Three strategies applied in priority order:

1. **Numbered heading detection** — regex matching `1.`, `1)`, `2.1.` patterns (highest confidence).
2. **ALL-CAPS heading detection** — matches lines like `DATA COLLECTION`.
3. **Title Case heading detection** — 3–10 word title-case lines.
4. **Paragraph fallback** — splits on double newlines when no headings are found.

After segmentation, long clauses (>2000 chars) are split on sentence boundaries.

### Step 4: Clause Classification (`app/classification/clause_classifier.py`)

**Hybrid approach:**

1. **Rule-based classifier** — keyword overlap scoring across 11 categories. Fast and transparent.
2. **Zero-shot classifier** — `facebook/bart-large-mnli` via HuggingFace pipeline. Used when rule-based confidence is below threshold.
3. **Hybrid mode** (default) — uses rule-based if confident (>0.3), zero-shot fallback otherwise.

Returns: category, category_id, confidence score, method used, secondary categories.

### Step 5: Severity Prior Assignment (`app/classification/severity_priors.py`)

Expert-set category weights from the research paper:

| Category | Severity |
|---|---:|
| Arbitration and Jurisdiction | 0.90 |
| Liability Limitation | 0.85 |
| Children and Age | 0.85 |
| Data Sharing with Third Parties | 0.80 |
| Unilateral Change of Terms | 0.75 |
| Auto-renewal and Fees | 0.70 |
| Content License | 0.60 |
| Account Termination | 0.60 |
| Data Retention | 0.55 |
| Data Collection | 0.50 |
| Other | 0.10 |

> These are **category-level priors only**. Member 5 computes personalized risk scores.

### Step 6: Embedding Generation (`app/embeddings/embedding_generator.py`)

- Uses **`sentence-transformers/all-MiniLM-L6-v2`** (384-dimensional vectors).
- Lazy model loading — model downloaded on first use.
- Batch processing with configurable batch size.
- Returns real embeddings (not random vectors).
- Provides cosine similarity and nearest-neighbour utilities.

### Step 7: LLM Summarization (`app/summarization/summarizer.py`)

- Configurable provider: OpenAI, Google Gemini, Anthropic, or Mock.
- Uses a carefully designed system prompt to ensure:
  - Simple English explanations.
  - Preservation of original meaning.
  - No legal advice claim.
  - Mandatory disclaimer on every summary.
- Returns `success=False` if the LLM API fails (never claims a summary was generated if it wasn't).

### Step 8: Explanation Assembly (`app/summarization/explanation_generator.py`)

Combines all component outputs into a `ClauseExplanation` record containing:
- Original text, title, number.
- Category, category_id, confidence, method, secondary categories.
- Severity prior.
- Embedding vector, model name, dimension.
- Simple explanation, model/provider info, mock flag.
- Processing status and error list.

---

## Change Processing Pipeline (`app/services/change_processor.py`)

Supports diff-only reprocessing for version updates (Member 6 integration):

```
Member 6 provides diff →
  ADDED    → Full NLP (classify + embed + summarize)
  MODIFIED → Full NLP (re-classify + re-embed + re-summarize)
  UNCHANGED → Return cached NLP results (no reprocessing)
  REMOVED  → Preserve old data for history (no new NLP)
```

---

## Module Independence

Each NLP component can be used independently:

```python
# Just segment
from app.segmentation.clause_segmenter import segment_document
clauses = segment_document(text)

# Just classify
from app.classification.clause_classifier import classify_clause
result = classify_clause("We collect your data.")

# Just embed
from app.embeddings.embedding_generator import embed_clause
emb = embed_clause("We collect your data.", clause_id=1)

# Just summarize
from app.summarization.summarizer import summarize_clause
summary = summarize_clause("We collect your data.", "Data Collection")
```

---

## Evaluation Readiness

The module supports future evaluation with:

- Per-category classification outputs (precision/recall/F1 measurement ready).
- Confidence scores for threshold analysis.
- Processing time metrics for each pipeline stage.
- Mock provider for testing without API costs.
- Clear separation of original text from AI-generated explanation.
