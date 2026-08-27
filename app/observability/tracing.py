from time import perf_counter

from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import RagTrace, RetrievalEvent, SecurityEvent
from app.db.repositories import AccessScope
from app.security.policies import ScanResult


class TraceRecorder:
    def __init__(self, session: AsyncSession, scope: AccessScope, trace_key: str) -> None:
        self.session = session
        self.scope = scope
        self.trace = RagTrace(
            tenant_id=scope.tenant_id,
            user_id=scope.user_id,
            trace_key=trace_key,
            route="POST /api/v1/queries",
            configuration_json={},
        )
        self.started = perf_counter()

    async def start(self) -> None:
        self.session.add(self.trace)
        await self.session.flush()

    def retrieval_event(self, stage: str, output_count: int, latency_ms: int = 0) -> None:
        self.session.add(
            RetrievalEvent(
                trace_id=self.trace.id,
                stage=stage,
                retriever=stage,
                input_count=0,
                output_count=output_count,
                latency_ms=latency_ms,
            )
        )

    def security_events(self, events: tuple[ScanResult, ...]) -> None:
        for event in events:
            decision = event.decision
            self.session.add(
                SecurityEvent(
                    trace_id=self.trace.id,
                    stage="context_or_output",
                    risk=decision.risk,
                    action=decision.action,
                    categories_json=list(decision.categories),
                    redacted_evidence=event.sanitized_text[:200],
                )
            )

    def finish(self, outcome: str) -> None:
        self.trace.outcome = outcome
        self.trace.total_latency_ms = round((perf_counter() - self.started) * 1000)
