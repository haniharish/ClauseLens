"""
Pytest configuration and shared fixtures for ClauseLens NLP tests.
"""
from __future__ import annotations

import os

import pytest

# Force test environment before any app imports
os.environ.setdefault("ENVIRONMENT", "test")
os.environ.setdefault("LLM_PROVIDER", "mock")
os.environ.setdefault("LLM_API_KEY", "")
os.environ.setdefault("LIGHTWEIGHT_MODE", "1")
os.environ.setdefault("CLASSIFICATION_METHOD", "rule_based")


@pytest.fixture(scope="session")
def sample_privacy_policy_text() -> str:
    from data.sample_documents.sample_texts import SAMPLE_PRIVACY_POLICY
    return SAMPLE_PRIVACY_POLICY


@pytest.fixture(scope="session")
def sample_no_headings_text() -> str:
    from data.sample_documents.sample_texts import SAMPLE_TERMS_NO_HEADINGS
    return SAMPLE_TERMS_NO_HEADINGS


@pytest.fixture(scope="session")
def sample_data_collection_clause() -> str:
    from data.sample_documents.sample_texts import SAMPLE_DATA_COLLECTION_CLAUSE
    return SAMPLE_DATA_COLLECTION_CLAUSE


@pytest.fixture(scope="session")
def sample_arbitration_clause() -> str:
    from data.sample_documents.sample_texts import SAMPLE_ARBITRATION_CLAUSE
    return SAMPLE_ARBITRATION_CLAUSE


@pytest.fixture(scope="session")
def sample_liability_clause() -> str:
    from data.sample_documents.sample_texts import SAMPLE_LIABILITY_CLAUSE
    return SAMPLE_LIABILITY_CLAUSE


@pytest.fixture(scope="session")
def sample_children_clause() -> str:
    from data.sample_documents.sample_texts import SAMPLE_CHILDREN_CLAUSE
    return SAMPLE_CHILDREN_CLAUSE


@pytest.fixture
def test_client():
    """FastAPI test client (uses lifespan context)."""
    from fastapi.testclient import TestClient
    from app.main import app
    with TestClient(app) as client:
        yield client
