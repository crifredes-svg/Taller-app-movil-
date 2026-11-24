"""Notification routes and HTTP controller."""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from ...database import get_db
from ...models.notificaciones.model import (
    listar_notificaciones_pendientes as ejecutar_listar_notificaciones_pendientes,
)
from ...models.notificaciones.model import (
    marcar_notificacion_leida as ejecutar_marcar_notificacion_leida,
)
from ...models.usuarios.model import Usuario
from ...security import get_current_user
from ...views.notificaciones.view import NotificacionOut

router_notificaciones = APIRouter(
    prefix="/api/v1/notificaciones",
    tags=["Notificaciones"],
)


@router_notificaciones.get("", response_model=list[NotificacionOut])
def listar_notificaciones_pendientes(
    limit: int = Query(default=100, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return ejecutar_listar_notificaciones_pendientes(
        current_user,
        limit,
        offset,
        db,
    )


@router_notificaciones.patch("/{notificacion_id}/leida", response_model=NotificacionOut)
def marcar_notificacion_leida(
    notificacion_id: int,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return ejecutar_marcar_notificacion_leida(notificacion_id, current_user, db)
