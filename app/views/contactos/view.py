"""Pydantic view models for contactos API requests and responses."""

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

class ContactoConfianzaIn(BaseModel):
    """
    Conserva el método anterior para crear un contacto introduciendo
    directamente sus datos.
    """

    nombre: str = Field(min_length=2, max_length=80)
    relacion: str = Field(min_length=2, max_length=40)
    apoyos: str = Field(min_length=2, max_length=200)
    disponibilidad: str = Field(min_length=2, max_length=120)

class ContactoPorCodigoIn(BaseModel):
    """
    Añade a una persona ya registrada usando su código único.
    """

    codigo_unico: str = Field(min_length=6, max_length=11)
    relacion: str = Field(min_length=2, max_length=40)
    apoyos: Optional[str] = Field(default=None, min_length=2, max_length=200)
    disponibilidad: Optional[str] = Field(default=None, min_length=2, max_length=120)

    @field_validator("codigo_unico", mode="before")
    @classmethod
    def normalizar_codigo(cls, codigo: str) -> str:
        codigo_normalizado = codigo.strip().upper()
        if codigo_normalizado.startswith("RC-"):
            codigo_normalizado = codigo_normalizado[3:]
        if not (
            len(codigo_normalizado) in {6, 8}
            and all(caracter in "0123456789ABCDEF" for caracter in codigo_normalizado)
        ):
            raise ValueError("El código debe tener el formato RC-XXXXXX")
        return codigo_normalizado

class ContactoConfianzaOut(BaseModel):
    id: int
    nombre: str
    relacion: str
    apoyos: str
    disponibilidad: str
    usuario_id: int
    contacto_usuario_id: Optional[int]

    model_config = {"from_attributes": True}

class BalanceContactoOut(BaseModel):
    contacto_id: int
    nombre: str
    relacion: str
    horas_apoyo: float
    porcentaje: float

class BalanceRedOut(BaseModel):
    desde: date
    hasta: date
    total_horas: float
    contactos: list[BalanceContactoOut]
