"""Compatibility exports for user model operations."""

from ..models.usuarios.model import (
    reenviar_codigo_registro,
    solicitar_registro,
    verificar_registro,
)

__all__ = ["reenviar_codigo_registro", "solicitar_registro", "verificar_registro"]
