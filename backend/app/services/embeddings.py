"""
Embeddings run locally via sentence-transformers rather than a hosted API.

Why: Groq (our LLM provider for this project) does not expose an embeddings
endpoint, and pulling in a second paid provider just for embeddings adds
cost/config for little benefit at this scale. A local MiniLM model is small
(~80MB), fast on CPU, and good enough for single-user semantic search.
"""

from functools import lru_cache

import numpy as np
from sentence_transformers import SentenceTransformer

from app.config import get_settings
from app.exceptions import EmbeddingError
from app.logging_config import get_logger, log_with_fields

logger = get_logger(__name__)


@lru_cache
def _get_model() -> SentenceTransformer:
    settings = get_settings()
    log_with_fields(logger, 20, "loading_embedding_model", model=settings.embedding_model)
    return SentenceTransformer(settings.embedding_model)


def embed_texts(texts: list[str]) -> list[list[float]]:
    if not texts:
        return []
    try:
        model = _get_model()
        vectors = model.encode(texts, normalize_embeddings=True, show_progress_bar=False)
        return np.asarray(vectors, dtype=np.float32).tolist()
    except Exception as exc:  # noqa: BLE001 - convert any backend failure to a domain error
        raise EmbeddingError(f"Failed to generate embeddings: {exc}") from exc


def embed_query(text: str) -> list[float]:
    return embed_texts([text])[0]
