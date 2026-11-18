"""Compatibility exports for trusted-contact model operations."""

from ..models.contactos.model import (
    crear_contacto,
    crear_contacto_por_codigo,
    listar_contactos,
    obtener_balance_red,
)

__all__ = [
    "crear_contacto",
    "crear_contacto_por_codigo",
    "listar_contactos",
    "obtener_balance_red",
]
