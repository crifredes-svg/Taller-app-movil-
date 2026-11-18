"""Pydantic view models for relevos API requests and responses."""

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

class SolicitudRelevoIn(BaseModel):
    titulo: str = Field(min_length=3, max_length=80)
    tipo: str = Field(
        pattern="^(estudio|clases|compras|casa)$"
    )
    descripcion: str = Field(min_length=10, max_length=200)
    fecha: date
    hora_inicio: str = Field(
        pattern="^([01][0-9]|2[0-3]):[0-5][0-9]$"
    )
    hora_fin: str = Field(
        pattern="^([01][0-9]|2[0-3]):[0-5][0-9]$"
    )
    solicitante_id: int

    @field_validator("fecha")
    @classmethod
    def validar_fecha(cls, fecha_solicitada: date) -> date:
        if fecha_solicitada < date.today():
            raise ValueError(
                "La fecha de la solicitud no puede estar en el pasado"
            )
        return fecha_solicitada

class SolicitudRelevoEstadoIn(BaseModel):
    estado: str = Field(
        pattern="^(pendiente|aceptada|completada)$"
    )
    cuidador_id: Optional[int] = None

class SolicitudRelevoOut(BaseModel):
    id: int
    titulo: str
    tipo: str
    descripcion: str
    fecha: date
    hora_inicio: str
    hora_fin: str
    estado: str
    solicitante_id: int
    cuidador_id: Optional[int]

    model_config = {"from_attributes": True}

class ResumenSemanaOut(BaseModel):
    desde: date
    hasta: date
    horas_protegidas: float
