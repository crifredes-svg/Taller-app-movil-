"""Sos database operations for the MVC model."""

from datetime import date, datetime, timedelta, timezone
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from ...repositories import SqlAlchemyRepository
from ..common import _commit_or_conflict
from ...domain.state_transitions import TRANSICIONES_SOS
from .entity import AlertaSOS
from ..contactos.entity import ContactoConfianza
from ..usuarios.entity import Usuario
from ...views.sos.view import AlertaSOSIn, AlertaSOSEstadoIn

def activar_sos(datos: AlertaSOSIn, current_user: Usuario, db: Session):
    repository = SqlAlchemyRepository(db)
    if current_user.id != datos.usuario_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado",
        )
    usuario = repository.get(Usuario, datos.usuario_id)

    if usuario is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado",
        )

    alerta = AlertaSOS(**datos.model_dump())

    repository.add(alerta)
    _commit_or_conflict(db, "No se pudo crear la alerta por un conflicto de datos")
    repository.refresh(alerta)

    return alerta

def listar_sos_recibidas(limit: int, offset: int, current_user: Usuario, db: Session):
    repository = SqlAlchemyRepository(db)
    usuarios_de_la_red = (
        repository.query(ContactoConfianza.usuario_id)
        .filter(
            ContactoConfianza.contacto_usuario_id == current_user.id
        )
    )
    return (
        repository.query(AlertaSOS)
        .filter(
            AlertaSOS.usuario_id.in_(usuarios_de_la_red),
            AlertaSOS.estado == "activa",
        )
        .order_by(AlertaSOS.fecha.desc(), AlertaSOS.id.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )

def listar_alertas_sos(usuario_id: int, limit: int, offset: int, current_user: Usuario, db: Session):
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
        repository.query(AlertaSOS)
        .filter(AlertaSOS.usuario_id == usuario_id)
        .order_by(AlertaSOS.fecha.desc(), AlertaSOS.id.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )

def actualizar_estado_sos(alerta_id: int, datos: AlertaSOSEstadoIn, current_user: Usuario, db: Session):
    repository = SqlAlchemyRepository(db)
    alerta = repository.get(
        AlertaSOS,
        alerta_id,
        with_for_update=True,
    )

    if alerta is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Alerta SOS no encontrada",
        )

    if datos.estado == "atendida":
        es_propietario = alerta.usuario_id == current_user.id
        pertenece_a_red = (
            repository.query(ContactoConfianza.id)
            .filter(
                ContactoConfianza.usuario_id == alerta.usuario_id,
                ContactoConfianza.contacto_usuario_id == current_user.id,
            )
            .first()
        )
        if not es_propietario and pertenece_a_red is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Alerta SOS no encontrada",
            )
    elif alerta.usuario_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Alerta SOS no encontrada",
        )

    if datos.estado not in TRANSICIONES_SOS.get(alerta.estado, set()):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Transición SOS '{alerta.estado}' → '{datos.estado}' no permitida",
        )

    alerta.estado = datos.estado

    _commit_or_conflict(db, "No se pudo actualizar la alerta por un conflicto de datos")
    repository.refresh(alerta)

    return alerta
