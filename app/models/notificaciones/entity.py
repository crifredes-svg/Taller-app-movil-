"""SQLAlchemy entity for persistent user notifications."""

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, text
from ...database.connection import Base
from ..usuarios.entity import utc_now_naive


class Notificacion(Base):
    """Notification retained until its recipient marks it as read."""

    __tablename__ = "notificaciones"

    id = Column(Integer, primary_key=True)
    usuario_id = Column(
        Integer,
        ForeignKey("usuarios.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    mensaje = Column(String(255), nullable=False)
    fecha = Column(DateTime, nullable=False, default=utc_now_naive)
    leida = Column(Boolean, nullable=False, default=False, server_default=text("0"))
