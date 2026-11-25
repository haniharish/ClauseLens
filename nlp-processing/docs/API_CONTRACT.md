# ClauseLens NLP — API Contract

**Version:** 1.0.0
**Service:** ClauseLens NLP Processing Service (Member 4)
**Consumer:** Django REST Backend (Member 2)
**Base URL:** `http://localhost:8001` (configurable via `NLP_SERVICE_URL`)

---

## Overview

The Django backend sends documents to this FastAPI service for NLP processing.
The service returns structured clause records. The backend stores results in PostgreSQL.
**The NLP service never accesses the database directly.**

---

## Authentication

Currently no authentication is enforced (development mode).
For production, the recommended approach is:

- Add a shared `X-API-Key` header to all requests.
- Configure the key in both services via environment variables.
- Never expose the NLP service publicly — keep it internal/private.

```
X-API-Key: your_internal_service_key
```

---

## Content Types

| Direction | Content-Type |
|---|---|
| JSON requests | `application/json` |
| File upload | `multipart/form-data` |
| Responses | `application/json` |

---

## Endpoints

### `GET /api/nlp/health/`

**Purpose:** Check if the NLP service is running.
**Used by:** Django health checks, deployment monitoring.

**Response 200:**
```json
{
  "status": "ok",
  "version": "1.0.0",
  "environment": "development",
  "models": {
    "embedding_model": "sentence-transformers/all-MiniLM-L6-v2",
    "classification_method": "hybrid",
    "llm_provider": "openai",
    "llm_model": "gpt-4o-mini",
    "lightweight_mode": false
  }
}
```

---

### `POST /api/nlp/extract/`

**Purpose:** Extract raw text from a PDF file.
**Used by:** Django when it wants text before full processing.

**Request:** `multipart/form-data`
| Field | Type | Required | Description |
|---|---|---|---|
| `file` | File | ✅ | PDF file (max 20 MB) |

**Response 200:**
```json
{
  "document_name": "privacy_policy.pdf",
  "total_pages": 15,
  "extracted_text": "Full document text...",
  "status": "success",
  "error_message": "",
  "is_scanned": false,
  "ocr_attempted": false
}
```

**Status values:** `success` | `scanned` | `error`

**Errors:**
| Code | Reason |
|---|---|
| 400 | Invalid or non-PDF file |
| 400 | File exceeds size limit |
| 400 | File is empty |

---

### `POST /api/nlp/segment/`

**Purpose:** Segment plain text into individual clauses.

**Request:** `application/json`
```json
{
  "text": "1. Data Collection\n\nWe collect your data...\n\n2. Data Sharing...",
  "document_name": "policy_v2"
}
```

**Response 200:**
```json
{
  "document_name": "policy_v2",
  "total_clauses": 2,
  "clauses": [
    {
      "clause_number": 1,
      "clause_title": "Data Collection",
      "clause_text": "We collect your data..."
    }
  ]
}
```

---

### `POST /api/nlp/classify/`

**Purpose:** Classify a list of clauses into categories.

**Request:** `application/json`
```json
{
  "clauses": [
    {
      "clause_number": 1,
      "clause_title": "Data Collection",
      "clause_text": "We collect your name and email address."
    }
  ]
}
```

**Response 200:**
```json
{
  "total_clauses": 1,
  "classifications": [
    {
      "clause_number": 1,
      "clause_title": "Data Collection",
      "category": "Data Collection",
      "category_id": 1,
      "confidence": 0.85,
      "method": "hybrid_rule",
      "secondary_categories": [],
      "severity_prior": 0.50
    }
  ]
}
```

---

### `POST /api/nlp/embed/`

**Purpose:** Generate semantic embeddings for clauses (for Member 5 personalization).

**Request:** `application/json`
```json
{
  "clauses": [
    {"clause_number": 1, "clause_title": "Test", "clause_text": "Your data may be shared."}
  ]
}
```

**Response 200:**
```json
{
  "total_clauses": 1,
  "model": "sentence-transformers/all-MiniLM-L6-v2",
  "embeddings": [
    {
      "clause_id": 1,
      "model": "sentence-transformers/all-MiniLM-L6-v2",
      "embedding_dimension": 384,
      "embedding": [0.12, -0.04, 0.32, "..."],
      "text_length": 32
    }
  ]
}
```

> Note: `embeddings[i]` may be `null` if embedding failed for that clause.

---

### `POST /api/nlp/summarize/`

**Purpose:** Generate plain-English summaries for clauses.

**Request:** `application/json`
```json
{
  "clauses": [
    {
      "clause_number": 1,
      "clause_title": "Third Party Sharing",
      "clause_text": "The company may disclose personal information to third-party service providers."
    }
  ]
}
```

