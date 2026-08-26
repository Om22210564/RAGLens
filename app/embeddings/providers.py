import hashlib
import math
import re
from typing import Protocol


class EmbeddingProvider(Protocol):
    def embed_documents(self, texts: list[str]) -> list[list[float]]: ...


class HashEmbeddingProvider:
    """Deterministic local baseline with no model download or external API.

    It is intentionally a temporary ingestion baseline. Phase 2 replaces it
    through the same interface with a sentence-transformer provider for quality.
    """

    def __init__(self, dimensions: int = 128) -> None:
        if dimensions <= 0:
            raise ValueError("Embedding dimensions must be positive")
        self.dimensions = dimensions

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        return [self._embed(text) for text in texts]

    def _embed(self, text: str) -> list[float]:
        vector = [0.0] * self.dimensions
        for token in re.findall(r"[\w'-]+", text.lower()):
            digest = hashlib.blake2b(token.encode(), digest_size=8).digest()
            index = int.from_bytes(digest[:4], "big") % self.dimensions
            sign = 1.0 if digest[4] & 1 else -1.0
            vector[index] += sign
        norm = math.sqrt(sum(value * value for value in vector))
        return vector if norm == 0 else [value / norm for value in vector]
