"""Compatibility exports for model-level persistence helpers."""

from ..models.common import (
    _commit_or_conflict,
    _dias_de_alta_carga,
    _duracion_horas,
)

__all__ = [
    "_commit_or_conflict",
    "_dias_de_alta_carga",
    "_duracion_horas",
]
