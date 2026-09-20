import os

from dotenv import load_dotenv

from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")


def embedding_model_name() -> str:
    """Return the configured SentenceTransformers model."""
    return os.getenv("RAG_EMBEDDING_MODEL", "BAAI/bge-m3")