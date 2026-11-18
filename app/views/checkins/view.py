"""Pydantic view models for checkins API requests and responses."""

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

class CheckInIn(BaseModel):
    nivel: str = Field(
        pattern="^(bien|algo_cansada|necesito_apoyo|sobrepasada)$"
    )
    factores: str | list[str] | None = None
    nota: Optional[str] = Field(
        default=None,
        max_length=200,
    )

    @field_validator("factores")
    @classmethod
    def normalizar_factores(cls, factores: str | list[str] | None) -> str | None:
        if isinstance(factores, list):
            opciones = [opcion.strip() for opcion in factores]
            if any(not opcion for opcion in opciones):
                raise ValueError("Los factores no pueden estar vacíos")
            factores = ",".join(opciones)
        if factores is not None and len(factores) > 200:
            raise ValueError("Los factores no pueden superar 200 caracteres")
        return factores

class CheckInOut(BaseModel):
    id: int
    nivel: str
    factores: Optional[str]
    nota: Optional[str]
    fecha: datetime
    usuario_id: int

    model_config = {"from_attributes": True}

class TendenciaCargaOut(BaseModel):
    dias_evaluados: int
    dias_alta_carga: int
    sugerir_pedir_apoyo: bool
