"""SQLAlchemy entity for relevos."""

from sqlalchemy import Column, Date, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from ...database.connection import Base

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
