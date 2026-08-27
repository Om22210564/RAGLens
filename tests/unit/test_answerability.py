from uuid import uuid4

from app.generation.context import ContextItem
from app.query.service import QueryService
from app.retrieval.types import RetrievedChunk


def _context(text: str) -> list[ContextItem]:
    chunk = RetrievedChunk(uuid4(), uuid4(), "doc", text, None, None, 30, 1.0, ("dense",))
    return [ContextItem(1, chunk)]


def test_answerability_rejects_command_only_context() -> None:
    service = object.__new__(QueryService)

    command = "curl -X POST example -H 'header' -d 'body'"
    assert not service._has_substantive_evidence(_context(command))


def test_answerability_accepts_substantive_prose() -> None:
    service = object.__new__(QueryService)
    prose = (
        "Hybrid retrieval combines lexical and semantic search to improve recall across queries."
    )

    assert service._has_substantive_evidence(_context(prose))
