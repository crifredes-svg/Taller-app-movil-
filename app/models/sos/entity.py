"""SQLAlchemy entity for sos."""

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from ...database.connection import Base
from ..usuarios.entity import utc_now_naive

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
        default=utc_now_naive,
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
