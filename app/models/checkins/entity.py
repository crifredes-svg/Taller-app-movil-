"""SQLAlchemy entity for checkins."""

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from ...database.connection import Base
from ..usuarios.entity import utc_now_naive

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
        backref="checkins",
    )
