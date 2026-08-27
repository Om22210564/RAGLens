from dataclasses import dataclass
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import Settings
from app.db.repositories import AccessScope
from app.generation.context import ContextItem, build_context
from app.generation.providers import ExtractiveGroundedProvider, LLMProvider
from app.query.transforms import QueryRouter
from app.reranking.providers import LexicalOverlapReranker, Reranker
from app.retrieval.fusion import reciprocal_rank_fusion
from app.retrieval.service import HybridRetriever
from app.retrieval.types import RetrievalResult
from app.security.context import filter_untrusted_context
from app.security.policies import DeterministicSecurityScanner, ScanResult, SecurityStage


@dataclass(frozen=True, slots=True)
class AnswerResult:
    answer: str
    answerable: bool
    confidence: float
    context: tuple[ContextItem, ...]
    retrieval: RetrievalResult
    security_events: tuple[ScanResult, ...]
    rewritten_queries: tuple[str, ...]


class QueryService:
    def __init__(
        self,
        session: AsyncSession,
        settings: Settings,
        llm: LLMProvider | None = None,
        reranker: Reranker | None = None,
    ) -> None:
        self.settings = settings
        self.retriever = HybridRetriever(session)
        self.llm = llm or ExtractiveGroundedProvider()
        self.scanner = DeterministicSecurityScanner()
        self.router = QueryRouter()
        self.reranker = reranker or LexicalOverlapReranker()

    async def ask(
        self,
        scope: AccessScope,
        query: str,
        top_k: int,
        document_ids: list[UUID],
        transform: bool = False,
        rerank: bool = False,
    ) -> AnswerResult:
        plan = self.router.plan(query, transform)
        retrievals = [
            await self.retriever.search(
                scope, expanded_query, self.settings.retrieval_candidate_count, document_ids
            )
            for expanded_query in plan.queries
        ]
        retrieval = self._combine(retrievals)
        candidates = list(retrieval.fused)
        if rerank:
            candidates = self.reranker.rerank(query, candidates)
        safe_chunks, context_events = filter_untrusted_context(candidates[:top_k], self.scanner)
        context = build_context(safe_chunks, self.settings.context_token_budget)
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
                security_events=tuple(context_events),
                rewritten_queries=plan.queries,
            )
        generated = await self.llm.generate(query, context)
        output_scan = self.scanner.scan(generated.answer, SecurityStage.OUTPUT)
        if output_scan.decision.action.value == "block":
            return AnswerResult(
                answer="I cannot provide that response.",
                answerable=False,
                confidence=0.0,
                context=(),
                retrieval=retrieval,
                security_events=tuple(context_events + [output_scan]),
                rewritten_queries=plan.queries,
            )
        cited = tuple(item for item in context if item.citation_id in generated.cited_ids)
        return AnswerResult(
            answer=output_scan.sanitized_text,
            answerable=True,
            confidence=min(0.95, 0.5 + len(cited) * 0.1),
            context=cited,
            retrieval=retrieval,
            security_events=tuple(context_events + [output_scan]),
            rewritten_queries=plan.queries,
        )

    def _combine(self, retrievals: list[RetrievalResult]) -> RetrievalResult:
        if len(retrievals) == 1:
            return retrievals[0]
        dense = reciprocal_rank_fusion([result.dense for result in retrievals])
        sparse = reciprocal_rank_fusion([result.sparse for result in retrievals])
        fused = reciprocal_rank_fusion([result.fused for result in retrievals])
        return RetrievalResult(tuple(dense), tuple(sparse), tuple(fused))
