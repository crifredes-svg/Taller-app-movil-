"""Compatibility exports for relief-request model operations."""

from ..models.relevos.model import (
    actualizar_relevo,
    crear_solicitud_relevo,
    listar_relevos_usuario,
    obtener_resumen_semana,
)

__all__ = [
    "actualizar_relevo",
    "crear_solicitud_relevo",
    "listar_relevos_usuario",
    "obtener_resumen_semana",
]
