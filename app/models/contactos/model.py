"""Contactos database operations for the MVC model."""

from datetime import date, datetime, timedelta, timezone
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from ...repositories import SqlAlchemyRepository
from ..common import _commit_or_conflict
from ..common import _duracion_horas
from .entity import ContactoConfianza
from ..relevos.entity import SolicitudRelevo
from ..usuarios.entity import Usuario
from ...views.contactos.view import ContactoConfianzaIn, ContactoPorCodigoIn

def crear_contacto(usuario_id: int, datos: ContactoConfianzaIn, current_user: Usuario, db: Session):
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

    contacto = ContactoConfianza(
        **datos.model_dump(),
        usuario_id=usuario_id,
    )

    repository.add(contacto)
    _commit_or_conflict(db, "No se pudo guardar el contacto por un conflicto de datos")
    repository.refresh(contacto)

    return contacto

def crear_contacto_por_codigo(usuario_id: int, datos: ContactoPorCodigoIn, current_user: Usuario, db: Session):
    repository = SqlAlchemyRepository(db)
    if current_user.id != usuario_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado",
        )
    propietario = repository.get(Usuario, usuario_id)

    if propietario is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado",
        )

    usuario_contacto = (
        repository.query(Usuario)
        .filter(Usuario.codigo_unico == datos.codigo_unico)
        .first()
    )

    if usuario_contacto is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No existe un usuario asociado a ese código",
        )

    if usuario_contacto.id == usuario_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No puedes añadirte a tu propia red de confianza",
        )

    contacto_existente = (
        repository.query(ContactoConfianza)
        .filter(
            ContactoConfianza.usuario_id == usuario_id,
            ContactoConfianza.contacto_usuario_id
            == usuario_contacto.id,
        )
        .first()
    )

    if contacto_existente:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Esta persona ya pertenece a tu red de confianza",
        )

    contacto = ContactoConfianza(
        nombre=usuario_contacto.nombre,
        relacion=datos.relacion,
        apoyos=datos.apoyos or "",
        disponibilidad=datos.disponibilidad or "",
        usuario_id=usuario_id,
        contacto_usuario_id=usuario_contacto.id,
    )

    repository.add(contacto)
    _commit_or_conflict(db, "El contacto ya existe o hay un conflicto de datos")
    repository.refresh(contacto)

    return contacto

def obtener_balance_red(usuario_id: int, current_user: Usuario, db: Session):
    repository = SqlAlchemyRepository(db)
    if current_user.id != usuario_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado",
        )

    hoy = date.today()
    desde = hoy.replace(day=1)
    contactos = (
        repository.query(ContactoConfianza)
        .filter(ContactoConfianza.usuario_id == usuario_id)
        .order_by(ContactoConfianza.id.asc())
        .all()
    )
    ids_red = {
        contacto.contacto_usuario_id
        for contacto in contactos
        if contacto.contacto_usuario_id is not None
    }

    horas_por_usuario: dict[int, float] = {}
    if ids_red:
        solicitudes = (
            repository.query(SolicitudRelevo)
            .filter(
                SolicitudRelevo.solicitante_id == usuario_id,
                SolicitudRelevo.cuidador_id.in_(ids_red),
                SolicitudRelevo.estado == "completada",
                SolicitudRelevo.fecha >= desde,
                SolicitudRelevo.fecha <= hoy,
            )
            .all()
        )
        for solicitud in solicitudes:
            cuidador_id = solicitud.cuidador_id
            if cuidador_id is not None:
                horas_por_usuario[cuidador_id] = (
                    horas_por_usuario.get(cuidador_id, 0.0)
                    + _duracion_horas(solicitud)
                )

    filas = []
    usuarios_agregados: set[int] = set()
    for contacto in contactos:
        contacto_usuario_id = contacto.contacto_usuario_id
        if contacto_usuario_id is not None and contacto_usuario_id in usuarios_agregados:
            continue
        if contacto_usuario_id is not None:
            usuarios_agregados.add(contacto_usuario_id)
        filas.append(
            {
                "contacto_id": contacto.id,
                "nombre": contacto.nombre,
                "relacion": contacto.relacion,
                "horas_apoyo": round(
                    horas_por_usuario.get(contacto_usuario_id, 0.0),
                    1,
                ),
            }
        )

    total_horas = round(sum(horas_por_usuario.values()), 1)
    for fila in filas:
        fila["porcentaje"] = (
            round(fila["horas_apoyo"] / total_horas * 100, 1)
            if total_horas
            else 0.0
        )

    return {
        "desde": desde,
        "hasta": hoy,
        "total_horas": total_horas,
        "contactos": filas,
    }

def listar_contactos(usuario_id: int, limit: int, offset: int, current_user: Usuario, db: Session):
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
        repository.query(ContactoConfianza)
        .filter(ContactoConfianza.usuario_id == usuario_id)
        .order_by(ContactoConfianza.id.asc())
        .offset(offset)
        .limit(limit)
        .all()
    )
