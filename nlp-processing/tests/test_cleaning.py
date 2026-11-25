"""
Tests for text cleaning (app/extraction/text_cleaner.py).
"""
from __future__ import annotations

import pytest
from app.extraction.text_cleaner import TextCleaner, clean_text


class TestTextCleaner:
    def setup_method(self):
        self.cleaner = TextCleaner()

    def test_removes_page_markers(self):
        text = "[Page 1]\nSome content here.\n\n[Page 2]\nMore content."
        result = self.cleaner.clean(text)
        assert "[Page 1]" not in result.cleaned_text
        assert "[Page 2]" not in result.cleaned_text
        assert "Some content" in result.cleaned_text

    def test_original_text_preserved(self):
        text = "[Page 1]\nOriginal text with markers."
        result = self.cleaner.clean(text)
        assert result.original_text == text
        assert result.original_text != result.cleaned_text

    def test_collapses_multiple_blank_lines(self):
        text = "Line 1.\n\n\n\n\nLine 2."
        result = self.cleaner.clean(text)
        assert "\n\n\n" not in result.cleaned_text

    def test_removes_non_breaking_spaces(self):
        text = "Hello\u00a0World\u00a0Test"
        result = self.cleaner.clean(text)
        assert "\u00a0" not in result.cleaned_text

    def test_legal_text_preserved(self):
        """Important legal terms must not be removed."""
        legal = (
            "The company shall not be liable for any consequential damages. "
            "You agree to arbitration. Data sharing with third parties is subject to consent."
        )
        result = self.cleaner.clean(legal)
        assert "liable" in result.cleaned_text
        assert "arbitration" in result.cleaned_text
        assert "third parties" in result.cleaned_text

    def test_fixes_hyphenated_line_breaks(self):
        text = "arbi-\ntration is required"
        result = self.cleaner.clean(text)
        assert "arbitration" in result.cleaned_text

    def test_empty_text(self):
        result = self.cleaner.clean("")
        assert result.cleaned_text == ""

    def test_changes_documented(self):
        text = "[Page 1]\n\n\n\nContent here."
        result = self.cleaner.clean(text)
        assert len(result.changes_made) > 0

    def test_module_function(self):
        result = clean_text("Hello   \n\n\n\nWorld")
        assert isinstance(result.cleaned_text, str)
