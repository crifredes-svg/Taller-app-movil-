from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field


class UsuarioIn(BaseModel):
    """Datos de entrada para crear un usuario."""
    nombre: str = Field(min_length=2, max_length=80)
    correo: EmailStr  # valida formato de correo automáticamente
    tipo: str = Field(default="estudiante", pattern="^(estudiante|monitor|tutor)$")


class UsuarioOut(BaseModel):
    id: int
    nombre: str
    correo: str
    tipo: str

    model_config = {"from_attributes": True}


class EstadoIn(BaseModel):
    """Datos de entrada para un check-in de bienestar."""
    nivel: str = Field(pattern="^(bien|cansado|sobrepasado)$")
    nota: Optional[str] = Field(default=None, max_length=200)


class EstadoOut(BaseModel):
    id: int
    nivel: str
    nota: Optional[str]
    fecha: datetime
    usuario_id: int

    model_config = {"from_attributes": True}


class SolicitudIn(BaseModel):
    """Datos de entrada para crear una solicitud de apoyo."""
    descripcion: str = Field(min_length=10, max_length=200)
    solicitante_id: int


class SolicitudEstadoIn(BaseModel):
    """Datos de entrada para cambiar el estado de una solicitud."""
    estado: str = Field(pattern="^(aceptada|rechazada|completada)$")


class SolicitudOut(BaseModel):
    id: int
    descripcion: str
    estado: str
    fecha_creacion: datetime
    solicitante_id: int

    model_config = {"from_attributes": True}