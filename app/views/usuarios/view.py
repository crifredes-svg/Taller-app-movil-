"""Pydantic view models for usuarios API requests and responses."""

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

EXTENSIONES_CORREO_PERMITIDAS = frozenset(
    {
        "ai", "app", "ar", "asia", "at", "au", "be", "biz", "bo", "br",
        "ca", "cat", "ch", "cl", "cn", "cloud", "co", "com", "coop", "cz",
        "de", "dev", "dk", "edu", "ec", "es", "eu", "fi", "fm", "fr", "gov",
        "hk", "hu", "id", "ie", "il", "in", "info", "int", "io", "is", "it",
        "jobs", "jp", "kr", "la", "ly", "me", "mil", "mobi", "museum", "mx",
        "name", "net", "nl", "no", "nz", "online", "org", "pe", "pl", "post",
        "pro", "pt", "py", "ru", "se", "sg", "site", "store", "tech", "tel",
        "th", "travel", "tr", "tv", "tw", "ua", "uk", "us", "uy", "ve",
        "xyz", "za",
    }
)


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

    @field_validator("correo")
    @classmethod
    def validar_extension_correo(cls, correo: EmailStr) -> EmailStr:
        extension = str(correo).rsplit("@", 1)[1].rsplit(".", 1)[-1].lower()
        if extension not in EXTENSIONES_CORREO_PERMITIDAS:
            raise ValueError("El correo debe usar una extensión permitida")
        return correo


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

class RegistroOut(UsuarioOut):
    detail: str = "Cuenta creada correctamente"

class RegistroPendienteOut(BaseModel):
    registro_id: str
    correo: str
    expira_en_minutos: int
    reenviar_en_segundos: int
    detail: str = "Te enviamos un código de verificación a tu correo"

class VerificacionRegistroIn(BaseModel):
    registro_id: str = Field(min_length=20, max_length=100)
    codigo: str = Field(pattern=r"^[0-9]{6}$")

class ReenvioCodigoIn(BaseModel):
    registro_id: str = Field(min_length=20, max_length=100)

class LoginIn(BaseModel):
    correo: EmailStr
    password: str = Field(min_length=1, max_length=128)

class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    usuario: UsuarioOut
    detail: str = "Inicio de sesión correcto"

class LogoutOut(BaseModel):
    detail: str

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
