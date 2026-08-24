"""initial tenant-aware foundation schema

Revision ID: 20260824_0001
Revises:
Create Date: 2026-08-24
"""

from alembic import op
import sqlalchemy as sa
from pgvector.sqlalchemy import Vector
from sqlalchemy.dialects import postgresql


revision = "20260824_0001"
down_revision = None
branch_labels = None
depends_on = None


def _id_column() -> sa.Column[object]:
    return sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True)


def _timestamps() -> list[sa.Column[object]]:
    return [
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    ]


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")
    op.create_table("tenants", _id_column(), sa.Column("name", sa.String(255), nullable=False, unique=True), sa.Column("status", sa.String(32), nullable=False, server_default="active"), *_timestamps())
    op.create_table("users", _id_column(), sa.Column("external_subject", sa.String(255), nullable=False, unique=True), sa.Column("email", sa.String(320)), *_timestamps())
    op.create_table("tenant_memberships", _id_column(), sa.Column("tenant_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False), sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False), sa.Column("role", sa.String(64), nullable=False, server_default="member"), sa.Column("status", sa.String(32), nullable=False, server_default="active"), sa.UniqueConstraint("tenant_id", "user_id", name="uq_membership_tenant_user"), *_timestamps())
    op.create_table("documents", _id_column(), sa.Column("tenant_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False), sa.Column("owner_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False), sa.Column("source", sa.String(64), nullable=False), sa.Column("filename", sa.String(512), nullable=False), sa.Column("mime_type", sa.String(255), nullable=False), sa.Column("content_hash", sa.String(64), nullable=False), sa.Column("storage_key", sa.String(512), nullable=False, unique=True), sa.Column("state", sa.String(32), nullable=False, server_default="queued"), sa.Column("metadata_json", postgresql.JSONB, nullable=False, server_default=sa.text("'{}'::jsonb")), sa.Column("ingested_at", sa.DateTime(timezone=True)), sa.UniqueConstraint("tenant_id", "content_hash", name="uq_document_tenant_content_hash"), *_timestamps())
    op.create_index("ix_documents_tenant_state", "documents", ["tenant_id", "state"])
    op.create_table("document_permissions", _id_column(), sa.Column("document_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("documents.id", ondelete="CASCADE"), nullable=False), sa.Column("grantee_type", sa.String(32), nullable=False), sa.Column("grantee_id", sa.String(255), nullable=False), sa.Column("access_level", sa.String(32), nullable=False, server_default="read"), *_timestamps())
    op.create_index("ix_document_permissions_document", "document_permissions", ["document_id"])
    op.create_table("chunks", _id_column(), sa.Column("tenant_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False), sa.Column("document_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("documents.id", ondelete="CASCADE"), nullable=False), sa.Column("ordinal", sa.Integer, nullable=False), sa.Column("text", sa.Text, nullable=False), sa.Column("text_hash", sa.String(64), nullable=False), sa.Column("page", sa.Integer), sa.Column("section", sa.String(512)), sa.Column("token_count", sa.Integer, nullable=False), sa.Column("metadata_json", postgresql.JSONB, nullable=False, server_default=sa.text("'{}'::jsonb")), sa.Column("embedding", Vector()), sa.UniqueConstraint("document_id", "ordinal", name="uq_chunk_document_ordinal"), *_timestamps())
    op.create_index("ix_chunks_tenant_document", "chunks", ["tenant_id", "document_id"])
    op.create_table("ingestion_jobs", _id_column(), sa.Column("tenant_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False), sa.Column("document_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("documents.id", ondelete="CASCADE"), nullable=False), sa.Column("state", sa.String(32), nullable=False, server_default="queued"), sa.Column("attempts", sa.Integer, nullable=False, server_default="0"), sa.Column("safe_error", sa.Text), sa.Column("started_at", sa.DateTime(timezone=True)), sa.Column("finished_at", sa.DateTime(timezone=True)), *_timestamps())
    op.create_index("ix_ingestion_jobs_tenant_state", "ingestion_jobs", ["tenant_id", "state"])
    op.create_table("rag_traces", _id_column(), sa.Column("tenant_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False), sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id")), sa.Column("route", sa.String(255), nullable=False), sa.Column("outcome", sa.String(32), nullable=False, server_default="started"), sa.Column("configuration_json", postgresql.JSONB, nullable=False, server_default=sa.text("'{}'::jsonb")), sa.Column("total_latency_ms", sa.Integer), *_timestamps())
    op.create_index("ix_rag_traces_tenant_created", "rag_traces", ["tenant_id", "created_at"])
    op.create_table("retrieval_events", _id_column(), sa.Column("trace_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("rag_traces.id", ondelete="CASCADE"), nullable=False), sa.Column("stage", sa.String(64), nullable=False), sa.Column("retriever", sa.String(64), nullable=False), sa.Column("input_count", sa.Integer, nullable=False, server_default="0"), sa.Column("output_count", sa.Integer, nullable=False, server_default="0"), sa.Column("latency_ms", sa.Integer, nullable=False, server_default="0"), sa.Column("details_json", postgresql.JSONB, nullable=False, server_default=sa.text("'{}'::jsonb")), *_timestamps())
    op.create_table("security_events", _id_column(), sa.Column("trace_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("rag_traces.id", ondelete="CASCADE"), nullable=False), sa.Column("stage", sa.String(64), nullable=False), sa.Column("risk", sa.String(16), nullable=False), sa.Column("action", sa.String(16), nullable=False), sa.Column("categories_json", postgresql.JSONB, nullable=False, server_default=sa.text("'[]'::jsonb")), sa.Column("text_fingerprint", sa.String(80)), sa.Column("redacted_evidence", sa.Text), *_timestamps())


def downgrade() -> None:
    op.drop_table("security_events")
    op.drop_table("retrieval_events")
    op.drop_index("ix_rag_traces_tenant_created", table_name="rag_traces")
    op.drop_table("rag_traces")
    op.drop_index("ix_ingestion_jobs_tenant_state", table_name="ingestion_jobs")
    op.drop_table("ingestion_jobs")
    op.drop_index("ix_chunks_tenant_document", table_name="chunks")
    op.drop_table("chunks")
    op.drop_index("ix_document_permissions_document", table_name="document_permissions")
    op.drop_table("document_permissions")
    op.drop_index("ix_documents_tenant_state", table_name="documents")
    op.drop_table("documents")
    op.drop_table("tenant_memberships")
    op.drop_table("users")
    op.drop_table("tenants")
