from dataclasses import dataclass
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import Settings
from app.db.repositories import AccessScope
from app.generation.context import ContextItem, build_context
from app.generation.providers import ExtractiveGroundedProvider, LLMProvider
from app.retrieval.service import HybridRetriever
from app.retrieval.types import RetrievalResult


@dataclass(frozen=True, slots=True)
class AnswerResult:
    answer: str
    answerable: bool
    confidence: float
    context: tuple[ContextItem, ...]
    retrieval: RetrievalResult


class QueryService:
    def __init__(
        self, session: AsyncSession, settings: Settings, llm: LLMProvider | None = None
    ) -> None:
        self.settings = settings
        self.retriever = HybridRetriever(session)
        self.llm = llm or ExtractiveGroundedProvider()

    async def ask(
        self, scope: AccessScope, query: str, top_k: int, document_ids: list[UUID]
    ) -> AnswerResult:
        retrieval = await self.retriever.search(
            scope, query, self.settings.retrieval_candidate_count, document_ids
        )
        context = build_context(list(retrieval.fused[:top_k]), self.settings.context_token_budget)
        if not context:
            return AnswerResult(
                answer=(
                    "I could not find enough evidence in the available documents "
                    "to answer this reliably."
                ),
                answerable=False,
                confidence=0.0,
                context=(),
                retrieval=retrieval,
            )
        generated = await self.llm.generate(query, context)
        cited = tuple(item for item in context if item.citation_id in generated.cited_ids)
        return AnswerResult(
            answer=generated.answer,
            answerable=True,
            confidence=min(0.95, 0.5 + len(cited) * 0.1),
            context=cited,
            retrieval=retrieval,
        )
