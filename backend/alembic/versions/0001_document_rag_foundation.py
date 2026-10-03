"""create document and chunk tables with pgvector

Revision ID: 0001_document_rag_foundation
Revises: 
Create Date: 2026-10-03 00:00:00
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from pgvector.sqlalchemy import Vector


# revision identifiers, used by Alembic.
revision: str = "0001_document_rag_foundation"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")

    op.create_table(
        "documents",
        sa.Column("id", sa.Uuid(), primary_key=True, nullable=False),
        sa.Column("filename", sa.String(length=255), nullable=False),
        sa.Column("content_type", sa.String(length=100), nullable=False),
        sa.Column("metadata", sa.JSON(), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("status", sa.String(length=32), nullable=False, server_default="processed"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    op.create_table(
        "document_chunks",
        sa.Column("id", sa.Uuid(), primary_key=True, nullable=False),
        sa.Column("document_id", sa.Uuid(), sa.ForeignKey("documents.id", ondelete="CASCADE"), nullable=False),
        sa.Column("chunk_index", sa.Integer(), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("metadata", sa.JSON(), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("embedding_model", sa.String(length=128), nullable=False),
        sa.Column("embedding", Vector(1536), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint("document_id", "chunk_index", name="uq_document_chunk_index"),
    )

    op.create_index("ix_document_chunks_document_id", "document_chunks", ["document_id"])
    op.create_index(
        "ix_document_chunks_embedding",
        "document_chunks",
        ["embedding"],
        postgresql_using="ivfflat",
    )


def downgrade() -> None:
    op.drop_index("ix_document_chunks_embedding", table_name="document_chunks")
    op.drop_index("ix_document_chunks_document_id", table_name="document_chunks")
    op.drop_table("document_chunks")
    op.drop_table("documents")
