"""Pydantic view models for sos API requests and responses."""

from datetime import date, datetime
from typing import Optional
from pydantic import (
    BaseModel,
    EmailStr,
    Field,
    field_serializer,
    field_validator,
    model_validator,
)

class AlertaSOSIn(BaseModel):
    mensaje: str = Field(min_length=5, max_length=200)
    usuario_id: int

class AlertaSOSEstadoIn(BaseModel):
    estado: str = Field(
        pattern="^(activa|atendida|cerrada)$"
    )

class AlertaSOSOut(BaseModel):
    id: int
    mensaje: str
    estado: str
    fecha: datetime
    usuario_id: int

    model_config = {"from_attributes": True}
