"""Compatibility exports for check-in model operations."""

from ..models.checkins.model import (
    consultar_tendencia_carga,
    crear_checkin,
    listar_checkins,
)

__all__ = [
    "consultar_tendencia_carga",
    "crear_checkin",
    "listar_checkins",
]
