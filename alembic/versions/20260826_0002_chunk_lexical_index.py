"""add lexical index for ingested chunks

Revision ID: 20260826_0002
Revises: 20260824_0001
Create Date: 2026-08-26
"""

from alembic import op


revision = "20260826_0002"
down_revision = "20260824_0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        "ALTER TABLE chunks ADD COLUMN search_vector tsvector "
        "GENERATED ALWAYS AS (to_tsvector('simple', text)) STORED"
    )
    op.execute("CREATE INDEX ix_chunks_search_vector ON chunks USING gin (search_vector)")


def downgrade() -> None:
    op.execute("DROP INDEX ix_chunks_search_vector")
    op.execute("ALTER TABLE chunks DROP COLUMN search_vector")
