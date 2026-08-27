import hashlib
from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import Settings
from app.db.models import Chunk, Document, DocumentState, IngestionJob, JobState
from app.db.repositories import AccessScope
from app.embeddings.providers import create_embedding_provider
from app.ingestion.chunking import chunk_document
from app.ingestion.parsers import parse_document
from app.ingestion.storage import LocalBlobStorage
from app.ingestion.validation import ValidatedUpload


class IngestionService:
    def __init__(self, session: AsyncSession, settings: Settings) -> None:
        self.session = session
        self.settings = settings
        self.storage = LocalBlobStorage(settings.storage_directory)
        self.embedding_provider = create_embedding_provider(
            settings.embedding_provider, settings.embedding_model
        )

    async def submit(
        self, scope: AccessScope, upload: ValidatedUpload
    ) -> tuple[Document, IngestionJob, bool]:
        existing = await self.session.scalar(
            select(Document).where(
                Document.tenant_id == scope.tenant_id,
                Document.content_hash == upload.content_hash,
            )
        )
        if existing is not None:
            job = await self.session.scalar(
                select(IngestionJob)
                .where(IngestionJob.document_id == existing.id)
                .order_by(IngestionJob.created_at.desc())
            )
            if job is None:
                raise RuntimeError("Duplicate document has no ingestion job")
            return existing, job, True

        document = Document(
            tenant_id=scope.tenant_id,
            owner_id=scope.user_id,
            source="upload",
            filename=upload.filename,
            mime_type=upload.mime_type,
            content_hash=upload.content_hash,
            storage_key=self.storage.save(upload.content),
            metadata_json={"original_filename": upload.filename},
        )
        self.session.add(document)
        await self.session.flush()
        job = IngestionJob(tenant_id=scope.tenant_id, document_id=document.id)
        self.session.add(job)
        await self.session.flush()
        return document, job, False

    async def process(self, job_id: UUID) -> bool:
        job = await self.session.get(IngestionJob, job_id)
        if job is None or job.state == JobState.SUCCEEDED.value:
            return True
        document = await self.session.get(Document, job.document_id)
        if document is None:
            raise RuntimeError("Ingestion job document is missing")

        job.state = JobState.RUNNING.value
        job.attempts += 1
        job.started_at = datetime.now(UTC)
        document.state = DocumentState.PROCESSING.value
        await self.session.flush()
        try:
            content = self.storage.load(document.storage_key)
            parsed = parse_document(content, document.mime_type, document.filename)
            drafts = chunk_document(
                parsed, self.settings.chunk_target_tokens, self.settings.chunk_overlap_tokens
            )
            if not drafts:
                raise ValueError("No extractable text was found")
            embeddings = self.embedding_provider.embed_documents([draft.text for draft in drafts])
            self.session.add_all(
                Chunk(
                    tenant_id=document.tenant_id,
                    document_id=document.id,
                    ordinal=draft.ordinal,
                    text=draft.text,
                    text_hash=hashlib.sha256(draft.text.encode()).hexdigest(),
                    page=draft.page,
                    section=draft.section,
                    token_count=draft.token_count,
                    embedding=embedding,
                )
                for draft, embedding in zip(drafts, embeddings, strict=True)
            )
            document.state = DocumentState.READY.value
            document.ingested_at = datetime.now(UTC)
            job.state = JobState.SUCCEEDED.value
            job.finished_at = datetime.now(UTC)
        except (OSError, ValueError):
            document.state = DocumentState.FAILED.value
            job.state = JobState.FAILED.value
            job.safe_error = "Document processing failed"
            job.finished_at = datetime.now(UTC)
            return False
        return True
