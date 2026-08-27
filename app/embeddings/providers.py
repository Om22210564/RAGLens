import hashlib
import math
import re
from typing import Any, Protocol, cast


class EmbeddingProvider(Protocol):
    def embed_documents(self, texts: list[str]) -> list[list[float]]: ...

    def embed_query(self, text: str) -> list[float]: ...


class HashEmbeddingProvider:
    """Deterministic local baseline with no model download or external API.

    It is intentionally a temporary ingestion baseline. Phase 2 replaces it
    through the same interface with a sentence-transformer provider for quality.
    """

    def __init__(self, dimensions: int = 384) -> None:
        if dimensions <= 0:
            raise ValueError("Embedding dimensions must be positive")
        self.dimensions = dimensions

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        return [self._embed(text) for text in texts]

    def embed_query(self, text: str) -> list[float]:
        return self._embed(text)

    def _embed(self, text: str) -> list[float]:
        vector = [0.0] * self.dimensions
        for token in re.findall(r"[\w'-]+", text.lower()):
            digest = hashlib.blake2b(token.encode(), digest_size=8).digest()
            index = int.from_bytes(digest[:4], "big") % self.dimensions
            sign = 1.0 if digest[4] & 1 else -1.0
            vector[index] += sign
        norm = math.sqrt(sum(value * value for value in vector))
        return vector if norm == 0 else [value / norm for value in vector]


class SentenceTransformerEmbeddingProvider:
    """Local semantic embeddings, loaded lazily to keep unit tests offline."""

    def __init__(self, model_name: str) -> None:
        self.model_name = model_name
        self._model: Any | None = None

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        model = self._load_model()
        vectors = model.encode_document(texts, normalize_embeddings=True)
        return [cast(list[float], vector.tolist()) for vector in vectors]

    def embed_query(self, text: str) -> list[float]:
        model = self._load_model()
        return cast(list[float], model.encode_query([text], normalize_embeddings=True)[0].tolist())

    def _load_model(self) -> Any:
        if self._model is None:
            from sentence_transformers import SentenceTransformer

            self._model = SentenceTransformer(self.model_name)
        return self._model


def create_embedding_provider(provider: str, model_name: str) -> EmbeddingProvider:
    if provider == "sentence_transformer":
        return SentenceTransformerEmbeddingProvider(model_name)
    if provider == "hash":
        return HashEmbeddingProvider()
    raise ValueError(f"Unsupported embedding provider: {provider}")
