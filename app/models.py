from datetime import datetime

from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship

from .database import Base


class Usuario(Base):
    """Tabla usuarios: estudiantes y personas de confianza."""
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True)
    nombre = Column(String(80), nullable=False)
    correo = Column(String(120), unique=True, nullable=False)
    tipo = Column(String(20), nullable=False, default="estudiante")


class EstadoBienestar(Base):
    """Tabla de check-ins de bienestar. Relación 1:N con Usuario."""
    __tablename__ = "estados_bienestar"

    id = Column(Integer, primary_key=True)
    nivel = Column(String(20), nullable=False)  # bien | cansado | sobrepasado
    nota = Column(String(200), nullable=True)
    fecha = Column(DateTime, nullable=False, default=datetime.utcnow)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    usuario = relationship("Usuario", backref="estados")


class SolicitudApoyo(Base):
    """Tabla de solicitudes de apoyo. Relación 1:N con Usuario (solicitante)."""
    __tablename__ = "solicitudes"

    id = Column(Integer, primary_key=True)
    descripcion = Column(String(200), nullable=False)
    estado = Column(String(20), nullable=False, default="pendiente")  # pendiente | aceptada | rechazada | completada
    fecha_creacion = Column(DateTime, nullable=False, default=datetime.utcnow)
    solicitante_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    solicitante = relationship("Usuario", foreign_keys=[solicitante_id])