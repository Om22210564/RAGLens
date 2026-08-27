"""add public trace key

Revision ID: 20260827_0004
Revises: 20260826_0003
Create Date: 2026-08-27
"""

from alembic import op
import sqlalchemy as sa


revision = "20260827_0004"
down_revision = "20260826_0003"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("rag_traces", sa.Column("trace_key", sa.String(40), nullable=True))
    op.execute("UPDATE rag_traces SET trace_key = 'legacy_' || replace(id::text, '-', '')")
    op.alter_column("rag_traces", "trace_key", nullable=False)
    op.create_unique_constraint("uq_rag_traces_trace_key", "rag_traces", ["trace_key"])


def downgrade() -> None:
    op.drop_constraint("uq_rag_traces_trace_key", "rag_traces", type_="unique")
    op.drop_column("rag_traces", "trace_key")
