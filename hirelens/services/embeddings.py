# hirelens/services/embeddings.py
from functools import lru_cache
from typing import List
import numpy as np
from sentence_transformers import SentenceTransformer


@lru_cache(maxsize=1)
def get_model(model_name: str) -> SentenceTransformer:
    """
    Lazily load and cache the SentenceTransformer model.
    Using LRU cache ensures we only load once per process.
    """
    return SentenceTransformer(model_name)


def embed_texts(texts: List[str], model_name: str) -> np.ndarray:
    """
    Encode a list of strings into normalized embeddings (float32).
    Normalization lets us use dot product as cosine similarity.
    """
    model = get_model(model_name)
    emb = model.encode(
        texts,
        normalize_embeddings=True,
        show_progress_bar=False
    )
    return np.asarray(emb, dtype="float32")
