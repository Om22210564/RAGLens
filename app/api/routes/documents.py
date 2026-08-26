from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import CurrentPrincipal
from app.core.config import Settings, get_settings
from app.db.models import IngestionJob
from app.db.repositories import DocumentRepository, resolve_development_scope
from app.db.session import get_session
from app.ingestion.service import IngestionService
from app.ingestion.validation import validate_upload
from app.workers.ingestion import process_ingestion_job

router = APIRouter(prefix="/documents", tags=["documents"])
Session = Annotated[AsyncSession, Depends(get_session)]
AppSettings = Annotated[Settings, Depends(get_settings)]


class IngestionAccepted(BaseModel):
    document_id: UUID
    ingestion_job_id: UUID
    status: str
    duplicate: bool


class DocumentStatus(BaseModel):
    id: UUID
    filename: str
    mime_type: str
    state: str
    ingestion_job_id: UUID
    ingestion_status: str


@router.post("", status_code=status.HTTP_202_ACCEPTED, response_model=IngestionAccepted)
async def upload_document(
    principal: CurrentPrincipal,
    session: Session,
    settings: AppSettings,
    file: Annotated[UploadFile, File(...)],
) -> IngestionAccepted:
    content = await file.read(settings.max_upload_bytes + 1)
    upload = validate_upload(file.filename, file.content_type, content, settings.max_upload_bytes)
    scope = await resolve_development_scope(session, principal)
    service = IngestionService(session, settings)
    document, job, duplicate = await service.submit(scope, upload)
    await session.commit()
    if not duplicate:
        process_ingestion_job.send(str(job.id))
    return IngestionAccepted(
        document_id=document.id,
        ingestion_job_id=job.id,
        status=job.state,
        duplicate=duplicate,
    )


@router.get("/{document_id}", response_model=DocumentStatus)
async def get_document(
    document_id: UUID, principal: CurrentPrincipal, session: Session
) -> DocumentStatus:
    scope = await resolve_development_scope(session, principal)
    document = await session.scalar(DocumentRepository().by_id(scope, document_id))
    if document is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Document not found")
    job = await session.scalar(
        select(IngestionJob)
        .where(IngestionJob.document_id == document.id)
        .order_by(IngestionJob.created_at.desc())
    )
    if job is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Ingestion job not found")
    return DocumentStatus(
        id=document.id,
        filename=document.filename,
        mime_type=document.mime_type,
        state=document.state,
        ingestion_job_id=job.id,
        ingestion_status=job.state,
    )
