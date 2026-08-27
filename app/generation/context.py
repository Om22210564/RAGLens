from dataclasses import dataclass

from app.retrieval.types import RetrievedChunk


@dataclass(frozen=True, slots=True)
class ContextItem:
    citation_id: int
    chunk: RetrievedChunk


def build_context(chunks: list[RetrievedChunk], token_budget: int) -> list[ContextItem]:
    selected: list[ContextItem] = []
    seen_text: set[str] = set()
    per_document: dict[object, int] = {}
    remaining = token_budget
    for chunk in chunks:
        normalized = " ".join(chunk.text.lower().split())
        if normalized in seen_text or chunk.token_count > remaining:
            continue
        if per_document.get(chunk.document_id, 0) >= 3:
            continue
        seen_text.add(normalized)
        per_document[chunk.document_id] = per_document.get(chunk.document_id, 0) + 1
        selected.append(ContextItem(citation_id=len(selected) + 1, chunk=chunk))
        remaining -= chunk.token_count
    return selected


def render_untrusted_context(items: list[ContextItem]) -> str:
    entries = [f"[Source {item.citation_id}] {item.chunk.text}" for item in items]
    return (
        "<UNTRUSTED_RETRIEVED_CONTEXT>\n"
        + "\n\n".join(entries)
        + "\n</UNTRUSTED_RETRIEVED_CONTEXT>"
    )
