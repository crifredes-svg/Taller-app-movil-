"""Add pending registrations verified by email code."""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "d5b3e8f1a2c7"
down_revision: Union[str, Sequence[str], None] = "c13f7a2d9e40"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "registros_pendientes",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("token_hash", sa.String(length=64), nullable=False),
        sa.Column("correo", sa.String(length=120), nullable=False),
        sa.Column("datos", sa.Text(), nullable=False),
        sa.Column("password_hash", sa.String(length=255), nullable=False),
        sa.Column("codigo_hash", sa.String(length=64), nullable=False),
        sa.Column(
            "intentos",
            sa.Integer(),
            server_default=sa.text("0"),
            nullable=False,
        ),
        sa.Column("expira_en", sa.DateTime(), nullable=False),
        sa.Column("enviado_en", sa.DateTime(), nullable=False),
        sa.Column("creado_en", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("correo"),
        sa.UniqueConstraint("token_hash"),
    )
    op.create_index(
        "ix_registros_pendientes_creado_en",
        "registros_pendientes",
        ["creado_en"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        "ix_registros_pendientes_creado_en",
        table_name="registros_pendientes",
    )
    op.drop_table("registros_pendientes")
