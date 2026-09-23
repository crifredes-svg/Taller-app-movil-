from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field


# ---------- Usuarios ----------

class UsuarioIn(BaseModel):
    nombre: str = Field(min_length=2, max_length=80)
    correo: EmailStr
    tipo: str = Field(default="estudiante", pattern="^(estudiante|red)$")


class UsuarioOut(BaseModel):
    id: int
    nombre: str
    correo: str
    tipo: str

    model_config = {"from_attributes": True}


# ---------- Mi carga / Check-in ----------

class CheckInIn(BaseModel):
    nivel: str = Field(
        pattern="^(bien|algo_cansada|necesito_apoyo|sobrepasada)$"
    )
    factores: Optional[str] = Field(default=None, max_length=200)
    nota: Optional[str] = Field(default=None, max_length=200)


class CheckInOut(BaseModel):
    id: int
    nivel: str
    factores: Optional[str]
    nota: Optional[str]
    fecha: datetime
    usuario_id: int

    model_config = {"from_attributes": True}


# ---------- Mi red de confianza ----------

class ContactoConfianzaIn(BaseModel):
    nombre: str = Field(min_length=2, max_length=80)
    relacion: str = Field(pattern="^(familia|companero|vecino)$")
    apoyos: str = Field(min_length=2, max_length=200)
    disponibilidad: str = Field(min_length=2, max_length=120)


class ContactoConfianzaOut(BaseModel):
    id: int
    nombre: str
    relacion: str
    apoyos: str
    disponibilidad: str
    usuario_id: int

    model_config = {"from_attributes": True}


# ---------- Solicitudes y calendario de relevos ----------

class SolicitudRelevoIn(BaseModel):
    titulo: str = Field(min_length=3, max_length=80)
    tipo: str = Field(pattern="^(estudio|clases|compras|casa)$")
    descripcion: str = Field(min_length=10, max_length=200)
    fecha: date
    hora_inicio: str = Field(pattern="^([01][0-9]|2[0-3]):[0-5][0-9]$")
    hora_fin: str = Field(pattern="^([01][0-9]|2[0-3]):[0-5][0-9]$")
    solicitante_id: int


class SolicitudRelevoEstadoIn(BaseModel):
    estado: str = Field(pattern="^(pendiente|aceptada|completada)$")
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


# ---------- SOS ----------

class AlertaSOSIn(BaseModel):
    mensaje: str = Field(min_length=5, max_length=200)
    usuario_id: int


class AlertaSOSEstadoIn(BaseModel):
    estado: str = Field(pattern="^(activa|atendida|cerrada)$")


class AlertaSOSOut(BaseModel):
    id: int
    mensaje: str
    estado: str
    fecha: datetime
    usuario_id: int

    model_config = {"from_attributes": True}