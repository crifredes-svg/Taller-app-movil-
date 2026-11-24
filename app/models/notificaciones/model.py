"""Notification database operations."""

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from ...repositories import SqlAlchemyRepository
from ..usuarios.entity import Usuario
from .entity import Notificacion


def listar_notificaciones_pendientes(
    current_user: Usuario,
    limit: int,
    offset: int,
    db: Session,
) -> list[Notificacion]:
    repository = SqlAlchemyRepository(db)
    return (
        repository.query(Notificacion)
        .filter(
            Notificacion.usuario_id == current_user.id,
            Notificacion.leida.is_(False),
        )
        .order_by(Notificacion.fecha.desc(), Notificacion.id.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )


def marcar_notificacion_leida(
    notificacion_id: int,
    current_user: Usuario,
    db: Session,
) -> Notificacion:
    repository = SqlAlchemyRepository(db)
    notificacion = (
        repository.query(Notificacion)
        .filter(
            Notificacion.id == notificacion_id,
            Notificacion.usuario_id == current_user.id,
        )
        .with_for_update()
        .first()
    )
    if notificacion is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notificación no encontrada",
        )
    if notificacion.leida:
        return notificacion

    notificacion.leida = True
    repository.commit()
    repository.refresh(notificacion)
    return notificacion
