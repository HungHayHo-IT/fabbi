"""add todo performance indexes

Revision ID: xxxxxxxxxxxx
Revises: a0790c76a129
Create Date: ...
"""

from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = "4d509292fb69"
down_revision: Union[str, None] = "a0790c76a129"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_index(
        "ix_todos_user_created_at",
        "todos",
        ["user_id", "created_at", "id"],
    )

    op.create_index(
        "ix_todos_user_completed_created_at",
        "todos",
        ["user_id", "completed", "created_at", "id"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_todos_user_completed_created_at",
        table_name="todos",
    )

    op.drop_index(
        "ix_todos_user_created_at",
        table_name="todos",
    )