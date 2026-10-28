"""Checkins database operations for the MVC model."""

from datetime import date, datetime, timedelta, timezone
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from ...repositories import SqlAlchemyRepository
from ..common import _commit_or_conflict
from ..common import _duracion_horas
from ..common import _dias_de_alta_carga
from .entity import CheckIn
from ..usuarios.entity import Usuario
from ...views.checkins.view import CheckInIn

def consultar_tendencia_carga(current_user: Usuario, db: Session):
    repository = SqlAlchemyRepository(db)
    ahora = datetime.now(timezone.utc).replace(tzinfo=None)
    fecha_inicio = ahora.date() - timedelta(days=4)
    fecha_inicio_utc = datetime.combine(fecha_inicio, datetime.min.time())
    dias_alta_carga = (
        repository.query(CheckIn)
        .with_entities(func.count(func.distinct(func.date(CheckIn.fecha))))
        .filter(
            CheckIn.usuario_id == current_user.id,
            CheckIn.fecha >= fecha_inicio_utc,
            CheckIn.fecha <= ahora,
            CheckIn.nivel.in_({"necesito_apoyo", "sobrepasada"}),
        )
        .scalar()
    )
    return {
        "dias_evaluados": 5,
        "dias_alta_carga": dias_alta_carga,
        "sugerir_pedir_apoyo": dias_alta_carga >= 3,
    }

def crear_checkin(usuario_id: int, datos: CheckInIn, current_user: Usuario, db: Session):
    repository = SqlAlchemyRepository(db)
    if current_user.id != usuario_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado",
        )
    usuario = repository.get(Usuario, usuario_id)

    if usuario is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado",
        )

    checkin = CheckIn(
        **datos.model_dump(),
        usuario_id=usuario_id,
    )

    repository.add(checkin)
    _commit_or_conflict(db, "No se pudo guardar el check-in por un conflicto de datos")
    repository.refresh(checkin)

    return checkin

def listar_checkins(usuario_id: int, limit: int, offset: int, current_user: Usuario, db: Session):
    repository = SqlAlchemyRepository(db)
    if current_user.id != usuario_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado",
        )
    usuario = repository.get(Usuario, usuario_id)

    if usuario is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado",
        )

    return (
        repository.query(CheckIn)
        .filter(CheckIn.usuario_id == usuario_id)
        .order_by(CheckIn.fecha.desc(), CheckIn.id.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )
