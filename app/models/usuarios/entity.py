"""SQLAlchemy entity for usuarios."""

from datetime import datetime, timezone
from uuid import uuid4
from sqlalchemy import Column, DateTime, Integer, String, Text, text
from ...database.connection import Base

def utc_now_naive() -> datetime:
    """Retorna UTC sin tzinfo para compatibilidad con columnas MySQL DATETIME."""
    return datetime.now(timezone.utc).replace(tzinfo=None)

def generar_codigo_usuario() -> str:
    """Genera el código único que permite añadir al usuario a una red."""
    return uuid4().hex[:6].upper()

class Usuario(Base):
    """La persona cuidadora y las personas que pueden integrar su red."""

    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True)
    nombre = Column(String(80), nullable=False)
    correo = Column(String(120), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=True)
    token_version = Column(
        Integer,
        nullable=False,
        default=0,
        server_default=text("0"),
    )
    ocupacion = Column(String(100), nullable=True)
    tipo = Column(
        String(20),
        nullable=False,
        default="estudiante",
    )  # estudiante | red

    genero = Column(String(20), nullable=True)  # femenino | masculino
    codigo_unico = Column(
        String(8),
        unique=True,
        nullable=True,
        default=generar_codigo_usuario,
    )

    # Estos datos corresponden a la persona que cuida el usuario.
    # Son opcionales porque los integrantes de la red no necesariamente
    # tienen una persona a su cuidado.
    persona_cuidada_nombre = Column(String(80), nullable=True)
    persona_cuidada_edad = Column(Integer, nullable=True)


class RegistroPendiente(Base):
    """Datos de registro que esperan la verificación del correo."""

    __tablename__ = "registros_pendientes"

    id = Column(Integer, primary_key=True)
    token_hash = Column(String(64), unique=True, nullable=False)
    correo = Column(String(120), unique=True, nullable=False)
    datos = Column(Text, nullable=False)
    password_hash = Column(String(255), nullable=False)
    codigo_hash = Column(String(64), nullable=False)
    intentos = Column(Integer, nullable=False, default=0, server_default=text("0"))
    expira_en = Column(DateTime, nullable=False)
    enviado_en = Column(DateTime, nullable=False)
    creado_en = Column(DateTime, nullable=False, default=utc_now_naive, index=True)
