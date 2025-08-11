# hirelens/api/deps.py
from hirelens.configs.settings import settings
from hirelens.services.embeddings import get_model

def warm_models() -> None:
    """
    Preload the sentence-transformers model so the first request isn't slow.
    Safe to no-op if the model is already cached.
    """
    try:
        get_model(settings.EMBEDDING_MODEL)
    except Exception as e:
        # Don't block startup if warmup fails; just log it
        print(f"[deps] warm_models warning: {e}")
