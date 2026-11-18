"""Relevos database operations for the MVC model."""

from datetime import date, datetime, timedelta, timezone
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from ...repositories import SqlAlchemyRepository
from ..common import _commit_or_conflict
from ...domain.state_transitions import TRANSICIONES_RELEVO
from ..common import _duracion_horas
from .entity import SolicitudRelevo
from ..contactos.entity import ContactoConfianza
from ..usuarios.entity import Usuario
from ...views.relevos.view import SolicitudRelevoIn, SolicitudRelevoEstadoIn

def obtener_resumen_semana(current_user: Usuario, db: Session):
    repository = SqlAlchemyRepository(db)
    hoy = date.today()
    desde = hoy - timedelta(days=hoy.weekday())
    hasta_exclusiva = desde + timedelta(days=7)
    solicitudes = (
        repository.query(SolicitudRelevo)
        .filter(
            SolicitudRelevo.solicitante_id == current_user.id,
            SolicitudRelevo.fecha >= desde,
            SolicitudRelevo.fecha < hasta_exclusiva,
            SolicitudRelevo.estado.in_({"aceptada", "completada"}),
        )
        .all()
    )
    horas = round(sum(_duracion_horas(item) for item in solicitudes), 1)
    return {
        "desde": desde,
        "hasta": hasta_exclusiva - timedelta(days=1),
        "horas_protegidas": horas,
    }

def crear_solicitud_relevo(datos: SolicitudRelevoIn, current_user: Usuario, db: Session):
    repository = SqlAlchemyRepository(db)
    if current_user.id != datos.solicitante_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="El solicitante no existe",
        )
    usuario = repository.get(Usuario, datos.solicitante_id)

    if usuario is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="El solicitante no existe",
        )

    if datos.hora_fin <= datos.hora_inicio:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La hora de término debe ser posterior a la hora de inicio",
        )

    solicitud = SolicitudRelevo(**datos.model_dump())

    repository.add(solicitud)
    _commit_or_conflict(db, "No se pudo guardar la solicitud por un conflicto de datos")
    repository.refresh(solicitud)

    return solicitud

def listar_relevos_usuario(usuario_id: int, limit: int, offset: int, current_user: Usuario, db: Session):
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
        repository.query(SolicitudRelevo)
        .filter(
            (SolicitudRelevo.solicitante_id == usuario_id)
            | (SolicitudRelevo.cuidador_id == usuario_id)
        )
        .order_by(
            SolicitudRelevo.fecha.asc(),
            SolicitudRelevo.hora_inicio.asc(),
            SolicitudRelevo.id.asc(),
        )
        .offset(offset)
        .limit(limit)
        .all()
    )

def listar_relevos_disponibles(limit: int, offset: int, current_user: Usuario, db: Session):
    repository = SqlAlchemyRepository(db)
    propietarios = repository.query(ContactoConfianza.usuario_id).filter(
        ContactoConfianza.contacto_usuario_id == current_user.id
    )
    return (
        repository.query(SolicitudRelevo)
        .filter(
            SolicitudRelevo.solicitante_id.in_(propietarios),
            SolicitudRelevo.solicitante_id != current_user.id,
            SolicitudRelevo.estado == "pendiente",
            SolicitudRelevo.fecha >= date.today(),
        )
        .order_by(
            SolicitudRelevo.fecha.asc(),
            SolicitudRelevo.hora_inicio.asc(),
            SolicitudRelevo.id.asc(),
        )
        .offset(offset)
        .limit(limit)
        .all()
    )

def actualizar_relevo(relevo_id: int, datos: SolicitudRelevoEstadoIn, current_user: Usuario, db: Session):
    repository = SqlAlchemyRepository(db)
    relevo = repository.get(
        SolicitudRelevo,
        relevo_id,
        with_for_update=True,
    )

    if relevo is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Solicitud de relevo no encontrada",
        )

    if datos.estado == "aceptada":
        if datos.cuidador_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Solicitud de relevo no encontrada",
            )
        pertenece_a_red = (
            repository.query(ContactoConfianza.id)
            .filter(
                ContactoConfianza.usuario_id == relevo.solicitante_id,
                ContactoConfianza.contacto_usuario_id == current_user.id,
            )
            .first()
        )
        if pertenece_a_red is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Solicitud de relevo no encontrada",
            )
    elif relevo.cuidador_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Solicitud de relevo no encontrada",
        )

    if datos.estado not in TRANSICIONES_RELEVO.get(relevo.estado, set()):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Transición de relevo '{relevo.estado}' → '{datos.estado}' no permitida",
        )

    if datos.cuidador_id is not None:
        if datos.estado != "aceptada" and datos.cuidador_id != relevo.cuidador_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No se puede cambiar el cuidador asignado al completar el relevo",
            )
        cuidador = repository.get(Usuario, datos.cuidador_id)

        if cuidador is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="El cuidador no existe",
            )

        if cuidador.id == relevo.solicitante_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El solicitante no puede aceptar su propia solicitud",
            )

        relevo.cuidador_id = datos.cuidador_id

    if datos.estado == "aceptada" and relevo.cuidador_id is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Debe indicarse quién cubrirá el relevo",
        )

    relevo.estado = datos.estado

    _commit_or_conflict(db, "No se pudo actualizar la solicitud por un conflicto de datos")
    repository.refresh(relevo)

    return relevo
