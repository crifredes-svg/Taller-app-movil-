"""User registration routes and HTTP controller."""

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from ...database import get_db
from ...models.usuarios.model import (
    reenviar_codigo_registro as ejecutar_reenviar_codigo_registro,
    solicitar_registro as ejecutar_solicitar_registro,
    verificar_registro as ejecutar_verificar_registro,
)
from ...views.usuarios.view import (
    ReenvioCodigoIn,
    RegistroOut,
    RegistroPendienteOut,
    UsuarioIn,
    VerificacionRegistroIn,
)

router_usuarios = APIRouter(
    prefix="/api/v1/usuarios",
    tags=["Usuarios"],
)

@router_usuarios.post(
    "",
    response_model=RegistroPendienteOut,
    status_code=status.HTTP_202_ACCEPTED,
)
def crear_usuario(
    datos: UsuarioIn,
    db: Session = Depends(get_db),
):
    return ejecutar_solicitar_registro(datos, db)


@router_usuarios.post(
    "/verificar",
    response_model=RegistroOut,
    status_code=status.HTTP_201_CREATED,
)
def verificar_registro(
    datos: VerificacionRegistroIn,
    db: Session = Depends(get_db),
):
    return ejecutar_verificar_registro(datos, db)


@router_usuarios.post(
    "/reenviar-codigo",
    response_model=RegistroPendienteOut,
    status_code=status.HTTP_202_ACCEPTED,
)
def reenviar_codigo_registro(
    datos: ReenvioCodigoIn,
    db: Session = Depends(get_db),
):
    return ejecutar_reenviar_codigo_registro(datos, db)
