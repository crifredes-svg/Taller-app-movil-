from datetime import datetime
from uuid import uuid4

from sqlalchemy import Column, Date, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from .database import Base


def generar_codigo_usuario() -> str:
    """Genera el código único que permite añadir al usuario a una red."""
    return uuid4().hex[:8].upper()


class Usuario(Base):
    """La persona cuidadora y las personas que pueden integrar su red."""

    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True)
    nombre = Column(String(80), nullable=False)
    correo = Column(String(120), unique=True, nullable=False)
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


class CheckIn(Base):
    """Nivel de sobrecarga, factores seleccionados y nota privada."""

    __tablename__ = "checkins"

    id = Column(Integer, primary_key=True)
    nivel = Column(
        String(20),
        nullable=False,
    )  # bien | algo_cansada | necesito_apoyo | sobrepasada

    factores = Column(
        String(200),
        nullable=True,
    )  # certamenes, proyectos, dormir_mal, clases, respiro

    nota = Column(
        String(200),
        nullable=True,
    )  # Desahogo personal; solo visible para el usuario.

    fecha = Column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
    )

    usuario_id = Column(
        Integer,
        ForeignKey("usuarios.id"),
        nullable=False,
    )

    usuario = relationship(
        "Usuario",
        foreign_keys=[usuario_id],
        backref="checkins",
    )


class ContactoConfianza(Base):
    """Persona perteneciente a la red de confianza de un usuario."""

    __tablename__ = "contactos_confianza"

    id = Column(Integer, primary_key=True)

    # Se conservan los campos anteriores para no perder los contactos
    # que ya existen en la base de datos.
    nombre = Column(String(80), nullable=False)
    relacion = Column(String(40), nullable=False)
    apoyos = Column(String(200), nullable=False)
    disponibilidad = Column(String(120), nullable=False)

    # Usuario propietario de la red de confianza.
    usuario_id = Column(
        Integer,
        ForeignKey("usuarios.id"),
        nullable=False,
    )

    # Usuario encontrado mediante codigo_unico. Es opcional para mantener
    # compatibles los contactos creados antes de incorporar los códigos.
    contacto_usuario_id = Column(
        Integer,
        ForeignKey("usuarios.id"),
        nullable=True,
    )

    usuario = relationship(
        "Usuario",
        foreign_keys=[usuario_id],
        backref="contactos",
    )

    contacto_usuario = relationship(
        "Usuario",
        foreign_keys=[contacto_usuario_id],
    )


class SolicitudRelevo(Base):
    """Solicitudes de apoyo y eventos del calendario de relevos."""

    __tablename__ = "solicitudes_relevo"

    id = Column(Integer, primary_key=True)
    titulo = Column(String(80), nullable=False)
    tipo = Column(
        String(20),
        nullable=False,
    )  # estudio | clases | compras | casa

    descripcion = Column(String(200), nullable=False)
    fecha = Column(Date, nullable=False)
    hora_inicio = Column(String(5), nullable=False)
    hora_fin = Column(String(5), nullable=False)

    estado = Column(
        String(20),
        nullable=False,
        default="pendiente",
    )  # pendiente | aceptada | completada

    solicitante_id = Column(
        Integer,
        ForeignKey("usuarios.id"),
        nullable=False,
    )

    cuidador_id = Column(
        Integer,
        ForeignKey("usuarios.id"),
        nullable=True,
    )

    solicitante = relationship(
        "Usuario",
        foreign_keys=[solicitante_id],
    )

    cuidador = relationship(
        "Usuario",
        foreign_keys=[cuidador_id],
    )


class AlertaSOS(Base):
    """Alerta generada por el botón SOS de confianza."""

    __tablename__ = "alertas_sos"

    id = Column(Integer, primary_key=True)
    mensaje = Column(String(200), nullable=False)

    estado = Column(
        String(20),
        nullable=False,
        default="activa",
    )  # activa | atendida | cerrada

    fecha = Column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
    )

    usuario_id = Column(
        Integer,
        ForeignKey("usuarios.id"),
        nullable=False,
    )

    usuario = relationship(
        "Usuario",
        foreign_keys=[usuario_id],
        backref="alertas",
    )