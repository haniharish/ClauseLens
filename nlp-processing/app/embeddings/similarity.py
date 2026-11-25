"""
ClauseLens — Embedding Similarity Utilities
Cosine similarity and nearest-neighbour search over clause embeddings.
"""
from __future__ import annotations

import numpy as np


def cosine_similarity(vec_a: list[float], vec_b: list[float]) -> float:
    """
    Compute cosine similarity between two embedding vectors.
    Returns a value in [-1, 1]. Returns 0.0 if either vector is zero-length.
    """
    a = np.array(vec_a, dtype=np.float32)
    b = np.array(vec_b, dtype=np.float32)

    norm_a = np.linalg.norm(a)
    norm_b = np.linalg.norm(b)

    if norm_a == 0 or norm_b == 0:
        return 0.0

    return float(np.dot(a, b) / (norm_a * norm_b))


def find_most_similar(
    query_embedding: list[float],
    candidate_embeddings: list[list[float]],
    top_k: int = 5,
) -> list[tuple[int, float]]:
    """
    Find the top-k most similar embeddings to a query.

    Parameters
    ----------
    query_embedding : list[float]
        The query vector.
    candidate_embeddings : list[list[float]]
        List of candidate vectors.
    top_k : int
        Number of top results to return.

    Returns
    -------
    List of (index, similarity_score) sorted descending by score.
    """
    if not candidate_embeddings:
        return []

    q = np.array(query_embedding, dtype=np.float32)
    q_norm = np.linalg.norm(q)
    if q_norm == 0:
        return []

    matrix = np.array(candidate_embeddings, dtype=np.float32)
    norms = np.linalg.norm(matrix, axis=1, keepdims=True)
    norms = np.where(norms == 0, 1e-10, norms)
    normalized = matrix / norms

    scores = normalized @ (q / q_norm)
    top_indices = np.argsort(scores)[::-1][:top_k]
    return [(int(idx), float(scores[idx])) for idx in top_indices]


def pairwise_similarity_matrix(embeddings: list[list[float]]) -> list[list[float]]:
    """
    Compute an N×N cosine similarity matrix.
    Returns a list of lists (not a numpy array) for JSON serialisability.
    """
    if not embeddings:
        return []

    matrix = np.array(embeddings, dtype=np.float32)
    norms = np.linalg.norm(matrix, axis=1, keepdims=True)
    norms = np.where(norms == 0, 1e-10, norms)
    normalized = matrix / norms
    sim_matrix = normalized @ normalized.T
    return sim_matrix.tolist()
