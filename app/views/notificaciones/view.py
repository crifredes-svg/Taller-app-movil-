"""Pydantic response views for notifications."""

from datetime import datetime
from pydantic import BaseModel


class NotificacionOut(BaseModel):
    id: int
    mensaje: str
    fecha: datetime
    leida: bool

    model_config = {"from_attributes": True}
