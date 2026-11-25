"""Embedding service for SmartWork AI MVP using sentence-transformers."""

from __future__ import annotations

import logging
import os
from typing import List, Optional

import numpy as np

logger = logging.getLogger(__name__)

# Model name sentence-transformers/multi-qa-mpnet-base-dot-v1
# or nomic-embed-text as specified in the stack
DEFAULT_EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

_embedding_model = None


def get_embedding_model():
    """Lazy-load the sentence-transformers model."""
    global _embedding_model
    if _embedding_model is None:
        try:
            from sentence_transformers import SentenceTransformer

            model_name = os.getenv(
                "EMBEDDING_MODEL", DEFAULT_EMBEDDING_MODEL
            )
            _embedding_model = SentenceTransformer(model_name)
            logger.info("Loaded embedding model: %s", model_name)
        except ImportError:
            logger.warning(
                "sentence-transformers not installed; embedding features disabled"
            )
            _embedding_model = None
    return _embedding_model


def embed_texts(texts: List[str]) -> Optional[List[List[float]]]:
    """Convert a list of texts into embeddings.

    Returns a list of embedding vectors (one per text), or None if
    sentence-transformers is not available.
    """
    model = get_embedding_model()
    if model is None:
        return None
    try:
        embeddings = model.encode(texts, normalize_embeddings=True)
        return embeddings.tolist()
    except Exception as exc:
        logger.error("Failed to embed texts: %s", exc)
        return None


def embed_query(question: str) -> Optional[List[float]]:
    """Embed a single query string.

    Returns a embedding vector, or None if sentence-transformers is not available.
    """
    model = get_embedding_model()
    if model is None:
        return None
    try:
        vec = model.encode(question, normalize_embeddings=True)
        return vec.tolist()
    except Exception as exc:
        logger.error("Failed to embed query: %s", exc)
        return None


def cosine_similarity(vec_a: List[float], vec_b: List[float]) -> float:
    """Compute cosine similarity between two vectors."""
    if not vec_a or not vec_b:
        return 0.0
    dot = sum(a * b for a, b in zip(vec_a, vec_b))
    norm_a = sum(a * a for a in vec_a) ** 0.5
    norm_b = sum(b * b for b in vec_b) ** 0.5
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot / (norm_a * norm_b)