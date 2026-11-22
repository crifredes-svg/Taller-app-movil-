"""Usuarios database operations for the MVC model."""

from datetime import date, datetime, timedelta, timezone
from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from ...repositories import SqlAlchemyRepository
from ..checkins.entity import CheckIn
from ..common import _commit_or_conflict
from ..contactos.entity import ContactoConfianza
from ..notificaciones.entity import Notificacion
from ..relevos.entity import SolicitudRelevo
from ..sos.entity import AlertaSOS
from ...security import hash_password
from ...security import ACCESS_TOKEN_SECONDS, create_access_token, verify_password
from .entity import Usuario, generar_codigo_usuario, utc_now_naive
from ...views.usuarios.view import (
    LoginIn,
    LogoutOut,
    PerfilUpdate,
    TokenOut,
    UsuarioIn,
)

def crear_usuario(datos: UsuarioIn, db: Session):
    repository = SqlAlchemyRepository(db)
    usuario_existente = (
        repository.query(Usuario)
        .filter(Usuario.correo == datos.correo)
        .first()
    )

    if usuario_existente:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El correo ya está registrado",
        )

    valores = datos.model_dump(exclude={"password"})
    usuario = Usuario(
        **valores,
        password_hash=hash_password(datos.password),
    )

    repository.add(usuario)
    _commit_or_conflict(db, "El correo o el código de usuario ya está en uso")
    repository.refresh(usuario)

    return usuario

def iniciar_sesion(datos: LoginIn, db: Session):
    repository = SqlAlchemyRepository(db)
    usuario = (
        repository.query(Usuario)
        .filter(Usuario.correo == datos.correo)
        .first()
    )
    password_hash = usuario.password_hash if usuario is not None else None
    password_valid = verify_password(datos.password, password_hash)
    if usuario is None or not password_valid:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Correo o contraseña incorrectos",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return TokenOut(
        access_token=create_access_token(usuario.id, usuario.token_version),
        expires_in=ACCESS_TOKEN_SECONDS,
        usuario=usuario,
    )

def cerrar_sesion(current_user: Usuario, db: Session):
    repository = SqlAlchemyRepository(db)
    actualizadas = (
        repository.query(Usuario)
        .filter(Usuario.id == current_user.id)
        .update(
            {Usuario.token_version: Usuario.token_version + 1},
            synchronize_session=False,
        )
    )
    if actualizadas != 1:
        repository.rollback()
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Autenticación requerida o token inválido",
            headers={"WWW-Authenticate": "Bearer"},
        )
    _commit_or_conflict(db, "No se pudo cerrar la sesión")
    return LogoutOut(detail="Sesión cerrada correctamente")

def actualizar_mi_perfil(datos: PerfilUpdate, current_user: Usuario, db: Session):
    repository = SqlAlchemyRepository(db)
    cambios = datos.model_dump(exclude_unset=True)
    if not cambios:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Debes enviar al menos un campo para actualizar",
        )

    for campo, valor in cambios.items():
        setattr(current_user, campo, valor)

    _commit_or_conflict(db, "No se pudo actualizar el perfil por un conflicto de datos")
    repository.refresh(current_user)
    return current_user


def eliminar_mi_cuenta(current_user: Usuario, db: Session) -> None:
    repository = SqlAlchemyRepository(db)
    usuario_id = current_user.id
    cuenta = repository.query(Usuario).filter(Usuario.id == usuario_id)
    if (
        cuenta.filter(Usuario.token_version == current_user.token_version)
        .with_for_update()
        .first()
        is None
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Autenticación requerida o token inválido",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        relevos_aceptados_como_cuidador = (
            repository.query(SolicitudRelevo)
            .filter(
                SolicitudRelevo.cuidador_id == usuario_id,
                SolicitudRelevo.solicitante_id != usuario_id,
                SolicitudRelevo.estado == "aceptada",
            )
            .with_for_update()
            .all()
        )
        for relevo in relevos_aceptados_como_cuidador:
            repository.add(
                Notificacion(
                    usuario_id=relevo.solicitante_id,
                    mensaje=(
                        "La persona que iba a cubrir tu relevo eliminó su "
                        "cuenta. El relevo ya no está disponible."
                    ),
                )
            )

        relevos_aceptados_como_solicitante = (
            repository.query(SolicitudRelevo)
            .filter(
                SolicitudRelevo.solicitante_id == usuario_id,
                SolicitudRelevo.cuidador_id.is_not(None),
                SolicitudRelevo.cuidador_id != usuario_id,
                SolicitudRelevo.estado == "aceptada",
            )
            .with_for_update()
            .all()
        )
        for relevo in relevos_aceptados_como_solicitante:
            repository.add(
                Notificacion(
                    usuario_id=relevo.cuidador_id,
                    mensaje=(
                        "La persona que solicitó el relevo eliminó su cuenta. "
                        "El relevo que habías aceptado ya no está disponible."
                    ),
                )
            )

        repository.query(CheckIn).filter(CheckIn.usuario_id == usuario_id).delete(
            synchronize_session=False
        )
        repository.query(AlertaSOS).filter(
            AlertaSOS.usuario_id == usuario_id
        ).delete(synchronize_session=False)
        repository.query(ContactoConfianza).filter(
            (ContactoConfianza.usuario_id == usuario_id)
            | (ContactoConfianza.contacto_usuario_id == usuario_id)
        ).delete(synchronize_session=False)
        repository.query(SolicitudRelevo).filter(
            (SolicitudRelevo.solicitante_id == usuario_id)
            | (SolicitudRelevo.cuidador_id == usuario_id)
        ).delete(synchronize_session=False)
        repository.query(Notificacion).filter(
            Notificacion.usuario_id == usuario_id
        ).delete(synchronize_session=False)
        cuenta.delete(synchronize_session=False)
        repository.commit()
    except IntegrityError as exc:
        repository.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="No se pudo eliminar la cuenta por un conflicto de datos",
        ) from exc
