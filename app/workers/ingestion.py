import asyncio
from uuid import UUID

import dramatiq

from app.core.config import get_settings
from app.db.session import SessionLocal
from app.ingestion.service import IngestionService
from app.workers import (
    broker as _broker,  # noqa: F401 - configures Dramatiq before actor registration
)


@dramatiq.actor(max_retries=3, min_backoff=5_000)
def process_ingestion_job(job_id: str) -> None:
    asyncio.run(_process(UUID(job_id)))


async def _process(job_id: UUID) -> None:
    async with SessionLocal() as session:
        service = IngestionService(session, get_settings())
        try:
            await service.process(job_id)
            await session.commit()
        except Exception:
            await session.rollback()
            raise
