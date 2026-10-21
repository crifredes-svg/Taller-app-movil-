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

class RegistroOut(UsuarioOut):
    detail: str = "Cuenta creada correctamente"

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
