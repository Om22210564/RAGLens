from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import CurrentPrincipal
from app.db.models import RagTrace, RetrievalEvent, SecurityEvent
from app.db.repositories import resolve_development_scope
from app.db.session import get_session

router = APIRouter(prefix="/traces", tags=["traces"])
Session = Annotated[AsyncSession, Depends(get_session)]


class TraceResponse(BaseModel):
    trace_id: str
    outcome: str
    latency_ms: int | None
    retrieval_events: list[dict[str, object]]
    security_events: list[dict[str, object]]


@router.get("/{trace_key}", response_model=TraceResponse)
async def get_trace(trace_key: str, principal: CurrentPrincipal, session: Session) -> TraceResponse:
    scope = await resolve_development_scope(session, principal)
    trace = await session.scalar(
        select(RagTrace).where(
            RagTrace.trace_key == trace_key,
            RagTrace.tenant_id == scope.tenant_id,
            RagTrace.user_id == scope.user_id,
        )
    )
    if trace is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Trace not found")
    retrieval_events = list(
        await session.scalars(select(RetrievalEvent).where(RetrievalEvent.trace_id == trace.id))
    )
    security_events = list(
        await session.scalars(select(SecurityEvent).where(SecurityEvent.trace_id == trace.id))
    )
    return TraceResponse(
        trace_id=trace.trace_key,
        outcome=trace.outcome,
        latency_ms=trace.total_latency_ms,
        retrieval_events=[
            {
                "stage": event.stage,
                "output_count": event.output_count,
                "latency_ms": event.latency_ms,
            }
            for event in retrieval_events
        ],
        security_events=[
            {
                "stage": event.stage,
                "risk": event.risk,
                "action": event.action,
                "categories": event.categories_json,
            }
            for event in security_events
        ],
    )
