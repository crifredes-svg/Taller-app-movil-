"""Add persistent notifications for account deletion events."""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "c13f7a2d9e40"
down_revision: Union[str, Sequence[str], None] = "b8c0576e4a21"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "notificaciones",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("usuario_id", sa.Integer(), nullable=False),
        sa.Column("mensaje", sa.String(length=255), nullable=False),
        sa.Column("fecha", sa.DateTime(), nullable=False),
        sa.Column(
            "leida",
            sa.Boolean(),
            server_default=sa.text("0"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["usuario_id"],
            ["usuarios.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_notificaciones_usuario_id",
        "notificaciones",
        ["usuario_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_notificaciones_usuario_id", table_name="notificaciones")
    op.drop_table("notificaciones")
