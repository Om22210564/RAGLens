from uuid import uuid4

from app.reranking.providers import LexicalOverlapReranker
from app.retrieval.types import RetrievedChunk


def test_lexical_reranker_prioritizes_query_overlap() -> None:
    chunks = [
        RetrievedChunk(uuid4(), uuid4(), "a", "unrelated content", None, None, 2, 0.9, ("dense",)),
        RetrievedChunk(
            uuid4(), uuid4(), "b", "hybrid retrieval uses RRF", None, None, 4, 0.2, ("dense",)
        ),
    ]

    ranked = LexicalOverlapReranker().rerank("hybrid retrieval", chunks)

    assert ranked[0].filename == "b"
    assert "lexical_reranker" in ranked[0].sources
