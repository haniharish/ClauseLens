"""
Tests for embedding generation (app/embeddings/).
Runs in lightweight mode (LIGHTWEIGHT_MODE=1) so no model is downloaded.
Provides a mock-embedding fallback path test.
"""
from __future__ import annotations

import os
import pytest
import numpy as np

# Lightweight mode is set in conftest.py


class TestEmbeddingGenerator:
    def test_generator_instantiates(self):
        from app.embeddings.embedding_generator import EmbeddingGenerator
        gen = EmbeddingGenerator()
        assert gen is not None

    def test_empty_text_returns_none(self):
        from app.embeddings.embedding_generator import EmbeddingGenerator
        gen = EmbeddingGenerator()
        result = gen.embed_text("", clause_id=1)
        assert result is None

    def test_whitespace_only_text_returns_none(self):
        from app.embeddings.embedding_generator import EmbeddingGenerator
        gen = EmbeddingGenerator()
        result = gen.embed_text("   \n  ", clause_id=1)
        assert result is None

    def test_batch_returns_list(self):
        from app.embeddings.embedding_generator import embed_clauses
        texts = ["Data collection clause.", "Arbitration clause.", ""]
        results = embed_clauses(texts)
        # In lightweight mode, all will be None; in full mode, non-empty will have results
        assert isinstance(results, list)
        assert len(results) == 3
        # Empty text must always be None
        assert results[2] is None

    def test_batch_aligned_with_input(self):
        from app.embeddings.embedding_generator import embed_clauses
        texts = ["clause 1", "clause 2", "clause 3"]
        results = embed_clauses(texts, clause_ids=[10, 20, 30])
        assert len(results) == len(texts)


class TestSimilarity:
    def test_identical_vectors_similarity_is_one(self):
        from app.embeddings.similarity import cosine_similarity
        vec = [1.0, 0.5, -0.3]
        sim = cosine_similarity(vec, vec)
        assert abs(sim - 1.0) < 1e-5

    def test_opposite_vectors_similarity_is_negative(self):
        from app.embeddings.similarity import cosine_similarity
        a = [1.0, 0.0]
        b = [-1.0, 0.0]
        sim = cosine_similarity(a, b)
        assert sim < 0

    def test_zero_vector_returns_zero(self):
        from app.embeddings.similarity import cosine_similarity
        sim = cosine_similarity([0.0, 0.0], [1.0, 0.0])
        assert sim == 0.0

    def test_find_most_similar_returns_ranked(self):
        from app.embeddings.similarity import find_most_similar
        query = [1.0, 0.0, 0.0]
        candidates = [
            [0.9, 0.1, 0.0],   # most similar
            [0.0, 1.0, 0.0],   # orthogonal
            [-1.0, 0.0, 0.0],  # opposite
        ]
        results = find_most_similar(query, candidates, top_k=3)
        assert len(results) == 3
        # First result should be index 0
        assert results[0][0] == 0
        # Scores should be descending
        scores = [r[1] for r in results]
        assert scores == sorted(scores, reverse=True)

    def test_find_most_similar_empty_candidates(self):
        from app.embeddings.similarity import find_most_similar
        result = find_most_similar([1.0, 0.0], [], top_k=3)
        assert result == []

    def test_pairwise_matrix_shape(self):
        from app.embeddings.similarity import pairwise_similarity_matrix
        embeddings = [[1.0, 0.0], [0.0, 1.0], [0.5, 0.5]]
        matrix = pairwise_similarity_matrix(embeddings)
        assert len(matrix) == 3
        assert len(matrix[0]) == 3

    def test_pairwise_diagonal_is_one(self):
        from app.embeddings.similarity import pairwise_similarity_matrix
        embeddings = [[1.0, 0.0], [0.0, 1.0]]
        matrix = pairwise_similarity_matrix(embeddings)
        assert abs(matrix[0][0] - 1.0) < 1e-5
        assert abs(matrix[1][1] - 1.0) < 1e-5
