"""Add per-user token version for JWT logout revocation."""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "b8c0576e4a21"
down_revision: Union[str, Sequence[str], None] = "a36bf49d8c12"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "usuarios",
        sa.Column(
            "token_version",
            sa.Integer(),
            nullable=False,
            server_default=sa.text("0"),
        ),
    )


def downgrade() -> None:
    op.drop_column("usuarios", "token_version")
