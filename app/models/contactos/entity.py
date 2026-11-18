"""SQLAlchemy entity for contactos."""

from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from ...database.connection import Base

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
