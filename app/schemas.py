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


# ---------- Usuarios ----------

class UsuarioIn(BaseModel):
    nombre: str = Field(min_length=2, max_length=80)
    correo: EmailStr
    password: str = Field(min_length=12, max_length=128)
    ocupacion: Optional[str] = Field(default=None, min_length=2, max_length=100)
    tipo: str = Field(
        default="estudiante",
        pattern="^(estudiante|red)$",
    )
    genero: Optional[str] = Field(
        default=None,
        pattern="^(femenino|masculino)$",
    )
    persona_cuidada_nombre: Optional[str] = Field(
        default=None,
        min_length=2,
        max_length=80,
    )
    persona_cuidada_edad: Optional[int] = Field(
        default=None,
        ge=0,
        le=130,
    )


class UsuarioOut(BaseModel):
    id: int
    nombre: str
    correo: str
    ocupacion: Optional[str]
    tipo: str
    genero: Optional[str]
    codigo_unico: Optional[str]
    persona_cuidada_nombre: Optional[str]
    persona_cuidada_edad: Optional[int]

    model_config = {"from_attributes": True}

    @field_serializer("codigo_unico")
    def serializar_codigo_unico(self, codigo: Optional[str]) -> Optional[str]:
        if codigo is not None and len(codigo) == 6:
            return f"RC-{codigo}"
        return codigo


# ---------- Mi carga / Check-in ----------

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


# ---------- Mi red de confianza ----------

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


# ---------- Solicitudes y calendario de relevos ----------

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


# ---------- SOS ----------

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


class LoginIn(BaseModel):
    correo: EmailStr
    password: str = Field(min_length=1, max_length=128)


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    usuario: UsuarioOut


class PerfilUpdate(BaseModel):
    nombre: Optional[str] = Field(default=None, min_length=2, max_length=80)
    ocupacion: Optional[str] = Field(default=None, min_length=2, max_length=100)
    tipo: Optional[str] = Field(default=None, pattern="^(estudiante|red)$")
    genero: Optional[str] = Field(
        default=None,
        pattern="^(femenino|masculino)$",
    )
    persona_cuidada_nombre: Optional[str] = Field(
        default=None,
        min_length=2,
        max_length=80,
    )
    persona_cuidada_edad: Optional[int] = Field(default=None, ge=0, le=130)

    @model_validator(mode="after")
    def rechazar_nulos_en_campos_requeridos(self):
        for campo in ("nombre", "tipo"):
            if campo in self.model_fields_set and getattr(self, campo) is None:
                raise ValueError(f"{campo} no puede ser null")
        return self


class HealthOut(BaseModel):
    status: str