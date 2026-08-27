from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import CurrentPrincipal
from app.core.config import Settings, get_settings
from app.core.errors import PolicyBlocked
from app.core.tracing import trace_id_var
from app.db.repositories import resolve_development_scope
from app.db.session import get_session
from app.observability.tracing import TraceRecorder
from app.query.service import QueryService
from app.security.policies import DeterministicSecurityScanner, PolicyAction, SecurityStage

router = APIRouter(prefix="/queries", tags=["queries"])
Session = Annotated[AsyncSession, Depends(get_session)]
AppSettings = Annotated[Settings, Depends(get_settings)]


class QueryRequest(BaseModel):
    query: str = Field(min_length=1)
    top_k: int = Field(default=8, ge=1, le=20)
    document_ids: list[UUID] = Field(default_factory=list)
    transform: bool = False
    rerank: bool = False


class Citation(BaseModel):
    id: int
    document_id: UUID
    chunk_id: UUID
    filename: str
    page: int | None
    section: str | None


class QueryResponse(BaseModel):
    trace_id: str
    answer: str
    answerability: dict[str, object]
    citations: list[Citation]
    usage: dict[str, int]
    security: dict[str, object]
    rewritten_queries: list[str]


@router.post("", response_model=QueryResponse)
async def ask_question(
    payload: QueryRequest, principal: CurrentPrincipal, session: Session, settings: AppSettings
) -> QueryResponse:
    if len(payload.query) > settings.max_query_characters:
        raise HTTPException(status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, "Query exceeds size limit")
    input_scan = DeterministicSecurityScanner().scan(payload.query, SecurityStage.INPUT)
    if input_scan.decision.action is PolicyAction.BLOCK:
        raise PolicyBlocked()
    scope = await resolve_development_scope(session, principal)
    trace_key = trace_id_var.get() or "unknown"
    recorder = TraceRecorder(session, scope, trace_key)
    await recorder.start()
    result = await QueryService(session, settings).ask(
        scope,
        payload.query,
        payload.top_k,
        payload.document_ids,
        transform=payload.transform,
        rerank=payload.rerank,
    )
    recorder.retrieval_event("dense", len(result.retrieval.dense))
    recorder.retrieval_event("sparse", len(result.retrieval.sparse))
    recorder.retrieval_event("fusion", len(result.retrieval.fused))
    recorder.security_events(result.security_events)
    recorder.finish("answered" if result.answerable else "insufficient")
    await session.commit()
    citations = [
        Citation(
            id=item.citation_id,
            document_id=item.chunk.document_id,
            chunk_id=item.chunk.chunk_id,
            filename=item.chunk.filename,
            page=item.chunk.page,
            section=item.chunk.section,
        )
        for item in result.context
    ]
    return QueryResponse(
        trace_id=trace_key,
        answer=result.answer,
        answerability={
            "status": "answerable" if result.answerable else "insufficient",
            "confidence": result.confidence,
        },
        citations=citations,
        usage={
            "dense_candidates": len(result.retrieval.dense),
            "sparse_candidates": len(result.retrieval.sparse),
            "context_chunks": len(result.context),
        },
        security={
            "action": "warn" if result.security_events else input_scan.decision.action,
            "events": [
                {
                    "stage": "context_or_output",
                    "risk": event.decision.risk,
                    "categories": event.decision.categories,
                    "action": event.decision.action,
                }
                for event in result.security_events
            ],
        },
        rewritten_queries=list(result.rewritten_queries),
    )
