from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True, slots=True)
class RetrievedChunk:
    chunk_id: UUID
    document_id: UUID
    filename: str
    text: str
    page: int | None
    section: str | None
    token_count: int
    score: float
    sources: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class RetrievalResult:
    dense: tuple[RetrievedChunk, ...]
    sparse: tuple[RetrievedChunk, ...]
    fused: tuple[RetrievedChunk, ...]
# which retrieval method(s) contributed this chunk.
