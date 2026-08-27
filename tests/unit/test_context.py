from uuid import uuid4

from app.generation.context import build_context, render_untrusted_context
from app.retrieval.types import RetrievedChunk


def test_context_deduplicates_and_delimits_untrusted_content() -> None:
    document_id = uuid4()
    chunks = [
        RetrievedChunk(
            uuid4(), document_id, "a.md", "same evidence", None, "Intro", 2, 1.0, ("dense",)
        ),
        RetrievedChunk(
            uuid4(), document_id, "a.md", "same evidence", None, "Intro", 2, 0.9, ("sparse",)
        ),
    ]

    context = build_context(chunks, token_budget=10)

    assert len(context) == 1
    assert "<UNTRUSTED_RETRIEVED_CONTEXT>" in render_untrusted_context(context)
