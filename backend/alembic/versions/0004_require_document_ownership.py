"""require explicit document ownership

Revision ID: 0004_require_document_ownership
Revises: 0003_cosine_vector_index
Create Date: 2026-10-08
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "0004_require_document_ownership"
down_revision: Union[str, None] = "0003_cosine_vector_index"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Refuse rather than silently assigning legacy rows to an arbitrary tenant.
    bind = op.get_bind()
    orphan_count = bind.execute(
        sa.text("SELECT count(*) FROM documents WHERE user_id IS NULL")
    ).scalar_one()
    if orphan_count:
        raise RuntimeError(
            "Cannot require document ownership while orphaned documents exist; "
            "migrate or delete those rows explicitly first."
        )

    op.alter_column("documents", "user_id", existing_type=sa.Uuid(), nullable=False)


def downgrade() -> None:
    op.alter_column("documents", "user_id", existing_type=sa.Uuid(), nullable=True)
