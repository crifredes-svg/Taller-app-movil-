"""estructura_inicial

Revision ID: e4d14b2b5a37
Revises: 
Create Date: 2026-09-30 01:08:46.136241

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e4d14b2b5a37'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "usuarios",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("nombre", sa.String(length=80), nullable=False),
        sa.Column("correo", sa.String(length=120), nullable=False),
        sa.Column("tipo", sa.String(length=20), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("correo"),
    )
    op.create_table(
        "checkins",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("nivel", sa.String(length=20), nullable=False),
        sa.Column("factores", sa.String(length=200), nullable=True),
        sa.Column("nota", sa.String(length=200), nullable=True),
        sa.Column("fecha", sa.DateTime(), nullable=False),
        sa.Column("usuario_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["usuario_id"], ["usuarios.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "contactos_confianza",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("nombre", sa.String(length=80), nullable=False),
        sa.Column("relacion", sa.String(length=20), nullable=False),
        sa.Column("apoyos", sa.String(length=200), nullable=False),
        sa.Column("disponibilidad", sa.String(length=120), nullable=False),
        sa.Column("usuario_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["usuario_id"], ["usuarios.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "solicitudes_relevo",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("titulo", sa.String(length=80), nullable=False),
        sa.Column("tipo", sa.String(length=20), nullable=False),
        sa.Column("descripcion", sa.String(length=200), nullable=False),
        sa.Column("fecha", sa.Date(), nullable=False),
        sa.Column("hora_inicio", sa.String(length=5), nullable=False),
        sa.Column("hora_fin", sa.String(length=5), nullable=False),
        sa.Column("estado", sa.String(length=20), nullable=False),
        sa.Column("solicitante_id", sa.Integer(), nullable=False),
        sa.Column("cuidador_id", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(["cuidador_id"], ["usuarios.id"]),
        sa.ForeignKeyConstraint(["solicitante_id"], ["usuarios.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "alertas_sos",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("mensaje", sa.String(length=200), nullable=False),
        sa.Column("estado", sa.String(length=20), nullable=False),
        sa.Column("fecha", sa.DateTime(), nullable=False),
        sa.Column("usuario_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["usuario_id"], ["usuarios.id"]),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("alertas_sos")
    op.drop_table("solicitudes_relevo")
    op.drop_table("contactos_confianza")
    op.drop_table("checkins")
    op.drop_table("usuarios")
