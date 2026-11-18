"""Usuarios database operations for the MVC model."""

from datetime import date, datetime, timedelta, timezone
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from ...repositories import SqlAlchemyRepository
from ..common import _commit_or_conflict
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
