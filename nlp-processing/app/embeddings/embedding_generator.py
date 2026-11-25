"""
ClauseLens — Embedding Generator
Generates semantic embeddings for clauses using Sentence Transformers.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

import numpy as np

from app.config import get_settings
from app.utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class EmbeddingResult:
    clause_id: int
    model: str
    embedding_dimension: int
    embedding: list[float]
    text_length: int


# ---------------------------------------------------------------------------
# Generator
# ---------------------------------------------------------------------------

class EmbeddingGenerator:
    """
    Wraps Sentence Transformers to produce clause embeddings.
    Uses lazy model loading to avoid startup delays.
    """

    def __init__(self):
        self._model = None
        self._model_name: str = ""

    def _get_model(self):
        if self._model is False:
            return None
        if self._model is not None:
            return self._model

        settings = get_settings()

        if settings.lightweight_mode:
            logger.warning("embedding_skipped_lightweight_mode")
            self._model = False
            return None

        try:
            from sentence_transformers import SentenceTransformer
            model_name = settings.embedding_model
            logger.info("loading_embedding_model", model=model_name)
            self._model = SentenceTransformer(model_name)
            self._model_name = model_name
            logger.info("embedding_model_loaded", model=model_name)
        except Exception as exc:
            logger.error("embedding_model_load_failed", exc=str(exc))
            self._model = False

        return self._model if self._model is not False else None

    @property
    def model_name(self) -> str:
        settings = get_settings()
        return self._model_name or settings.embedding_model

    def embed_text(self, text: str, clause_id: int = 0) -> Optional[EmbeddingResult]:
        """
        Generate embedding for a single text.
        Returns None if the model is unavailable or text is invalid.
        """
        if not text or not text.strip():
            logger.warning("empty_text_skipped_embedding", clause_id=clause_id)
            return None

        model = self._get_model()
        if model is None:
            return None

        try:
            vec = model.encode(text, convert_to_numpy=True, show_progress_bar=False)
            embedding: list[float] = vec.tolist()
            return EmbeddingResult(
                clause_id=clause_id,
                model=self.model_name,
                embedding_dimension=len(embedding),
                embedding=embedding,
                text_length=len(text),
            )
        except Exception as exc:
            logger.error("embedding_generation_failed", clause_id=clause_id, exc=str(exc))
            return None

    def embed_batch(
        self,
        texts: list[str],
        clause_ids: Optional[list[int]] = None,
    ) -> list[Optional[EmbeddingResult]]:
        """
        Generate embeddings for a batch of texts.
        Returns a list aligned with the input (None for failed items).
        """
        if clause_ids is None:
            clause_ids = list(range(1, len(texts) + 1))

        model = self._get_model()
        if model is None:
            return [None] * len(texts)

        settings = get_settings()
        batch_size = settings.embedding_batch_size

        results: list[Optional[EmbeddingResult]] = []
        valid_indices = [i for i, t in enumerate(texts) if t and t.strip()]
        valid_texts = [texts[i] for i in valid_indices]

        try:
            vecs = model.encode(
                valid_texts,
                batch_size=batch_size,
                convert_to_numpy=True,
                show_progress_bar=len(valid_texts) > 10,
            )
        except Exception as exc:
            logger.error("batch_embedding_failed", exc=str(exc))
            return [None] * len(texts)

        vec_map: dict[int, np.ndarray] = {
            valid_indices[j]: vecs[j] for j in range(len(valid_indices))
        }

        for i in range(len(texts)):
            if i not in vec_map:
                results.append(None)
            else:
                vec = vec_map[i]
                results.append(EmbeddingResult(
                    clause_id=clause_ids[i],
                    model=self.model_name,
                    embedding_dimension=len(vec),
                    embedding=vec.tolist(),
                    text_length=len(texts[i]),
                ))

        return results


# ---------------------------------------------------------------------------
# Module-level convenience
# ---------------------------------------------------------------------------
_generator: Optional[EmbeddingGenerator] = None


def get_generator() -> EmbeddingGenerator:
    global _generator
    if _generator is None:
        _generator = EmbeddingGenerator()
    return _generator


def embed_clause(text: str, clause_id: int = 0) -> Optional[EmbeddingResult]:
    return get_generator().embed_text(text, clause_id)


def embed_clauses(
    texts: list[str],
    clause_ids: Optional[list[int]] = None,
) -> list[Optional[EmbeddingResult]]:
    return get_generator().embed_batch(texts, clause_ids)
