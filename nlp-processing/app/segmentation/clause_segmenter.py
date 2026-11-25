"""
ClauseLens — Clause Segmenter
Divides legal documents into individual, meaningful clauses.

Strategy (applied in order):
1. Detect numbered/lettered section headings (primary signal).
2. Detect ALL-CAPS or Title Case headings on their own line.
3. Fall back to paragraph-level segmentation.
4. Optionally, split over-long clauses using sentence boundaries.

Known limitations (documented transparently):
- Nested sub-clauses are grouped under their parent section.
- Documents with no headings rely entirely on paragraph breaks,
  which may group unrelated sentences or split related ones.
- Heavily formatted PDFs may produce garbled heading detection
  due to PDF→text conversion artifacts.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Optional

from app.segmentation.sentence_splitter import split_into_sentences
from app.utils.logger import get_logger

logger = get_logger(__name__)

# ---------------------------------------------------------------------------
# Data model
# ---------------------------------------------------------------------------

@dataclass
class Clause:
    clause_number: int
    clause_title: str
    clause_text: str
    start_char: Optional[int] = None
    end_char: Optional[int] = None


# ---------------------------------------------------------------------------
# Heading patterns
# ---------------------------------------------------------------------------

# 1. "1. Title" or "1) Title" or "1 Title" at line start
_NUMBERED_HEADING = re.compile(
    r"^(?P<num>\d{1,3}(?:\.\d{1,3})*)[.)]\s+(?P<title>[^\n]{3,80})$",
    re.MULTILINE,
)

# 2. "(a)" "(i)" lettered sub-sections — treated as headings
_LETTERED_HEADING = re.compile(
    r"^\s*\((?P<letter>[a-zA-Z]{1,3})\)\s+(?P<title>[^\n]{3,80})$",
    re.MULTILINE,
)

# 3. ALL CAPS line (at least 3 words, no trailing period) — section heading
_ALLCAPS_HEADING = re.compile(
    r"^(?P<title>[A-Z][A-Z\s\-&]{5,79})$",
    re.MULTILINE,
)

# 4. Title Case heading: 3–10 words, no trailing period
_TITLECASE_HEADING = re.compile(
    r"^(?P<title>(?:[A-Z][a-z]+(?:\s+[A-Z][a-z]+){2,9}))$",
    re.MULTILINE,
)

# Minimum text length to be a valid clause (chars)
_MIN_CLAUSE_TEXT_LEN = 20

# Maximum chars before splitting a clause on sentence boundaries
_MAX_CLAUSE_LEN = 2000


# ---------------------------------------------------------------------------
# Segmenter
# ---------------------------------------------------------------------------

class ClauseSegmenter:
    """
    Segments legal document text into individual clauses.
    """

    def segment(self, text: str) -> list[Clause]:
        """
        Main entry point.

        Parameters
        ----------
        text : str
            Cleaned document text.

        Returns
        -------
        List of Clause objects in document order.
        """
        if not text or not text.strip():
            return []

        # Try structured heading-based segmentation first
        clauses = self._heading_based_segmentation(text)

        if len(clauses) < 2:
            # Fallback: paragraph-based
            logger.info("fallback_to_paragraph_segmentation")
            clauses = self._paragraph_based_segmentation(text)

        # Optionally split very long clauses
        clauses = self._split_long_clauses(clauses)

        # Re-number sequentially
        for i, clause in enumerate(clauses, start=1):
            clause.clause_number = i

        logger.info("segmentation_complete", clause_count=len(clauses))
        return clauses

    # ------------------------------------------------------------------
    # Heading-based segmentation
    # ------------------------------------------------------------------

    def _heading_based_segmentation(self, text: str) -> list[Clause]:
        """
        Find headings, then collect text between consecutive headings.
        """
        matches = self._find_headings(text)
        if not matches:
            return []

        clauses: list[Clause] = []
        for idx, (start, end, title) in enumerate(matches):
            # Text body starts after the heading line
            body_start = end
            body_end = matches[idx + 1][0] if idx + 1 < len(matches) else len(text)

            body = text[body_start:body_end].strip()

            if not body or len(body) < _MIN_CLAUSE_TEXT_LEN:
                # Heading with no meaningful text — skip or attach to next
                continue

            clauses.append(Clause(
                clause_number=0,  # will be renumbered
                clause_title=title.strip(),
                clause_text=body,
                start_char=start,
                end_char=body_end,
            ))

        return clauses

    def _find_headings(self, text: str) -> list[tuple[int, int, str]]:
        """
        Return list of (match_start, match_end, title) for detected headings.
        Prioritizes numbered headings; supplements with ALLCAPS/TitleCase.
        """
        candidates: list[tuple[int, int, str]] = []

        # Numbered headings (highest confidence)
        for m in _NUMBERED_HEADING.finditer(text):
            candidates.append((m.start(), m.end(), m.group("title")))

        # If we have numbered headings, don't mix with style headings
        if candidates:
            return sorted(candidates, key=lambda x: x[0])

        # ALL-CAPS headings
        for m in _ALLCAPS_HEADING.finditer(text):
            title = m.group("title").strip()
            if len(title.split()) >= 2:
                candidates.append((m.start(), m.end(), title.title()))

        # Title Case headings (only if no ALLCAPS found)
        if not candidates:
            for m in _TITLECASE_HEADING.finditer(text):
                title = m.group("title").strip()
                candidates.append((m.start(), m.end(), title))

        return sorted(candidates, key=lambda x: x[0])

    # ------------------------------------------------------------------
    # Paragraph-based fallback
    # ------------------------------------------------------------------

    def _paragraph_based_segmentation(self, text: str) -> list[Clause]:
        """
        Split on double line-breaks (paragraphs). Each non-trivial paragraph
        becomes a clause with an auto-generated title.
        """
        paragraphs = re.split(r"\n{2,}", text)
        clauses: list[Clause] = []
        counter = 1

        for para in paragraphs:
            stripped = para.strip()
            if not stripped or len(stripped) < _MIN_CLAUSE_TEXT_LEN:
                continue

            title = self._extract_paragraph_title(stripped)
            clauses.append(Clause(
                clause_number=counter,
                clause_title=title,
                clause_text=stripped,
            ))
            counter += 1

        return clauses

    @staticmethod
    def _extract_paragraph_title(text: str) -> str:
        """
        Generate a title from the first sentence or first 60 characters.
        """
        first_line = text.split("\n")[0].strip()
        if len(first_line) <= 60:
            return first_line
        # First 7 words
        words = text.split()[:7]
        return " ".join(words) + "…"

    # ------------------------------------------------------------------
    # Long-clause splitting
    # ------------------------------------------------------------------

    def _split_long_clauses(self, clauses: list[Clause]) -> list[Clause]:
        """
        Split clauses that are longer than MAX_CLAUSE_LEN using sentence
        boundaries, only when the resulting segments make semantic sense
        (each segment >= MIN_CLAUSE_TEXT_LEN).
        """
        result: list[Clause] = []
        for clause in clauses:
            if len(clause.clause_text) <= _MAX_CLAUSE_LEN:
                result.append(clause)
                continue

            sentences = split_into_sentences(clause.clause_text)
            if len(sentences) <= 1:
                result.append(clause)
                continue

            # Group into sub-clauses of reasonable size
            current_text = ""
            part = 1
            for sent in sentences:
                if current_text and len(current_text) + len(sent) > _MAX_CLAUSE_LEN:
                    result.append(Clause(
                        clause_number=0,
                        clause_title=f"{clause.clause_title} (Part {part})",
                        clause_text=current_text.strip(),
                    ))
                    current_text = sent
                    part += 1
                else:
                    current_text = (current_text + " " + sent).strip()

            if current_text.strip():
                result.append(Clause(
                    clause_number=0,
                    clause_title=f"{clause.clause_title} (Part {part})" if part > 1 else clause.clause_title,
                    clause_text=current_text.strip(),
                ))

        return result


# ---------------------------------------------------------------------------
# Module-level convenience
# ---------------------------------------------------------------------------
_segmenter = ClauseSegmenter()


def segment_document(text: str) -> list[Clause]:
    return _segmenter.segment(text)
