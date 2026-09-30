"""agregar_genero_codigo_y_vinculo_contacto

Revision ID: 47f6bba6ab15
Revises: e4d14b2b5a37
Create Date: 2026-09-30 01:20:47.371680

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# Identificadores de la migración.
revision: str = "47f6bba6ab15"
down_revision: Union[str, Sequence[str], None] = "e4d14b2b5a37"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Agrega los campos nuevos conservando los datos existentes."""

    with op.batch_alter_table(
        "usuarios",
        schema=None,
    ) as batch_op:
        batch_op.add_column(
            sa.Column(
                "genero",
                sa.String(length=20),
                nullable=True,
            )
        )
        batch_op.add_column(
            sa.Column(
                "codigo_unico",
                sa.String(length=8),
                nullable=True,
            )
        )
        batch_op.add_column(
            sa.Column(
                "persona_cuidada_nombre",
                sa.String(length=80),
                nullable=True,
            )
        )
        batch_op.add_column(
            sa.Column(
                "persona_cuidada_edad",
                sa.Integer(),
                nullable=True,
            )
        )
        batch_op.create_unique_constraint(
            "uq_usuarios_codigo_unico",
            ["codigo_unico"],
        )

    with op.batch_alter_table(
        "contactos_confianza",
        schema=None,
    ) as batch_op:
        batch_op.add_column(
            sa.Column(
                "contacto_usuario_id",
                sa.Integer(),
                nullable=True,
            )
        )
        batch_op.alter_column(
            "relacion",
            existing_type=sa.String(length=20),
            type_=sa.String(length=40),
            existing_nullable=False,
        )
        batch_op.create_foreign_key(
            "fk_contactos_confianza_contacto_usuario_id",
            "usuarios",
            ["contacto_usuario_id"],
            ["id"],
        )


def downgrade() -> None:
    """Revierte los campos agregados por esta migración."""

    with op.batch_alter_table(
        "contactos_confianza",
        schema=None,
    ) as batch_op:
        batch_op.drop_constraint(
            "fk_contactos_confianza_contacto_usuario_id",
            type_="foreignkey",
        )
        batch_op.alter_column(
            "relacion",
            existing_type=sa.String(length=40),
            type_=sa.String(length=20),
            existing_nullable=False,
        )
        batch_op.drop_column("contacto_usuario_id")

    with op.batch_alter_table(
        "usuarios",
        schema=None,
    ) as batch_op:
        batch_op.drop_constraint(
            "uq_usuarios_codigo_unico",
            type_="unique",
        )
        batch_op.drop_column("persona_cuidada_edad")
        batch_op.drop_column("persona_cuidada_nombre")
        batch_op.drop_column("codigo_unico")
        batch_op.drop_column("genero")