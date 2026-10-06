"""correct pgvector index for cosine retrieval

Revision ID: 0003_cosine_vector_index
Revises: 0002_accounts_conversations
Create Date: 2026-10-06
"""

from typing import Sequence, Union

from alembic import op


revision: str = "0003_cosine_vector_index"
down_revision: Union[str, None] = "0002_accounts_conversations"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("DROP INDEX IF EXISTS ix_document_chunks_embedding")
    op.execute(
        "CREATE INDEX ix_document_chunks_embedding "
        "ON document_chunks USING ivfflat (embedding vector_cosine_ops)"
    )


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS ix_document_chunks_embedding")
    op.execute(
        "CREATE INDEX ix_document_chunks_embedding "
        "ON document_chunks USING ivfflat (embedding)"
    )
