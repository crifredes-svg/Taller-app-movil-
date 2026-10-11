"""Add password hash for user authentication."""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "f1d7a63c9b20"
down_revision: Union[str, Sequence[str], None] = "c8a2d5e91f40"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "usuarios",
        sa.Column("password_hash", sa.String(length=255), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("usuarios", "password_hash")