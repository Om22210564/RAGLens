import re
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class QueryPlan:
    queries: tuple[str, ...]
    transformed: bool
    reason: str | None = None


class QueryRouter:
    """Conservative deterministic router; an LLM classifier can replace it later."""

    def plan(self, query: str, enabled: bool) -> QueryPlan:
        normalized = " ".join(query.split())
        if not enabled:
            return QueryPlan((normalized,), False)
        lowered = normalized.lower()
        comparison_markers = ("compare ", "difference between", " versus ", " vs. ")
        if any(marker in lowered for marker in comparison_markers):
            return QueryPlan(
                tuple(self._decompose_comparison(normalized)), True, "comparison_decomposition"
            )
        if " and " in lowered and len(re.findall(r"\w+", normalized)) >= 10:
            parts = [part.strip(" ?.") for part in re.split(r"\s+and\s+", normalized, maxsplit=1)]
            if len(parts) == 2 and all(parts):
                return QueryPlan((normalized, *parts), True, "compound_expansion")
        return QueryPlan((normalized,), False)

    def _decompose_comparison(self, query: str) -> list[str]:
        match = re.search(r"compare\s+(.+?)\s+(?:and|with|versus|vs\.?)\s+(.+)", query, re.I)
        if match is None:
            return [query]
        left, right = match.group(1).strip(" ?."), match.group(2).strip(" ?.")
        return [
            query,
            f"What is {left}?",
            f"What is {right}?",
            f"How do {left} and {right} compare?",
        ]
