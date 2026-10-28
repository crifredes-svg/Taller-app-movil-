"""Trusted-contact router."""

from .router import (
    crear_contacto,
    crear_contacto_por_codigo,
    listar_contactos,
    obtener_balance_red,
    router_contactos,
)

__all__ = [
    "crear_contacto",
    "crear_contacto_por_codigo",
    "listar_contactos",
    "obtener_balance_red",
    "router_contactos",
]
