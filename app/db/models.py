import uuid
from datetime import datetime
from enum import StrEnum

from pgvector.sqlalchemy import Vector
from sqlalchemy import DateTime, ForeignKey, Index, Integer, String, Text, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class DocumentState(StrEnum):
    QUEUED = "queued"
    PROCESSING = "processing"
    READY = "ready"
    FAILED = "failed"


class JobState(StrEnum):
    QUEUED = "queued"
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    FAILED = "failed"


class TimestampedModel:
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


class Tenant(TimestampedModel, Base):
    __tablename__ = "tenants"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(255), unique=True)
    status: Mapped[str] = mapped_column(String(32), default="active")


class User(TimestampedModel, Base):
    __tablename__ = "users"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    external_subject: Mapped[str] = mapped_column(String(255), unique=True)
    email: Mapped[str | None] = mapped_column(String(320))


class TenantMembership(TimestampedModel, Base):
    __tablename__ = "tenant_memberships"
    __table_args__ = (UniqueConstraint("tenant_id", "user_id", name="uq_membership_tenant_user"),)
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("tenants.id", ondelete="CASCADE"))
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    role: Mapped[str] = mapped_column(String(64), default="member")
    status: Mapped[str] = mapped_column(String(32), default="active")


class Document(TimestampedModel, Base):
    __tablename__ = "documents"
    __table_args__ = (
        UniqueConstraint("tenant_id", "content_hash", name="uq_document_tenant_content_hash"),
        Index("ix_documents_tenant_state", "tenant_id", "state"),
    )
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("tenants.id", ondelete="CASCADE"))
    owner_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"))
    source: Mapped[str] = mapped_column(String(64))
    filename: Mapped[str] = mapped_column(String(512))
    mime_type: Mapped[str] = mapped_column(String(255))
    content_hash: Mapped[str] = mapped_column(String(64))
    storage_key: Mapped[str] = mapped_column(String(512), unique=True)
    state: Mapped[str] = mapped_column(String(32), default=DocumentState.QUEUED.value)
    metadata_json: Mapped[dict[str, object]] = mapped_column(JSONB, default=dict)
    ingested_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


class DocumentPermission(TimestampedModel, Base):
    __tablename__ = "document_permissions"
    __table_args__ = (Index("ix_document_permissions_document", "document_id"),)
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    document_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("documents.id", ondelete="CASCADE"))
    grantee_type: Mapped[str] = mapped_column(String(32))
    grantee_id: Mapped[str] = mapped_column(String(255))
    access_level: Mapped[str] = mapped_column(String(32), default="read")


class Chunk(TimestampedModel, Base):
    __tablename__ = "chunks"
    __table_args__ = (
        UniqueConstraint("document_id", "ordinal", name="uq_chunk_document_ordinal"),
        Index("ix_chunks_tenant_document", "tenant_id", "document_id"),
    )
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("tenants.id", ondelete="CASCADE"))
    document_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("documents.id", ondelete="CASCADE"))
    ordinal: Mapped[int] = mapped_column(Integer)
    text: Mapped[str] = mapped_column(Text)
    text_hash: Mapped[str] = mapped_column(String(64))
    page: Mapped[int | None] = mapped_column(Integer)
    section: Mapped[str | None] = mapped_column(String(512))
    token_count: Mapped[int] = mapped_column(Integer)
    metadata_json: Mapped[dict[str, object]] = mapped_column(JSONB, default=dict)
    embedding: Mapped[list[float] | None] = mapped_column(Vector(), nullable=True)


class IngestionJob(TimestampedModel, Base):
    __tablename__ = "ingestion_jobs"
    __table_args__ = (Index("ix_ingestion_jobs_tenant_state", "tenant_id", "state"),)
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("tenants.id", ondelete="CASCADE"))
    document_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("documents.id", ondelete="CASCADE"))
    state: Mapped[str] = mapped_column(String(32), default=JobState.QUEUED.value)
    attempts: Mapped[int] = mapped_column(Integer, default=0)
    safe_error: Mapped[str | None] = mapped_column(Text)
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


class RagTrace(TimestampedModel, Base):
    __tablename__ = "rag_traces"
    __table_args__ = (Index("ix_rag_traces_tenant_created", "tenant_id", "created_at"),)
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("tenants.id", ondelete="CASCADE"))
    user_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("users.id"))
    route: Mapped[str] = mapped_column(String(255))
    outcome: Mapped[str] = mapped_column(String(32), default="started")
    configuration_json: Mapped[dict[str, object]] = mapped_column(JSONB, default=dict)
    total_latency_ms: Mapped[int | None] = mapped_column(Integer)


class RetrievalEvent(TimestampedModel, Base):
    __tablename__ = "retrieval_events"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    trace_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("rag_traces.id", ondelete="CASCADE"))
    stage: Mapped[str] = mapped_column(String(64))
    retriever: Mapped[str] = mapped_column(String(64))
    input_count: Mapped[int] = mapped_column(Integer, default=0)
    output_count: Mapped[int] = mapped_column(Integer, default=0)
    latency_ms: Mapped[int] = mapped_column(Integer, default=0)
    details_json: Mapped[dict[str, object]] = mapped_column(JSONB, default=dict)


class SecurityEvent(TimestampedModel, Base):
    __tablename__ = "security_events"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    trace_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("rag_traces.id", ondelete="CASCADE"))
    stage: Mapped[str] = mapped_column(String(64))
    risk: Mapped[str] = mapped_column(String(16))
    action: Mapped[str] = mapped_column(String(16))
    categories_json: Mapped[list[str]] = mapped_column(JSONB, default=list)
    text_fingerprint: Mapped[str | None] = mapped_column(String(80))
    redacted_evidence: Mapped[str | None] = mapped_column(Text)
