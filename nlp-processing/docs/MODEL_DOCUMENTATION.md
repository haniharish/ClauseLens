# ClauseLens — Model Documentation

## Overview

This document describes all models, methods, and configurations used in the
ClauseLens NLP module, including known limitations and evaluation guidance.

---

## 1. NLP Preprocessing Model

**Library:** spaCy
**Model:** `en_core_web_sm`
**Size:** ~12 MB
**Purpose:** Sentence boundary detection, tokenization.

**Usage in ClauseLens:**
- Sentence splitting for long-clause subdivision.
- Used in `app/segmentation/sentence_splitter.py`.
- Falls back to rule-based splitting if spaCy fails to load.

**Limitations:**
- `en_core_web_sm` is a small efficiency model; not fine-tuned on legal text.
- May split incorrectly on legal abbreviations (mitigation: abbreviation protection regex).
- For better performance, upgrade to `en_core_web_lg` or `en_core_web_trf`.

---

## 2. Clause Classification

### Method 1: Rule-Based Classifier

**Type:** Keyword overlap scoring
**Location:** `app/classification/clause_classifier.py` → `RuleBasedClassifier`

**How it works:**
1. For each of the 11 categories, counts keyword hits in the clause text.
2. Normalizes scores by keyword count.
3. Returns the highest-scoring category.

**Transparency:** Fully interpretable — keyword lists are visible in `taxonomy.py`.

**Limitations:**
- Accuracy depends heavily on keyword coverage.
- Cannot understand context (e.g., "not liable" may score high for Liability Limitation even in a dismissal).
- Multi-label detection is based on a 50%-of-best-score heuristic.
- **No formal accuracy measurement has been performed.** An evaluation study with human-annotated clauses is needed.

### Method 2: Zero-Shot Classification

**Model:** `facebook/bart-large-mnli`
**Size:** ~1.6 GB
**Type:** Natural Language Inference (NLI) repurposed for classification
**Location:** `app/classification/clause_classifier.py` → `ZeroShotClassifier`

**How it works:**
- Uses HuggingFace `zero-shot-classification` pipeline.
- Each category name serves as a candidate label.
- The NLI model scores how likely the clause text "entails" each label.

**Limitations:**
- BART-large-MNLI is not fine-tuned on legal text.
- Accuracy may be lower for specialized legal terminology.
- Performance varies by clause length (truncated to 1024 tokens).
- Requires ~1.6 GB RAM/disk.
- **Accuracy has not been formally measured** on legal clause datasets.
- For production use, fine-tuning on a labeled legal clause dataset is recommended.

### Method 3: Hybrid (Default)

Combines rule-based (fast, interpretable) with zero-shot fallback (better for ambiguous clauses).
See `app/classification/clause_classifier.py` → `ClauseClassifier`.

---

## 3. Embedding Model

**Model:** `sentence-transformers/all-MiniLM-L6-v2`
**Size:** ~90 MB
**Embedding Dimension:** 384
**Library:** Sentence Transformers
**Location:** `app/embeddings/embedding_generator.py`

**Purpose:**
- Converts clause text into dense 384-dimensional vectors.
- Enables semantic similarity search.
- Provided to Member 5 for personalized relevance scoring.

**How it works:**
- Transformer-based encoder (MiniLM-L6) trained on semantic similarity tasks.
- Encodes entire clause texts into single fixed-size vectors.
- Cosine similarity used for semantic comparison.

**Limitations:**
- MiniLM-L6-v2 is a general-purpose model, not legal-domain-specific.
- 384 dimensions capture general semantics; a larger model (e.g., `all-mpnet-base-v2`, 768-dim) may capture more nuance.
- Maximum input length: 256 tokens (longer clauses are truncated).
- Embeddings should not be used as the sole measure of clause similarity for critical decisions.

**Alternative models for upgrade:**
| Model | Dimensions | Notes |
|---|---|---|
| `all-MiniLM-L6-v2` | 384 | Fast, default |
| `all-mpnet-base-v2` | 768 | Better quality, larger |
| `legal-bert-base-uncased` | 768 | Legal domain, requires fine-tuning |

---

## 4. Summarization (LLM)

**Provider:** Configurable (OpenAI, Google Gemini, Anthropic, Mock)
**Default Model (OpenAI):** `gpt-4o-mini`
**Location:** `app/summarization/summarizer.py`

**System Prompt Design:**
- Instructs the model to explain in plain English.
- Prohibits inventing legal facts.
- Requires a disclaimer on every output.
- Limits to 2–4 sentences.

**Disclaimer (always included):**
> ⚠️ This is an AI-generated explanation for informational purposes, not legal advice.

**Limitations:**
- LLM summaries may contain hallucinations despite prompt guardrails.
- Accuracy is not formally measured; human review is recommended for high-stakes use.
- API latency adds 1–5 seconds per clause.
- API cost scales with document length.
- Mock provider is clearly labelled and must not be used in production.

**Faithfulness considerations:**
- Prompts explicitly prohibit adding information not in the source.
- Output should be reviewed for faithfulness before user display.
- A future evaluation step (rouge, BERTScore, human review) is recommended.

---

## 5. Severity Priors

**Source:** Expert-set values from the ClauseLens research paper.
**Location:** `app/classification/severity_priors.py`

| Category | Prior |
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

**Important:** These are **initial priors**, not legally validated risk scores. They reflect the research team's expert judgment about category-level risk. Member 5 is responsible for computing personalized relevance scores using these priors as inputs.

---

## 6. Clause Segmentation

**Method:** Rule-based heading detection + paragraph fallback
**Location:** `app/segmentation/clause_segmenter.py`

**Strategies (in order):**
1. Numbered section headers (regex).
2. ALL-CAPS headers.
3. Title Case headers.
4. Paragraph-level splitting (fallback).

**Limitations (documented transparently):**
- Nested sub-clauses (e.g., `1.1`, `(a)`) are grouped under their parent.
- Documents without clear headings rely on paragraph breaks, which may group unrelated sentences.
- PDF-to-text conversion artifacts may confuse heading detection.
- Very long clauses (>2000 chars) are split on sentence boundaries — splits may not always be semantically correct.
- **This is not a perfect segmentation system.** Legal document structure varies significantly.

---

## 7. Evaluation Plan

The following measurements can be performed once human-annotated ground truth is available:

### Classification Evaluation
- Metric: Precision, Recall, F1-score per category.
- Method: Annotate a held-out set of clauses with human-assigned categories.
- Compare rule-based vs. zero-shot vs. hybrid.

### Segmentation Evaluation
- Metric: Precision/Recall on clause boundaries.
- Method: Manual annotation of clause boundaries in sample documents.

### Summarization Evaluation
- Metric: Faithfulness (human judgment), ROUGE-L, BERTScore.
- Method: Human reviewers rate whether summaries accurately reflect original clauses.

### Performance Metrics
- Pipeline timing already captured in `ProcessingMetrics`.
- Monitor: total processing time, per-stage breakdown, clauses per second.

> **No accuracy figures are claimed in this module.** All metrics must be measured empirically.
