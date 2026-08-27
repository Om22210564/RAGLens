from dataclasses import dataclass
from typing import Protocol

from app.generation.context import ContextItem


@dataclass(frozen=True, slots=True)
class GenerationResult:
    answer: str
    cited_ids: tuple[int, ...]#The answer cites chunks


class LLMProvider(Protocol):
    async def generate(self, query: str, context: list[ContextItem]) -> GenerationResult: ...
# Any LLM provider in this application must provide a generate() method like this.

class ExtractiveGroundedProvider:
    """No-network baseline; replace with an LLM provider through this interface."""

    async def generate(self, query: str, context: list[ContextItem]) -> GenerationResult:
        first = context[0]# Taking into account the first context item as the most relevant one for generating an answer.
        excerpt = first.chunk.text.strip().replace("\n", " ")
        if len(excerpt) > 600:
            excerpt = excerpt[:597].rsplit(" ", maxsplit=1)[0] + "..."
        return GenerationResult(
            answer=f"Based on the available evidence: {excerpt} [{first.citation_id}]",
            cited_ids=(first.citation_id,),
        )
