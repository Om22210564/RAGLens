from uuid import uuid4

from app.retrieval.fusion import reciprocal_rank_fusion
from app.retrieval.types import RetrievedChunk


def _chunk(score: float, source: str) -> RetrievedChunk:
    return RetrievedChunk(uuid4(), uuid4(), "a.md", "evidence", None, None, 1, score, (source,))


def test_rrf_prioritizes_results_present_in_both_lists() -> None:
    shared = _chunk(0.9, "dense")
    sparse_shared = RetrievedChunk(
        shared.chunk_id,
        shared.document_id,
        shared.filename,
        shared.text,
        shared.page,
        shared.section,
        shared.token_count,
        0.9,
        ("sparse",),
    )

    fused = reciprocal_rank_fusion([[shared, _chunk(0.8, "dense")], [sparse_shared]])

    assert fused[0].chunk_id == shared.chunk_id
    assert fused[0].sources == ("dense", "sparse")
