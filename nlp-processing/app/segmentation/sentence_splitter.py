"""
ClauseLens — Sentence Splitter
Thin wrapper around spaCy sentence segmentation with a rule-based fallback.
"""
from __future__ import annotations

import re
from typing import Optional

from app.utils.logger import get_logger

logger = get_logger(__name__)

_nlp = None  # Lazy loaded


def _get_nlp():
    global _nlp
    if _nlp is None:
        try:
            import spacy
            from app.config import get_settings
            settings = get_settings()
            _nlp = spacy.load(settings.spacy_model, disable=["ner", "lemmatizer"])
            logger.info("spacy_loaded", model=settings.spacy_model)
        except Exception as exc:
            logger.warning("spacy_load_failed", exc=str(exc))
            _nlp = False  # Mark as unavailable
    return _nlp if _nlp is not False else None


def split_into_sentences(text: str) -> list[str]:
    """
    Split text into sentences.
    Uses spaCy when available, falls back to rule-based splitting.
    """
    if not text or not text.strip():
        return []

    nlp = _get_nlp()
    if nlp is not None:
        try:
            # Process in chunks to avoid spaCy token limit
            max_len = 100_000
            if len(text) > max_len:
                # Split on paragraph boundaries then merge
                paragraphs = text.split("\n\n")
                sentences = []
                for para in paragraphs:
                    sentences.extend(_spacy_sentences(nlp, para.strip()))
                return [s for s in sentences if s.strip()]
            return _spacy_sentences(nlp, text)
        except Exception as exc:
            logger.warning("spacy_sentence_split_failed", exc=str(exc))

    return _rule_based_sentences(text)


def _spacy_sentences(nlp, text: str) -> list[str]:
    doc = nlp(text)
    return [sent.text.strip() for sent in doc.sents if sent.text.strip()]


def _rule_based_sentences(text: str) -> list[str]:
    """
    Rule-based sentence splitting for when spaCy is unavailable.
    Handles legal abbreviations to avoid false splits.
    """
    # Protect common legal abbreviations
    abbrevs = [
        r"(?<![A-Z])(?<!\w)(Inc|Ltd|LLC|Corp|Co|No|vs|v|Art|Sec|Para|et al|i\.e|e\.g|cf|pp|vol|ch|Fig|Jan|Feb|Mar|Apr|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\."
    ]
    protected = text
    for abbrev in abbrevs:
        protected = re.sub(abbrev, lambda m: m.group().replace(".", "<!DOT!>"), protected)

    # Split on sentence-ending punctuation followed by space and uppercase
    sentences = re.split(r"(?<=[.!?])\s+(?=[A-Z\"])", protected)
    # Restore protected dots
    sentences = [s.replace("<!DOT!>", ".").strip() for s in sentences]
    return [s for s in sentences if s]
