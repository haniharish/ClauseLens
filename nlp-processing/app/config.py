"""
ClauseLens NLP Service — Central Configuration
Loads settings from environment variables / .env file.
"""
from __future__ import annotations

from functools import lru_cache
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Service
    environment: Literal["development", "production", "test"] = "development"
    api_host: str = "0.0.0.0"
    api_port: int = 8001

    # Models
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    spacy_model: str = "en_core_web_sm"

    # LLM
    llm_provider: Literal["openai", "google", "anthropic", "mock"] = "mock"
    llm_api_key: str = ""
    llm_model: str = "gpt-4o-mini"
    llm_base_url: str = ""

    # Classification
    classification_method: Literal["rule_based", "zero_shot", "hybrid"] = "hybrid"
    zero_shot_model: str = "facebook/bart-large-mnli"

    # File limits
    max_document_size_mb: int = 20

    # Performance
    lightweight_mode: bool = Field(default=False)
    embedding_batch_size: int = 32

    # Integration
    django_backend_url: str = "http://localhost:8000"
    nlp_service_url: str = "http://localhost:8001"

    @property
    def max_document_size_bytes(self) -> int:
        return self.max_document_size_mb * 1024 * 1024


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return cached settings singleton."""
    return Settings()