**Response 200:**
```json
{
  "total_clauses": 1,
  "summaries": [
    {
      "clause_number": 1,
      "clause_title": "Third Party Sharing",
      "source_text": "The company may disclose personal information...",
      "category": "Unknown",
      "simple_explanation": "The company can share your information with other organizations that help run its services.\n⚠️ This is an AI-generated explanation for informational purposes, not legal advice.",
      "model_used": "gpt-4o-mini",
      "provider": "openai",
      "is_mock": false,
      "success": true,
      "error": null
    }
  ]
}
```

---

### `POST /api/nlp/process-document/`

**Purpose:** Run the complete NLP pipeline on a document.
**This is the primary endpoint Django will use.**

**Request:** `multipart/form-data`
| Field | Type | Required | Description |
|---|---|---|---|
| `file` | File | ✅ or `text` | PDF file |
| `text` | string | ✅ or `file` | Pre-extracted text |
| `document_name` | string | ❌ | Friendly name |
| `include_embeddings` | bool | ❌ | Default: true |
| `include_summaries` | bool | ❌ | Default: true |

**Response 200:**
```json
{
  "success": true,
  "document_name": "privacy_policy.pdf",
  "total_pages": 12,
  "total_clauses": 25,
  "processing_status": "completed",
  "clauses": [
    {
      "clause_number": 1,
      "clause_title": "Third Party Data Sharing",
      "original_text": "The company may share personal information with third-party service providers.",
      "category": "Data Sharing with Third Parties",
      "category_id": 2,
      "classification_confidence": 0.87,
      "classification_method": "hybrid_rule",
      "secondary_categories": [],
      "severity_prior": 0.80,
      "embedding": [0.12, -0.04, "..."],
      "embedding_model": "sentence-transformers/all-MiniLM-L6-v2",
      "embedding_dimension": 384,
      "simple_explanation": "The company can share your personal information with external organizations.\n⚠️ This is an AI-generated explanation for informational purposes, not legal advice.",
      "summarization_model": "gpt-4o-mini",
      "summarization_provider": "openai",
      "is_mock_summary": false,
      "processing_status": "completed",
      "errors": []
    }
  ],
  "metrics": {
    "extraction_time_s": 0.4,
    "cleaning_time_s": 0.05,
    "segmentation_time_s": 0.2,
    "classification_time_s": 0.3,
    "embedding_time_s": 1.5,
    "summarization_time_s": 3.2,
    "total_time_s": 5.65
  },
  "error_message": ""
}
```

**`processing_status` values per clause:** `completed` | `partial` | `failed`

---

### `POST /api/nlp/process-changes/`

**Purpose:** Reprocess only changed clauses for version updates (supports Member 6).

**Request:** `application/json`
```json
{
  "changes": [
    {
      "clause_number": 1,
      "clause_title": "New Clause",
      "clause_text": "We now also collect your location data.",
      "change_type": "added",
      "cached_nlp_result": null
    },
    {
      "clause_number": 3,
      "clause_title": "Existing Clause",
      "clause_text": "Unchanged clause text.",
      "change_type": "unchanged",
      "cached_nlp_result": { "...": "previous NLP result object" }
    }
  ],
  "include_embeddings": true,
  "include_summaries": true
}
```

**`change_type` values:** `added` | `modified` | `unchanged` | `removed`

**Response 200:**
```json
{
  "success": true,
  "total_changes": 2,
  "added_processed": 1,
  "modified_processed": 0,
  "unchanged_reused": 1,
  "removed_count": 0,
  "clauses": ["...clause records with change_type and reprocessed fields..."],
  "error_message": ""
}
```

---

## Error Responses

All errors follow this format:

```json
{
  "detail": "Human-readable error message"
}
```

| HTTP Code | Meaning |
|---|---|
| 400 | Bad request (invalid file, missing input, oversized file) |
| 422 | Validation error (missing required fields, wrong type) |
| 500 | Internal NLP service error |

---

## Service Configuration for Django

Add to Django's `.env`:
```
NLP_SERVICE_URL=http://localhost:8001
NLP_API_KEY=your_internal_key   # if authentication is enabled
NLP_TIMEOUT_SECONDS=120
```

---

## Data Flow

```
Django Backend
     │
     │ POST /api/nlp/process-document/ (PDF or text)
     ▼
NLP Service (this module)
     │
     ├─► PDF Extraction (PyMuPDF)
     ├─► Text Cleaning (spaCy / regex)
     ├─► Clause Segmentation (heading detection)
     ├─► Classification (rule-based / zero-shot)
     ├─► Severity Priors (research paper values)
     ├─► Embedding Generation (Sentence Transformers)
     └─► LLM Summarization (OpenAI / Google / Anthropic)
     │
     │ JSON response (clause records)
     ▼
Django Backend
     │
     └─► Store in PostgreSQL (Member 3's schema)
          └─► Pass embeddings to Member 5 (Personalization)
          └─► Pass version diff to Member 6 (Change Tracking)
```
