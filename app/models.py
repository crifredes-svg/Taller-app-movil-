from datetime import datetime

from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Date
from sqlalchemy.orm import relationship

from .database import Base


class Usuario(Base):
    """Tabla usuarios: la estudiante cuidadora y las personas de su red."""
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True)
    nombre = Column(String(80), nullable=False)
    correo = Column(String(120), unique=True, nullable=False)
    tipo = Column(String(20), nullable=False, default="estudiante")  # estudiante | red


class CheckIn(Base):
    """Pantalla 'Mi Carga (Check-in)': nivel de sobrecarga, factores y nota privada."""
    __tablename__ = "checkins"

    id = Column(Integer, primary_key=True)
    nivel = Column(String(20), nullable=False)  # bien | algo_cansada | necesito_apoyo | sobrepasada
    factores = Column(String(200), nullable=True)  # certamenes, proyectos, dormir_mal, clases, respiro
    nota = Column(String(200), nullable=True)  # desahogo personal, solo visible para la usuaria
    fecha = Column(DateTime, nullable=False, default=datetime.utcnow)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    usuario = relationship("Usuario", backref="checkins")


class ContactoConfianza(Base):
    """Pantalla 'Mi Red de Confianza': quién la integra, qué apoyos da y cuándo está disponible."""
    __tablename__ = "contactos_confianza"

    id = Column(Integer, primary_key=True)
    nombre = Column(String(80), nullable=False)
    relacion = Column(String(20), nullable=False)  # familia | companero | vecino
    apoyos = Column(String(200), nullable=False)  # relevo_casa, compras, apoyo_academico
    disponibilidad = Column(String(120), nullable=False)  # ej. Martes y Jueves 17:00-20:00
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    usuario = relationship("Usuario", backref="contactos")


class SolicitudRelevo(Base):
    """Pantallas 'Solicitudes de Apoyo' y 'Calendario de Relevos'."""
    __tablename__ = "solicitudes_relevo"

    id = Column(Integer, primary_key=True)
    titulo = Column(String(80), nullable=False)  # ej. Relevo para ir a clases
    tipo = Column(String(20), nullable=False)  # estudio | clases | compras | casa
    descripcion = Column(String(200), nullable=False)
    fecha = Column(Date, nullable=False)
    hora_inicio = Column(String(5), nullable=False)  # ej. 09:30
    hora_fin = Column(String(5), nullable=False)     # ej. 13:00
    estado = Column(String(20), nullable=False, default="pendiente")  # pendiente | aceptada | completada
    solicitante_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    cuidador_id = Column(Integer, ForeignKey("usuarios.id"), nullable=True)
    solicitante = relationship("Usuario", foreign_keys=[solicitante_id])
    cuidador = relationship("Usuario", foreign_keys=[cuidador_id])


class AlertaSOS(Base):
    """Botón 'Activar SOS de Confianza' de la pantalla de inicio."""
    __tablename__ = "alertas_sos"

    id = Column(Integer, primary_key=True)
    mensaje = Column(String(200), nullable=False)
    estado = Column(String(20), nullable=False, default="activa")  # activa | atendida | cerrada
    fecha = Column(DateTime, nullable=False, default=datetime.utcnow)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    usuario = relationship("Usuario", backref="alertas")