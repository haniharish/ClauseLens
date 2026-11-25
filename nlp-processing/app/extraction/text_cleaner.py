"""
ClauseLens — Text Cleaner & Preprocessor
Cleans extracted PDF text without removing meaningful legal content.
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Optional

from app.utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class CleaningResult:
    original_text: str
    cleaned_text: str
    changes_made: list[str]


class TextCleaner:
    """
    Cleans raw PDF-extracted text for legal documents.

    Design principles:
    - NEVER remove text just because it looks repetitive — legal documents
      often repeat definitions and cross-references intentionally.
    - Only remove structural noise: page markers, excessive whitespace, etc.
    - Preserve section numbers, clause references, special characters with
      legal meaning (§, ©, ®, em-dash, etc.).
    - Store original text separately from cleaned text.
    """

    # Page markers inserted by the extractor
    _PAGE_MARKER_RE = re.compile(r"\[Page \d+\]\n?", re.MULTILINE)

    # Standalone page numbers: a line that is only digits (possibly with spaces)
    _STANDALONE_PAGE_NUM_RE = re.compile(r"^\s*\d{1,4}\s*$", re.MULTILINE)

    # Three or more consecutive blank lines → two blank lines
    _MULTI_BLANK_RE = re.compile(r"\n{3,}")

    # Trailing whitespace on each line
    _TRAILING_WS_RE = re.compile(r"[ \t]+$", re.MULTILINE)

    # Leading whitespace on each line (keep indentation only if <= 4 spaces)
    _EXCESS_LEADING_WS_RE = re.compile(r"^[ \t]{5,}", re.MULTILINE)

    # Hyphenated line-break (PDF word-wrap artifact): word-\nword → wordword
    _HYPHEN_BREAK_RE = re.compile(r"(\w)-\n(\w)")

    # Soft-hyphen character
    _SOFT_HYPHEN_RE = re.compile(r"\u00ad")

    # Non-breaking space → regular space
    _NBSP_RE = re.compile(r"\u00a0")

    # Repeated header/footer patterns: lines that appear 3+ times verbatim
    # (only applied to very short lines to avoid removing legal text)
    _MIN_FOOTER_REPEAT = 3
    _MAX_FOOTER_LINE_LEN = 80

    def clean(self, raw_text: str, aggressive: bool = False) -> CleaningResult:
        """
        Clean extracted document text.

        Parameters
        ----------
        raw_text : str
            The raw text as returned by the PDF extractor.
        aggressive : bool
            If True, also attempt to remove repeated headers/footers.
            Use with caution on legal documents.

        Returns
        -------
        CleaningResult with original and cleaned text.
        """
        original = raw_text
        text = raw_text
        changes: list[str] = []

        # 1. Remove page markers added by extractor
        text, n = self._PAGE_MARKER_RE.subn("", text)
        if n:
            changes.append(f"Removed {n} page markers")

        # 2. Normalize non-breaking spaces
        text_new = self._NBSP_RE.sub(" ", text)
        if text_new != text:
            changes.append("Normalized non-breaking spaces")
            text = text_new

        # 3. Remove soft hyphens
        text_new = self._SOFT_HYPHEN_RE.sub("", text)
        if text_new != text:
            changes.append("Removed soft hyphens")
            text = text_new

        # 4. Fix hyphenated line breaks (PDF reflow artifact)
        text_new = self._HYPHEN_BREAK_RE.sub(r"\1\2", text)
        if text_new != text:
            changes.append("Fixed hyphenated line breaks")
            text = text_new

        # 5. Remove standalone page numbers
        text_new = self._STANDALONE_PAGE_NUM_RE.sub("", text)
        if text_new != text:
            changes.append("Removed standalone page numbers")
            text = text_new

        # 6. Normalize trailing whitespace
        text_new = self._TRAILING_WS_RE.sub("", text)
        if text_new != text:
            changes.append("Removed trailing whitespace")
            text = text_new

        # 7. Normalize excessive leading whitespace
        text_new = self._EXCESS_LEADING_WS_RE.sub("    ", text)
        if text_new != text:
            changes.append("Normalized excessive leading whitespace")
            text = text_new

        # 8. Collapse multiple blank lines
        text_new = self._MULTI_BLANK_RE.sub("\n\n", text)
        if text_new != text:
            changes.append("Collapsed multiple blank lines")
            text = text_new

        # 9. Optional: remove repeated short header/footer lines
        if aggressive:
            text_new, removed = self._remove_repeated_headers_footers(text)
            if removed:
                changes.append(f"Removed {removed} repeated header/footer lines")
                text = text_new

        # 10. Final strip
        text = text.strip()

        logger.info(
            "text_cleaned",
            changes=len(changes),
            original_len=len(original),
            cleaned_len=len(text),
        )

        return CleaningResult(
            original_text=original,
            cleaned_text=text,
            changes_made=changes,
        )

    def _remove_repeated_headers_footers(self, text: str) -> tuple[str, int]:
        """
        Identify lines shorter than MAX_FOOTER_LINE_LEN that appear
        SCANNED_THRESHOLD or more times and remove all but the first occurrence.

        CAUTION: This is a heuristic. Legal boilerplate that repeats (e.g.,
        "CONFIDENTIAL") will also be removed. Only use in aggressive mode.
        """
        lines = text.split("\n")
        from collections import Counter

        # Count stripped lines
        stripped_lines = [l.strip() for l in lines]
        counts = Counter(stripped_lines)

        candidates: set[str] = set()
        for line, count in counts.items():
            if (
                count >= self._MIN_FOOTER_REPEAT
                and 0 < len(line) <= self._MAX_FOOTER_LINE_LEN
                and not self._looks_like_legal_text(line)
            ):
                candidates.add(line)

        if not candidates:
            return text, 0

        seen: set[str] = set()
        result_lines: list[str] = []
        removed = 0

        for line in lines:
            stripped = line.strip()
            if stripped in candidates:
                if stripped not in seen:
                    seen.add(stripped)
                    result_lines.append(line)  # keep first occurrence
                else:
                    removed += 1  # remove duplicates
            else:
                result_lines.append(line)

        return "\n".join(result_lines), removed

    @staticmethod
    def _looks_like_legal_text(line: str) -> bool:
        """
        Heuristic: does this line look like meaningful legal text
        (and therefore should NOT be treated as a removable header/footer)?
        """
        legal_keywords = (
            "shall", "may", "must", "rights", "obligations", "agree",
            "terms", "policy", "data", "information", "user", "company",
            "service", "liability", "arbitration", "clause", "section",
            "paragraph", "pursuant", "herein", "thereof", "hereof",
            "provided", "under", "applicable", "law", "consent",
        )
        lower = line.lower()
        return any(kw in lower for kw in legal_keywords)


# ---------------------------------------------------------------------------
# Module-level convenience
# ---------------------------------------------------------------------------
_cleaner = TextCleaner()


def clean_text(raw_text: str, aggressive: bool = False) -> CleaningResult:
    return _cleaner.clean(raw_text, aggressive=aggressive)
