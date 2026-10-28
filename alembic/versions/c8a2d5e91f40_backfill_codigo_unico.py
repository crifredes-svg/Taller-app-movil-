"""Genera códigos únicos para usuarios previos a la función de códigos."""

from typing import Sequence, Union
from uuid import uuid4

from alembic import op
import sqlalchemy as sa


revision: str = "c8a2d5e91f40"
down_revision: Union[str, Sequence[str], None] = "47f6bba6ab15"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Asigna un código aleatorio sin colisionar con los ya existentes."""
    connection = op.get_bind()
    usuarios_sin_codigo = connection.execute(
        sa.text("SELECT id FROM usuarios WHERE codigo_unico IS NULL")
    ).scalars().all()
    codigos_usados = set(
        connection.execute(
            sa.text("SELECT codigo_unico FROM usuarios WHERE codigo_unico IS NOT NULL")
        ).scalars()
    )

    for usuario_id in usuarios_sin_codigo:
        codigo = uuid4().hex[:8].upper()
        while codigo in codigos_usados:
            codigo = uuid4().hex[:8].upper()

        connection.execute(
            sa.text(
                "UPDATE usuarios SET codigo_unico = :codigo WHERE id = :usuario_id"
            ),
            {"codigo": codigo, "usuario_id": usuario_id},
        )
        codigos_usados.add(codigo)


def downgrade() -> None:
    """No revierte el backfill para evitar borrar códigos de usuarios."""