"""Usuarios database operations for the MVC model."""

import json
import math
import secrets
from datetime import date, datetime, timedelta, timezone
from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from ...correo import CorreoNoEnviadoError, enviar_codigo_verificacion
from ...repositories import SqlAlchemyRepository
from ..checkins.entity import CheckIn
from ..common import _commit_or_conflict
from ..contactos.entity import ContactoConfianza
from ..notificaciones.entity import Notificacion
from ..relevos.entity import SolicitudRelevo
from ..sos.entity import AlertaSOS
from ...security import (
    hash_password,
    hash_registration_token,
    hash_verification_code,
    verify_verification_code,
)
from ...security import ACCESS_TOKEN_SECONDS, create_access_token, verify_password
from .entity import RegistroPendiente, Usuario, generar_codigo_usuario, utc_now_naive
from ...views.usuarios.view import (
    LoginIn,
    LogoutOut,
    PerfilUpdate,
    ReenvioCodigoIn,
    RegistroPendienteOut,
    TokenOut,
    UsuarioIn,
    VerificacionRegistroIn,
)

CODIGO_VERIFICACION_MINUTOS = 35
CODIGO_VERIFICACION_MAX_INTENTOS = 4
REENVIO_CODIGO_SEGUNDOS = 60
REGISTRO_PENDIENTE_HORAS = 24


def _validar_correo_disponible(repository: SqlAlchemyRepository, correo: str) -> None:
    if repository.query(Usuario).filter(Usuario.correo == correo).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El correo ya está registrado",
        )


def _validar_espera_reenvio(registro: RegistroPendiente, ahora: datetime) -> None:
    transcurrido = (ahora - registro.enviado_en).total_seconds()
    espera = math.ceil(REENVIO_CODIGO_SEGUNDOS - transcurrido)
    if espera > 0:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Espera {espera} segundos antes de pedir otro código",
            headers={"Retry-After": str(espera)},
        )


def _enviar_nuevo_codigo(
    db: Session,
    registro: RegistroPendiente,
    ahora: datetime,
) -> None:
    repository = SqlAlchemyRepository(db)
    codigo = f"{secrets.randbelow(1_000_000):06d}"
    registro.codigo_hash = hash_verification_code(registro.token_hash, codigo)
    registro.intentos = 0
    registro.enviado_en = ahora
    registro.expira_en = ahora + timedelta(minutes=CODIGO_VERIFICACION_MINUTOS)
    try:
        repository.flush()
    except IntegrityError as exc:
        repository.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Ya hay un registro en curso para este correo. Intenta nuevamente",
        ) from exc

    # Si el correo no sale, se revierte para no dejar un código que nadie recibió.
    try:
        enviar_codigo_verificacion(
            registro.correo,
            codigo,
            CODIGO_VERIFICACION_MINUTOS,
        )
    except CorreoNoEnviadoError as exc:
        repository.rollback()
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=(
                "No pudimos enviar el código de verificación. "
                "Intenta nuevamente más tarde"
            ),
        ) from exc
    _commit_or_conflict(db, "No se pudo guardar el registro pendiente")


def _respuesta_registro_pendiente(registro_id: str, correo: str) -> RegistroPendienteOut:
    return RegistroPendienteOut(
        registro_id=registro_id,
        correo=correo,
        expira_en_minutos=CODIGO_VERIFICACION_MINUTOS,
        reenviar_en_segundos=REENVIO_CODIGO_SEGUNDOS,
    )


def _obtener_registro_pendiente(
    repository: SqlAlchemyRepository,
    registro_id: str,
) -> RegistroPendiente:
    limite = utc_now_naive() - timedelta(hours=REGISTRO_PENDIENTE_HORAS)
    registro = (
        repository.query(RegistroPendiente)
        .filter(RegistroPendiente.token_hash == hash_registration_token(registro_id))
        .with_for_update()
        .first()
    )
    if registro is None or registro.creado_en < limite:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="El registro no existe o expiró. Vuelve a registrarte",
        )
    return registro


def solicitar_registro(datos: UsuarioIn, db: Session) -> RegistroPendienteOut:
    repository = SqlAlchemyRepository(db)
    _validar_correo_disponible(repository, datos.correo)
    password_hash = hash_password(datos.password)
    ahora = utc_now_naive()

    repository.query(RegistroPendiente).filter(
        RegistroPendiente.creado_en
        < ahora - timedelta(hours=REGISTRO_PENDIENTE_HORAS)
    ).delete(synchronize_session=False)

    # Un nuevo registro con el mismo correo invalida el registro_id anterior.
    anterior = (
        repository.query(RegistroPendiente)
        .filter(RegistroPendiente.correo == datos.correo)
        .with_for_update()
        .first()
    )
    if anterior is not None:
        _validar_espera_reenvio(anterior, ahora)
        repository.delete(anterior)
        repository.flush()

    registro_id = secrets.token_urlsafe(32)
    registro = RegistroPendiente(
        token_hash=hash_registration_token(registro_id),
        correo=datos.correo,
        datos=json.dumps(datos.model_dump(exclude={"correo", "password"})),
        password_hash=password_hash,
        creado_en=ahora,
    )
    repository.add(registro)
    _enviar_nuevo_codigo(db, registro, ahora)
    return _respuesta_registro_pendiente(registro_id, datos.correo)


def verificar_registro(datos: VerificacionRegistroIn, db: Session) -> Usuario:
    repository = SqlAlchemyRepository(db)
    registro = _obtener_registro_pendiente(repository, datos.registro_id)
    if registro.intentos >= CODIGO_VERIFICACION_MAX_INTENTOS:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Superaste los intentos permitidos. Pide un código nuevo",
        )
    if utc_now_naive() >= registro.expira_en:
        raise HTTPException(
            status_code=status.HTTP_410_GONE,
            detail="El código expiró. Pide un código nuevo",
        )

    if not verify_verification_code(
        registro.token_hash,
        datos.codigo,
        registro.codigo_hash,
    ):
        registro.intentos += 1
        restantes = CODIGO_VERIFICACION_MAX_INTENTOS - registro.intentos
        _commit_or_conflict(db, "No se pudo registrar el intento")
        if restantes == 0:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=(
                    "Código incorrecto. Superaste los intentos permitidos; "
                    "pide un código nuevo"
                ),
            )
        intentos = "intento" if restantes == 1 else "intentos"
        queda = "queda" if restantes == 1 else "quedan"
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Código incorrecto. Te {queda} {restantes} {intentos}",
        )

    usuario = Usuario(
        **json.loads(registro.datos),
        correo=registro.correo,
        password_hash=registro.password_hash,
    )
    repository.add(usuario)
    repository.delete(registro)
    _commit_or_conflict(db, "El correo o el código de usuario ya está en uso")
    repository.refresh(usuario)
    return usuario


def reenviar_codigo_registro(
    datos: ReenvioCodigoIn,
    db: Session,
) -> RegistroPendienteOut:
    repository = SqlAlchemyRepository(db)
    registro = _obtener_registro_pendiente(repository, datos.registro_id)
    ahora = utc_now_naive()
    _validar_espera_reenvio(registro, ahora)
    correo = registro.correo
    _enviar_nuevo_codigo(db, registro, ahora)
    return _respuesta_registro_pendiente(datos.registro_id, correo)

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
