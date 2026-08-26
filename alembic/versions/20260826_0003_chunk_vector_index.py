"""add fixed-dimension vector index for chunk embeddings

Revision ID: 20260826_0003
Revises: 20260826_0002
Create Date: 2026-08-26
"""

from alembic import op


revision = "20260826_0003"
down_revision = "20260826_0002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("ALTER TABLE chunks ALTER COLUMN embedding TYPE vector(128) USING embedding::vector(128)")
    op.execute(
        "CREATE INDEX ix_chunks_embedding_hnsw "
        "ON chunks USING hnsw (embedding vector_cosine_ops) WHERE embedding IS NOT NULL"
    )


def downgrade() -> None:
    op.execute("DROP INDEX ix_chunks_embedding_hnsw")
    op.execute("ALTER TABLE chunks ALTER COLUMN embedding TYPE vector USING embedding::vector")
