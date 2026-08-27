from collections import defaultdict
from collections.abc import Sequence
from dataclasses import replace
from uuid import UUID

from app.retrieval.types import RetrievedChunk


def reciprocal_rank_fusion(
    result_sets: Sequence[Sequence[RetrievedChunk]], k: int = 60
) -> list[RetrievedChunk]:
    """Fuse rank lists without requiring comparable source scores."""
    scores: dict[UUID, float] = defaultdict(float)
    chunks: dict[UUID, RetrievedChunk] = {}
    sources: dict[UUID, set[str]] = defaultdict(set)
    for result_set in result_sets:
        for rank, chunk in enumerate(result_set, start=1):
            scores[chunk.chunk_id] += 1 / (k + rank)
            chunks[chunk.chunk_id] = chunk
            sources[chunk.chunk_id].update(chunk.sources)
    return [
        replace(chunks[chunk_id], score=score, sources=tuple(sorted(sources[chunk_id])))
        for chunk_id, score in sorted(scores.items(), key=lambda item: item[1], reverse=True)
    ]
