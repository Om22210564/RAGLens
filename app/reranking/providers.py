import re
from dataclasses import replace
from typing import Protocol

from app.retrieval.types import RetrievedChunk


class Reranker(Protocol):
    def rerank(self, query: str, candidates: list[RetrievedChunk]) -> list[RetrievedChunk]: ...


class LexicalOverlapReranker:
    """Fast local baseline; replace with a cross-encoder through `Reranker`."""

    def rerank(self, query: str, candidates: list[RetrievedChunk]) -> list[RetrievedChunk]:
        query_terms = set(re.findall(r"\w+", query.lower()))
        if not query_terms:
            return candidates

        def score(chunk: RetrievedChunk) -> float:
            terms = set(re.findall(r"\w+", chunk.text.lower()))
            overlap = len(query_terms & terms) / len(query_terms)
            return overlap + (chunk.score * 0.01)

        return [
            replace(chunk, score=score(chunk), sources=(*chunk.sources, "lexical_reranker"))
            for chunk in sorted(candidates, key=score, reverse=True)
        ]
