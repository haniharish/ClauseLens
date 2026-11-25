"""
ClauseLens — LLM Summarizer
Converts legal clause text into plain-English explanations via a configurable LLM API.
Provider: openai | google | anthropic | mock

IMPORTANT:
- API keys are loaded from environment variables only. Never hardcoded.
- If the LLM service is unavailable, a proper error is returned.
- Mock provider is clearly labelled and used only for development/testing.
"""
from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Optional

from app.config import get_settings
from app.summarization.prompts import (
    SYSTEM_PROMPT,
    build_context_explanation_prompt,
    build_user_prompt,
)
from app.utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class SummarizationResult:
    simple_explanation: str
    model_used: str
    provider: str
    is_mock: bool = False
    error: Optional[str] = None
    success: bool = True


# ---------------------------------------------------------------------------
# Provider implementations
# ---------------------------------------------------------------------------

class _OpenAIProvider:
    def __init__(self, api_key: str, model: str, base_url: str = ""):
        self.api_key = api_key
        self.model = model
        self.base_url = base_url

    def complete(self, system_prompt: str, user_prompt: str) -> str:
        from openai import OpenAI
        kwargs = {"api_key": self.api_key}
        if self.base_url:
            kwargs["base_url"] = self.base_url
        client = OpenAI(**kwargs)
        response = client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            max_tokens=400,
            temperature=0.3,
        )
        return response.choices[0].message.content.strip()


class _GoogleProvider:
    def __init__(self, api_key: str, model: str):
        self.api_key = api_key
        self.model = model

    def complete(self, system_prompt: str, user_prompt: str) -> str:
        import google.generativeai as genai
        genai.configure(api_key=self.api_key)
        model = genai.GenerativeModel(
            model_name=self.model,
            system_instruction=system_prompt,
        )
        response = model.generate_content(user_prompt)
        return response.text.strip()


class _AnthropicProvider:
    def __init__(self, api_key: str, model: str):
        self.api_key = api_key
        self.model = model

    def complete(self, system_prompt: str, user_prompt: str) -> str:
        import anthropic
        client = anthropic.Anthropic(api_key=self.api_key)
        response = client.messages.create(
            model=self.model,
            max_tokens=400,
            system=system_prompt,
            messages=[{"role": "user", "content": user_prompt}],
        )
        return response.content[0].text.strip()


class _MockProvider:
    """
    Returns a clearly-labelled mock summary.
    Used in development/testing when no real LLM API is configured.
    """
    def complete(self, system_prompt: str, user_prompt: str) -> str:
        # Extract clause snippet for context
        lines = user_prompt.split("\n")
        snippet = ""
        for line in lines:
            if line.startswith('"""') or (snippet and not line.startswith('"""')):
                snippet = line.replace('"""', "").strip()[:100]
                break
        return (
            f"[MOCK SUMMARY] This clause relates to: \"{snippet}...\". "
            "In a real deployment, the AI would explain this clause in simple English. "
            "⚠️ This is an AI-generated explanation for informational purposes, not legal advice."
        )


# ---------------------------------------------------------------------------
# Main Summarizer
# ---------------------------------------------------------------------------

class Summarizer:
    """
    Routes summarization requests to the configured LLM provider.
    """

    def __init__(self):
        self._provider = None
        self._provider_name: str = ""
        self._model_name: str = ""

    def _get_provider(self):
        if self._provider is not None:
            return self._provider

        settings = get_settings()
        p = settings.llm_provider.lower()
        self._provider_name = p

        if p == "mock" or not settings.llm_api_key:
            if p != "mock":
                logger.warning(
                    "llm_api_key_missing_using_mock",
                    provider=p,
                    hint="Set LLM_API_KEY in .env to enable real summarization.",
                )
            self._provider = _MockProvider()
            self._model_name = "mock"
            return self._provider

        try:
            if p == "openai":
                self._provider = _OpenAIProvider(
                    settings.llm_api_key,
                    settings.llm_model,
                    settings.llm_base_url,
                )
                self._model_name = settings.llm_model
            elif p == "google":
                self._provider = _GoogleProvider(settings.llm_api_key, settings.llm_model)
                self._model_name = settings.llm_model
            elif p == "anthropic":
                self._provider = _AnthropicProvider(settings.llm_api_key, settings.llm_model)
                self._model_name = settings.llm_model
            else:
                logger.warning("unknown_llm_provider_using_mock", provider=p)
                self._provider = _MockProvider()
                self._model_name = "mock"
        except Exception as exc:
            logger.error("llm_provider_init_failed", exc=str(exc))
            self._provider = _MockProvider()
            self._model_name = "mock"

        return self._provider

    def summarize(
        self,
        clause_text: str,
        category: str = "Unknown",
        user_context: Optional[dict[str, str]] = None,
    ) -> SummarizationResult:
        """
        Generate a plain-English explanation for a legal clause.
        If user_context is provided, tailors the explanation to highlight why
        the clause matters for that context (without computing relevance scores).

        Returns SummarizationResult with success=False if the LLM fails.
        Never claims an AI summary was generated if it was not.
        """
        if not clause_text or not clause_text.strip():
            return SummarizationResult(
                simple_explanation="",
                model_used="",
                provider="",
                success=False,
                error="Empty clause text provided.",
            )

        provider = self._get_provider()
        if user_context:
            user_prompt = build_context_explanation_prompt(clause_text, category, user_context)
        else:
            user_prompt = build_user_prompt(clause_text, category)
        is_mock = isinstance(provider, _MockProvider)

        try:
            explanation = provider.complete(SYSTEM_PROMPT, user_prompt)
            # Ensure disclaimer is present even if model omitted it
            disclaimer = "⚠️ This is an AI-generated explanation for informational purposes, not legal advice."
            if disclaimer not in explanation:
                explanation = explanation.rstrip() + "\n" + disclaimer

            return SummarizationResult(
                simple_explanation=explanation,
                model_used=self._model_name,
                provider=self._provider_name,
                is_mock=is_mock,
                success=True,
            )
        except Exception as exc:
            logger.error("summarization_failed", exc=str(exc))
            return SummarizationResult(
                simple_explanation="",
                model_used=self._model_name,
                provider=self._provider_name,
                is_mock=is_mock,
                success=False,
                error=f"LLM provider error: {exc}",
            )

    def summarize_batch(
        self,
        clauses: list[tuple[str, str]],
    ) -> list[SummarizationResult]:
        """
        Summarize a batch of (clause_text, category) tuples.
        """
        return [self.summarize(text, cat) for text, cat in clauses]


# ---------------------------------------------------------------------------
# Module-level convenience
# ---------------------------------------------------------------------------
_summarizer: Optional[Summarizer] = None


def get_summarizer() -> Summarizer:
    global _summarizer
    if _summarizer is None:
        _summarizer = Summarizer()
    return _summarizer


def summarize_clause(clause_text: str, category: str = "Unknown") -> SummarizationResult:
    return get_summarizer().summarize(clause_text, category)
